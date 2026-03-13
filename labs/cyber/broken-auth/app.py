from flask import Flask, request, render_template_string, make_response, jsonify
import time

app = Flask(__name__)

# Mock database (internal reference)
USERS = {
    "admin": "skillev_hard_to_guess_password_9921",
    "guest": "guest_access_token_001"
}

@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    response.headers['Content-Security-Policy'] = "frame-ancestors *"
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Skillev Lab - Broken Auth</title>
    <style>
        body { 
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
            background: #030303; color: #FFFFFF; margin: 0; display: flex; 
            height: 100vh; width: 100vw; overflow: hidden; 
        }
        .sidebar { 
            width: 400px; flex-shrink: 0; background: #080808; 
            border-right: 2px solid #ef4444; padding: 40px 30px; 
            overflow-y: auto; box-sizing: border-box; display: flex; flex-direction: column;
        }
        .section-title { 
            color: #ef4444; font-size: 1.1rem; font-weight: 900; 
            text-transform: uppercase; letter-spacing: 3px; margin-bottom: 30px; 
            display: flex; align-items: center; gap: 12px; 
        }
        .logic-step { 
            background: #0c0c0c; border: 1px solid #222; border-left: 4px solid #ef4444;
            padding: 20px; border-radius: 8px; margin-bottom: 25px; 
        }
        .logic-step b { color: #ef4444; display: block; margin-bottom: 10px; text-transform: uppercase; }
        .code-box { 
            background: #000000; padding: 15px; border-radius: 6px; 
            font-family: 'Consolas', monospace; font-size: 0.9rem; margin-top: 15px; border: 1px solid #333; 
        }
        .timer-box { 
            font-family: 'JetBrains Mono', monospace; font-size: 1rem; color: #f59e0b; 
            background: rgba(245, 158, 11, 0.1); padding: 15px; border-radius: 8px; 
            border: 1px solid rgba(245, 158, 11, 0.3); text-align: center; margin-bottom: 20px;
        }
        .hint-item { font-size: 0.95rem; padding: 20px; border-radius: 8px; margin-bottom: 15px; display: none; background: #111; border: 1px solid #333; }
        .hint-active { display: block; border-left: 4px solid #f59e0b; }
        .main-content { flex-grow: 1; background: radial-gradient(circle at center, #0a0a0a 0%, #030303 100%); display: flex; align-items: center; justify-content: center; padding: 40px; }
        .container { width: 100%; max-width: 420px; background: #080808; padding: 45px; border-radius: 20px; border: 1px solid #222; }
        .evidence-banner { background: rgba(239, 68, 68, 0.1); color: #ef4444; padding: 12px; border-radius: 6px; font-size: 0.75rem; margin-bottom: 30px; text-align: center; font-weight: 900; border: 1px solid rgba(239, 68, 68, 0.3); letter-spacing: 2px; }
        input { width: 100%; padding: 16px; margin: 12px 0; background: #111; border: 1px solid #333; color: white; border-radius: 10px; box-sizing: border-box; font-size: 1rem; outline: none; }
        input[type="submit"] { background: #ef4444; cursor: pointer; border: none; font-weight: 900; text-transform: uppercase; color: #000; }
    </style>
</head>
<body>
    {% if mode == 'learning' %}
    <div class="sidebar">
        <div class="section-title">Analysis_Report</div>
        <div class="logic-step">
            <b>01. Vulnerability Detected</b>
            <p>The system relies on client-side cookies for identity verification without any cryptographic signature.</p>
        </div>
        <div id="hint-timer" class="timer-box">NEXT HINT IN: <span id="time-display">03:00</span></div>
        <div id="hint1" class="hint-item"><b>HINT 01: Inspect the Session</b><br>Open DevTools (F12) > Application > Cookies.</div>
        <div id="hint2" class="hint-item"><b>HINT 02: Value Manipulation</b><br>Change <code>user_role</code> from 'guest' to 'admin'.</div>
        <div id="hint3" class="hint-item"><b>HINT 03: Administrative Bypass</b><br>Refresh the page after editing the cookie.</div>
    </div>
    {% endif %}

    <div class="main-content">
        <div class="container">
            <div class="evidence-banner">🛡️ SKILLEV_PROTOCOL: {{ mode | upper }}_ACTIVE</div>
            <h1>Broken_Auth_Lab</h1>
            <form method="POST">
                <input type="text" name="username" id="username" value="guest" readonly>
                <input type="password" name="password" id="password" value="********" readonly>
                <input type="submit" value="Verify_Identity">
            </form>
            {% if message %} 
                <div style="margin-top:25px; padding:18px; background:#000; border-radius: 12px; border-left: 4px solid #ef4444; font-family: 'Consolas', monospace;">
                    {{ message | safe }}
                </div> 
            {% endif %}
        </div>
    </div>

    <script>
        // --- ANTI-CHEAT TELEMETRY ---
        function initTelemetry() {
            const inputs = ['username', 'password'];
            inputs.forEach(id => {
                const el = document.getElementById(id);
                if (el) {
                    el.addEventListener('paste', (e) => {
                        const pastedData = (e.clipboardData || window.clipboardData).getData('text');
                        fetch('/telemetry', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                event: "PASTE_DETECTED",
                                field: id,
                                content: pastedData
                            })
                        });
                    });
                }
            });
        }
        window.addEventListener('DOMContentLoaded', initTelemetry);

        // --- HINT SYSTEM ---
        let totalSeconds = 180; let currentHintLevel = 1;
        const timeDisplay = document.getElementById('time-display');
        setInterval(() => {
            if (currentHintLevel > 3) return;
            totalSeconds--;
            if (timeDisplay) {
                const mins = Math.floor(totalSeconds / 60);
                const secs = totalSeconds % 60;
                timeDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            }
            if (totalSeconds <= 0) {
                const h = document.getElementById('hint' + currentHintLevel);
                if (h) h.classList.add('hint-active');
                currentHintLevel++;
                totalSeconds = 180;
            }
        }, 1000);
    </script>
</body>
</html>
'''

@app.route('/telemetry', methods=['POST'])
def telemetry():
    """Captures browser events and prints them for the Evidence Engine."""
    data = request.json
    # This print is intercepted by container_manager.py for the integrity score
    print(f"EVIDENCE_LOG: [INTEGRITY_VIOLATION] {data['event']} in {data['field']}: '{data['content']}'", flush=True)
    return jsonify({"status": "captured"}), 200

@app.route('/', methods=['GET', 'POST'])
def login():
    mode = request.args.get('mode', 'hiring').strip().lower()
    message = ""
    
    # Check for the cookie bypass
    user_role = request.cookies.get('user_role')
    
    if user_role == 'admin':
        result_msg = "SUCCESS: Broken_Auth_Bypass_Complete"
        print(f"EVIDENCE_LOG: {result_msg}", flush=True)
        message = f"<span style='color:#ef4444;'>✅ <b>{result_msg}</b></span>"
    
    elif request.method == 'POST':
        username = request.form.get('username')
        # Log normal interaction
        print(f"EVIDENCE_LOG: [MODE:{mode.upper()}] Verification attempt: {username}", flush=True)
        # Log unauthorized error to Evidence Report
        print(f"EVIDENCE_LOG: [ERROR] AUTH_ERROR: User role '{user_role}' denied administrative access.", flush=True)
        message = "Access Denied: Session state 'guest' does not have required permissions."

    resp = make_response(render_template_string(HTML_TEMPLATE, message=message, mode=mode))
    
    # Initialize the vulnerable cookie if it doesn't exist
    if not user_role:
        resp.set_cookie('user_role', 'guest')
        
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)