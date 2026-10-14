# ShootOut API
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # fill MONGODB_URL and JWT_SECRET_KEY
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Open http://localhost:8000/docs. Use Authorize with the accessToken from /auth/login.
Make an admin: in Atlas set `isAdmin: true` on your user document, then POST /admin/matches.
Games in URLs: BGMI, BGMI_TDM, FREE_FIRE. Join requires an Atlas cluster (transactions need a replica set).
