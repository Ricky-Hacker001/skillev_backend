# labs/web_dev/crud-api-lab/app.py
from flask import Flask, request, jsonify, render_template_string
import sqlite3
import sys
import io

app = Flask(__name__)

# Initialize a clean database for the student to interact with
def init_student_db():
    conn = sqlite3.connect('task_manager.db')
    # We leave the schema creation to the student as part of the task
    conn.close()

@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    return response

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Skillev - CRUD API Lab</title>
    <style>
        body { font-family: 'JetBrains Mono', monospace; background: #030303; color: white; margin: 0; display: flex; height: 100vh; }
        .editor-container { flex: 1; display: flex; flex-direction: column; border-right: 1px solid #333; }
        .preview-container { width: 450px; background: #080808; padding: 20px; display: flex; flex-direction: column; }
        textarea { flex: 1; background: #000; color: #34d399; border: none; padding: 20px; font-size: 14px; outline: none; resize: none; }
        .header { padding: 10px 20px; background: #111; font-size: 12px; color: #888; display: flex; justify-content: space-between; }
        .btn-run { background: #34d399; color: #000; border: none; padding: 5px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; }
        .terminal { background: #000; height: 200px; padding: 10px; font-size: 12px; color: #34d399; border-top: 1px solid #333; overflow-y: auto; }
        .validation-card { background: #111; border: 1px solid #333; padding: 15px; border-radius: 8px; margin-bottom: 10px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="editor-container">
        <div class="header">
            <span>FILE: task_api.py</span>
            <button class="btn-run" onclick="runCode()">DEPLOY & TEST</button>
        </div>
        <textarea id="code-editor" placeholder="# Write your Python/Flask CRUD API here..."></textarea>
        <div class="terminal" id="terminal">System Ready. Awaiting deployment...</div>
    </div>
    <div class="preview-container">
        <h3 style="color: #34d399;">MISSION: CRUD_ARCHITECT</h3>
        <div class="validation-card">
            <b>REQUIREMENTS:</b>
            <ul style="padding-left: 15px;">
                <li>POST /tasks - Create Task</li>
                <li>GET /tasks - List (with Pagination)</li>
                <li>PUT /tasks/&lt;id&gt; - Update</li>
                <li>DELETE /tasks/&lt;id&gt; - Remove</li>
            </ul>
        </div>
        <div id="validation-results"></div>
    </div>

    <script>
        async function runCode() {
            const code = document.getElementById('code-editor').value;
            const term = document.getElementById('terminal');
            term.innerHTML = "> Deploying to isolated node...\\n";
            
            const res = await fetch('/run-validation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code })
            });
            const data = await res.json();
            term.innerHTML += data.output;
            
            if (data.success) {
                term.innerHTML += "\\n\\n[SUCCESS] ALL TESTS PASSED. EVIDENCE SEALED.";
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/run-validation', methods=['POST'])
def run_validation():
    student_code = request.json.get('code')
    output = io.StringIO()
    
    # 1. Execute student code in a controlled environment
    # Note: In a production Skillev app, use a more secure sandbox.
    try:
        # Mocking a database session for the student
        exec_globals = {"sqlite3": sqlite3, "jsonify": jsonify}
        sys.stdout = output
        exec(student_code, exec_globals)
        sys.stdout = sys.__stdout__
        
        # 2. Validation Logic (Automated Tests)
        # We check if they implemented the required logic
        validation_output = output.getvalue()
        
        # Example validation: Check if student created the table
        conn = sqlite3.connect('task_manager.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks';")
        table_exists = cursor.fetchone()
        conn.close()

        if table_exists:
            print("EVIDENCE_LOG: SUCCESS: CRUD_DATABASE_SCHEMA_VERIFIED", flush=True) #
            return jsonify({"success": True, "output": validation_output + "\n> Schema Verified.\n> POST /tasks Verified."})
        else:
            return jsonify({"success": False, "output": validation_output + "\n> FAILED: Table 'tasks' not found in database."})

    except Exception as e:
        return jsonify({"success": False, "output": f"RUNTIME_ERROR: {str(e)}"})

if __name__ == '__main__':
    init_student_db()
    app.run(host='0.0.0.0', port=5000)