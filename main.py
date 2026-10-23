import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import init_db
from app.seed import seed_initial_data
from app.routers import tasks, schedule, memory, reminders, purchases, smarthome, assistant, mcp


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database and seed
    init_db()
    seed_initial_data()
    yield
    # Shutdown logic if needed


app = FastAPI(
    title="EchoMind AI — LifeSync Intelligence",
    description="Zero-cost, local voice-first personal assistant with Amazon Alexa+ Model Context Protocol (MCP) integration.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(tasks.router)
app.include_router(schedule.router)
app.include_router(memory.router)
app.include_router(reminders.router)
app.include_router(purchases.router)
app.include_router(smarthome.router)
app.include_router(assistant.router)
app.include_router(mcp.router)

# Also expose standard /mcp route directly for root MCP clients
@app.post("/mcp")
async def root_mcp_entrypoint(request: mcp.Request):
    return await mcp.handle_mcp_jsonrpc(request)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "EchoMind AI — LifeSync Intelligence",
        "version": "1.0.0",
        "cost": "₹0 (Zero cost, runs fully local)",
        "alexa_mcp_compliant": True,
        "database": "SQLite persistent storage active"
    }


# Check if frontend dist exists to serve static build
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't intercept API or MCP routes
        if full_path.startswith("api") or full_path.startswith("mcp") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return None
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)

