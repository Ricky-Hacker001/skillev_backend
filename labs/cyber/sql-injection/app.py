from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE users (id INTEGER, username TEXT, password TEXT)')
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'skillev_secret_123')")
    return conn

db = init_db()

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
    <title>Skillev Lab</title>
    <style>
        body { 
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
            background: #030303; 
            color: #FFFFFF; 
            margin: 0; 
            display: flex; 
            height: 100vh; 
            width: 100vw;
            overflow: hidden; 
        }
        
        /* SIDEBAR - Analysis Report */
        .sidebar { 
            width: 400px; 
            flex-shrink: 0;
            background: #080808; 
            border-right: 2px solid #10b981; 
            padding: 40px 30px; 
            overflow-y: auto; 
            box-sizing: border-box; 
            display: flex;
            flex-direction: column;
        }

        .section-title { 
            color: #10b981; 
            font-size: 1.1rem; 
            font-weight: 900; 
            text-transform: uppercase; 
            letter-spacing: 3px; 
            margin-bottom: 30px; 
            display: flex; 
            align-items: center; 
            gap: 12px; 
        }

        .section-title::after {
            content: "";
            height: 1px;
            flex-grow: 1;
            background: rgba(16, 185, 129, 0.2);
        }

        /* LOGIC CARDS */
        .logic-step { 
            background: #0c0c0c; 
            border: 1px solid #222; 
            border-left: 4px solid #10b981;
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 25px; 
        }

        .logic-step b { 
            color: #10b981; 
            font-size: 1rem; 
            display: block; 
            margin-bottom: 10px; 
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .logic-step p { 
            margin: 0; 
            font-size: 0.95rem; 
            color: #E0E0E0; 
            line-height: 1.6; 
        }
        
        /* CODE BOXES */
        .code-box { 
            background: #000000; 
            padding: 15px; 
            border-radius: 6px; 
            font-family: 'Consolas', 'Fira Code', monospace; 
            font-size: 0.9rem; 
            color: #FFFFFF; 
            margin-top: 15px; 
            border: 1px solid #333; 
            white-space: pre-wrap; 
            line-height: 1.5;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
        }

        .highlight { color: #f59e0b; font-weight: bold; }
        .comment { color: #666; font-style: italic; }

        /* HINT SYSTEM */
        .timer-box { 
            font-family: 'JetBrains Mono', monospace; 
            font-size: 1rem; 
            color: #f59e0b; 
            background: rgba(245, 158, 11, 0.1); 
            padding: 15px; 
            border-radius: 8px; 
            border: 1px solid rgba(245, 158, 11, 0.3); 
            text-align: center; 
            font-weight: bold;
            margin-bottom: 20px;
        }
        
        .hint-item { 
            font-size: 0.95rem; 
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 15px; 
            display: none; 
            background: #111; 
            border: 1px solid #333; 
            color: #FFFFFF; 
            line-height: 1.6; 
            animation: fadeIn 0.5s ease-in-out;
        }

        .hint-active { 
            display: block; 
            border-left: 4px solid #f59e0b; 
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* MAIN LAB AREA */
        .main-content { 
            flex-grow: 1; 
            background: radial-gradient(circle at center, #0a0a0a 0%, #030303 100%);
            display: flex; 
            align-items: center; 
            justify-content: center; 
            padding: 40px; 
        }

        .container { 
            width: 100%; 
            max-width: 420px; 
            background: #080808; 
            padding: 45px; 
            border-radius: 20px; 
            border: 1px solid #222; 
            box-shadow: 0 30px 60px rgba(0,0,0,0.6); 
        }

        .evidence-banner { 
            background: rgba(16, 185, 129, 0.1); 
            color: #10b981; 
            padding: 12px; 
            border-radius: 6px; 
            font-size: 0.75rem; 
            margin-bottom: 30px; 
            text-align: center; 
            font-weight: 900; 
            border: 1px solid rgba(16, 185, 129, 0.3); 
            letter-spacing: 2px;
        }

        h1 { font-style: italic; font-size: 1.8rem; margin: 0 0 10px 0; color: #fff; letter-spacing: -1px; }
        
        input { 
            width: 100%; 
            padding: 16px; 
            margin: 12px 0; 
            background: #111; 
            border: 1px solid #333; 
            color: white; 
            border-radius: 10px; 
            box-sizing: border-box; 
            font-size: 1rem;
            outline: none;
            transition: all 0.2s ease;
        }

        input:focus { border-color: #10b981; background: #151515; box-shadow: 0 0 15px rgba(16, 185, 129, 0.1); }

        input[type="submit"] { 
            background: #10b981; 
            cursor: pointer; 
            border: none; 
            font-weight: 900; 
            text-transform: uppercase; 
            margin-top: 20px; 
            color: #000; 
            letter-spacing: 1px;
        }

        input[type="submit"]:hover { background: #34d399; transform: translateY(-1px); }
        input[type="submit"]:active { transform: translateY(0); }
    </style>
</head>
<body>
    {% if mode == 'learning' %}
    <div class="sidebar">
        <div class="section-title">Analysis_Report</div>
        
        <div class="logic-step">
            <b>01. Vulnerability Detected</b>
            <p>The system builds queries using unsafe string concatenation. Your input is injected directly into the command string.</p>
            <div class="code-box">
<span class="comment"># Vulnerable SQL Logic</span>
query = "SELECT * FROM users 
WHERE user = '" + <span class="highlight">user_input</span> + "'"
            </div>
        </div>

        <div class="logic-step">
            <b>02. Logical Bypass</b>
            <p>Use a single quote to terminate the field and a comment marker to nullify the rest of the query logic.</p>
            <div class="code-box">
<span class="comment"># Result of injection</span>
WHERE user = '<span class="highlight">'</span>' <span class="comment"># Syntax Error!</span>
            </div>
        </div>

        <div class="hint-container">
            <div id="hint-timer" class="timer-box">
                NEXT HINT IN: <span id="time-display">03:00</span>
            </div>
            
            <div id="hint1" class="hint-item">
                <b style="color:#f59e0b">HINT 01: Break the String</b><br>
                Try entering a single quote <code>'</code>. This breaks the SQL syntax and usually reveals if the input is unsanitized.
            </div>
            
            <div id="hint2" class="hint-item">
                <b style="color:#f59e0b">HINT 02: Commenting</b><br>
                In SQL, <code>-- </code> (dash-dash-space) is a comment. It forces the database to ignore the password check.
            </div>
            
            <div id="hint3" class="hint-item">
                <b style="color:#f59e0b">HINT 03: The Payload</b><br>
                Try the full bypass: <code style="color: #fff; background: #222; padding: 2px 6px; border-radius: 4px;">admin' -- </code>
                <div class="code-box">
SELECT * FROM users 
WHERE user = '<span class="highlight">admin'</span> <span class="highlight">-- </span>' AND ...
                </div>
            </div>
        </div>
    </div>
    {% endif %}

    <div class="main-content">
        <div class="container">
            <div class="evidence-banner">🛡️ SKILLEV_PROTOCOL: {{ mode | upper }}_ACTIVE</div>
            
            <h1>SQL_Injection_Lab</h1>
            <p style="color: #666; font-size: 0.9rem; margin-bottom: 25px;">Task: Bypass the identity check to gain administrative access.</p>

            <form method="POST">
                <input type="text" name="username" placeholder="User_Identity" required autocomplete="off">
                <input type="password" name="password" placeholder="Access_Key" autocomplete="off">
                <input type="submit" value="Verify_Credentials">
            </form>

            {% if message %} 
                <div style="margin-top:25px; padding:18px; background:#000; border-radius: 12px; border-left: 4px solid #10b981; font-size: 0.9rem; font-family: 'Consolas', monospace; line-height: 1.5;">
                    {{ message | safe }}
                </div> 
            {% endif %}
        </div>
    </div>

    <script>
        let totalSeconds = 180; 
        let currentHintLevel = 1;
        const timeDisplay = document.getElementById('time-display');
        const timerBox = document.getElementById('hint-timer');

        function updateTimerDisplay(seconds) {
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            timeDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }

        const hintInterval = setInterval(() => {
            if (currentHintLevel > 3) {
                clearInterval(hintInterval);
                timerBox.textContent = "ALL HINTS UNLOCKED";
                return;
            }

            totalSeconds--;
            updateTimerDisplay(totalSeconds);

            if (totalSeconds <= 0) {
                const hintToReveal = document.getElementById('hint' + currentHintLevel);
                if (hintToReveal) {
                    hintToReveal.classList.add('hint-active');
                    currentHintLevel++;
                    if (currentHintLevel <= 3) {
                        totalSeconds = 180;
                        updateTimerDisplay(totalSeconds);
                    } else {
                        timerBox.textContent = "ALL HINTS UNLOCKED";
                        clearInterval(hintInterval);
                    }
                }
            }
        }, 1000);
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def login():
    mode = request.args.get('mode', 'hiring').strip().lower()
    message = ""
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"EVIDENCE_LOG: [MODE:{mode.upper()}] Execution Attempt: {username}", flush=True)
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        
        try:
            cursor = db.cursor()
            user = cursor.execute(query).fetchone()
            if user:
                result_msg = f"SUCCESS: Flag_Captured_By_{user[1]}"
                print(f"EVIDENCE_LOG: {result_msg}", flush=True)
                message = f"<span style='color:#10b981;'>✅ <b>{result_msg}</b></span><br><br><span style='color: #888;'>Recruiter Evidence Node updated with bypass signature.</span>"
            else:
                message = "<span style='color:#ef4444;'>❌ ACCESS_DENIED: Credential verification failed.</span>"
        except Exception as e:
            message = f"<span style='color:#f59e0b;'>⚠️ <b>SQL_ERROR:</b> Syntax Malformed in query string.</span>"
            
    return render_template_string(HTML_TEMPLATE, message=message, mode=mode)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)