from flask import Flask, request, render_template_string, jsonify
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE users (id INTEGER, username TEXT, password TEXT)')
    # Initial admin record for the lab challenge
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'skillev_secret_123')")
    return conn

db = init_db()

@app.after_request
def add_security_headers(response):
    # This tells the browser it's okay to send data from port 5173
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    response.headers['Content-Security-Policy'] = "frame-ancestors *"
    return response

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Skillev Lab</title>
    <style>
        body { 
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
            background: #030303; color: #FFFFFF; margin: 0; display: flex; 
            height: 100vh; width: 100vw; overflow: hidden; 
        }
        
        .sidebar { 
            width: 400px; flex-shrink: 0; background: #080808; 
            border-right: 2px solid #10b981; padding: 40px 30px; 
            overflow-y: auto; box-sizing: border-box; display: flex; flex-direction: column;
        }

        .section-title { 
            color: #10b981; font-size: 1.1rem; font-weight: 900; 
            text-transform: uppercase; letter-spacing: 3px; margin-bottom: 30px; 
            display: flex; align-items: center; gap: 12px; 
        }

        .logic-step { 
            background: #0c0c0c; border: 1px solid #222; border-left: 4px solid #10b981;
            padding: 20px; border-radius: 8px; margin-bottom: 25px; 
        }

        .logic-step b { color: #10b981; display: block; margin-bottom: 10px; text-transform: uppercase; }
        
        .code-box { 
            background: #000000; padding: 15px; border-radius: 6px; 
            font-family: 'Consolas', monospace; font-size: 0.9rem; margin-top: 15px; border: 1px solid #333; 
        }

        .timer-box { 
            font-family: 'JetBrains Mono', monospace; font-size: 1rem; color: #f59e0b; 
            background: rgba(245, 158, 11, 0.1); padding: 15px; border-radius: 8px; 
            border: 1px solid rgba(245, 158, 11, 0.3); text-align: center; margin-bottom: 20px;
        }
        
        .hint-item { font-size: 0.95rem; padding: 20px; border-radius: 8px; margin-bottom: 15px; display: none; background: #111; border: 1px solid #333; animation: fadeIn 0.5s ease-in-out; }
        .hint-active { display: block; border-left: 4px solid #f59e0b; }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        .main-content { flex-grow: 1; background: radial-gradient(circle at center, #0a0a0a 0%, #030303 100%); display: flex; align-items: center; justify-content: center; padding: 40px; }
        .container { width: 100%; max-width: 420px; background: #080808; padding: 45px; border-radius: 20px; border: 1px solid #222; box-shadow: 0 30px 60px rgba(0,0,0,0.6); }
        .evidence-banner { background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 12px; border-radius: 6px; font-size: 0.75rem; margin-bottom: 30px; text-align: center; font-weight: 900; border: 1px solid rgba(16, 185, 129, 0.3); letter-spacing: 2px; }

        input { width: 100%; padding: 16px; margin: 12px 0; background: #111; border: 1px solid #333; color: white; border-radius: 10px; box-sizing: border-box; font-size: 1rem; outline: none; }
        input:focus { border-color: #10b981; background: #151515; }
        input[type="submit"] { background: #10b981; cursor: pointer; border: none; font-weight: 900; text-transform: uppercase; margin-top: 20px; color: #000; }
    </style>
</head>
<body>
    {% if mode == 'learning' %}
    <div class="sidebar">
        <div class="section-title">Analysis_Report</div>
        <div class="logic-step">
            <b>01. Vulnerability Detected</b>
            <p>Direct string concatenation allows user input to modify the query logic.</p>
        </div>

        <div id="hint-timer" class="timer-box">NEXT HINT IN: <span id="time-display">03:00</span></div>
        <div id="hint1" class="hint-item"><b>HINT 01: Break the String</b><br>Try entering <code>'</code> to cause a syntax error.</div>
        <div id="hint2" class="hint-item"><b>HINT 02: Commenting</b><br>Use <code>-- </code> to ignore the rest of the query.</div>
        <div id="hint3" class="hint-item"><b>HINT 03: Payload</b><br>Full bypass: <code>admin' -- </code></div>
    </div>
    {% endif %}

    <div class="main-content">
        <div class="container">
            <div class="evidence-banner">🛡️ SKILLEV_PROTOCOL: {{ mode | upper }}_ACTIVE</div>
            <h1>SQL_Injection_Lab</h1>
            <form method="POST">
                <input type="text" name="username" id="username" placeholder="User_Identity" required autocomplete="off">
                <input type="password" name="password" id="password" placeholder="Access_Key" autocomplete="off">
                <input type="submit" value="Verify_Credentials">
            </form>
            {% if message %} 
                <div style="margin-top:25px; padding:18px; background:#000; border-radius: 12px; border-left: 4px solid #10b981; font-family: 'Consolas', monospace; font-size: 0.9rem;">
                    {{ message | safe }}
                </div> 
            {% endif %}
        </div>
    </div>

    <script>

        // --- ANTI-CHEAT TELEMETRY ---
    // Use a function to ensure listeners are attached even if DOM loads late
    function initTelemetry() {
        const inputs = ['username', 'password'];
        inputs.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                // Remove existing to avoid duplicates
                el.removeEventListener('paste', handlePaste);
                el.addEventListener('paste', handlePaste);
            }
        });
    }

    function handlePaste(e) {
        const pastedData = (e.clipboardData || window.clipboardData).getData('text');
        console.log("Telemetry Triggered: Paste detected"); // Check console for this!
        
        fetch('/telemetry', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                event: "PASTE_DETECTED",
                field: e.target.name,
                content: pastedData
            })
        }).catch(err => console.error("Telemetry Failed:", err));
    }

    // Run on load
    window.addEventListener('DOMContentLoaded', initTelemetry);
    // Run immediately just in case
    initTelemetry();

        // --- HINT SYSTEM ---
        let totalSeconds = 180; let currentHintLevel = 1;
        const timeDisplay = document.getElementById('time-display');
        setInterval(() => {
            if (currentHintLevel > 3) return;
            totalSeconds--;
            if (timeDisplay) {
                const mins = Math.floor(totalSeconds / 60);
                const secs = totalSeconds % 60;
                timeDisplay.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
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



# Also, update the telemetry route to handle preflight
@app.route('/telemetry', methods=['POST', 'OPTIONS'])
def telemetry():
    if request.method == 'OPTIONS':
        return '', 204 # Return "OK" to the browser's preflight check
        
    data = request.json
    print(f"EVIDENCE_LOG: [INTEGRITY_VIOLATION] {data['event']} in {data['field']}: '{data['content']}'", flush=True)
    return jsonify({"status": "captured"}), 200

@app.route('/', methods=['GET', 'POST'])
def login():
    mode = request.args.get('mode', 'hiring').strip().lower()
    message = ""
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Log basic attempt
        print(f"EVIDENCE_LOG: [MODE:{mode.upper()}] Execution Attempt: {username}", flush=True)
        
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        
        try:
            cursor = db.cursor()
            user = cursor.execute(query).fetchone()
            if user:
                result_msg = f"SUCCESS: Flag_Captured_By_{user[1]}"
                print(f"EVIDENCE_LOG: {result_msg}", flush=True)
                message = f"<span style='color:#10b981;'>✅ <b>{result_msg}</b></span>"
            else:
                message = "<span style='color:#ef4444;'>❌ ACCESS_DENIED: Credential verification failed.</span>"
        except Exception as e:
            # Detailed error logging for the report
            error_msg = f"SQL_ERROR: Syntax Malformed. Full Error: {str(e)}"
            print(f"EVIDENCE_LOG: [ERROR] {error_msg}", flush=True)
            message = f"<span style='color:#f59e0b;'>⚠️ <b>SQL_ERROR:</b> Syntax Malformed in query string.</span>"
            
    return render_template_string(HTML_TEMPLATE, message=message, mode=mode)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)