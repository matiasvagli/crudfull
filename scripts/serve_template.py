from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
import os

app = FastAPI()

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "crudfull", "templates")
TEMPLATE_DIR = os.path.join(BASE_DIR, "project")

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), auto_reload=True)


@app.get("/", response_class=HTMLResponse)
async def preview(project_name: str = "MiProyecto", db: str = "sql"):
    """Render the `main.jinja2` template on every request so you can edit it live.

    Run with uvicorn for autoreload on code changes:
      python -m uvicorn scripts.serve_template:app --reload --reload-dir crudfull/crudfull/templates/project

    Or run without reload and edits to the template will still be reflected
    on each request because we call `get_template()` every time and `auto_reload=True`.
    """
    template = env.get_template("main.jinja2")
    html = template.render(project_name=project_name, db=db)
    return HTMLResponse(content=html)


if __name__ == "__main__":
    import uvicorn

    # Start uvicorn programmatically (useful if you prefer a single command)
    uvicorn.run("scripts.serve_template:app", host="127.0.0.1", port=8001, reload=True, reload_dirs=[TEMPLATE_DIR])
