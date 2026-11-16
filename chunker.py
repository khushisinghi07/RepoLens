from pathlib import Path

EXTENSIONS = {".py",".js",".jsx",".ts",".tsx",".java",".cpp",".c",".h",".hpp",".cs",".go",".rs",".php",".rb",".swift",".kt",".html",".css",".scss",".json",".yaml",".yml",".toml",".md",".sql",".sh",".xml"}
IGNORED_DIRS = {"node_modules",".git",".venv","venv","__pycache__","dist","build",".next","coverage","vendor","target"}
IGNORED_FILES = {".env",".env.local","package-lock.json","yarn.lock","pnpm-lock.yaml"}

def collect_chunks(root: Path, chunk_lines=70, overlap=12):
    chunks = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in rel.parts) or path.name in IGNORED_FILES or path.suffix.lower() not in EXTENSIONS:
            continue
        try:
            if path.stat().st_size > 500_000:
                continue
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        step = max(1, chunk_lines-overlap)
        for start in range(0, len(lines), step):
            end = min(start+chunk_lines, len(lines))
            body = "\n".join(lines[start:end]).strip()
            if body:
                chunks.append({"text": body, "file_path": rel.as_posix(), "start_line": start+1, "end_line": end})
            if end == len(lines):
                break
    return chunks
