from flask import Flask, request, render_template_string, make_response

app = Flask(__name__)

# Mock Database of sensitive information
DOCUMENTS = {
    "1001": {"owner": "guest", "content": "Welcome to Skillev! This is your public welcome note.", "status": "Public"},
    "1002": {"owner": "admin", "content": "ADMIN_FLAG{IDOR_MASTER_5521}", "status": "Restricted"},
    "1003": {"owner": "hr_manager", "content": "Candidate shortlist: Ricky, Charles, Prabhavathi.", "status": "Private"}
}

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
    <title>Skillev Lab - IDOR</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #030303; color: #FFFFFF; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        .sidebar { width: 400px; background: #080808; border-right: 2px solid #f59e0b; padding: 40px 30px; overflow-y: auto; box-sizing: border-box; }
        .section-title { color: #f59e0b; font-size: 1.1rem; font-weight: 900; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 30px; }
        .logic-step { background: #0c0c0c; border: 1px solid #222; border-left: 4px solid #f59e0b; padding: 20px; border-radius: 8px; margin-bottom: 25px; }
        .logic-step b { color: #f59e0b; display: block; margin-bottom: 10px; text-transform: uppercase; }
        .main-content { flex-grow: 1; display: flex; align-items: center; justify-content: center; padding: 40px; }
        .container { width: 100%; max-width: 500px; background: #080808; padding: 45px; border-radius: 20px; border: 1px solid #222; }
        .doc-box { background: #000; padding: 20px; border-radius: 12px; border: 1px solid #333; font-family: monospace; }
        .nav-links { margin-top: 20px; display: flex; gap: 10px; }
        .nav-links a { color: #f59e0b; text-decoration: none; font-size: 0.8rem; border: 1px solid #f59e0b; padding: 5px 10px; rounded: 4px; }
    </style>
</head>
<body>
    {% if mode == 'learning' %}
    <div class="sidebar">
        <div class="section-title">Forensic_Analysis</div>
        <div class="logic-step">
            <b>01. Parameter Manipulation</b>
            <p>The application fetches documents based on the <code>doc_id</code> parameter in the URL. It checks if the ID exists but fails to verify if the <i>current user</i> owns it.</p>
        </div>
        <div class="logic-step">
            <b>02. Discovery</b>
            <p>Try changing the ID in the navigation links to find hidden or administrative files.</p>
        </div>
    </div>
    {% endif %}

    <div class="main-content">
        <div class="container">
            <h2 style="color: #f59e0b;">Document_Vault_v1.0</h2>
            <p style="color: #666;">Authenticated as: <b style="color: #fff;">guest</b></p>
            
            <div class="doc-box">
                {% if doc %}
                    <p style="color: #f59e0b;">ID: {{ doc_id }}</p>
                    <p>{{ doc.content }}</p>
                {% else %}
                    <p style="color: #ef4444;">404: Document Not Found</p>
                {% endif %}
            </div>

            <div class="nav-links">
                <a href="/?doc_id=1001&mode={{mode}}">View My Welcome Note</a>
            </div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    mode = request.args.get('mode', 'hiring').strip().lower()
    doc_id = request.args.get('doc_id', '1001')
    
    doc = DOCUMENTS.get(doc_id)
    
    # Logic to capture success
    if doc_id == "1002":
        result_msg = "SUCCESS: IDOR_Bypass_Flag_Captured"
        print(f"EVIDENCE_LOG: {result_msg}", flush=True)

    return render_template_string(HTML_TEMPLATE, doc=doc, doc_id=doc_id, mode=mode)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)