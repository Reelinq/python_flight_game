# python flight game

Flight game, that were done in a team as first python course project in Metropolia AMK.

## Prereqs

- Python 3.11+ (3.13 OK)
- MySQL running with the school schema loaded (airport, country)
- `requirements.txt` in the repo root

## Setup

### 1) Create & activate venv

bash / zsh
```bash
python -m venv .venv
source .venv/bin/activate
```

fish
```fish
python -m venv .venv
source .venv/bin/activate.fish
```

PowerShell (Windows)
```ps
python -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process
.\.venv\Scripts\Activate.ps1
```

### 2) Install deps

```bash
pip install -r requirements.txt
```

### 3) .env

Create `.env` in the project root:
```ini
DATABASE_URL=mysql+mysqlconnector://user:pass@localhost/flight_game
INITIAL_CO2_BUDGET=2000
CO2_PER_100KM=20
```

### 4) Run

From repo root:
```bash
# make sure backend is running in another terminal:
uvicorn app.main:app --reload

# run CLI (frontend):
python -m app.cli.main
```
Server: http://127.0.0.1:8000
Docs: http://127.0.0.1:8000/docs

## Testing

### Health check:
```bash
curl http://127.0.0.1:8000/
# {"ok": true}
```

### Airports
Search (minimal fields):
```bash
curl "http://127.0.0.1:8000/airports/search?q=hel&limit=5"
```
Get airport (full fields):
```bash
curl http://127.0.0.1:8000/airports/EFHK
```

### Game
Start a game:
```bash
curl -X POST http://127.0.0.1:8000/game/start \
  -H "Content-Type: application/json" \
  -d '{"screen_name":"zero","start_airport_ident":"EFHK"}'
# -> note the "id" in the response
```
Get state:
```bash
curl http://127.0.0.1:8000/game/{id}/state
```
Travel:
```bash
curl -X POST http://127.0.0.1:8000/game/{id}/travel \
  -H "Content-Type: application/json" \
  -d '{"destination_ident":"EGLL"}'
```
List reachable with remaining budget:
```bash
curl http://127.0.0.1:8000/game/{id}/reachable
```
Check game over:
```bash
curl http://127.0.0.1:8000/game/{id}/over
```

### Settings
Get current:
```bash
curl http://127.0.0.1:8000/settings
```
Update (runtime only):
```bash
curl -X PUT http://127.0.0.1:8000/settings \
  -H "Content-Type: application/json" \
  -d '{"co2_per_100km":18}'
```
