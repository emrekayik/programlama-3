import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT_DIR / "dist"
NOTEBOOKS_DIR = ROOT_DIR / "notebooks"
GITHUB_REPO_URL = "https://github.com/emrekayik/programlama-3"
GITHUB_BRANCH = "main"


def natural_sort_key(s: str):
    """Sort strings with embedded numbers naturally (e.g. ders2 before ders10)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", s)]


def find_marimo_notebooks():
    """Finds all Marimo python notebooks in the project."""
    notebooks = []
    seen = set()

    scan_dirs = [ROOT_DIR / "src", ROOT_DIR / "notebooks", ROOT_DIR]

    for base_dir in scan_dirs:
        if not base_dir.exists():
            continue
        for py_file in base_dir.rglob("*.py"):
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
        html_file = item["html_file"]
        static_html_file = item["static_html_file"]
        ipynb_file = item["ipynb_file"]
        github_ipynb_url = item["github_ipynb_url"]
        colab_url = item["colab_url"]
        rel_path = item["rel_path"]

        cards_html += f"""
        <div class="card">
            <div class="card-header">
                <div class="card-title-group">
                    <span class="card-icon">📓</span>
                    <div>
                        <h2 class="card-title">{title}</h2>
                        <span class="card-path">{rel_path}</span>
                    </div>
                </div>
            </div>
            <div class="card-actions">
                <a class="btn btn-primary" href="{html_file}">
                    <span class="btn-icon">⚡</span> Canlı Çalıştır (WASM)
                </a>
                <a class="btn btn-static" href="{static_html_file}">
                    <span class="btn-icon">📄</span> Statik HTML Görünüm
                </a>
                <a class="btn btn-secondary" href="{ipynb_file}" download>
                    <span class="btn-icon">📥</span> .ipynb İndir
                </a>
                <a class="btn btn-outline" href="{github_ipynb_url}" target="_blank" rel="noopener noreferrer">
                    <span class="btn-icon">🐙</span> GitHub'da İncele
                </a>
                <a class="btn btn-colab" href="{colab_url}" target="_blank" rel="noopener noreferrer">
                    <span class="btn-icon">🟡</span> Colab
                </a>
            </div>
        </div>
"""

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Programlama 3 - Marimo & Jupyter Defterleri</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #090d16;
            --card-bg: rgba(255, 255, 255, 0.04);
            --card-border: rgba(255, 255, 255, 0.08);
            --card-hover-border: rgba(99, 102, 241, 0.4);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --primary-glow: rgba(99, 102, 241, 0.2);
            --static-color: #06b6d4;
            --static-glow: rgba(6, 182, 212, 0.2);
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
                radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.15) 0%, transparent 45%),
                radial-gradient(circle at 85% 85%, rgba(168, 85, 247, 0.12) 0%, transparent 45%);
            min-height: 100vh;
            color: var(--text-main);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 3rem 1.5rem;
        }}

        .container {{
            width: 100%;
            max-width: 880px;
        }}

        header {{
            text-align: center;
            margin-bottom: 2.75rem;
        }}

        .badge-tag {{
            display: inline-block;
            background: rgba(99, 102, 241, 0.15);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #a5b4fc;
            padding: 0.35rem 0.85rem;
            border-radius: 9999px;
            font-size: 0.825rem;
            font-weight: 500;
            margin-bottom: 1rem;
        }}

        h1 {{
            font-size: 2.25rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 20%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.6rem;
            letter-spacing: -0.02em;
        }}

        p.subtitle {{
            color: var(--text-muted);
            font-size: 1.05rem;
            max-width: 620px;
            margin: 0 auto;
            line-height: 1.5;
        }}

        .grid {{
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }}

        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(12px);
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        .card:hover {{
            border-color: var(--card-hover-border);
            transform: translateY(-2px);
            box-shadow: 0 12px 30px -8px var(--primary-glow);
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.25rem;
        }}

        .card-title-group {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .card-icon {{
            font-size: 1.75rem;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 48px;
            height: 48px;
            background: rgba(99, 102, 241, 0.12);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 12px;
        }}

        .card-title {{
            font-size: 1.25rem;
            font-weight: 600;
            letter-spacing: -0.01em;
            margin-bottom: 0.2rem;
        }}

        .card-path {{
            font-size: 0.8rem;
            color: var(--text-muted);
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        }}

        .card-actions {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.65rem;
        }}

        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.55rem 0.95rem;
            font-size: 0.875rem;
            font-weight: 500;
            border-radius: 9px;
            text-decoration: none;
            transition: all 0.15s ease;
            cursor: pointer;
        }}

        .btn-icon {{
            font-size: 1rem;
        }}

        .btn-primary {{
            background: var(--primary);
            color: #ffffff;
            box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
        }}

        .btn-primary:hover {{
            background: var(--primary-hover);
            transform: translateY(-1px);
        }}

        .btn-static {{
            background: rgba(6, 182, 212, 0.12);
            border: 1px solid rgba(6, 182, 212, 0.3);
            color: #67e8f9;
        }}

        .btn-static:hover {{
            background: rgba(6, 182, 212, 0.22);
            border-color: rgba(6, 182, 212, 0.5);
            transform: translateY(-1px);
        }}

        .btn-secondary {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: var(--text-main);
        }}

        .btn-secondary:hover {{
            background: rgba(255, 255, 255, 0.13);
            border-color: rgba(255, 255, 255, 0.25);
            transform: translateY(-1px);
        }}

        .btn-outline {{
            background: transparent;
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: var(--text-muted);
        }}

        .btn-outline:hover {{
            color: var(--text-main);
            border-color: rgba(255, 255, 255, 0.35);
            background: rgba(255, 255, 255, 0.04);
            transform: translateY(-1px);
        }}

        .btn-colab {{
            background: rgba(245, 158, 11, 0.1);
            border: 1px solid rgba(245, 158, 11, 0.25);
            color: #fbbf24;
        }}

        .btn-colab:hover {{
            background: rgba(245, 158, 11, 0.18);
            border-color: rgba(245, 158, 11, 0.45);
            transform: translateY(-1px);
        }}

        .empty-state {{
            text-align: center;
            padding: 3.5rem 1.5rem;
            background: var(--card-bg);
            border: 1px dashed var(--card-border);
            border-radius: 16px;
            color: var(--text-muted);
        }}

        footer {{
            margin-top: 3.5rem;
            font-size: 0.85rem;
            color: var(--text-muted);
            text-align: center;
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }}

        footer a {{
            color: #a5b4fc;
            text-decoration: none;
        }}

        footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="badge-tag">Interactive Python & Marimo</div>
            <h1>Programlama 3</h1>
        </header>

        <main class="grid">
            {cards_html if cards_html.strip() else '<div class="empty-state">Henüz export edilecek marimo defteri bulunamadı.</div>'}
        </main>

        <footer>
            <span>Marimo & GitHub Pages ile otomatik oluşturuldu</span>
            <a href="{GITHUB_REPO_URL}" target="_blank" rel="noopener noreferrer">Depoyu GitHub'da Gör &rarr;</a>
        </footer>
    </div>
</body>
</html>
"""


def main():
    notebooks = find_marimo_notebooks()
    print(f"🔍 Bulunan Marimo defteri sayısı: {len(notebooks)}")
    for nb in notebooks:
        print(f"  - {nb.relative_to(ROOT_DIR)}")

    if not notebooks:
        print("Export edilecek defter bulunamadı.")
        sys.exit(0)

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)

    exported_items = []

    for nb in notebooks:
        stem = nb.stem
        out_wasm_html = f"{stem}.html"
        out_wasm_path = DIST_DIR / out_wasm_html
        
        out_static_html = f"{stem}_static.html"
        out_static_path = DIST_DIR / out_static_html
        
        repo_ipynb_path = NOTEBOOKS_DIR / f"{stem}.ipynb"
        dist_ipynb_path = DIST_DIR / f"{stem}.ipynb"

        # 1. Export or copy to .ipynb
        legacy_ipynb = ROOT_DIR / "__marimo__" / f"{stem}.ipynb"
        if legacy_ipynb.exists() and not repo_ipynb_path.exists():
            shutil.copy2(legacy_ipynb, repo_ipynb_path)
            print(f"📋 __marimo__/{stem}.ipynb -> notebooks/{stem}.ipynb kopyalandı")

        if not repo_ipynb_path.exists():
            print(f"📓 .ipynb oluşturuluyor: {repo_ipynb_path.relative_to(ROOT_DIR)}...")
            cmd_ipynb = [
                "uv", "run", "marimo", "export", "ipynb",
                str(nb), "-o", str(repo_ipynb_path)
            ]
            subprocess.run(cmd_ipynb, cwd=ROOT_DIR, check=False)

        # Copy .ipynb to dist/ for direct website downloads
        if repo_ipynb_path.exists():
            shutil.copy2(repo_ipynb_path, dist_ipynb_path)
            print(f"💾 dist/{stem}.ipynb hazırlandı (webden indirme için)")

        # 2. Export to Pre-rendered Static HTML (loads instantly, includes all cell outputs)
        print(f"📄 Statik HTML export ediliyor: dist/{out_static_html}...")
        cmd_static = [
            "uv",
            "run",
            "marimo",
            "export",
            "html",
            str(nb),
            "-o",
            str(out_static_path),
            "-f",
        ]
        res_static = subprocess.run(cmd_static, cwd=ROOT_DIR)
        if res_static.returncode != 0:
            print(f"⚠️ Statik HTML export uyarısı (kod {res_static.returncode})", file=sys.stderr)

        # 3. Export to WASM HTML (Interactive in-browser app)
        print(f"⚡ WASM HTML export ediliyor: dist/{out_wasm_html}...")
        cmd_wasm = [
            "uv",
            "run",
            "marimo",
            "export",
            "html-wasm",
            str(nb),
            "-o",
            str(out_wasm_path),
            "--mode",
            "run",
            "-f",
        ]
        res_wasm = subprocess.run(cmd_wasm, cwd=ROOT_DIR)
        if res_wasm.returncode != 0:
            print(f"❌ WASM Export başarısız: {nb}", file=sys.stderr)
            sys.exit(res_wasm.returncode)

        github_ipynb_url = f"{GITHUB_REPO_URL}/blob/{GITHUB_BRANCH}/notebooks/{stem}.ipynb"
        colab_url = f"https://colab.research.google.com/github/emrekayik/programlama-3/blob/{GITHUB_BRANCH}/notebooks/{stem}.ipynb"

        exported_items.append({
            "name": stem,
            "html_file": out_wasm_html,
            "static_html_file": out_static_html,
            "ipynb_file": f"{stem}.ipynb",
            "github_ipynb_url": github_ipynb_url,
            "colab_url": colab_url,
            "rel_path": str(nb.relative_to(ROOT_DIR)),
        })

    # Generate index.html
    index_file = DIST_DIR / "index.html"
    index_content = generate_index_html(exported_items)
    index_file.write_text(index_content, encoding="utf-8")
    print(f"\n✨ Portal sayfası oluşturuldu: {index_file}")

    # Ensure .nojekyll exists
    nojekyll_file = DIST_DIR / ".nojekyll"
    nojekyll_file.touch()
    print(f"✨ {nojekyll_file} doğrulandı")


if __name__ == "__main__":
    main()
