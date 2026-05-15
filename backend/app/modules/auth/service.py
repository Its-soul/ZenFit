from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
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
        user = self.users.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        return self._token_response(user)

    def _token_response(self, user: User) -> TokenResponse:
        token = create_access_token(subject=str(user.id), extra_claims={"email": user.email})
        onboarding_complete = bool(user.profile and user.profile.onboarding_complete)
        return TokenResponse(
            access_token=token,
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                onboarding_complete=onboarding_complete,
            ),
        )

