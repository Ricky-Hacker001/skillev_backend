from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

class LogData(BaseModel):
    raw_logs: str

@app.post("/analyze-logs")
async def analyze_logs(data: LogData):
    prompt = f"""
    Analyze the following technical logs and provide a 3-5 line summary.
    Focus on:
    1. The user's technical approach (e.g., payloads used).
    2. Any security or integrity violations.
    3. The final result (Success/Failure).

    LOGS:
    {data.raw_logs}
    """

    try:
        # Calling Ollama's local API (default port 11434)
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3",
                "prompt": prompt,
                "stream": False
            }
        )
        result = response.json()
        return {"summary": result["response"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)