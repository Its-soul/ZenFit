from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository
from app.modules.auth.schemas import (
    LoginRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    PasswordResetRequestResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.modules.users.repository import UserProfileRepository


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.profiles = UserProfileRepository(db)

    def register(self, payload: RegisterRequest) -> TokenResponse:
        existing_user = self.users.get_by_email(payload.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

        user = self.users.create(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
        )
        self.profiles.create_for_user(user.id)
        self.db.commit()
        self.db.refresh(user)
        return self._token_response(user)

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.authenticate_user(payload.email, payload.password)
        return self._token_response(user)

    def authenticate_user(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")
        return user

    def refresh(self, payload: RefreshTokenRequest) -> TokenResponse:
        token_payload = self._decode_user_token(payload.refresh_token, expected_type="refresh")
        user = self._get_active_user(token_payload["sub"])
        self._assert_token_version(user, token_payload)
        return self._token_response(user)

    def logout(self, user: User) -> dict[str, str]:
        self.users.revoke_tokens(user)
        self.db.commit()
        return {"message": "Logged out"}

    def request_password_reset(self, payload: PasswordResetRequest) -> PasswordResetRequestResponse:
        message = "If that email exists, a password reset has been prepared."
        user = self.users.get_by_email(payload.email)
        if user is None or not user.is_active:
            return PasswordResetRequestResponse(message=message)

        reset_token = create_password_reset_token(
            subject=str(user.id),
            extra_claims={"email": user.email, "ver": user.token_version},
        )
        return PasswordResetRequestResponse(
            message=message,
            reset_token=reset_token if settings.password_reset_return_token else None,
        )

    def confirm_password_reset(self, payload: PasswordResetConfirmRequest) -> dict[str, str]:
        token_payload = self._decode_user_token(payload.reset_token, expected_type="password_reset")
        user = self._get_active_user(token_payload["sub"])
        self._assert_token_version(user, token_payload)
        self.users.save_password(user, hashed_password=hash_password(payload.new_password))
        self.db.commit()
        return {"message": "Password has been reset"}

    def _token_response(self, user: User) -> TokenResponse:
        extra_claims = {"email": user.email, "role": user.role, "ver": user.token_version}
        access_token = create_access_token(subject=str(user.id), extra_claims=extra_claims)
        refresh_token = create_refresh_token(subject=str(user.id), extra_claims=extra_claims)
        onboarding_complete = bool(user.profile and user.profile.onboarding_complete)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                onboarding_complete=onboarding_complete,
            ),
        )

    def _decode_user_token(self, token: str, *, expected_type: str) -> dict:
        try:
            return decode_token(token, expected_type=expected_type)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc

    def _get_active_user(self, user_id: str) -> User:
        try:
            parsed_user_id = UUID(user_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token") from exc

        user = self.users.get_by_id(parsed_user_id)
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive or missing")
        return user

    def _assert_token_version(self, user: User, token_payload: dict) -> None:
        if token_payload.get("ver") != user.token_version:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
