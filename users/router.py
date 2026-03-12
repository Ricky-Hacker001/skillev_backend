from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Internal Imports
from database import get_db
import models  # <--- Updated: Importing from the root models.py
from users import schemas, utils

router = APIRouter(prefix="/users", tags=["Users"])

# --- 1. REGISTER ---
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists in the root models.User table
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered in the system.")
    
    # Generate Security Credentials
    otp = utils.generate_otp()
    hashed_pw = utils.get_password_hash(user.password)
    
    # Create new user instance
    new_user = models.User(
        email=user.email, 
        hashed_password=hashed_pw, 
        otp_code=otp, 
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Send OTP to terminal console (Mock Email)
    utils.send_email_otp(user.email, otp, "Account Verification")
    
    return {"message": "Identity created. Check console for verification OTP."}

# --- 2. VERIFY EMAIL ---
@router.post("/verify")
def verify_email(data: schemas.UserVerify, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    
    if not user or user.otp_code != data.otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")
    
    # Update verification status and clear OTP buffer
    user.is_verified = True
    user.otp_code = None 
    db.commit()
    
    return {"message": "Protocol access granted. You can now login."}

# --- 3. LOGIN ---
@router.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_data.email).first()
    
    # Security Validation
    if not user or not utils.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Identity verification failed.")
    
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email verification required.")
    
    # Generate JWT Token for Session Management
    access_token = utils.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- 4. FORGOT PASSWORD ---
@router.post("/forgot-password")
def forgot_password(data: schemas.ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        # For security, we typically don't reveal if an email exists, 
        # but for this MVP, we'll keep it direct.
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
    
    # Hash new password and clear recovery code
    user.hashed_password = utils.get_password_hash(data.new_password)
    user.otp_code = None
    db.commit()
    
    return {"message": "Master Key updated successfully."}