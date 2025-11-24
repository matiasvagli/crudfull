from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager

from app.db.session import init_db
from app.products.router import router as products_router
from app.auth.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    
    await init_db()
    
    yield
    # Shutdown
    pass

app = FastAPI(
    title="test_welcome",
    lifespan=lifespan
)

app.include_router(auth_router)

app.include_router(products_router)

# Mount static files (logos, CSS, etc.)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Welcome page with project info"""
    html_path = os.path.join(os.path.dirname(__file__), "welcome.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return """
    <html>
        <body style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1>🚀 test_welcome API</h1>
            <p>Visit <a href="/docs">/docs</a> for API documentation</p>
        </body>
    </html>
    """