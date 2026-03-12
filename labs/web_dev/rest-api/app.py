from flask import Flask, request, jsonify, render_template_string
import time

app = Flask(__name__)

# Mock Database for the session
data_store = [{"id": 1, "name": "Initial Resource"}]

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
    <title>Skillev Lab - REST API Visualizer</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #050505; color: #FFFFFF; margin: 0; display: flex; height: 100vh; width: 100vw; overflow: hidden; }
        
        /* SIDEBAR - Architecture Report */
        .sidebar { width: 400px; flex-shrink: 0; background: #080808; border-right: 2px solid #10b981; padding: 40px 30px; overflow-y: auto; box-sizing: border-box; display: flex; flex-direction: column; }
        .section-title { color: #10b981; font-size: 1.1rem; font-weight: 900; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 30px; display: flex; align-items: center; gap: 12px; }
        .section-title::after { content: ""; height: 1px; flex-grow: 1; background: rgba(16, 185, 129, 0.2); }

        .logic-step { background: #0c0c0c; border: 1px solid #222; border-left: 4px solid #10b981; padding: 20px; border-radius: 8px; margin-bottom: 25px; }
        .logic-step b { color: #10b981; font-size: 1rem; display: block; margin-bottom: 10px; text-transform: uppercase; }
        
        /* JSON Visualizer in Sidebar */
        .json-viz { background: #000; border: 1px dashed #444; padding: 12px; margin-top: 10px; border-radius: 6px; font-family: monospace; font-size: 0.85rem; }
        .key { color: #f59e0b; }
        .val { color: #10b981; }

        /* HINT SYSTEM */
        .timer-box { font-family: monospace; font-size: 1rem; color: #f59e0b; background: rgba(245, 158, 11, 0.1); padding: 15px; border-radius: 8px; border: 1px solid rgba(245, 158, 11, 0.3); text-align: center; margin-bottom: 20px; }
        .hint-item { font-size: 0.95rem; padding: 20px; border-radius: 8px; margin-bottom: 15px; display: none; background: #111; border: 1px solid #333; animation: fadeIn 0.5s ease-in-out; }
        .hint-active { display: block; border-left: 4px solid #f59e0b; }

        /* MAIN WORKSPACE */
        .main-content { flex-grow: 1; background: radial-gradient(circle at center, #0a0a0a 0%, #030303 100%); display: flex; flex-direction: column; padding: 40px; gap: 20px; }
        
        /* PIPELINE ANIMATION */
        .pipeline { display: flex; align-items: center; justify-content: space-between; background: #080808; padding: 25px; border-radius: 20px; border: 1px solid #222; margin-bottom: 10px; }
        .node { padding: 12px; border-radius: 8px; border: 1px solid #333; background: #000; text-align: center; width: 110px; font-size: 10px; font-weight: bold; letter-spacing: 1px; }
        .arrow { flex-grow: 1; height: 2px; background: #222; margin: 0 15px; position: relative; overflow: hidden; }
        .pulse { position: absolute; width: 60px; height: 100%; background: linear-gradient(90deg, transparent, #10b981, transparent); left: -60px; }
        .active-pulse { animation: movePulse 1s infinite linear; }
        @keyframes movePulse { from { left: -60px; } to { left: 100%; } }

        /* INTERACTIVE CONSOLE */
        .console-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; flex-grow: 1; }
        .box { background: #080808; border: 1px solid #222; border-radius: 15px; display: flex; flex-direction: column; overflow: hidden; }
        .box-header { padding: 12px 18px; background: #111; font-size: 10px; text-transform: uppercase; font-weight: bold; color: #444; border-bottom: 1px solid #222; }
        textarea { flex-grow: 1; background: #000; border: none; color: #10b981; padding: 20px; resize: none; outline: none; font-family: monospace; font-size: 14px; }
        .history { flex-grow: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; background: #050505; }
        .history-item { padding: 12px; border-radius: 8px; background: #080808; border: 1px solid #222; border-left-width: 4px; font-size: 11px; font-family: monospace; }
        .btn { background: #10b981; color: #000; border: none; padding: 18px; font-weight: 900; cursor: pointer; text-transform: uppercase; letter-spacing: 1px; }
        .btn:hover { background: #34d399; }
        
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    {% if mode == 'learning' %}
    <div class="sidebar">
        <div class="section-title">Architecture_Report</div>
        
        <div class="logic-step">
            <b>01. REST Protocol</b>
            <p>RESTful APIs use HTTP methods to define actions. <code>POST</code> is used specifically to create new resources on the server.</p>
        </div>

        <div class="logic-step">
            <b>02. Schema Validation</b>
            <p>The backend requires a specific JSON structure. If the "name" key is missing, the request will be rejected.</p>
            <div class="json-viz">
                { <span class="key">"name"</span>: <span class="val">"..."</span> }
            </div>
        </div>

        <div class="hint-container">
            <div id="hint-timer" class="timer-box">NEXT HINT IN: <span id="time-display">03:00</span></div>
            <div id="hint1" class="hint-item">
                <b style="color:#f59e0b">HINT 01: Body Construction</b><br>
                Ensure your JSON is valid. Every key and string value must be wrapped in double quotes <code>"</code>.
            </div>
            <div id="hint2" class="hint-item">
                <b style="color:#f59e0b">HINT 02: Verification Payload</b><br>
                The server is looking for the "name" property. Try sending: <code style="color:#10b981">{"name": "Verified_Node"}</code>
            </div>
        </div>
    </div>
    {% endif %}

    <div class="main-content">
        <div class="pipeline">
            <div class="node" id="node-client">CLIENT_UI</div>
            <div class="arrow"><div id="p-req" class="pulse"></div></div>
            <div class="node" id="node-server">API_SERVER</div>
            <div class="arrow"><div id="p-res" class="pulse"></div></div>
            <div class="node" id="node-db">DATABASE</div>
        </div>

        <div class="console-grid">
            <div class="box">
                <div class="box-header">Request Payload (JSON)</div>
                <textarea id="json-payload"></textarea>
                <button class="btn" onclick="executeREST()">Execute POST Request</button>
            </div>
            <div class="box">
                <div class="box-header">Traffic History & DB State</div>
                <div class="history" id="history-log">
                    <div style="color: #444; font-size: 10px; margin-bottom: 10px;">DB_COUNT: <span id="db-count" style="color: #10b981;">{{ count }}</span></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // --- HINT TIMER ---
        let totalSeconds = 180;
        let currentHintLevel = 1;
        const timeDisplay = document.getElementById('time-display');

        if (timeDisplay) {
            setInterval(() => {
                if (currentHintLevel > 2) return;
                totalSeconds--;
                const mins = Math.floor(totalSeconds / 60);
                const secs = totalSeconds % 60;
                timeDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

                if (totalSeconds <= 0) {
                    document.getElementById('hint' + currentHintLevel).classList.add('hint-active');
                    currentHintLevel++;
                    totalSeconds = 180;
                }
            }, 1000);
        }

        // --- REST EXECUTION & VISUALIZATION ---
        async function executeREST() {
            const payload = document.getElementById('json-payload').value;
            const log = document.getElementById('history-log');
            const pReq = document.getElementById('p-req');
            const pRes = document.getElementById('p-res');

            // 1. Client to Server Pulse
            pReq.classList.add('active-pulse');
            
            try {
                const response = await fetch('/api/items', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: payload
                });
                const data = await response.json();
                
                // 2. Server to DB Pulse (simulated delay)
                setTimeout(() => { if (response.status === 201) pRes.classList.add('active-pulse'); }, 300);

                // 3. Update History UI
                const item = document.createElement('div');
                item.className = 'history-item';
                const success = response.status === 201;
                item.style.borderColor = success ? '#10b981' : '#ef4444';
                
                item.innerHTML = `
                    <div style="color: ${success ? '#10b981' : '#ef4444'}">POST /api/items [${response.status}]</div>
                    <div style="color: #666; margin-top: 4px;">REQ: ${payload}</div>
                    <div style="color: #fff; margin-top: 4px;">RES: ${data.message || data.error}</div>
                `;
                log.insertBefore(item, log.children[1]); // Insert below DB count
                
                if(success) {
                    document.getElementById('db-count').innerText = data.total_items;
                }

            } catch (err) {
                console.error("API Error:", err);
            }

            // 4. Cleanup pulses
            setTimeout(() => {
                pReq.classList.remove('active-pulse');
                pRes.classList.remove('active-pulse');
            }, 1000);
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    mode = request.args.get('mode', 'hiring').strip().lower()
    return render_template_string(HTML_TEMPLATE, mode=mode, count=len(data_store))

@app.route('/api/items', methods=['POST'])
def items():
    try:
        data = request.json
        if data and 'name' in data:
            data_store.append(data)
            msg = "SUCCESS: REST_API_Resource_Created"
            print(f"EVIDENCE_LOG: {msg}", flush=True)
            return jsonify({
                "message": f"✅ {msg}", 
                "total_items": len(data_store)
            }), 201
        return jsonify({"error": "❌ Schema Mismatch: 'name' key missing"}), 400
    except Exception:
        return jsonify({"error": "❌ Invalid JSON Format"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)