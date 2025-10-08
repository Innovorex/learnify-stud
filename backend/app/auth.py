from fastapi import APIRouter, HTTPException
from app.db import SessionLocal
from app.models import User
from app.schemas import RegisterRequest, LoginRequest
from passlib.hash import bcrypt
import jwt, os, datetime

router = APIRouter()
SECRET_KEY = os.getenv("JWT_SECRET", "secret")

@router.post("/register")
def register(req: RegisterRequest):
    db = SessionLocal()
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pwd = bcrypt.hash(req.password)
    new_user = User(name=req.name, email=req.email, password=hashed_pwd, role=req.role)
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
            "role": new_user.role
        }
    }

@router.post("/login")
def login(req: LoginRequest):
    db = SessionLocal()
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
            "role": user.role
        }
    }
