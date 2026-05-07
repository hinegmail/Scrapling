"""Authentication service"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from uuid import uuid4

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.models.user import User
from app.models.session import Session as SessionModel
from app.config import settings
from app.exceptions import AuthenticationError, ConflictError, NotFoundError, ValidationError


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {"sub": user_id, "exp": expire, "type": "access"}
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT refresh token"""
        if expires_delta is None:
            expires_delta = timedelta(days=settings.refresh_token_expire_days)

        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {"sub": user_id, "exp": expire, "type": "refresh"}
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> str:
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: str = payload.get("sub")
            token_type_claim: str = payload.get("type")

            if user_id is None or token_type_claim != token_type:
                raise AuthenticationError("Invalid token")

            return user_id
        except JWTError:
            raise AuthenticationError("Invalid token")

    @staticmethod
    def register_user(db: Session, username: str, email: str, password: str) -> User:
        """Register a new user"""
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            if existing_user.username == username:
                raise ConflictError("Username already exists")
            else:
                raise ConflictError("Email already exists")

        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=AuthService.hash_password(password),
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def login_user(
        db: Session,
        username: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        remember_me: bool = False,
    ) -> Tuple[User, str, str]:
        """Login user and create session"""
        # Find user by username
        user = db.query(User).filter(User.username == username).first()

        if not user or not AuthService.verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid username or password")

        if not user.is_active:
            raise AuthenticationError("User account is inactive")

        # Create tokens
        access_token = AuthService.create_access_token(str(user.id))
        refresh_token = AuthService.create_refresh_token(str(user.id))

        # Determine session expiration
        if remember_me:
            expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        else:
            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=settings.access_token_expire_minutes
            )

        # Create session
        session = SessionModel(
            user_id=user.id,
            token=access_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        db.add(session)

        # Update last login
        user.last_login = datetime.now(timezone.utc)

        db.commit()
        db.refresh(user)

        return user, access_token, refresh_token

    @staticmethod
    def logout_user(db: Session, token: str) -> None:
        """Logout user and delete session"""
        session = db.query(SessionModel).filter(SessionModel.token == token).first()

        if session:
            db.delete(session)
            db.commit()

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> str:
        """Refresh access token using refresh token"""
        user_id = AuthService.verify_token(refresh_token, token_type="refresh")

        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User not found")

        # Create new access token
        access_token = AuthService.create_access_token(str(user.id))
        return access_token

    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        """Get current user from token"""
        user_id = AuthService.verify_token(token, token_type="access")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User not found")

        return user

    @staticmethod
    def change_password(db: Session, user_id: str, old_password: str, new_password: str) -> None:
        """Change user password"""
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise NotFoundError("User not found")

        if not AuthService.verify_password(old_password, user.password_hash):
            raise ValidationError("Old password is incorrect")

        user.password_hash = AuthService.hash_password(new_password)
        db.commit()
