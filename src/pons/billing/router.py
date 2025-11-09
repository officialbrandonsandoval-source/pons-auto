"""Billing API endpoints."""

from typing import Annotated, Optional, Union, List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
import stripe
import os
import json

from pons.auth import User
from pons.auth.router import get_current_active_user
from pons.billing import (
    PLANS,
    get_plan_details,
    create_checkout_session,
    check_subscription_status,
    create_customer_portal_session,
    record_usage,
    check_limit,
    get_usage_stats,
    SubscriptionPlan
)
from pons.auth import update_user_subscription


router = APIRouter()


class CheckoutRequest(BaseModel):
    """Request to create checkout session."""
    plan_id: str
    success_url: str = "https://ponsauto.com/success"
    cancel_url: str = "https://ponsauto.com/pricing"


class CheckoutResponse(BaseModel):
    """Checkout session response."""
    checkout_url: str
    session_id: str


class UsageCheckRequest(BaseModel):
    """Request to check feature usage limit."""
    feature: str


class UsageCheckResponse(BaseModel):
    """Usage check response."""
    allowed: bool
    message: Optional[str] = None
    current_usage: int
    limit: Union[int, str]


@router.get("/plans", response_model=List[SubscriptionPlan])
async def list_plans() -> List[SubscriptionPlan]:
    """
    List all available subscription plans.
    
    Returns:
        List of subscription plans
    """
    plans = []
    
    for plan_id in PLANS.keys():
        plan = get_plan_details(plan_id)
        if plan:
            plans.append(plan)
    
    return plans


@router.get("/plans/{plan_id}", response_model=SubscriptionPlan)
async def get_plan(plan_id: str) -> SubscriptionPlan:
    """
    Get details for a specific plan.
    
    Args:
        plan_id: Plan identifier
    
    Returns:
        Plan details
    
    Raises:
        HTTPException: If plan not found
    """
    plan = get_plan_details(plan_id)
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    return plan


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    request: CheckoutRequest,
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> CheckoutResponse:
    """
    Create Stripe checkout session for subscription.
    
    Args:
        request: Checkout request with plan ID
        current_user: Current authenticated user
    
    Returns:
        Checkout session URL
    
    Raises:
        HTTPException: If plan invalid or Stripe error
    """
    try:
        session = create_checkout_session(
            plan_id=request.plan_id,
            customer_email=current_user.email,
            success_url=request.success_url,
            cancel_url=request.cancel_url
        )
        
        return CheckoutResponse(
            checkout_url=session.checkout_url,
            session_id=session.session_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/webhook")
async def stripe_webhook(request: Request) -> dict:
    """
    Handle Stripe webhooks for subscription events.
    
    Args:
        request: FastAPI request with webhook payload
    
    Returns:
        Status response
    
    Raises:
        HTTPException: If webhook signature invalid
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        # In development, accept webhooks without verification
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    else:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except Exception as e:
            # Handle stripe signature verification errors
            if "signature" in str(e).lower():
                raise HTTPException(status_code=400, detail="Invalid signature")
            raise
    
    # Handle different event types
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Update user subscription
        customer_email = session['customer_email']
        plan_id = session['metadata'].get('plan_id', 'professional')
        customer_id = session['customer']
        
        update_user_subscription(customer_email, plan_id, customer_id)
    
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        # Handle subscription updates
        pass
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        customer_id = subscription['customer']
        
        # Downgrade user to trial
        # Would need to look up user by customer_id in production
        pass
    
    return {"status": "success"}


@router.get("/subscription")
async def get_subscription(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> dict:
    """
    Get current user's subscription details.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Subscription details
    """
    plan = get_plan_details(current_user.subscription_plan)
    
    subscription_data = {
        "plan": plan,
        "status": current_user.subscription_status,
        "stripe_customer_id": current_user.stripe_customer_id
    }
    
    # If user has Stripe customer ID, check Stripe for details
    if current_user.stripe_customer_id:
        stripe_status = check_subscription_status(current_user.stripe_customer_id)
        subscription_data.update(stripe_status)
    
    return subscription_data


@router.post("/portal")
async def create_portal(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> dict:
    """
    Create Stripe customer portal session for managing subscription.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Portal URL
    
    Raises:
        HTTPException: If user has no Stripe customer ID
    """
    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found"
        )
    
    try:
        portal_url = create_customer_portal_session(
            stripe_customer_id=current_user.stripe_customer_id,
            return_url="https://ponsauto.com/account"
        )
        
        return {"portal_url": portal_url}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/check-limit", response_model=UsageCheckResponse)
async def check_feature_limit(
    request: UsageCheckRequest,
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> UsageCheckResponse:
    """
    Check if user can use a feature based on their plan limits.
    
    Args:
        request: Feature to check
        current_user: Current authenticated user
    
    Returns:
        Usage check result
    """
    allowed, message = check_limit(
        user_email=current_user.email,
        plan_id=current_user.subscription_plan,
        feature=request.feature
    )
    
    from pons.billing import get_usage, PLANS
    current_usage = get_usage(current_user.email, request.feature)
    plan = PLANS.get(current_user.subscription_plan, {})
    limit = plan.get("limits", {}).get(request.feature, 0)
    
    return UsageCheckResponse(
        allowed=allowed,
        message=message,
        current_usage=current_usage,
        limit=limit if limit != -1 else "unlimited"
    )


@router.get("/usage")
async def get_usage(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> dict:
    """
    Get usage statistics for current user.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Usage stats for all features
    """
    stats = get_usage_stats(
        user_email=current_user.email,
        plan_id=current_user.subscription_plan
    )
    
    return {
        "plan": current_user.subscription_plan,
        "usage": stats
    }
