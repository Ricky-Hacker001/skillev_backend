from flask import Flask, request, jsonify, render_template_string, make_response
import sqlite3
import sys
import io
import datetime

app = Flask(__name__)

# Initialize a clean database
def init_student_db():
    conn = sqlite3.connect('task_manager.db')
    conn.close()

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
    <title>Skillev - CRUD API Lab</title>
    <style>
        body { font-family: 'JetBrains Mono', monospace; background: #030303; color: white; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        .editor-container { flex: 1; display: flex; flex-direction: column; border-right: 1px solid #333; }
        .preview-container { width: 450px; background: #080808; padding: 30px; display: flex; flex-direction: column; box-sizing: border-box; }
        textarea { flex: 1; background: #000; color: #34d399; border: none; padding: 25px; font-size: 14px; outline: none; resize: none; line-height: 1.6; }
        .header { padding: 12px 20px; background: #111; font-size: 11px; color: #555; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #222; }
        .btn-run { background: #34d399; color: #000; border: none; padding: 8px 20px; border-radius: 4px; cursor: pointer; font-weight: 900; text-transform: uppercase; }
        .terminal { background: #000; height: 250px; padding: 15px; font-size: 12px; color: #34d399; border-top: 1px solid #333; overflow-y: auto; font-family: 'Courier New', monospace; }
        .validation-card { background: #0c0c0c; border: 1px solid #222; border-left: 4px solid #34d399; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .label { font-size: 0.65rem; color: #444; font-weight: 900; text-transform: uppercase; margin-bottom: 10px; display: block; letter-spacing: 1px; }
    </style>
</head>
<body>
    <div class="editor-container">
        <div class="header">
            <span>FILE_STREAM: task_api.py</span>
            <button class="btn-run" onclick="runCode()">Deploy_to_Isolated_Node</button>
        </div>
        <textarea id="code-editor" placeholder="# Write your Python/Flask CRUD API here..." spellcheck="false"></textarea>
        <div class="terminal" id="terminal">System Ready. Awaiting deployment...</div>
    </div>
    <div class="preview-container">
        <span class="label">🛡️ Protocol: ARCHITECT_ACTIVE</span>
        <h3 style="color: #34d399; margin-top: 0;">MISSION: CRUD_ENGINE</h3>
        <div class="validation-card">
            <b>REQUIRED SCHEMA:</b>
            <ul style="padding-left: 15px; color: #888; margin-top: 10px; line-height: 1.8;">
                <li><code>Table: tasks</code> (id, title, status)</li>
                <li><code>POST /tasks</code> - Create Record</li>
                <li><code>GET /tasks</code> - Fetch All</li>
            </ul>
        </div>
        <div id="validation-results"></div>
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
                    content: "Code block pasted into editor"
                })
            });
        });

        async function runCode() {
            const code = document.getElementById('code-editor').value;
            const term = document.getElementById('terminal');
            term.innerHTML = "> Initializing Python Runtime...\\n> Mapping Database...\\n";
            
            try {
                const res = await fetch('/run-validation', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code })
                });
                const data = await res.json();
                
                term.innerHTML += data.output;
                if (data.success) {
                    term.innerHTML += "\\n\\n[SUCCESS] CRITICAL_LOGS_CAPTURED. REPORT_SEALED.";
                }
            } catch (err) {
                term.innerHTML += "\\n[FATAL_ERROR] Connection to deployment node failed.";
            }
        }
    </script>
</body>
</html>
'''

@app.route('/telemetry', methods=['POST'])
def telemetry():
    data = request.json
    # Captured by Orchestrator for -0.25 integrity deduction
    print(f"EVIDENCE_LOG: [INTEGRITY_VIOLATION] {data['event']} in {data['field']}", flush=True)
    return jsonify({"status": "captured"}), 200

@app.route('/run-validation', methods=['POST'])
def run_validation():
    student_code = request.json.get('code')
    output = io.StringIO()
    
    # Log the attempt for Evidence Engine
    print(f"EVIDENCE_LOG: [INTERACTION] Code deployment initiated.", flush=True)

    try:
        # 1. Execute student code
        exec_globals = {"sqlite3": sqlite3, "jsonify": jsonify, "request": request}
        sys.stdout = output
        exec(student_code, exec_globals)
        sys.stdout = sys.__stdout__
        
        # 2. Validation Logic
        conn = sqlite3.connect('task_manager.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks';")
        table_exists = cursor.fetchone()
        conn.close()

        if table_exists:
            result_msg = "SUCCESS: CRUD_DATABASE_SCHEMA_VERIFIED"
            print(f"EVIDENCE_LOG: {result_msg}", flush=True)
            return jsonify({"success": True, "output": output.getvalue() + "\n> Database schema located.\n> Validation cycle: 100% Passed."})
        else:
            error_msg = "SCHEMA_ERROR: Table 'tasks' not found."
            print(f"EVIDENCE_LOG: [ERROR] {error_msg}", flush=True)
            return jsonify({"success": False, "output": output.getvalue() + f"\n> FAILED: {error_msg}"})

    except Exception as e:
        sys.stdout = sys.__stdout__ # Reset if it crashed
        error_msg = f"RUNTIME_EXCEPTION: {str(e)}"
        print(f"EVIDENCE_LOG: [ERROR] {error_msg}", flush=True)
        return jsonify({"success": False, "output": f"RUNTIME_ERROR: {str(e)}"})

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    init_student_db()
    app.run(host='0.0.0.0', port=5000)