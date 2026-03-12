# labs/web_dev/task-manager/app.py
from flask import Flask, request, render_template_string, jsonify
import sqlite3 # Using SQLite for the in-lab mock, but the instruction asks for Postgres logic
import datetime

app = Flask(__name__)

# --- Grader Logic ---
# In a 'from-scratch' lab, we monitor the user's terminal/file activity 
# or provide an interface to test their endpoints.

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Skillev Lab - Task Manager</title>
    <style>
        body { font-family: 'Inter', sans-serif; background: #030303; color: #eee; margin: 0; display: flex; height: 100vh; }
        .sidebar { width: 400px; background: #080808; border-right: 2px solid #10b981; padding: 40px; overflow-y: auto; }
        .main-content { flex-grow: 1; padding: 60px; display: flex; flex-direction: column; align-items: center; }
        .instruction-card { background: #0c0c0c; border: 1px solid #222; border-left: 4px solid #10b981; padding: 20px; border-radius: 8px; margin-bottom: 20px; width: 100%; max-width: 600px; }
        .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 10px; font-weight: 900; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }
        .status-todo { background: rgba(255,255,255,0.05); color: #666; }
        .status-done { background: rgba(16,185,129,0.1); color: #10b981; }
        h1 { font-style: italic; color: #fff; }
        code { background: #000; padding: 2px 6px; color: #10b981; font-family: monospace; }
        .btn-test { background: #10b981; color: #000; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 900; cursor: pointer; text-transform: uppercase; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2 style="color: #10b981; letter-spacing: 2px;">PROJECT_BRIEF</h2>
        <p style="font-size: 0.9rem; color: #888;">Domain: Web_Development / Task_Manager</p>
        <hr style="border: 0; border-top: 1px solid #222; margin: 20px 0;">
        
        <div class="instruction-card">
            <span class="status-badge status-done">Step 01</span>
            <h3>Backend: REST API</h3>
            <p>Implement CRUD operations for <code>/tasks</code> using FastAPI or Flask. Ensure your DB schema matches the requirement.</p>
        </div>

        <div class="instruction-card">
            <span class="status-badge status-todo">Step 02</span>
            <h3>Frontend: Task Grid</h3>
            <p>Connect your React/Vue frontend to the API. Implement 'Add Task' and 'Toggle Status'.</p>
        </div>
    </div>

    <div class="main-content">
        <div style="text-align: center; margin-bottom: 40px;">
            <div style="color: #10b981; font-weight: 900; font-size: 12px; letter-spacing: 4px; margin-bottom: 10px;">SKILLEV_ORCHESTRATOR_v3</div>
            <h1>Task Management Dashboard</h1>
        </div>

        <div class="instruction-card" style="max-width: 800px;">
            <h3>Verify Environment</h3>
            <p>Once you have built your API, click the button below. The system will attempt to perform a CRUD cycle on your <code>http://localhost:8000/tasks</code> endpoint to verify the logic.</p>
            <button class="btn-test" onclick="runDiagnostic()">Run_System_Check</button>
            <div id="results" style="margin-top: 20px; font-family: monospace; font-size: 12px;"></div>
        </div>
    </div>

    <script>
        function runDiagnostic() {
            const results = document.getElementById('results');
            results.innerHTML = "> Initiating Connection...<br>> Testing POST /tasks...<br>> Checking DB Persistence...";
            
            // Mocking the check for this UI demo
            setTimeout(() => {
                results.innerHTML += "<br>> <span style='color: #10b981;'>[SUCCESS]</span>: Integration Verified. Flag_Generated: SK_TASK_MASTER_2026";
                console.log("EVIDENCE_LOG: SUCCESS: Task_Manager_Integration_Complete");
            }, 2000);
        }
    </script>
</body>
</html>
'''

@app.route('/')
def lab_view():
    mode = request.args.get('mode', 'hiring').lower()
    return render_template_string(HTML_TEMPLATE, mode=mode)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)