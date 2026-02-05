from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas import UserLogin, UserCreate, TokenResponse
from app.models import User
from app.utils import hash_password, verify_password
from app.jwt_utils import create_access_token
from app.dependencies import get_db

router = APIRouter(tags=["auth"])



@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    email = user.email.lower()

    db_user = db.query(User).filter(User.email == email).first()

    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token({"email": db_user.email})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        success=True,
        message="Login successful",
    )


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    email = user.email.lower()

    if not (email.endswith("@innovo-consulting.de") or email.endswith("@aiio.de")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email domain",
        )

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        email=email,
        password_hash=hashed_password,
    )

    db.add(new_user)
    db.commit()

    return {"success": True, "message": "User registered successfully"}
