#!/usr/bin/env python3
"""
Render the Jinja2 template `crudfull/crudfull/templates/project/main.jinja2`
and write the resulting HTML to `tmp_main.html`.

Usage:
  python scripts/render_main_template.py [--db sql|mongo|ghost] [--name ProjectName]

Requires: jinja2
"""
import argparse
import os
from jinja2 import Environment, FileSystemLoader

parser = argparse.ArgumentParser()
parser.add_argument("--db", choices=["sql", "mongo", "ghost"], default="sql")
parser.add_argument("--name", default="MiProyecto")
parser.add_argument("--logo-url", default=None, help="URL or path to a project logo to include in the preview")
args = parser.parse_args()

# locate templates folder relative to repo
base_dir = os.path.join(os.path.dirname(__file__), "..", "crudfull", "templates")
project_tpl_dir = os.path.join(base_dir, "project")

env = Environment(loader=FileSystemLoader(project_tpl_dir))
template = env.get_template("main.jinja2")

html = template.render(project_name=args.name, db=args.db, logo_url=args.logo_url)

out_path = os.path.join(os.getcwd(), "tmp_main.html")
with open(out_path, "w") as f:
    f.write(html)

print("Wrote:", out_path)
print("To open in your desktop browser:")
print("  xdg-open", out_path)
print("Or serve it locally:")
print("  python -m http.server 8000 --directory .")
print("Then open http://localhost:8000/tmp_main.html in your browser")
