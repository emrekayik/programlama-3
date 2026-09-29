import os
import re
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT_DIR / "dist"
SCAN_DIRS = [ROOT_DIR / "src", ROOT_DIR]


def natural_sort_key(s: str):
    """Sort strings with embedded numbers naturally (e.g. ders2 before ders10)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", s)]


def find_marimo_notebooks():
    notebooks = []
    seen = set()

    for base_dir in SCAN_DIRS:
        if not base_dir.exists():
            continue
        for py_file in base_dir.rglob("*.py"):
            # Skip hidden dirs, virtualenvs, dist, build, tests etc.
            rel_parts = py_file.relative_to(ROOT_DIR).parts
            if any(part.startswith(".") or part in {"dist", "build", "scripts"} for part in rel_parts):
                continue
            if py_file.name == "__init__.py":
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                if "marimo.App(" in content:
                    real_path = py_file.resolve()
                    if real_path not in seen:
                        seen.add(real_path)
                        notebooks.append(py_file)
            except Exception as e:
                print(f"Warning: could not read {py_file}: {e}", file=sys.stderr)

    notebooks.sort(key=lambda p: natural_sort_key(p.stem))
    return notebooks


def generate_index_html(notebook_items):
    cards_html = ""
    for item in notebook_items:
        title = item["name"].replace("_", " ").title()
        filename = item["html_file"]
        rel_path = item["rel_path"]
        cards_html += f"""
        <a class="card" href="{filename}">
            <div class="card-icon">📓</div>
            <div class="card-content">
                <h2 class="card-title">{title}</h2>
                <span class="card-path">{rel_path}</span>
            </div>
            <span class="card-badge">Çalıştır &rarr;</span>
        </a>
"""

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Programlama 3 - Marimo Defterleri</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #090d16;
            --card-bg: rgba(255, 255, 255, 0.05);
            --card-border: rgba(255, 255, 255, 0.1);
            --card-hover-border: #6366f1;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #6366f1;
            --primary-glow: rgba(99, 102, 241, 0.25);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg);
            background-image: 
                radial-gradient(circle at 20% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 80% 80%, rgba(168, 85, 247, 0.12) 0%, transparent 40%);
            min-height: 100vh;
            color: var(--text-main);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 3rem 1.5rem;
        }}

        .container {{
            width: 100%;
            max-width: 800px;
        }}

        header {{
            text-align: center;
            margin-bottom: 2.5rem;
        }}

        h1 {{
            font-size: 2.25rem;
            font-weight: 700;
            background: linear-gradient(135deg, #fff 0%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.75rem;
        }}

        p.subtitle {{
            color: var(--text-muted);
            font-size: 1rem;
        }}

        .grid {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}

        .card {{
            display: flex;
            align-items: center;
            gap: 1.25rem;
            padding: 1.25rem 1.5rem;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 14px;
            text-decoration: none;
            color: inherit;
            backdrop-filter: blur(12px);
            transition: all 0.2s ease;
        }}

        .card:hover {{
            border-color: var(--card-hover-border);
            transform: translateY(-2px);
            box-shadow: 0 10px 25px -5px var(--primary-glow);
        }}

        .card-icon {{
            font-size: 1.75rem;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 48px;
            height: 48px;
            background: rgba(99, 102, 241, 0.1);
            border-radius: 10px;
        }}

        .card-content {{
            flex: 1;
        }}

        .card-title {{
            font-size: 1.15rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }}

        .card-path {{
            font-size: 0.825rem;
            color: var(--text-muted);
            font-family: monospace;
        }}

        .card-badge {{
            padding: 0.4rem 0.85rem;
            font-size: 0.85rem;
            font-weight: 500;
            color: #a5b4fc;
            background: rgba(99, 102, 241, 0.15);
            border-radius: 8px;
            border: 1px solid rgba(99, 102, 241, 0.3);
            white-space: nowrap;
        }}

        .empty-state {{
            text-align: center;
            padding: 3rem;
            background: var(--card-bg);
            border: 1px dashed var(--card-border);
            border-radius: 14px;
            color: var(--text-muted);
        }}

        footer {{
            margin-top: 3rem;
            font-size: 0.825rem;
            color: var(--text-muted);
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Programlama 3</h1>
            <p class="subtitle">WASM destekli etkileşimli Marimo defterleri</p>
        </header>

        <main class="grid">
            {cards_html if cards_html.strip() else '<div class="empty-state">Henüz export edilecek marimo defteri bulunamadı.</div>'}
        </main>

        <footer>
            Marimo & GitHub Pages ile otomatik oluşturuldu
        </footer>
    </div>
</body>
</html>
"""


def main():
    notebooks = find_marimo_notebooks()
    print(f"🔍 Found {len(notebooks)} Marimo notebook(s):")
    for nb in notebooks:
        print(f"  - {nb.relative_to(ROOT_DIR)}")

    if not notebooks:
        print("No notebooks found to export.")
        sys.exit(0)

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    exported_items = []

    for nb in notebooks:
        stem = nb.stem
        out_html = f"{stem}.html"
        out_path = DIST_DIR / out_html

        print(f"\n📦 Exporting {nb.relative_to(ROOT_DIR)} -> dist/{out_html}...")
        cmd = [
            "uv",
            "run",
            "marimo",
            "export",
            "html-wasm",
            str(nb),
            "-o",
            str(out_path),
            "--mode",
            "run",
        ]
        res = subprocess.run(cmd, cwd=ROOT_DIR)
        if res.returncode != 0:
            print(f"❌ Failed to export {nb}", file=sys.stderr)
            sys.exit(res.returncode)

        exported_items.append({
            "name": stem,
            "html_file": out_html,
            "rel_path": str(nb.relative_to(ROOT_DIR)),
        })

    # Generate index.html
    index_file = DIST_DIR / "index.html"
    index_content = generate_index_html(exported_items)
    index_file.write_text(index_content, encoding="utf-8")
    print(f"\n✨ Generated portal index page: {index_file}")

    # Ensure .nojekyll exists
    nojekyll_file = DIST_DIR / ".nojekyll"
    if not nojekyll_file.exists():
        nojekyll_file.touch()
        print(f"✨ Created {nojekyll_file}")


if __name__ == "__main__":
    main()
