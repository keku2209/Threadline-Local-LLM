from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routes_communities import router as communities_router
from .routes_posts import router as posts_router
from .routes_search import router as search_router
from .routes_users import router as users_router

Base.metadata.create_all(bind=engine)
app = FastAPI(title='Threadline Discussion API', version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173', 'http://localhost:5174', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.include_router(users_router); app.include_router(communities_router); app.include_router(posts_router); app.include_router(search_router)

@app.get('/api/health')
def health():
    return {'status': 'ok'}
