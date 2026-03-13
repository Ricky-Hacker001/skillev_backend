from flask import Flask, request, render_template_string, jsonify, make_response
import time

app = Flask(__name__)

# --- MOCK BACKEND DATA ---
DATABASE = {
    "system_status": "Online",
    "secure_data": "SKILLEV{FULL_STACK_INTEGRATION_MASTERED}",
    "authorized_token": "SK-9921-X"
}

@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    response.headers['Content-Security-Policy'] = "frame-ancestors *"
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

# --- API ENDPOINTS ---
@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"status": DATABASE["system_status"]})

@app.route('/api/data', methods=['POST'])
def get_data():
    auth_header = request.headers.get('Authorization')
    try:
        data = request.json
    except Exception:
        data = "INVALID_JSON_BODY"

    # Log the attempt for Evidence Engine analysis
    print(f"EVIDENCE_LOG: [INTERACTION] API_CALL: Auth='{auth_header}' | Payload='{data}'", flush=True)
    
    if auth_header == f"Bearer {DATABASE['authorized_token']}" and isinstance(data, dict) and data.get("request_code") == "REQ_DATA":
        result_msg = "SUCCESS: API_Link_Established"
        print(f"EVIDENCE_LOG: {result_msg}", flush=True)
        return jsonify({"success": True, "secret": DATABASE["secure_data"]})
    
    # Log specific error for the report
    error_msg = "AUTH_ERROR: Unauthorized access attempt or malformed request schema."
    print(f"EVIDENCE_LOG: [ERROR] {error_msg}", flush=True)
    return jsonify({"success": False, "message": error_msg}), 401

@app.route('/telemetry', methods=['POST'])
def telemetry():
    """Captures browser events and prints them for the Evidence Engine."""
    data = request.json
    # Intercepted by Orchestrator for -0.25 integrity deduction
    print(f"EVIDENCE_LOG: [INTEGRITY_VIOLATION] {data['event']} in {data['field']}: '{data['content']}'", flush=True)
    return jsonify({"status": "captured"}), 200

# --- LAB TEMPLATE ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Full-Stack Link Lab</title>
    <style>
        body { font-family: 'Inter', sans-serif; background: #030303; color: white; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        .sidebar { width: 380px; background: #080808; border-right: 1px solid #333; display: flex; flex-direction: column; padding: 30px; box-sizing: border-box; overflow-y: auto; }
        .editor-side { flex-grow: 1; display: flex; flex-direction: column; border-right: 1px solid #333; }
        .preview-side { width: 350px; background: #050505; padding: 30px; box-sizing: border-box; }
        .header { padding: 15px; background: #111; border-bottom: 1px solid #333; font-size: 0.7rem; font-weight: 800; letter-spacing: 2px; color: #10b981; }
        #code-editor { flex-grow: 1; background: #000; color: #10b981; font-family: 'Consolas', monospace; font-size: 14px; padding: 20px; border: none; outline: none; resize: none; line-height: 1.5; }
        .timer-box { font-family: monospace; font-size: 0.8rem; color: #f59e0b; background: rgba(245, 158, 11, 0.1); padding: 10px; border-radius: 4px; text-align: center; margin-bottom: 20px; border: 1px solid rgba(245, 158, 11, 0.2); }
        .hint-card { background: #111; border: 1px solid #222; padding: 15px; border-radius: 8px; margin-bottom: 15px; font-size: 0.85rem; display: none; border-left: 3px solid #f59e0b; }
        .hint-card b { color: #f59e0b; display: block; margin-bottom: 5px; text-transform: uppercase; font-size: 0.7rem; }
        .hint-visible { display: block; animation: slideIn 0.3s ease-out; }
        @keyframes slideIn { from { opacity: 0; transform: translateX(-5px); } to { opacity: 1; transform: translateX(0); } }
        .run-btn { background: #10b981; color: black; border: none; padding: 15px; font-weight: 900; cursor: pointer; text-transform: uppercase; }
        .preview-box { background: #000; border: 1px solid #222; border-radius: 8px; padding: 15px; min-height: 150px; font-family: monospace; font-size: 0.9rem; white-space: pre-wrap; word-break: break-all; }
        .label { color: #444; font-size: 0.65rem; text-transform: uppercase; margin-bottom: 10px; display: block; font-weight: 800; margin-top: 20px; }
        code { background: #222; padding: 2px 4px; border-radius: 3px; color: #fff; }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="header" style="background:transparent; padding:0; margin-bottom:20px;">ANALYSIS_HINTS</div>
        <div id="timer" class="timer-box">NEXT HINT IN: <span id="time-display">03:00</span></div>
        <div id="hint1" class="hint-card hint-visible"><b>Hint 01: Method</b><br>Set <code>method: 'POST'</code> in the fetch options.</div>
        <div id="hint2" class="hint-card hint-visible"><b>Hint 02: Headers</b><br>Add <code>'Content-Type': 'application/json'</code>.</div>
        <div id="hint3" class="hint-card"><b>Hint 03: Auth</b><br>Include <code>'Authorization': 'Bearer SK-9921-X'</code>.</div>
        <div id="hint4" class="hint-card"><b>Hint 04: Body</b><br>Use <code>JSON.stringify({ request_code: 'REQ_DATA' })</code>.</div>
    </div>

    <div class="editor-side">
        <div class="header">SYSTEM_ORCHESTRATOR: EDIT FRONTEND LINKAGE</div>
        <textarea id="code-editor" spellcheck="false" placeholder="// Write your integration code here...">async function syncWithBackend() {
    // 1. Check system status (GET)
    const statusRes = await fetch('/api/status');
    const statusData = await statusRes.json();
    console.log('Status:', statusData.status);

    // 2. Authorize and Fetch Secure Data (POST)
    const dataRes = await fetch('/api/data', {
        // CODE_NEEDED: Add method, headers, and body
    });

    const finalData = await dataRes.json();
    return finalData.secret || finalData.message;
}

return await syncWithBackend();</textarea>
        <button class="run-btn" onclick="executeCode()">Execute Integration Test</button>
    </div>

    <div class="preview-side">
        <span class="label">Backend Documentation</span>
        <div style="font-size: 0.75rem; color: #888; line-height: 1.6;">
            Endpoint: <code>/api/data</code><br>
            Method: <code>POST</code><br>
            Auth: <code>Bearer SK-9921-X</code><br>
            Body: <code>{"request_code": "REQ_DATA"}</code>
        </div>
        
        <span class="label">Terminal Output</span>
        <div id="output" class="preview-box">Awaiting Execution...</div>
    </div>

    <script>
        // --- ANTI-CHEAT TELEMETRY ---
        document.getElementById('code-editor').addEventListener('paste', (e) => {
            const pastedData = (e.clipboardData || window.clipboardData).getData('text');
            fetch('/telemetry', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    event: "PASTE_DETECTED",
                    field: "code-editor",
                    content: pastedData
                })
            });
        });

        // --- HINT TIMER ---
        let totalSeconds = 180;
        let currentHint = 3;
        const timeDisplay = document.getElementById('time-display');

        setInterval(() => {
            if (currentHint > 4) {
                document.getElementById('timer').innerText = "ALL HINTS UNLOCKED";
                return;
            }
            totalSeconds--;
            const mins = Math.floor(totalSeconds / 60);
            const secs = totalSeconds % 60;
            timeDisplay.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;

            if (totalSeconds <= 0) {
                const h = document.getElementById('hint' + currentHint);
                if (h) h.classList.add('hint-visible');
                currentHint++;
                totalSeconds = 180;
            }
        }, 1000);

        async function executeCode() {
            const output = document.getElementById('output');
            const code = document.getElementById('code-editor').value;
            output.innerHTML = "<span style='color: #444'>Linking...</span>";
            
            try {
                // We wrap the code in a function block that allows 'return' to work via eval
                const result = await eval(`(async () => { ${code} })()`);
                output.innerHTML = result ? `<span style="color:#10b981">${result}</span>` : "No data returned.";
            } catch (err) {
                output.innerHTML = `<span style="color:#ef4444">ERR: ${err.message}</span>`;
                // Log runtime error to terminal for Evidence Engine
                console.log("EVIDENCE_LOG: [ERROR] RUNTIME_EXCEPTION: " + err.message);
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)