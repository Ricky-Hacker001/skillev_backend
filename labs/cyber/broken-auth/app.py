from flask import Flask, request, render_template_string, make_response
import time

app = Flask(__name__)

# Mock database (internal reference)
USERS = {
    "admin": "skillev_hard_to_guess_password_9921",
    "guest": "guest_access_token_001"
}

@app.after_request
def add_security_headers(response):
    # Essential for rendering inside the Skillev Workspace iframe
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
            background: #030303; 
            color: #FFFFFF; 
            margin: 0; 
            display: flex; 
            height: 100vh; 
            width: 100vw;
            overflow: hidden; 
        }
        
        /* SIDEBAR - Analysis Report */
        .sidebar { 
            width: 400px; 
            flex-shrink: 0;
            background: #080808; 
            border-right: 2px solid #ef4444; 
            padding: 40px 30px; 
            overflow-y: auto; 
            box-sizing: border-box; 
            display: flex;
            flex-direction: column;
        }

        .section-title { 
            color: #ef4444; 
            font-size: 1.1rem; 
            font-weight: 900; 
            text-transform: uppercase; 
            letter-spacing: 3px; 
            margin-bottom: 30px; 
            display: flex; 
            align-items: center; 
            gap: 12px; 
        }

        .section-title::after {
            content: "";
            height: 1px;
            flex-grow: 1;
            background: rgba(239, 68, 68, 0.2);
        }

        /* LOGIC CARDS */
        .logic-step { 
            background: #0c0c0c; 
            border: 1px solid #222; 
            border-left: 4px solid #ef4444;
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 25px; 
        }

        .logic-step b { 
            color: #ef4444; 
            font-size: 1rem; 
            display: block; 
            margin-bottom: 10px; 
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .logic-step p { 
            margin: 0; 
            font-size: 0.95rem; 
            color: #E0E0E0; 
            line-height: 1.6; 
        }
        
        /* CODE BOXES */
        .code-box { 
            background: #000000; 
            padding: 15px; 
            border-radius: 6px; 
            font-family: 'Consolas', 'Fira Code', monospace; 
            font-size: 0.9rem; 
            color: #FFFFFF; 
            margin-top: 15px; 
            border: 1px solid #333; 
            white-space: pre-wrap; 
            line-height: 1.5;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
        }

        .highlight { color: #f59e0b; font-weight: bold; }
        .comment { color: #666; font-style: italic; }

        /* HINT SYSTEM */
        .timer-box { 
            font-family: 'JetBrains Mono', monospace; 
            font-size: 1rem; 
            color: #f59e0b; 
            background: rgba(245, 158, 11, 0.1); 
            padding: 15px; 
            border-radius: 8px; 
            border: 1px solid rgba(245, 158, 11, 0.3); 
            text-align: center; 
            font-weight: bold;
            margin-bottom: 20px;
        }
        
        .hint-item { 
            font-size: 0.95rem; 
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 15px; 
            display: none; 
            background: #111; 
            border: 1px solid #333; 
            color: #FFFFFF; 
            line-height: 1.6; 
            animation: fadeIn 0.5s ease-in-out;
        }

        .hint-active { 
            display: block; 
            border-left: 4px solid #f59e0b; 
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* MAIN LAB AREA */
        .main-content { 
            flex-grow: 1; 
            background: radial-gradient(circle at center, #0a0a0a 0%, #030303 100%);
            display: flex; 
            align-items: center; 
            justify-content: center; 
            padding: 40px; 
        }

        .container { 
            width: 100%; 
            max-width: 420px; 
            background: #080808; 
            padding: 45px; 
            border-radius: 20px; 
            border: 1px solid #222; 
            box-shadow: 0 30px 60px rgba(0,0,0,0.6); 
        }

        .evidence-banner { 
            background: rgba(239, 68, 68, 0.1); 
            color: #ef4444; 
            padding: 12px; 
            border-radius: 6px; 
            font-size: 0.75rem; 
            margin-bottom: 30px; 
            text-align: center; 
            font-weight: 900; 
            border: 1px solid rgba(239, 68, 68, 0.3); 
            letter-spacing: 2px;
        }

        h1 { font-style: italic; font-size: 1.8rem; margin: 0 0 10px 0; color: #fff; letter-spacing: -1px; }
        
        input { 
            width: 100%; 
            padding: 16px; 
            margin: 12px 0; 
            background: #111; 
            border: 1px solid #333; 
            color: white; 
            border-radius: 10px; 
            box-sizing: border-box; 
            font-size: 1rem;
            outline: none;
            transition: all 0.2s ease;
        }

        input:focus { border-color: #ef4444; background: #151515; box-shadow: 0 0 15px rgba(239, 68, 68, 0.1); }

        input[type="submit"] { 
            background: #ef4444; 
            cursor: pointer; 
            border: none; 
            font-weight: 900; 
            text-transform: uppercase; 
            margin-top: 20px; 
            color: #000; 
            letter-spacing: 1px;
        }

        input[type="submit"]:hover { background: #ff5a5a; transform: translateY(-1px); }
        input[type="submit"]:active { transform: translateY(0); }
    </style>
</head>
<body>
    {% if mode == 'learning' %}
    <div class="sidebar">
        <div class="section-title">Analysis_Report</div>
        
        <div class="logic-step">
            <b>01. Vulnerability Detected</b>
            <p>The system relies on client-side cookies for identity verification without any cryptographic signature or server-side state check.</p>
            <div class="code-box">
<span class="comment"># Insecure Cookie Handling</span>
user_role = request.cookies.get(<span class="highlight">'user_role'</span>)
if user_role == 'admin':
    <span class="comment"># Admin access granted</span>
            </div>
        </div>

        <div class="logic-step">
            <b>02. Privilege Escalation</b>
            <p>By manually modifying the cookie value in the browser, you can assume the identity of any authorized role in the system.</p>
        </div>

        <div class="hint-container">
            <div id="hint-timer" class="timer-box">
                NEXT HINT IN: <span id="time-display">03:00</span>
            </div>
            
            <div id="hint1" class="hint-item">
                <b style="color:#f59e0b">HINT 01: Inspect the Session</b><br>
                Open Browser DevTools (F12) and navigate to the <b>Application</b> tab (Chrome) or <b>Storage</b> tab (Firefox). Select 'Cookies'.
            </div>
            
            <div id="hint2" class="hint-item">
                <b style="color:#f59e0b">HINT 02: Value Manipulation</b><br>
                Locate the <code>user_role</code> cookie. Its value is currently <code>guest</code>. Double-click it to edit.
            </div>
            
            <div id="hint3" class="hint-item">
                <b style="color:#f59e0b">HINT 03: Administrative Bypass</b><br>
                Change the value to <code>admin</code> and refresh the page. The server will trust the new value and grant access.
            </div>
        </div>
    </div>
    {% endif %}

    <div class="main-content">
        <div class="container">
            <div class="evidence-banner">🛡️ SKILLEV_PROTOCOL: {{ mode | upper }}_ACTIVE</div>
            
            <h1>Broken_Auth_Lab</h1>
            <p style="color: #666; font-size: 0.9rem; margin-bottom: 25px;">Task: Escalate session privileges to gain administrative access.</p>

            <form method="POST">
                <input type="text" name="username" placeholder="Username" value="guest" readonly>
                <input type="password" name="password" placeholder="Password" value="********" readonly>
                <input type="submit" value="Verify_Identity">
            </form>

            {% if message %} 
                <div style="margin-top:25px; padding:18px; background:#000; border-radius: 12px; border-left: 4px solid #ef4444; font-size: 0.9rem; font-family: 'Consolas', monospace; line-height: 1.5;">
                    {{ message | safe }}
                </div> 
            {% endif %}
        </div>
    </div>

    <script>
        let totalSeconds = 180; 
        let currentHintLevel = 1;
        const timeDisplay = document.getElementById('time-display');
        const timerBox = document.getElementById('hint-timer');

        function updateTimerDisplay(seconds) {
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            timeDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }

        const hintInterval = setInterval(() => {
            if (currentHintLevel > 3) {
                clearInterval(hintInterval);
                timerBox.textContent = "ALL HINTS UNLOCKED";
                return;
            }

            totalSeconds--;
            updateTimerDisplay(totalSeconds);

            if (totalSeconds <= 0) {
                const hintToReveal = document.getElementById('hint' + currentHintLevel);
                if (hintToReveal) {
                    hintToReveal.classList.add('hint-active');
                    currentHintLevel++;
                    if (currentHintLevel <= 3) {
                        totalSeconds = 180;
                        updateTimerDisplay(totalSeconds);
                    } else {
                        timerBox.textContent = "ALL HINTS UNLOCKED";
                        clearInterval(hintInterval);
                    }
                }
            }
        }, 1000);
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def login():
    mode = request.args.get('mode', 'hiring').strip().lower()
    message = ""
    
    # Check for the cookie bypass
    user_role = request.cookies.get('user_role')
    
    if user_role == 'admin':
        result_msg = "SUCCESS: Broken_Auth_Bypass_Complete"
        print(f"EVIDENCE_LOG: {result_msg}", flush=True)
        message = f"<span style='color:#ef4444;'>✅ <b>{result_msg}</b></span><br><br><span style='color: #888;'>Forensic Integrity Check: Identity spoofing successfully detected and logged to the audit chain.</span>"
    
    elif request.method == 'POST':
        username = request.form.get('username')
        print(f"EVIDENCE_LOG: [MODE:{mode.upper()}] Verification attempt: {username}", flush=True)
        message = "Access Denied: Session state 'guest' does not have required permissions."

    resp = make_response(render_template_string(HTML_TEMPLATE, message=message, mode=mode))
    
    # Initialize the vulnerable cookie if it doesn't exist
    if not user_role:
        resp.set_cookie('user_role', 'guest')
        
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)