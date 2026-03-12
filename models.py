from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, Float, func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Verification & Reset Logic
    otp_code = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)

    # --- ANTI-CHEAT: BIOMETRIC PROFILE ---
    # Stores average WPM, burst speed, and keystroke rhythm intervals
    # Collected during 'learning' mode to baseline the user
    typing_profile = Column(JSON, nullable=True) 

class EvidenceReport(Base):
    __tablename__ = "evidence_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    task_id = Column(String)
    domain = Column(String)
    container_id = Column(String, unique=True)
    
    # Quoted to avoid conflict with Postgres reserved aggregate 'MODE()'
    mode = Column("mode", String, default="hiring", quote=True)
    
    logs = Column(JSON, default=[]) 
    status = Column(String, default="active") # active, completed, flagged
    
    # --- ANTI-CHEAT: VERIFICATION METRICS ---
    # integrity_score: 0.0 to 1.0 (Higher means rhythm matches profile)
    # is_verified: False if typing speed is physically impossible (pasting)
    integrity_score = Column(Float, default=1.0)
    identity_verified = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    visual_evidence = Column(JSON, default=[])
