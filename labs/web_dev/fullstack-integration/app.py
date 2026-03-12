from flask import Flask, request, render_template_string, jsonify
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
    return response

# --- API ENDPOINTS ---
@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"status": DATABASE["system_status"]})

@app.route('/api/data', methods=['POST'])
def get_data():
    auth_header = request.headers.get('Authorization')
    data = request.json
    
    if auth_header == f"Bearer {DATABASE['authorized_token']}" and data.get("request_code") == "REQ_DATA":
        print("EVIDENCE_LOG: SUCCESS: API_Link_Established", flush=True)
        return jsonify({"success": True, "secret": DATABASE["secure_data"]})
    
    return jsonify({"success": False, "message": "Unauthorized or Invalid Request Code"}), 401

# --- LAB TEMPLATE ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Full-Stack Link Lab</title>
    <style>
        body { font-family: 'Inter', sans-serif; background: #030303; color: white; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        
        /* SIDEBAR / HINT SECTION */
        .sidebar { 
            width: 380px; 
            background: #080808; 
            border-right: 1px solid #333; 
            display: flex; 
            flex-direction: column; 
            padding: 30px;
            box-sizing: border-box;
            overflow-y: auto;
        }

        .editor-side { flex-grow: 1; display: flex; flex-direction: column; border-right: 1px solid #333; }
        .preview-side { width: 350px; background: #050505; padding: 30px; box-sizing: border-box; }
        
        .header { padding: 15px; background: #111; border-bottom: 1px solid #333; font-size: 0.7rem; font-weight: 800; letter-spacing: 2px; color: #10b981; }
        
        #code-editor { 
            flex-grow: 1; 
            background: #000; 
            color: #10b981; 
            font-family: 'Consolas', monospace; 
            font-size: 14px; 
            padding: 20px; 
            border: none; 
            outline: none; 
            resize: none; 
        }

        /* HINT STYLING */
        .timer-box { 
            font-family: monospace; 
            font-size: 0.8rem; 
            color: #f59e0b; 
            background: rgba(245, 158, 11, 0.1); 
            padding: 10px; 
            border-radius: 4px; 
            text-align: center; 
            margin-bottom: 20px;
            border: 1px solid rgba(245, 158, 11, 0.2);
        }

        .hint-card { 
            background: #111; 
            border: 1px solid #222; 
            padding: 15px; 
            border-radius: 8px; 
            margin-bottom: 15px; 
            font-size: 0.85rem; 
            line-height: 1.4;
            display: none; 
            animation: slideIn 0.4s ease-out;
        }
        .hint-card b { color: #f59e0b; display: block; margin-bottom: 5px; text-transform: uppercase; font-size: 0.7rem; }
        .hint-visible { display: block; border-left: 3px solid #f59e0b; }

        @keyframes slideIn { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }

        .run-btn { background: #10b981; color: black; border: none; padding: 15px; font-weight: 900; cursor: pointer; text-transform: uppercase; }
        .preview-box { background: #000; border: 1px solid #222; border-radius: 8px; padding: 15px; min-height: 150px; font-family: monospace; font-size: 0.9rem; }
        .label { color: #444; font-size: 0.65rem; text-transform: uppercase; margin-bottom: 10px; display: block; font-weight: 800; }
        code { background: #222; padding: 2px 4px; border-radius: 3px; color: #fff; }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="header" style="background:transparent; padding:0; margin-bottom:20px;">ANALYSIS_HINTS</div>
        
        <div id="timer" class="timer-box">NEXT HINT IN: 03:00</div>

        <div id="hint1" class="hint-card hint-visible">
            <b>Hint 01: Method Selection</b>
            The default <code>fetch()</code> is a GET. To send data to <code>/api/data</code>, you must set the <code>method</code> property to <code>'POST'</code>.
        </div>

        <div id="hint2" class="hint-card hint-visible">
            <b>Hint 02: Content-Type</b>
            The backend expects JSON. Add <code>'Content-Type': 'application/json'</code> to your <code>headers</code> object.
        </div>

        <div id="hint3" class="hint-card">
            <b>Hint 03: Authorization</b>
            The documentation mentions a token. Use the header key <code>'Authorization'</code> with the value <code>'Bearer SK-9921-X'</code>.
        </div>

        <div id="hint4" class="hint-card">
            <b>Hint 04: JSON Body</b>
            You cannot send a raw object. You must use <code>JSON.stringify({ request_code: 'REQ_DATA' })</code> as the body.
        </div>

        <div id="hint5" class="hint-card">
            <b>Hint 05: The Final Link</b>
            Combine them: <code>fetch('/api/data', { method: 'POST', headers: {...}, body: JSON.stringify(...) })</code>. Don't forget to <code>await</code> the result!
        </div>
    </div>

    <div class="editor-side">
        <div class="header">SYSTEM_ORCHESTRATOR: EDIT FRONTEND LINKAGE</div>
        <textarea id="code-editor" spellcheck="false">async function syncWithBackend() {
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

syncWithBackend();</textarea>
        <button class="run-btn" onclick="executeCode()">Execute Integration Test</button>
    </div>

    <div class="preview-side">
        <span class="label">Backend Documentation</span>
        <div style="font-size: 0.75rem; color: #888; margin-bottom: 20px; line-height: 1.6;">
            Endpoint: <code>/api/data</code><br>
            Method: <code>POST</code><br>
            Auth: <code>Bearer SK-9921-X</code><br>
            Body: <code>{"request_code": "REQ_DATA"}</code>
        </div>
        
        <span class="label">Terminal Output</span>
        <div id="output" class="preview-box">Awaiting Execution...</div>
    </div>

    <script>
        // HINT TIMER LOGIC
        let totalSeconds = 180;
        let currentHint = 3; // Starting with 3 because 1 & 2 are visible by default

        const timerEl = document.getElementById('timer');

        setInterval(() => {
            if (currentHint > 5) {
                timerEl.innerText = "ALL HINTS UNLOCKED";
                return;
            }

            totalSeconds--;
            
            let mins = Math.floor(totalSeconds / 60);
            let secs = totalSeconds % 60;
            timerEl.innerText = `NEXT HINT IN: ${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

            if (totalSeconds <= 0) {
                document.getElementById('hint' + currentHint).classList.add('hint-visible');
                currentHint++;
                totalSeconds = 180; // Reset for next hint
            }
        }, 1000);

        async function executeCode() {
            const output = document.getElementById('output');
            const code = document.getElementById('code-editor').value;
            output.innerHTML = "<span style='color: #444'>Linking...</span>";
            
            try {
                const result = await eval(`(async () => { ${code} })()`);
                output.innerHTML = result ? `<span style="color:#10b981">${result}</span>` : "No data returned.";
            } catch (err) {
                output.innerHTML = `<span style="color:#ef4444">ERR: ${err.message}</span>`;
            }
        }

        // Tab support
        document.getElementById('code-editor').addEventListener('keydown', function(e) {
            if (e.key == 'Tab') {
                e.preventDefault();
                var start = this.selectionStart;
                var end = this.selectionEnd;
                this.value = this.value.substring(0, start) + "    " + this.value.substring(end);
                this.selectionStart = this.selectionEnd = start + 4;
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)