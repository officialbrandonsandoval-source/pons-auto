"""Authentication API endpoints."""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from pons.auth import (
    authenticate_user,
    create_user,
    create_access_token,
    verify_token,
    get_user,
    User,
    Token,
    TokenData
)


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class SignupRequest(BaseModel):
    """User signup request."""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    dealership_name: Optional[str] = None


class LoginResponse(BaseModel):
    """Login response with token and user info."""
    access_token: str
    token_type: str
    user: User


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """
    Dependency to get current authenticated user.
    
    Args:
        token: JWT token from Authorization header
    
    Returns:
        Current user
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(token)
    
    if token_data is None or token_data.email is None:
        raise credentials_exception
    
    user = get_user(email=token_data.email)
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency to get current active user.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Current user if active
    
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user


@router.post("/signup", response_model=LoginResponse, status_code=201)
async def signup(request: SignupRequest) -> LoginResponse:
    """
    Create a new user account.
    
    Args:
        request: Signup request with email, password, etc.
    
    Returns:
        Access token and user info
    
    Raises:
        HTTPException: If email already registered
    """
    # Check if user already exists
    existing_user = get_user(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = create_user(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        dealership_name=request.dealership_name
    )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@router.post("/login", response_model=LoginResponse)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> LoginResponse:
    """
    Login with email and password.
    
    Args:
        form_data: OAuth2 form with username (email) and password
    
    Returns:
        Access token and user info
    
    Raises:
        HTTPException: If credentials are invalid
    """
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@router.get("/me", response_model=User)
async def get_me(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    """
    Get current user profile.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Current user info
    """
    return current_user


@router.get("/verify")
async def verify(current_user: Annotated[User, Depends(get_current_active_user)]) -> dict:
    """
    Verify token is valid.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Verification status
    """
    return {
        "valid": True,
        "email": current_user.email,
        "subscription_plan": current_user.subscription_plan,
        "subscription_status": current_user.subscription_status
    }
