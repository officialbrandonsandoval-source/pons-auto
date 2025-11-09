"""Billing and subscription management for PONS AUTO."""

from datetime import datetime
from typing import Optional
import os

import stripe
from pydantic import BaseModel


# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

# Subscription plans
PLANS = {
    "trial": {
        "name": "Free Trial",
        "price": 0,
        "price_id": None,
        "limits": {
            "vehicles_per_month": 2,
            "ai_backgrounds": 5,
            "ai_descriptions": 2,
            "platforms": ["facebook"]
        },
        "features": [
            "2 vehicles/month",
            "5 AI backgrounds",
            "2 AI descriptions",
            "Facebook Marketplace only",
            "Email support"
        ]
    },
    "starter": {
        "name": "Starter",
        "price": 49,
        "price_id": os.getenv("STRIPE_STARTER_PRICE_ID", "price_starter"),
        "limits": {
            "vehicles_per_month": 5,
            "ai_backgrounds": 50,
            "ai_descriptions": 5,
            "platforms": ["facebook"]
        },
        "features": [
            "5 vehicles/month",
            "50 AI backgrounds",
            "5 AI descriptions",
            "Facebook Marketplace",
            "Photo cropping",
            "Email support"
        ]
    },
    "professional": {
        "name": "Professional",
        "price": 149,
        "price_id": os.getenv("STRIPE_PROFESSIONAL_PRICE_ID", "price_professional"),
        "limits": {
            "vehicles_per_month": 50,
            "ai_backgrounds": 500,
            "ai_descriptions": 50,
            "platforms": ["facebook", "autotrader", "carscom"]
        },
        "features": [
            "50 vehicles/month",
            "500 AI backgrounds",
            "50 AI descriptions with SEO",
            "All platforms (Facebook, AutoTrader, Cars.com)",
            "Priority support",
            "Advanced analytics"
        ]
    },
    "business": {
        "name": "Business",
        "price": 299,
        "price_id": os.getenv("STRIPE_BUSINESS_PRICE_ID", "price_business"),
        "limits": {
            "vehicles_per_month": 200,
            "ai_backgrounds": 2000,
            "ai_descriptions": 200,
            "platforms": ["facebook", "autotrader", "carscom", "ebay"]
        },
        "features": [
            "200 vehicles/month",
            "2000 AI backgrounds",
            "200 AI descriptions",
            "All platforms + eBay Motors",
            "Multi-user accounts (5 users)",
            "Custom branding",
            "Phone support",
            "API access"
        ]
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 499,
        "price_id": os.getenv("STRIPE_ENTERPRISE_PRICE_ID", "price_enterprise"),
        "limits": {
            "vehicles_per_month": -1,  # unlimited
            "ai_backgrounds": -1,
            "ai_descriptions": -1,
            "platforms": ["facebook", "autotrader", "carscom", "ebay", "custom"]
        },
        "features": [
            "Unlimited vehicles",
            "Unlimited AI features",
            "All platforms",
            "White-label option",
            "Custom integrations",
            "Dedicated account manager",
            "SLA guarantee",
            "On-premise deployment"
        ]
    }
}


class SubscriptionPlan(BaseModel):
    """Subscription plan details."""
    id: str
    name: str
    price: int
    features: list[str]
    limits: dict


class CheckoutSession(BaseModel):
    """Stripe checkout session response."""
    checkout_url: str
    session_id: str


def get_plan_details(plan_id: str) -> Optional[SubscriptionPlan]:
    """
    Get subscription plan details.
    
    Args:
        plan_id: Plan identifier (trial, starter, professional, etc.)
    
    Returns:
        Plan details if found, None otherwise
    """
    plan = PLANS.get(plan_id)
    
    if not plan:
        return None
    
    return SubscriptionPlan(
        id=plan_id,
        name=plan["name"],
        price=plan["price"],
        features=plan["features"],
        limits=plan["limits"]
    )


def create_checkout_session(plan_id: str, customer_email: str, success_url: str, cancel_url: str) -> CheckoutSession:
    """
    Create a Stripe checkout session for subscription.
    
    Args:
        plan_id: Plan to subscribe to
        customer_email: Customer email
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if payment cancelled
    
    Returns:
        Checkout session with URL
    
    Raises:
        ValueError: If plan not found or Stripe API error
    """
    plan = PLANS.get(plan_id)
    
    if not plan or plan["price"] == 0:
        raise ValueError(f"Invalid plan: {plan_id}")
    
    if not stripe.api_key or stripe.api_key == "":
        raise ValueError("Stripe API key not configured")
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': plan['price_id'],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=cancel_url,
            customer_email=customer_email,
            metadata={
                'plan_id': plan_id,
                'email': customer_email
            }
        )
        
        return CheckoutSession(
            checkout_url=session.url,
            session_id=session.id
        )
    except stripe.error.StripeError as e:
        raise ValueError(f"Stripe error: {str(e)}")


def check_subscription_status(stripe_customer_id: str) -> dict:
    """
    Check customer's subscription status in Stripe.
    
    Args:
        stripe_customer_id: Stripe customer ID
    
    Returns:
        Subscription status info
    """
    if not stripe.api_key or stripe.api_key == "":
        return {"active": False, "plan": "trial"}
    
    try:
        subscriptions = stripe.Subscription.list(
            customer=stripe_customer_id,
            status='active',
            limit=1
        )
        
        if len(subscriptions.data) > 0:
            sub = subscriptions.data[0]
            
            # Get plan ID from metadata
            plan_id = sub.metadata.get('plan_id', 'professional')
            
            return {
                "active": True,
                "plan": plan_id,
                "current_period_end": sub.current_period_end,
                "cancel_at_period_end": sub.cancel_at_period_end
            }
        
        return {"active": False, "plan": "trial"}
    except stripe.error.StripeError:
        return {"active": False, "plan": "trial"}


def create_customer_portal_session(stripe_customer_id: str, return_url: str) -> str:
    """
    Create a Stripe customer portal session for managing subscription.
    
    Args:
        stripe_customer_id: Stripe customer ID
        return_url: URL to return to after portal session
    
    Returns:
        Portal session URL
    """
    if not stripe.api_key or stripe.api_key == "":
        raise ValueError("Stripe API key not configured")
    
    try:
        session = stripe.billing_portal.Session.create(
            customer=stripe_customer_id,
            return_url=return_url,
        )
        
        return session.url
    except stripe.error.StripeError as e:
        raise ValueError(f"Stripe error: {str(e)}")


# Usage tracking (in-memory, replace with database in production)
usage_db: dict[str, dict] = {}


def record_usage(user_email: str, feature: str, amount: int = 1):
    """
    Record feature usage for a user.
    
    Args:
        user_email: User email
        feature: Feature name (vehicles_per_month, ai_backgrounds, etc.)
        amount: Amount to increment by
    """
    if user_email not in usage_db:
        usage_db[user_email] = {}
    
    current_month = datetime.now().strftime("%Y-%m")
    key = f"{current_month}:{feature}"
    
    if key not in usage_db[user_email]:
        usage_db[user_email][key] = 0
    
    usage_db[user_email][key] += amount


def get_usage(user_email: str, feature: str) -> int:
    """
    Get current month usage for a feature.
    
    Args:
        user_email: User email
        feature: Feature name
    
    Returns:
        Usage count for current month
    """
    if user_email not in usage_db:
        return 0
    
    current_month = datetime.now().strftime("%Y-%m")
    key = f"{current_month}:{feature}"
    
    return usage_db[user_email].get(key, 0)


def check_limit(user_email: str, plan_id: str, feature: str) -> tuple[bool, Optional[str]]:
    """
    Check if user has reached their plan limit for a feature.
    
    Args:
        user_email: User email
        plan_id: User's subscription plan
        feature: Feature to check
    
    Returns:
        Tuple of (allowed: bool, error_message: Optional[str])
    """
    plan = PLANS.get(plan_id)
    
    if not plan:
        return False, "Invalid subscription plan"
    
    limit = plan["limits"].get(feature)
    
    # -1 means unlimited
    if limit == -1:
        return True, None
    
    # No limit defined for this feature
    if limit is None:
        return True, None
    
    current_usage = get_usage(user_email, feature)
    
    if current_usage >= limit:
        return False, f"Monthly limit reached for {feature} ({limit}/{limit}). Upgrade your plan for more."
    
    return True, None


def get_usage_stats(user_email: str, plan_id: str) -> dict:
    """
    Get usage statistics for all features.
    
    Args:
        user_email: User email
        plan_id: User's subscription plan
    
    Returns:
        Dictionary with usage stats for each feature
    """
    plan = PLANS.get(plan_id)
    
    if not plan:
        return {}
    
    stats = {}
    
    for feature, limit in plan["limits"].items():
        usage = get_usage(user_email, feature)
        
        stats[feature] = {
            "used": usage,
            "limit": limit if limit != -1 else "unlimited",
            "remaining": limit - usage if limit != -1 else "unlimited",
            "percentage": (usage / limit * 100) if limit > 0 else 0
        }
    
    return stats
