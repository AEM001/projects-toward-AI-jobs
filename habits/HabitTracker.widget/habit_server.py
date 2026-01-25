#!/usr/bin/env python3
"""
Habit Tracker Backend Server (Optional)
Provides API endpoints for habit data management, analytics, and sync
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# === Configuration ===
AUTH_TOKEN = "your-secret-token-here"  # Change this!
DATA_FILE = os.path.expanduser("~/.habit-tracker-data.json")
BACKUP_DIR = os.path.expanduser("~/.habit-tracker-backups")

# === Models ===
class HabitEntry(BaseModel):
    habit_id: str
    date: str
    completed: bool

class HabitStats(BaseModel):
    habit_id: str
    total_days: int
    completed_days: int
    current_streak: int
    longest_streak: int
    completion_rate: float
    last_7_days: int
    last_30_days: int

class BulkUpdate(BaseModel):
    updates: List[HabitEntry]

# === App Setup ===
app = FastAPI(title="Habit Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the directory where this script is located
BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"

# Mount static files if web directory exists
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

# === Helper Functions ===
def verify_auth(x_auth: str = Header(...)):
    if x_auth != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid authentication token")

def load_data() -> Dict:
    """Load habit data from JSON file"""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load data: {str(e)}")

def save_data(data: Dict):
    """Save habit data to JSON file"""
    try:
        # Create backup before saving
        if os.path.exists(DATA_FILE):
            backup_file = os.path.join(
                BACKUP_DIR, 
                f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            os.makedirs(BACKUP_DIR, exist_ok=True)
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                backup_data = f.read()
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(backup_data)
        
        # Save new data
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save data: {str(e)}")

def calculate_streak(dates: List[str], from_date: str = None) -> int:
    """Calculate consecutive streak from a given date backwards"""
    if not dates:
        return 0
    
    sorted_dates = sorted([datetime.strptime(d, '%Y-%m-%d') for d in dates], reverse=True)
    start_date = datetime.strptime(from_date, '%Y-%m-%d') if from_date else datetime.now()
    
    streak = 0
    current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    for i in range(365):  # Max 1 year
        check_date = current_date - timedelta(days=i)
        if check_date in sorted_dates:
            streak += 1
        else:
            break
    
    return streak

def calculate_longest_streak(dates: List[str]) -> int:
    """Calculate the longest streak ever"""
    if not dates:
        return 0
    
    sorted_dates = sorted([datetime.strptime(d, '%Y-%m-%d') for d in dates])
    
    max_streak = 1
    current_streak = 1
    
    for i in range(1, len(sorted_dates)):
        diff = (sorted_dates[i] - sorted_dates[i-1]).days
        if diff == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1
    
    return max_streak

# === API Endpoints ===

@app.get("/")
async def root():
    """Serve the web interface"""
    web_file = WEB_DIR / "index.html"
    if web_file.exists():
        return FileResponse(str(web_file))
    return {
        "status": "ok",
        "service": "Habit Tracker API",
        "version": "1.0.0",
        "message": "Web interface not found. API is running."
    }

@app.get("/habits")
async def get_all_habits():
    """Get all habit data"""
    data = load_data()
    return {"habits": data}

@app.get("/habits/{habit_id}")
async def get_habit(habit_id: str, x_auth: str = Header(...)):
    """Get data for a specific habit"""
    verify_auth(x_auth)
    data = load_data()
    
    if habit_id not in data:
        return {"habit_id": habit_id, "data": {}}
    
    return {
        "habit_id": habit_id,
        "data": data[habit_id]
    }

@app.post("/habits/{habit_id}/{date}")
async def toggle_habit(
    habit_id: str, 
    date: str, 
    completed: Optional[bool] = None,
    x_auth: str = Header(...)
):
    """Toggle or set habit completion for a specific date"""
    verify_auth(x_auth)
    
    # Validate date format
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    data = load_data()
    
    if habit_id not in data:
        data[habit_id] = {}
    
    if completed is None:
        # Toggle
        data[habit_id][date] = not data[habit_id].get(date, False)
    else:
        # Set
        data[habit_id][date] = completed
    
    save_data(data)
    
    return {
        "habit_id": habit_id,
        "date": date,
        "completed": data[habit_id][date]
    }

@app.post("/habits/bulk")
async def bulk_update(updates: BulkUpdate, x_auth: str = Header(...)):
    """Bulk update multiple habit entries"""
    verify_auth(x_auth)
    
    data = load_data()
    
    for entry in updates.updates:
        if entry.habit_id not in data:
            data[entry.habit_id] = {}
        data[entry.habit_id][entry.date] = entry.completed
    
    save_data(data)
    
    return {
        "status": "success",
        "updated": len(updates.updates)
    }

@app.delete("/habits/{habit_id}")
async def delete_habit(habit_id: str, x_auth: str = Header(...)):
    """Delete a habit and all its data"""
    verify_auth(x_auth)
    
    data = load_data()
    
    if habit_id in data:
        del data[habit_id]
        save_data(data)
        return {"status": "success", "message": f"Habit {habit_id} deleted"}
    
    raise HTTPException(status_code=404, detail="Habit not found")

@app.get("/stats/{habit_id}")
async def get_habit_stats(habit_id: str, x_auth: str = Header(...)) -> HabitStats:
    """Get detailed statistics for a habit"""
    verify_auth(x_auth)
    
    data = load_data()
    
    if habit_id not in data:
        return HabitStats(
            habit_id=habit_id,
            total_days=0,
            completed_days=0,
            current_streak=0,
            longest_streak=0,
            completion_rate=0.0,
            last_7_days=0,
            last_30_days=0
        )
    
    habit_data = data[habit_id]
    completed_dates = [date for date, completed in habit_data.items() if completed]
    
    # Calculate stats
    total_days = len(habit_data)
    completed_days = len(completed_dates)
    completion_rate = (completed_days / total_days * 100) if total_days > 0 else 0.0
    
    current_streak = calculate_streak(completed_dates)
    longest_streak = calculate_longest_streak(completed_dates)
    
    # Last 7 and 30 days
    now = datetime.now()
    last_7_days = sum(
        1 for date in completed_dates 
        if (now - datetime.strptime(date, '%Y-%m-%d')).days <= 7
    )
    last_30_days = sum(
        1 for date in completed_dates 
        if (now - datetime.strptime(date, '%Y-%m-%d')).days <= 30
    )
    
    return HabitStats(
        habit_id=habit_id,
        total_days=total_days,
        completed_days=completed_days,
        current_streak=current_streak,
        longest_streak=longest_streak,
        completion_rate=round(completion_rate, 2),
        last_7_days=last_7_days,
        last_30_days=last_30_days
    )

@app.get("/stats")
async def get_all_stats(x_auth: str = Header(...)):
    """Get statistics for all habits"""
    verify_auth(x_auth)
    
    data = load_data()
    stats = {}
    
    for habit_id in data.keys():
        stats[habit_id] = await get_habit_stats(habit_id, x_auth)
    
    return {"stats": stats}

@app.delete("/habits/{habit_id}")
async def delete_habit(habit_id: str, x_auth: str = Header(...)):
    """Delete all data for a habit"""
    verify_auth(x_auth)
    
    data = load_data()
    
    if habit_id in data:
        del data[habit_id]
        save_data(data)
        return {"status": "deleted", "habit_id": habit_id}
    
    raise HTTPException(status_code=404, detail="Habit not found")

@app.delete("/habits/{habit_id}/{date}")
async def delete_habit_entry(habit_id: str, date: str, x_auth: str = Header(...)):
    """Delete a specific habit entry"""
    verify_auth(x_auth)
    
    data = load_data()
    
    if habit_id in data and date in data[habit_id]:
        del data[habit_id][date]
        save_data(data)
        return {"status": "deleted", "habit_id": habit_id, "date": date}
    
    raise HTTPException(status_code=404, detail="Entry not found")

@app.get("/export")
async def export_data(x_auth: str = Header(...)):
    """Export all habit data"""
    verify_auth(x_auth)
    
    data = load_data()
    return {
        "exported_at": datetime.now().isoformat(),
        "data": data
    }

@app.post("/import")
async def import_data(import_data: Dict, merge: bool = False, x_auth: str = Header(...)):
    """Import habit data (merge or replace)"""
    verify_auth(x_auth)
    
    if merge:
        existing_data = load_data()
        for habit_id, habit_data in import_data.items():
            if habit_id not in existing_data:
                existing_data[habit_id] = {}
            existing_data[habit_id].update(habit_data)
        save_data(existing_data)
    else:
        save_data(import_data)
    
    return {
        "status": "success",
        "mode": "merge" if merge else "replace",
        "habits_imported": len(import_data)
    }

@app.get("/backups")
async def list_backups(x_auth: str = Header(...)):
    """List all available backups"""
    verify_auth(x_auth)
    
    if not os.path.exists(BACKUP_DIR):
        return {"backups": []}
    
    backups = []
    for filename in sorted(os.listdir(BACKUP_DIR), reverse=True):
        if filename.endswith('.json'):
            filepath = os.path.join(BACKUP_DIR, filename)
            backups.append({
                "filename": filename,
                "created_at": datetime.fromtimestamp(os.path.getctime(filepath)).isoformat(),
                "size": os.path.getsize(filepath)
            })
    
    return {"backups": backups}

@app.post("/backups/{filename}/restore")
async def restore_backup(filename: str, x_auth: str = Header(...)):
    """Restore from a backup file"""
    verify_auth(x_auth)
    
    backup_path = os.path.join(BACKUP_DIR, filename)
    
    if not os.path.exists(backup_path):
        raise HTTPException(status_code=404, detail="Backup not found")
    
    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        save_data(backup_data)
        return {"status": "restored", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restore: {str(e)}")

# === Run Server ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8788, log_level="info")
