from flask import Flask, request, render_template_string, jsonify
import time

app = Flask(__name__)

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
    <title>Skillev Lab - Task Manager</title>
    <style>
        body { font-family: 'Inter', sans-serif; background: #030303; color: #eee; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        
        /* SIDEBAR */
        .sidebar { width: 350px; background: #080808; border-right: 1px solid #222; padding: 30px; overflow-y: auto; box-sizing: border-box; }
        
        /* CENTER - CODE SPACE */
        .code-workspace { flex-grow: 1; display: flex; flex-direction: column; background: #000; border-right: 1px solid #222; }
        .tab-bar { display: flex; background: #111; border-bottom: 1px solid #222; }
        .tab { padding: 12px 20px; font-size: 11px; font-weight: 800; cursor: pointer; color: #555; text-transform: uppercase; border-right: 1px solid #222; }
        .tab.active { background: #000; color: #10b981; border-bottom: 2px solid #10b981; }
        
        .editor-container { flex-grow: 1; position: relative; }
        textarea { 
            width: 100%; height: 100%; background: #000; color: #10b981; border: none; 
            padding: 20px; font-family: 'JetBrains Mono', 'Consolas', monospace; font-size: 13px; 
            outline: none; resize: none; line-height: 1.6; box-sizing: border-box;
        }

        /* RIGHT - DIAGNOSTIC */
        .diagnostic-panel { width: 380px; padding: 30px; display: flex; flex-direction: column; box-sizing: border-box; background: #050505; }
        .instruction-card { background: #0c0c0c; border: 1px solid #222; border-left: 4px solid #10b981; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-size: 0.85rem; }
        
        .btn-test { background: #10b981; color: #000; border: none; padding: 15px; border-radius: 8px; font-weight: 900; cursor: pointer; text-transform: uppercase; margin-bottom: 15px; }
        #results { background: #000; padding: 15px; border-radius: 8px; border: 1px solid #333; flex-grow: 1; font-family: monospace; font-size: 11px; color: #aaa; white-space: pre-wrap; overflow-y: auto; }
        
        input { width: 100%; padding: 10px; background: #111; border: 1px solid #333; color: #10b981; border-radius: 4px; margin-bottom: 15px; outline: none; box-sizing: border-box; }
        .label { font-size: 0.65rem; color: #444; font-weight: 900; text-transform: uppercase; margin-bottom: 8px; display: block; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2 style="color: #10b981; font-size: 1.2rem;">PROJECT_BRIEF</h2>
        <div class="instruction-card">
            <b style="color: #10b981;">Phase 01:</b> Build a REST API using the templates provided. Ensure <code>cors</code> is enabled so this dashboard can connect.
        </div>
        <div class="instruction-card">
            <b style="color: #10b981;">Phase 02:</b> Run your server on <b>Port 8001</b> and verify using the Health Check panel.
        </div>
    </div>

    <div class="code-workspace">
        <div class="tab-bar">
            <div class="tab active" onclick="switchTab('fastapi')">Python (FastAPI)</div>
            <div class="tab" onclick="switchTab('node')">Node.js (Express)</div>
        </div>
        <div class="editor-container">
            <textarea id="editor" spellcheck="false"></textarea>
        </div>
    </div>

    <div class="diagnostic-panel">
        <span class="label">🛡️ Protocol: {{ mode | upper }}</span>
        <span class="label">Target API Endpoint</span>
        <input type="text" id="api_url" value="http://localhost:8001/tasks">
        
        <button class="btn-test" onclick="runDiagnostic()">Run_System_Check</button>
        
        <span class="label">Audit Log</span>
        <div id="results">System idle... awaiting connection.</div>
    </div>

    <script>
        const editors = {
            fastapi: `from fastapi import FastAPI\\nfrom fastapi.middleware.cors import CORSMiddleware\\nfrom pydantic import BaseModel\\n\\napp = FastAPI()\\n\\napp.add_middleware(\\n    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]\\n)\\n\\ntasks_db = []\\n\\nclass Task(BaseModel):\\n    title: str\\n    status: str\\n\\n@app.post("/tasks")\\nasync def create(task: Task):\\n    tasks_db.append(task.dict())\\n    return {"status": "saved"}\\n\\n@app.get("/tasks")\\nasync def list_tasks():\\n    return tasks_db\\n\\n# Run: uvicorn main:app --port 8001`,
            node: `const express = require('express');\\nconst cors = require('cors');\\nconst app = express();\\n\\napp.use(express.json());\\napp.use(cors());\\n\\nlet tasks = [];\\n\\napp.post('/tasks', (req, res) => {\\n    tasks.push(req.body);\\n    res.status(201).json({ status: "saved" });\\n});\\n\\napp.get('/tasks', (req, res) => {\\n    res.json(tasks);\\n});\\n\\napp.listen(8001, () => console.log('Server on 8001'));`
        };

        const editorEl = document.getElementById('editor');
        editorEl.value = editors.fastapi;

        function switchTab(lang) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            editorEl.value = editors[lang];
        }

        // --- TELEMETRY ---
        editorEl.addEventListener('paste', (e) => {
            fetch('/telemetry', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ event: "PASTE_DETECTED", field: "code_editor", content: "Code block pasted into editor" })
            });
        });

        async function runDiagnostic() {
            const results = document.getElementById('results');
            const targetUrl = document.getElementById('api_url').value;
            results.innerHTML = `> PINGing ${targetUrl}...\\n`;
            
            try {
                const testTitle = "Audit_" + Math.floor(Math.random() * 9999);
                
                // POST Test
                results.innerHTML += "> Testing POST /tasks...\\n";
                const postRes = await fetch(targetUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title: testTitle, status: "todo" })
                });
                if (!postRes.ok) throw new Error("POST Failed");

                // GET Test
                results.innerHTML += "> Verifying GET /tasks...\\n";
                const getRes = await fetch(targetUrl);
                const data = await getRes.json();

                if (Array.isArray(data) && data.some(t => t.title === testTitle)) {
                    results.innerHTML += "> <span style='color:#10b981'>[SUCCESS]</span>: Integration Verified.\\n> Flag: SK_TASK_MASTER_2026";
                    fetch('/report_success', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ flag: "SK_TASK_MASTER_2026" }) });
                } else {
                    throw new Error("Persistence Mismatch");
                }
            } catch (err) {
                results.innerHTML += `> <span style='color:#ef4444'>[ERROR]</span>: ${err.message}\\n> Check CORS and Port 8001.`;
                fetch('/telemetry', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ event: "FAIL", content: err.message }) });
            }
        }
    </script>
</body>
</html>
'''

@app.route('/telemetry', methods=['POST'])
def telemetry():
    data = request.json
    print(f"EVIDENCE_LOG: [INTEGRITY_VIOLATION] {data['event']} in {data['field']}", flush=True)
    return jsonify({"status": "captured"}), 200

@app.route('/report_success', methods=['POST'])
def report_success():
    data = request.json
    print(f"EVIDENCE_LOG: SUCCESS: Task_Manager_Complete via {data.get('flag')}", flush=True)
    return jsonify({"status": "ok"}), 200

@app.route('/')
def lab_view():
    mode = request.args.get('mode', 'hiring').strip().lower()
    return render_template_string(HTML_TEMPLATE, mode=mode)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)