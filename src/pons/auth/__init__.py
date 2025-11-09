"""Authentication module for PONS AUTO."""

from datetime import datetime, timedelta
from typing import Optional
import os

from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


class User(BaseModel):
    """User model."""
    email: EmailStr
    full_name: Optional[str] = None
    dealership_name: Optional[str] = None
    subscription_plan: str = "trial"
    subscription_status: str = "active"
    stripe_customer_id: Optional[str] = None
    created_at: datetime
    is_active: bool = True


class UserInDB(User):
    """User model with password hash."""
    password_hash: str


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """JWT token payload."""
    email: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in token (should include 'sub' with user email)
        expires_delta: Optional custom expiration time
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        TokenData if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            return None
        
        return TokenData(email=email)
    except JWTError:
        return None


# In-memory user store (replace with database in production)
users_db: dict[str, UserInDB] = {}


def create_user(email: str, password: str, full_name: Optional[str] = None, 
                dealership_name: Optional[str] = None) -> User:
    """
    Create a new user account.
    
    Args:
        email: User email
        password: Plain text password
        full_name: User's full name
        dealership_name: Dealership name
    
    Returns:
        Created user (without password hash)
    """
    password_hash = get_password_hash(password)
    
    user_in_db = UserInDB(
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        dealership_name=dealership_name,
        subscription_plan="trial",
        subscription_status="active",
        created_at=datetime.now(),
        is_active=True
    )
    
    users_db[email] = user_in_db
    
    # Return user without password hash
    return User(**user_in_db.model_dump(exclude={"password_hash"}))


def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Authenticate a user with email and password.
    
    Args:
        email: User email
        password: Plain text password
    
    Returns:
        User if authentication successful, None otherwise
    """
    user = users_db.get(email)
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return User(**user.model_dump(exclude={"password_hash"}))


def get_user(email: str) -> Optional[User]:
    """
    Get user by email.
    
    Args:
        email: User email
    
    Returns:
        User if found, None otherwise
    """
    user = users_db.get(email)
    
    if not user:
        return None
    
    return User(**user.model_dump(exclude={"password_hash"}))


def update_user_subscription(email: str, plan: str, stripe_customer_id: Optional[str] = None) -> Optional[User]:
    """
    Update user's subscription plan.
    
    Args:
        email: User email
        plan: Subscription plan name
        stripe_customer_id: Stripe customer ID
    
    Returns:
        Updated user if found, None otherwise
    """
    user = users_db.get(email)
    
    if not user:
        return None
    
    user.subscription_plan = plan
    user.subscription_status = "active"
    
    if stripe_customer_id:
        user.stripe_customer_id = stripe_customer_id
    
    users_db[email] = user
    
    return User(**user.model_dump(exclude={"password_hash"}))
