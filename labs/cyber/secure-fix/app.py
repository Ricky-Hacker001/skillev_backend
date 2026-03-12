from flask import Flask, request, render_template_string, make_response

app = Flask(__name__)

# Initial state: Vulnerable
app_config = {"is_patched": False}

@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    response.headers['Content-Security-Policy'] = "frame-ancestors *"
    return response

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Skillev - Secure Fix Lab</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #030303; color: #eee; margin: 0; display: flex; height: 100vh; }
        .sidebar { width: 400px; background: #080808; border-right: 2px solid #a855f7; padding: 40px; }
        .main-content { flex-grow: 1; display: flex; align-items: center; justify-content: center; padding: 40px; }
        .card { width: 100%; max-width: 500px; background: #080808; padding: 40px; border-radius: 20px; border: 1px solid #222; }
        .status { padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 20px; }
        .vuln { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid #ef4444; }
        .secure { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid #10b981; }
        pre { background: #000; padding: 15px; border-radius: 8px; border: 1px solid #333; color: #a855f7; font-size: 0.85rem; }
        input[type="text"] { width: 100%; padding: 12px; margin: 10px 0; background: #111; border: 1px solid #333; color: white; border-radius: 8px; }
        button { width: 100%; padding: 12px; background: #a855f7; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2 style="color: #a855f7;">Forensic_Fix</h2>
        <p>The current code trusts unsanitized input for the <code>eval()</code> function.</p>
        <p><b>Task:</b> Submit the word <code>"sanitize"</code> to simulate applying a secure middleware patch.</p>
        <pre># Current Bug:
eval(user_input) 

# Desired Fix:
int(user_input)</pre>
    </div>
    <div class="main-content">
        <div class="card">
            <div class="status {{ 'secure' if patched else 'vuln' }}">
                SYSTEM_STATUS: {{ 'SECURE' if patched else 'VULNERABLE' }}
            </div>
            <form method="POST">
                <label>Enter Security Patch Keyword:</label>
                <input type="text" name="patch_key" placeholder="Keyword..." required>
                <button type="submit">Deploy Patch</button>
            </form>
            {% if msg %}<p style="margin-top:20px; color: #a855f7;">{{ msg }}</p>{% endif %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    msg = ""
    if request.method == 'POST':
        key = request.form.get('patch_key', '').lower()
        if key == "sanitize":
            app_config["is_patched"] = True
            msg = "SUCCESS: Secure_Logic_Verified. Remote Code Execution (RCE) mitigated."
            print(f"EVIDENCE_LOG: {msg}", flush=True)
        else:
            msg = "ERROR: Invalid patch syntax."
    
    return render_template_string(HTML_TEMPLATE, patched=app_config["is_patched"], msg=msg)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)