from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
# main.py - Top of the file
from datetime import datetime  # <--- Add this line

# Internal Imports
import models 
import users.utils as utils
from database import engine, Base, get_db
from users import router as user_router
from users.utils import SECRET_KEY, ALGORITHM
import container_manager 

# Initialize Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Skillev API")

# Setup OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# --- 1. CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. AUTHENTICATION DEPENDENCY ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# --- 3. ROUTER REGISTRATION ---
app.include_router(user_router.router)

# --- 4. CORE ROUTES ---

@app.get("/")
def root():
    return {
        "message": "Skillev Protocol API is running!", 
        "engine": "Docker-Orchestrator-v1",
        "status": "Online"
    }

# --- 5. DYNAMIC TASK EXECUTION ---

@app.post("/tasks/start/{domain}/{task_id}")
async def start_task(
    domain: str, 
    task_id: str, 
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    mode = request.query_params.get("mode", "hiring").lower()
    
    valid_domains = ["cybersecurity", "fullstack"]
    if domain not in valid_domains:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Domain '{domain}' is not authorized."
        )

    # Force kill any existing isolated container for this specific mode/user
    container_manager.cleanup_existing_task(current_user.id, task_id, mode)

    # Start fresh container with mode isolation
    result, error = container_manager.start_sub_room_container(
        user_id=current_user.id, 
        domain=domain, 
        task_id=task_id, 
        mode=mode
    )
    
    if error and not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Orchestration Failure: {error}"
        )
    
    return {
        "status": "success",
        "container_id": result["container_id"],
        "port": result["port"],
        "mode": mode,
        "url": f"http://127.0.0.1:{result['port']}?mode={mode}",
        "message": f"Protocol initialized in {mode} mode"
    }

@app.delete("/tasks/stop/{container_id}")
async def stop_task(
    container_id: str, 
    current_user = Depends(get_current_user)
):
    success = container_manager.kill_sub_room(container_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Node not found or already terminated."
        )
    return {"status": "success", "message": "Environment wiped."}

# --- 6. ANTI-CHEAT: BIOMETRIC & INTEGRITY SYNC ---

@app.post("/users/sync-typing-profile")
async def sync_typing_profile(
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    data = await request.json()
    report_id = data.get("report_id")
    keystrokes = data.get("keystrokes", [])
    violations = data.get("focus_violations", [])
    mode = data.get("mode")

    if not report_id:
        raise HTTPException(status_code=400, detail="Report ID is required.")

    report = db.query(models.EvidenceReport).filter(models.EvidenceReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Evidence Protocol not found.")
    
    db.refresh(report)

    # 1. Analyze Typing Biometrics
    metrics = utils.analyze_typing_behavior(keystrokes)
    
    # 2. Process Violations & Update Log Timeline
    updated_logs = list(report.logs) if report.logs else []
    existing_timestamps = {l.get("timestamp") for l in updated_logs if l.get("type") == "security_alert"}

    for v in violations:
        if v["time"] not in existing_timestamps:
            updated_logs.append({
                "timestamp": v["time"],
                "type": "security_alert",
                "message": "EVIDENCE_LOG: Integrity_Violation - Browser tab focus lost. External research suspected."
            })
    
    report.logs = updated_logs

    # 3. Identity & Integrity Scoring
    if mode == "learning":
        current_user.typing_profile = metrics
        report.integrity_score = 1.0
        report.identity_verified = True
    else:
        is_match, base_score = utils.verify_identity_match(current_user.typing_profile, metrics)
        
        # Deduct 10% per focus violation, 50% for identity mismatch
        focus_penalty = len(violations) * 0.10
        identity_penalty = 0.0 if is_match else 0.50
        
        final_score = max(0.0, base_score - focus_penalty - identity_penalty)
        report.identity_verified = is_match
        report.integrity_score = round(final_score, 2)

    db.commit()
    return {
        "status": "sealed",
        "integrity": report.integrity_score,
        "identity_match": report.identity_verified
    }

# --- 7. EVIDENCE & AI AUDIT ROUTES ---

@app.get("/evidence/ai-analysis/{report_id}")
async def get_ai_analysis(
    report_id: int, 
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Triggers the Phi-3 AI engine to analyze forensic logs for a specific report.
    """
    report = db.query(models.EvidenceReport).filter(
        models.EvidenceReport.id == report_id,
        models.EvidenceReport.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Evidence report not found.")

    # Call the Phi-3 analysis function from utils
    analysis = utils.analyze_forensic_evidence(report.logs, report.task_id, report.mode)
    
    return {
        "report_id": report_id,
        "ai_insight": analysis
    }

@app.get("/users/my-evidence")
def get_my_evidence(
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    return db.query(models.EvidenceReport)\
             .filter(models.EvidenceReport.user_id == current_user.id)\
             .order_by(models.EvidenceReport.created_at.desc())\
             .all()

@app.get("/evidence/task-history/{task_id}")
def get_task_history(
    task_id: str, 
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    reports = db.query(models.EvidenceReport)\
                .filter(models.EvidenceReport.user_id == current_user.id)\
                .filter(models.EvidenceReport.task_id == task_id)\
                .order_by(models.EvidenceReport.mode.desc(), models.EvidenceReport.created_at.asc())\
                .all()
    
    if not reports:
        raise HTTPException(status_code=404, detail="No history found for this task.")
    
    return reports

@app.post("/evidence/upload-visual")
async def upload_visual_evidence(
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    data = await request.json()
    report_id = data.get("report_id")
    img_data = data.get("image") 
    img_type = data.get("type")

    report = db.query(models.EvidenceReport).filter(models.EvidenceReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Forensic Node Not Found")

    new_capture = {
        "timestamp": datetime.now().isoformat(), # This was causing the error
        "type": img_type,
        "data": img_data
    }

    # Important: Re-assign to trigger SQLAlchemy JSON change detection
    current_visuals = list(report.visual_evidence) if report.visual_evidence else []
    current_visuals.append(new_capture)
    report.visual_evidence = current_visuals 
    
    db.commit()
    return {"status": "captured"}

# --- NEW: PATCH ROUTE FOR FORENSIC UPDATES ---

@app.patch("/evidence/update/{report_id}")
async def update_evidence(
    report_id: int,
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find the report
    report = db.query(models.EvidenceReport).filter(
        models.EvidenceReport.id == report_id,
        models.EvidenceReport.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Forensic Report not found.")

    # Get the update data from the request body
    data = await request.json()
    
    # Update only the provided fields (Surgical Update)
    if "status" in data:
        report.status = data["status"]
    if "integrity_score" in data:
        report.integrity_score = data["integrity_score"]

    db.commit()
    db.refresh(report)
    
    return report
    