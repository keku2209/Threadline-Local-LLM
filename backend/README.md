# Threadline backend

Install dependencies with `pip install -r requirements.txt`.

From this directory:

```powershell
python -m app.seed
uvicorn app.main:app --reload
```

SQLite is created at `backend/threadline.db`. The API docs are available at `http://127.0.0.1:8000/docs`.

This module is intentionally separate from the existing root `app.py` AI analyzer. It does not call Reddit or any AI service.
