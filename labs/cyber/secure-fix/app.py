from flask import Flask, request, render_template_string, make_response, jsonify
import time

app = Flask(__name__)

# Initial state: Vulnerable
app_config = {"is_patched": False}

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
    <title>Skillev - Secure Fix Lab</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #030303; color: #eee; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        .sidebar { width: 400px; background: #080808; border-right: 2px solid #a855f7; padding: 40px; box-sizing: border-box; overflow-y: auto; }
        .main-content { flex-grow: 1; display: flex; align-items: center; justify-content: center; padding: 40px; background: radial-gradient(circle at center, #111 0%, #030303 100%); }
        .card { width: 100%; max-width: 500px; background: #080808; padding: 40px; border-radius: 20px; border: 1px solid #222; box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
        .status { padding: 12px; border-radius: 8px; text-align: center; font-weight: 900; margin-bottom: 25px; letter-spacing: 1px; font-size: 0.8rem; }
        .vuln { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
        .secure { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
        pre { background: #000; padding: 15px; border-radius: 8px; border: 1px solid #333; color: #a855f7; font-size: 0.85rem; white-space: pre-wrap; }
        input[type="text"] { width: 100%; padding: 14px; margin: 15px 0; background: #111; border: 1px solid #333; color: white; border-radius: 8px; box-sizing: border-box; outline: none; }
        input[type="text"]:focus { border-color: #a855f7; }
        button { width: 100%; padding: 14px; background: #a855f7; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; text-transform: uppercase; color: #000; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2 style="color: #a855f7; font-style: italic;">Forensic_Fix</h2>
        <p style="font-size: 0.9rem; color: #888;">The current logic utilizes <code>eval()</code>, creating a Critical RCE vulnerability.</p>
        <p><b>Task:</b> Implement the patch by submitting the verification keyword: <code>"sanitize"</code>.</p>
        <pre># VULNERABLE CODE
result = eval(user_input)

# PROPOSED PATCH
result = int(user_input)</pre>
    </div>
    <div class="main-content">
        <div class="card">
            <div class="status {{ 'secure' if patched else 'vuln' }}">
                SHIELD_PROTOCOL: {{ 'SECURE_ID_01' if patched else 'VULNERABLE_THREAT_ACTIVE' }}
            </div>
            <form method="POST">
                <label style="font-size: 0.8rem; color: #888;">Enter Patch Verification Key:</label>
                <input type="text" name="patch_key" id="patch_key" placeholder="Awaiting Input..." required autocomplete="off">
                <button type="submit">Deploy Logic Patch</button>
            </form>
            {% if msg %}<p style="margin-top:20px; color: #a855f7; font-family: monospace; font-size: 0.9rem;">{{ msg }}</p>{% endif %}
        </div>
    </div>

    <script>
        // --- ANTI-CHEAT TELEMETRY ---
        document.getElementById('patch_key').addEventListener('paste', (e) => {
            const pastedData = (e.clipboardData || window.clipboardData).getData('text');
            fetch('/telemetry', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    event: "PASTE_DETECTED",
                    field: "patch_key",
                    content: pastedData
                })
            });
        });
    </script>
</body>
</html>
'''

@app.route('/telemetry', methods=['POST'])
def telemetry():
    data = request.json
    # Captured by Orchestrator for -0.25 integrity deduction
    print(f"EVIDENCE_LOG: [INTEGRITY_VIOLATION] {data['event']} in {data['field']}: '{data['content']}'", flush=True)
    return jsonify({"status": "captured"}), 200

@app.route('/', methods=['GET', 'POST'])
def index():
    mode = request.args.get('mode', 'hiring').strip().lower()
    msg = ""
    
    if request.method == 'POST':
        key = request.form.get('patch_key', '').lower()
        
        # Log the raw attempt
        print(f"EVIDENCE_LOG: [MODE:{mode.upper()}] Patch Attempt: '{key}'", flush=True)
        
        if key == "sanitize":
            app_config["is_patched"] = True
            result_msg = "SUCCESS: Secure_Logic_Verified. RCE mitigated."
            print(f"EVIDENCE_LOG: {result_msg}", flush=True)
            msg = f"✅ {result_msg}"
        else:
            # Log specific syntax errors for the report
            error_log = f"ERROR: Invalid patch syntax entered: '{key}'"
            print(f"EVIDENCE_LOG: [ERROR] {error_log}", flush=True)
            msg = "⚠️ ERROR: Invalid patch syntax. Deployment aborted."
    
    return render_template_string(HTML_TEMPLATE, patched=app_config["is_patched"], msg=msg, mode=mode)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)