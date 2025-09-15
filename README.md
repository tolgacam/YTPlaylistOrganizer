# YTPlaylistOrganizer

## Setup Instructions
Backend
1. Open a terminal and navigate to the `backend/` folder:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the backend server:
```bash
uvicorn app:app --reload --port 8000
```
The server will start on [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Installing FFmpeg on Windows via command line
You can install FFmpeg easily without manual downloads:

**Using winget (Windows 10/11): (Recommended)**
```powershell
winget install --id Gyan.FFmpeg -e --source winget
```

**Using Chocolatey:**
```powershell
choco install ffmpeg
```

**Using Scoop:**
```powershell
scoop install ffmpeg
```

After installing, restart your terminal and verify:
```powershell
ffmpeg -version
```