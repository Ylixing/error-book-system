"""Authentication endpoints"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
from app.config import get_settings
from app.database import get_db
from app.schemas import WeChatLoginRequest, WeChatLoginResponse, UserResponse
from app.models.database import User
from app.services.wechat_service import wechat_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


@router.post("/wechat/login", response_model=WeChatLoginResponse)
async def wechat_login(request: WeChatLoginRequest, db: Session = Depends(get_db)):
    """
    WeChat mini program login
    
    Args:
        request: Login request with WeChat code
        db: Database session
        
    Returns:
        Access token and user info
    """
    try:
        # Exchange code for session
        session_data = wechat_service.code_to_session(request.code)
        openid = session_data.get("openid")
        
        if not openid:
            raise HTTPException(status_code=400, detail="Failed to get openid from WeChat")
        
        # Check if user exists
        user = db.query(User).filter(User.openid == openid).first()
        
        if not user:
            # Create new user
            user = User(
                openid=openid,
                name=request.userInfo.get("nickName", "User") if request.userInfo else "User",
                role="student"  # Default to student for mini program
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user with openid: {openid}")
        
        # Generate access token
        access_token = create_access_token(
            data={"sub": str(user.id), "openid": openid, "role": user.role}
        )
        
        return WeChatLoginResponse(
            access_token=access_token,
            user_id=user.id,
            openid=openid,
            user_type=user.role
        )
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str, db: Session = Depends(get_db)):
    """
    Get current user info
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = int(payload.get("sub"))
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
