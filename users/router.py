from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Internal Imports
import models
from database import get_db
from users import schemas, utils

# IMPORTANT: Importing get_current_user from main to handle dependency injection
# If this causes a circular import, move get_current_user to a separate dependencies.py file.
# users/router.py
# DELETE: from main import get_current_user
from dependencies import get_current_user # <--- ADD THIS

router = APIRouter(prefix="/users", tags=["Users"])

# --- 1. REGISTER ---
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered in the system.")
    
    otp = utils.generate_otp()
    hashed_pw = utils.get_password_hash(user.password)
    
    new_user = models.User(
        email=user.email, 
        hashed_password=hashed_pw, 
        otp_code=otp, 
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    utils.send_email_otp(user.email, otp, "Account Verification")
    return {"message": "Identity created. Check console for verification OTP."}

# --- 2. VERIFY EMAIL ---
@router.post("/verify")
def verify_email(data: schemas.UserVerify, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    
    if not user or user.otp_code != data.otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")
    
    user.is_verified = True
    user.otp_code = None 
    db.commit()
    
    return {"message": "Protocol access granted. You can now login."}

# --- 3. LOGIN ---
@router.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_data.email).first()
    
    if not user or not utils.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Identity verification failed.")
    
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email verification required.")
    
    access_token = utils.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- 4. FORGOT PASSWORD ---
@router.post("/forgot-password")
def forgot_password(data: schemas.ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Identity not found.")
    
    otp = utils.generate_otp()
    user.otp_code = otp
    db.commit()
    
    utils.send_email_otp(user.email, otp, "Password Reset")
    return {"message": "Recovery OTP sent to console."}

# --- 5. RESET PASSWORD ---
@router.post("/reset-password")
def reset_password(data: schemas.ResetPassword, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    
    if not user or user.otp_code != data.otp:
        raise HTTPException(status_code=400, detail="Authorization code invalid.")
    
    user.hashed_password = utils.get_password_hash(data.new_password)
    user.otp_code = None
    db.commit()
    
    return {"message": "Master Key updated successfully."}

# --- 6. ADMIN DASHBOARD ---
@router.get("/admin/dashboard")
def get_admin_dashboard(
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # Security Gatekeeper: Hardcoded for now, but better as a user.is_admin boolean
    if current_user.email != "admin@skillev.io":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access denied. Protocol Admin clearance required."
        )

    users_list = db.query(models.User).all()
    dashboard_data = []

    for user in users_list:
        # Fetch all forensic evidence reports for this user
        reports = db.query(models.EvidenceReport).filter(models.EvidenceReport.user_id == user.id).all()
        
        dashboard_data.append({
            "user_id": user.id,
            "email": user.email,
            "labs": [
                {
                    "id": r.id,
                    "report_id": r.id,
                    "task_id": r.task_id,
                    "status": r.status,
                    "integrity_score": r.integrity_score,
                    "mode": r.mode,
                    "completed_at": r.completed_at
                } for r in reports
            ]
        })
    
    return dashboard_data