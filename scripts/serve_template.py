from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
import os

app = FastAPI()

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "crudfull", "templates")
TEMPLATE_DIR = os.path.join(BASE_DIR, "project")
STATIC_DIR = os.path.join(TEMPLATE_DIR, "static")

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), auto_reload=True)


@app.get("/", response_class=HTMLResponse)
async def preview(project_name: str = "MiProyecto", db: str = "sql", logo_url: str | None = None):
    """Render the `main.jinja2` template on every request so you can edit it live.

    Run with uvicorn for autoreload on code changes:
      python -m uvicorn scripts.serve_template:app --reload --reload-dir crudfull/templates/project

    Or run without reload and edits to the template will still be reflected
    on each request because we call `get_template()` every time and `auto_reload=True`.
    """
    # Get the raw template content
    template = env.get_template("main.jinja2")
    
    # Render it with the context to get the final FastAPI code
    rendered_code = template.render(project_name=project_name, db=db, logo_url=logo_url)
    
    # Now we need to extract just the HTML from the rendered FastAPI code
    # The rendered code contains a FastAPI route that returns HTML
    # We need to extract that HTML and return it directly
    
    # Find the HTML content between triple quotes
    import re
    html_match = re.search(r'return """(.*?)"""', rendered_code, re.DOTALL)
    
    if html_match:
        html_content = html_match.group(1)
        # Process any remaining Jinja2 variables that weren't rendered
        html_content = html_content.replace("{{ project_name }}", project_name)
        if db == 'sql':
            html_content = html_content.replace("{% if db=='sql' %}SQL{% elif db=='mongo' %}MongoDB{% else %}Ghost{% endif %}", "SQL")
        elif db == 'mongo':
            html_content = html_content.replace("{% if db=='sql' %}SQL{% elif db=='mongo' %}MongoDB{% else %}Ghost{% endif %}", "MongoDB")
        else:
            html_content = html_content.replace("{% if db=='sql' %}SQL{% elif db=='mongo' %}MongoDB{% else %}Ghost{% endif %}", "Ghost")
        
        return HTMLResponse(content=html_content)
    else:
        # Fallback if we can't parse the template
        return HTMLResponse(content=f"""
        <html><body>
        <h1>Error parsing template</h1>
        <pre>{rendered_code}</pre>
        </body></html>
        """)


# Mount static files from the template's `static/` folder so the preview can load
# the default logo (and any other assets placed there).
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


if __name__ == "__main__":
    import uvicorn

    # Start uvicorn programmatically (useful if you prefer a single command)
    uvicorn.run("scripts.serve_template:app", host="127.0.0.1", port=8001, reload=True, reload_dirs=[TEMPLATE_DIR])
