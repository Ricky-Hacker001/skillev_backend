from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import random
import numpy as np
import ollama  # Required for Phi-3 Integration

# CONFIGURATION
SECRET_KEY = "hackathon_secret_key" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Hashing ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --- JWT Token ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- OTP Logic ---
def generate_otp():
    return str(random.randint(100000, 999999))

def send_email_otp(email: str, otp: str, type: str = "Verification"):
    print(f"\n{'='*30}")
    print(f"📧 [MOCK EMAIL] To: {email}")
    print(f"🔑 Subject: {type} Code")
    print(f"🔢 OTP: {otp}")
    print(f"{'='*30}\n")

# --- AI FORENSIC ENGINE (Phi-3) ---

def analyze_forensic_evidence(logs, task_id, mode):
    """
    Feeds captured execution logs into Phi-3 to generate a 
    technical proficiency audit and behavioral ranking.
    """
    # 1. Filter logs to focus on execution attempts and successes
    significant_logs = [
        l.get("message", "") for l in logs 
        if "EXECUTION ATTEMPT" in l.get("message", "").upper() 
        or "SUCCESS" in l.get("message", "").upper()
        or "INTEGRITY_VIOLATION" in l.get("message", "").upper()
    ]
    
    log_stream = "\n".join(significant_logs)
    
    # 2. Construct the Forensic Prompt
    prompt = f"""
    [STRICT FORENSIC AUDIT MODE: ON]
    SYSTEM ROLE: You are an elite cybersecurity technical recruiter.
    
    CONTEXT:
    - LAB_TASK: {task_id}
    - SESSION_MODE: {mode}
    - LOG_TRACE: 
    {log_stream}

    REQUIREMENTS:
    Based on the payload patterns and speed in the logs:
    1. RANK: Assign a level (Novice, Script-Kiddie, Intermediate, Professional, Elite).
    2. METHODOLOGY: Describe their attack/solution style (e.g., 'Surgical Precision', 'Trial-and-Error', 'Automated/Pasted').
    3. SUMMARY: A 2-sentence cynical but professional evaluation of their proficiency.
    
    Tone: Concise, technical, and analytical.
    """

    try:
        # Utilizing local Phi-3 via Ollama
        response = ollama.chat(model='phi3', messages=[
            {'role': 'user', 'content': prompt},
        ])
        return response['message']['content']
    except Exception as e:
        return f"AI_AUDIT_OFFLINE: Analysis unavailable. Error: {str(e)}"

# --- ANTI-CHEAT: KEYSTROKE DYNAMICS ENGINE ---



def analyze_typing_behavior(keystrokes):
    """
    Analyzes raw keystroke data from the frontend.
    Detects rhythm, WPM, and aggressive paste attempts.
    """
    if len(keystrokes) < 5:
        return {"wpm": 0, "rhythm_variance": 0, "is_pasted": False, "mean_interval": 0}

    # 1. Calculate Intervals (Flight Time)
    timestamps = [k['time'] for k in keystrokes]
    intervals = np.diff(timestamps) # ms differences

    # 2. AGGRESSIVE PASTE DETECTION
    # Humans rarely type keys faster than 40ms consistently. 
    # If more than 20% of intervals are < 5ms, it's a paste.
    fast_bursts = [i for i in intervals if i < 5]
    paste_threshold_triggered = len(fast_bursts) > (len(intervals) * 0.2)
    
    mean_interval = np.mean(intervals)
    is_pasted = paste_threshold_triggered or (mean_interval < 10)

    # 3. Calculate WPM
    total_time_min = (timestamps[-1] - timestamps[0]) / 60000
    if total_time_min <= 0: total_time_min = 0.00001
    wpm = (len(keystrokes) / 5) / total_time_min

    # 4. Generate Rhythm Signature (Standard Deviation)
    rhythm_variance = np.std(intervals)

    return {
        "wpm": round(wpm, 2),
        "rhythm_variance": round(rhythm_variance, 4),
        "is_pasted": is_pasted,
        "mean_interval": round(mean_interval, 2)
    }

def verify_identity_match(stored_profile, current_metrics):
    """
    Compares the current hiring attempt against the stored learning profile.
    """
    if not stored_profile or 'rhythm_variance' not in stored_profile:
        return True, 0.5 
    
    if 'rhythm_variance' not in current_metrics:
        return True, 0.5

    # PASTE CHECK: Immediate failure if pasting detected
    if current_metrics.get('is_pasted', False):
        return False, 0.0

    # BIOMETRIC RHYTHM COMPARISON
    stored_var = stored_profile.get('rhythm_variance', 0)
    current_var = current_metrics.get('rhythm_variance', 0)
    
    variance_diff = abs(stored_var - current_var)
    
    if stored_var == 0:
        return True, 0.5

    # Tolerance: 50% deviation allowed before flagging mismatch
    threshold = stored_var * 0.5
    is_verified = variance_diff <= threshold
    
    # Calculate integrity score (linear decay based on rhythm difference)
    integrity_score = max(0, 1 - (variance_diff / (stored_var + 1)))

    return is_verified, round(integrity_score, 2)
