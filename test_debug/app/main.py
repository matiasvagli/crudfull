from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager

from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    
    await init_db()
    
    yield
    # Shutdown
    pass

app = FastAPI(
    title="test_debug",
    lifespan=lifespan
)

# Mount static files (logos, CSS, etc.)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>test_debug — API</title>
    <link rel="icon" type="image/svg+xml" href="/static/logo.svg">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Inter, system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 700px;
            width: 100%;
            box-shadow: 0 20px 50px rgba(0,0,0,0.1);
        }
        .header {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 30px;
        }
        .logo {
            height: 64px;
            width: 64px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        h1 {
            font-size: 2rem;
            color: #1a202c;
            margin-bottom: 8px;
        }
        .subtitle {
            color: #64748b;
            margin-bottom: 24px;
        }
        .badge {
            background: linear-gradient(45deg, #0ea5a0, #0d8b87);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .actions {
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
        }
        .btn {
            padding: 12px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn-primary {
            background: #0ea5a0;
            color: white;
        }
        .btn-outline {
            background: transparent;
            color: #0ea5a0;
            border: 2px solid #0ea5a0;
        }
        .footer {
            text-align: center;
            color: #64748b;
            font-size: 0.9rem;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
        }
        .code {
            background: #f1f5f9;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }
        @media (max-width: 640px) {
            .header { flex-direction: column; text-align: center; }
            .card { padding: 24px; }
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <img src="/static/logo.svg" alt="Logo" class="logo">
            <img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" alt="FastAPI" class="logo">
            <div>
                <h1>🚀 test_debug — API</h1>
                <p class="subtitle">
                    Generado con <strong>CRUD-FULL</strong>. 
                    Motor: <span class="badge">SQL</span>
                </p>
            </div>
        </div>
        
        <div class="actions">
            <a href="/docs" class="btn btn-primary">📚 Open API Docs</a>
            <a href="/redoc" class="btn btn-outline">📖 Redoc</a>
        </div>
        
        <div class="footer">
            <p>Reemplaza el logo en <span class="code">static/logo.svg</span></p>
            <p>Revisa el código en <span class="code">models/</span>, <span class="code">routers/</span> y <span class="code">services/</span></p>
        </div>
    </div>
</body>
</html>"""