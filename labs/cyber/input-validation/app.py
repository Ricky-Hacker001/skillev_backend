from flask import Flask, request, render_template_string, make_response, jsonify
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
    <title>Skillev Lab - Input Validation</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #030303; color: #FFFFFF; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        .sidebar { width: 400px; background: #080808; border-right: 2px solid #3b82f6; padding: 40px 30px; overflow-y: auto; box-sizing: border-box; }
        .section-title { color: #3b82f6; font-size: 1.1rem; font-weight: 900; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 30px; }
        .logic-step { background: #0c0c0c; border: 1px solid #222; border-left: 4px solid #3b82f6; padding: 20px; border-radius: 8px; margin-bottom: 25px; }
        .logic-step b { color: #3b82f6; display: block; margin-bottom: 10px; text-transform: uppercase; }
        .main-content { flex-grow: 1; display: flex; align-items: center; justify-content: center; padding: 40px; }
        .container { width: 100%; max-width: 450px; background: #080808; padding: 45px; border-radius: 20px; border: 1px solid #222; }
        input[type="text"] { width: 100%; padding: 12px; margin: 10px 0; background: #111; border: 1px solid #333; color: white; border-radius: 8px; box-sizing: border-box; outline: none; }
        input[type="text"]:focus { border-color: #3b82f6; }
        .btn { width: 100%; padding: 12px; background: #3b82f6; color: black; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; text-transform: uppercase; }
    </style>
</head>
<body>
    {% if mode == 'learning' %}
    <div class="sidebar">
        <div class="section-title">Forensic_Analysis</div>
        <div class="logic-step">
            <b>01. Client-Side Constraints</b>
            <p>The form uses <code>maxlength="10"</code>. This is easily removed via Browser DevTools (Right-click > Inspect).</p>
        </div>
        <div class="logic-step">
            <b>02. Server-Side Failure</b>
            <p>The backend assumes the frontend has already validated the length. By bypassing the UI, you can send oversized payloads.</p>
        </div>
    </div>
    {% endif %}

    <div class="main-content">
        <div class="container">
            <h2 style="color: #3b82f6;">Identity_Profile_Update</h2>
            <form method="POST" id="updateForm">
                <label style="font-size: 0.8rem; color: #888;">Display Name (Max 10 chars):</label>
                <input type="text" name="display_name" id="displayName" maxlength="10" placeholder="Ricky" required autocomplete="off">
                <button type="submit" class="btn">Update Protocol</button>
            </form>
            {% if message %}
                <div style="margin-top:25px; padding:18px; background:#000; border-radius: 12px; border-left: 4px solid #3b82f6; font-family: monospace;">
                    {{ message | safe }}
                </div>
            {% endif %}
        </div>
    </div>

    <script>
        // --- ANTI-CHEAT TELEMETRY ---
        document.getElementById('displayName').addEventListener('paste', (e) => {
            const pastedData = (e.clipboardData || window.clipboardData).getData('text');
            fetch('/telemetry', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    event: "PASTE_DETECTED",
                    field: "display_name",
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
    # Intercepted by Orchestrator for -0.25 integrity deduction
    print(f"EVIDENCE_LOG: [INTEGRITY_VIOLATION] {data['event']} in {data['field']}: '{data['content']}'", flush=True)
    return jsonify({"status": "captured"}), 200

@app.route('/', methods=['GET', 'POST'])
def index():
    mode = request.args.get('mode', 'hiring').strip().lower()
    message = ""
    
    if request.method == 'POST':
        name = request.form.get('display_name', '')
        
        # Log the attempt length
        print(f"EVIDENCE_LOG: [MODE:{mode.upper()}] Input Received: '{name}' (Length: {len(name)})", flush=True)
        
        # Validation Logic
        if len(name) > 10:
            result_msg = "SUCCESS: Validation_Bypass_Confirmed"
            print(f"EVIDENCE_LOG: {result_msg}", flush=True)
            message = f"<span style='color:#10b981;'>✅ <b>{result_msg}</b></span><br><br>Length Violation Detected: {len(name)} chars accepted."
        else:
            # Log as a standard interaction or potential "soft error" if they didn't succeed
            print(f"EVIDENCE_LOG: [INTERACTION] Standard update within limits.", flush=True)
            message = f"Profile updated to: {name}"

    return render_template_string(HTML_TEMPLATE, mode=mode, message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)