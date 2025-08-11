<<<<<<< HEAD
"""
Authentication routes for login, logout, and token management.
"""
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from core.auth import (
    authenticate_user, 
    create_access_token, 
    create_refresh_token,
    get_current_active_user,
    User,
    Token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """
    Authenticate user and return JWT tokens.
    
    Default users:
    - admin/admin123 (full access)
    - user/user123 (read/write access)
    - viewer/viewer123 (read-only access)
    """
    try:
        user = authenticate_user(login_data.username, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role},
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": user.username, "role": user.role}
        )
        
        logger.info(f"User {user.username} logged in successfully")
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except HTTPException:
        # Propagate intended HTTP errors like 401
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_data: RefreshRequest):
    """Refresh access token using refresh token."""
    try:
        from jose import JWTError, jwt
        from core.auth import SECRET_KEY, ALGORITHM
        
        payload = jwt.decode(refresh_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify user still exists and is active
        from core.auth import get_user
        user = get_user(username)
        if not user or user.disabled:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role},
            expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(
            data={"sub": user.username, "role": user.role}
        )
        
        logger.info(f"Token refreshed for user {username}")
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except HTTPException:
        raise
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh"
        )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """Logout user (client should discard tokens)."""
    logger.info(f"User {current_user.username} logged out")
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user

@router.get("/health")
async def auth_health_check():
    """Health check for authentication service."""
    return {"status": "ok", "service": "authentication"} 
=======
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone
from typing import Optional, Literal
from jose import jwt, JWTError
from passlib.context import CryptContext
from core.settings import settings
from core.database import users_collection

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    id: str
    email: EmailStr
    role: Literal["guest", "editor", "admin"]

COOKIE_NAME = "access_token"

async def get_user_by_email(email: str) -> Optional[dict]:
    return await users_collection.find_one({"email": email})

async def create_user(email: str, password: str, role: str = "editor") -> str:
    hashed = pwd_context.hash(password)
    doc = {"email": email, "password_hash": hashed, "role": role, "created_at": datetime.now(timezone.utc)}
    result = await users_collection.insert_one(doc)
    return str(result.inserted_id)

async def ensure_default_editor():
    if settings.DEFAULT_EDITOR_EMAIL and settings.DEFAULT_EDITOR_PASSWORD:
        existing = await users_collection.find_one({"email": settings.DEFAULT_EDITOR_EMAIL})
        if not existing:
            await create_user(settings.DEFAULT_EDITOR_EMAIL, settings.DEFAULT_EDITOR_PASSWORD, role="editor")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

async def get_current_user(request: Request) -> dict:
    # Prefer Authorization header
    auth_header = request.headers.get("authorization")
    token = None
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    # Fallback to cookie
    if not token:
        token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def role_required(min_role: Literal["guest", "editor", "admin"]):
    order = {"guest": 0, "editor": 1, "admin": 2}
    async def dependency(user: dict = Depends(get_current_user)):
        user_role = user.get("role", "guest")
        if order[user_role] < order[min_role]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return dependency

# Allow internal calls (e.g., from same service/scripts) via X-API-KEY header
# If header matches SECRET_KEY, bypass role checks; else require min_role
def role_or_internal(min_role: Literal["guest", "editor", "admin"]):
    order = {"guest": 0, "editor": 1, "admin": 2}
    async def dependency(request: Request):
        api_key = request.headers.get("x-api-key")
        if api_key and api_key == settings.SECRET_KEY:
            return {"role": "admin", "email": "internal@local"}
        # fallback to user auth
        user = await get_current_user(request)
        user_role = user.get("role", "guest")
        if order[user_role] < order[min_role]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return dependency

@router.post("/login")
async def login(data: LoginRequest, response: Response):
    await ensure_default_editor()
    user = await get_user_by_email(data.email)
    if not user or not pwd_context.verify(data.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user["email"], "role": user.get("role", "guest")})
    # httpOnly cookie (best-effort; frontend primarily uses Authorization header)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return {"status": "success", "access_token": token, "token_type": "bearer"}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"status": "success"}

@router.get("/me", response_model=UserPublic)
async def me(user: dict = Depends(get_current_user)):
    return {"id": str(user.get("_id")), "email": user["email"], "role": user.get("role", "guest")}

# Expose utilities for other routers
get_current_user_dep = get_current_user
role_required_dep = role_required
role_or_internal_dep = role_or_internal
>>>>>>> 9de1e983acf572c97ba2cb123b7d2f0bd6cc1985
