import os
import requests
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from scout import analyze_team

load_dotenv()

app = FastAPI()

# Allow origins for both local dev and production
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://your-fpl-scout.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === BACKGROUND SCHEDULER LOGIC ===
scheduler = BackgroundScheduler()

def scheduled_scout_job():
    """Autonomous job to run the scout analysis."""
    print(f"[{datetime.now()}] Running autonomous FPL Agent Scout Job...")
    manager_id = os.getenv("FPL_MANAGER_ID")
    if manager_id:
        try:
            result = analyze_team(manager_id)
            print(f"Autonomous Scout Job Complete. Target GW: {result.get('target_gw')}")
            # In a full production app, you might email this result or save it to a DB
        except Exception as e:
            print(f"Error running autonomous scout job: {e}")
    else:
        print("Skipping autonomous job: FPL_MANAGER_ID not set.")

def setup_scheduler():
    """Finds the next deadline and schedules the job 8 hours prior."""
    try:
        data = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
        next_event = next((e for e in data['events'] if e['is_next']), None)
        
        if next_event:
            # Deadline time format: 2026-05-09T09:30:00Z
            deadline_str = next_event['deadline_time']
            # Parse it
            deadline_dt = datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M:%SZ")
            # Calculate execution time: 8 hours before deadline
            run_time = deadline_dt - timedelta(hours=8)
            
            # If the run time is in the future, schedule it
            if run_time > datetime.utcnow():
                scheduler.add_job(scheduled_scout_job, 'date', run_date=run_time, id="scout_job", replace_existing=True)
                print(f"[*] Autonomous Agent scheduled to run at {run_time} UTC (8 hours before GW{next_event['id']} deadline).")
            else:
                print(f"[*] Deadline for GW{next_event['id']} is too close or has passed. Job not scheduled.")
    except Exception as e:
        print(f"Failed to setup scheduler: {e}")

@app.on_event("startup")
def startup_event():
    setup_scheduler()
    scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
# ===================================

@app.get("/")
def health_check():
    """Basic health check to ensure the deployed server is awake."""
    return {"status": "FPL Agent Active", "server_time": datetime.utcnow().isoformat()}

@app.get("/api/scout-report")
def get_scout_report():
    """Returns the full intelligent scout analysis and optimal lineup."""
    manager_id = os.getenv("FPL_MANAGER_ID")
    if not manager_id:
        raise HTTPException(status_code=400, detail="FPL_MANAGER_ID not configured in backend")
        
    result = analyze_team(manager_id)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
