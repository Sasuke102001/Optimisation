from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import close_pools, init_pools, sync_venues_from_m2
from routers import kpi, session_brief, show, venues

ALLOWED_ORIGINS = [
    "http://localhost:5173",   # Dashboard dev server
    "http://localhost:5174",   # SE app dev server
    "http://localhost:3000",
    # Vercel deployments added after deploy
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pools()
    await sync_venues_from_m2()   # preload all M2 venues into m3_venues on every startup
    yield
    await close_pools()


app = FastAPI(
    title="PolyNovea Module 3 API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(kpi.router,           prefix="/api/kpi",     tags=["kpi"])
app.include_router(session_brief.router, prefix="/api/session", tags=["session"])
app.include_router(show.router,          prefix="/api/show",    tags=["show"])
app.include_router(venues.router,        prefix="/api/venues",  tags=["venues"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "polynovea-m3"}
