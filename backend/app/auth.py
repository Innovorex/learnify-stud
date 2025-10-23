from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.schemas import RegisterRequest, LoginRequest
from passlib.hash import bcrypt
import jwt, os, datetime

router = APIRouter()
SECRET_KEY = os.getenv("JWT_SECRET", "secret")

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pwd = bcrypt.hash(req.password)
    new_user = User(
        name=req.name,
        email=req.email,
        password=hashed_pwd,
        role=req.role,
        class_name=req.class_name if req.role == "student" else None,
        section=req.section if req.role == "student" else None
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT token
    payload = {
        "id": new_user.id,
        "email": new_user.email,
        "role": new_user.role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=5)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return {
        "access_token": token,
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role,
            "class_name": new_user.class_name,
            "section": new_user.section
        }
    }

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not bcrypt.verify(req.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    payload = {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=5)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return {
        "access_token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "class_name": user.class_name,
            "section": user.section
        }
    }
