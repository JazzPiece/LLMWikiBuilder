"""
wiki/index.py — Build index.md (master content index) and folder-level index files.

Two kinds of index files:
  1. Folder index  — <wiki_dir>/<FolderName>.md — lists files and subdirs in that folder
  2. Master index  — wiki/index.md — top-level catalog of all folders + quick stats
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from ..config import WikiConfig
from ..extractor import format_size, mtime_str, path_to_uri, slugify
from .article import wikilink_name


def folder_index_path(wiki_dir: Path) -> Path:
    """Return <wiki_dir>/<FolderName>.md"""
    return wiki_dir / f"{wiki_dir.name}.md"


def write_folder_index(
    source_dir: Path,
    wiki_dir: Path,
    wiki_root: Path,
    subdirs: list[Path],
    files: list[Path],
    excluded_subdirs: list[str],
    cfg: WikiConfig,
) -> None:
    today = date.today().isoformat()

    # Breadcrumb (skip for top-level)
    try:
        parts = wiki_dir.relative_to(wiki_root).parts
    except ValueError:
        parts = ()
    is_root = len(parts) <= 1
    crumb_line = ""
    if not is_root:
        crumbs = []
        for i, part in enumerate(parts):
            ancestor = wiki_root.joinpath(*parts[: i + 1])
            idx = folder_index_path(ancestor)
            wl = wikilink_name(wiki_root, idx)
            if i < len(parts) - 1:
                crumbs.append(f"[[{wl}|{part}]]")
            else:
                crumbs.append(f"**{part}**")
        crumb_line = "\n" + " > ".join(crumbs) + "\n"

    # Subdirectories
    subdir_lines = []
    for sd in sorted(subdirs, key=lambda p: p.name.lower()):
        child_idx = folder_index_path(wiki_dir / sd.name)
        child_wl = wikilink_name(wiki_root, child_idx)
        subdir_lines.append(f"- [[{child_wl}|{sd.name}]]")

    if excluded_subdirs:
        subdir_lines.append("")
        subdir_lines.append("### Excluded folders")
        for name in sorted(excluded_subdirs):
            subdir_lines.append(f"- **{name}** — *excluded by config*")

    # File table
    file_rows = []
    for f in sorted(files, key=lambda p: p.name.lower()):
        slug = slugify(f.stem)
        art_file = wiki_dir / f"{slug}{f.suffix.lower()}.md"
        art_wl = wikilink_name(wiki_root, art_file)
        size = format_size(f.stat().st_size) if f.exists() else "?"
        mod = mtime_str(f)
        file_rows.append(
            f"| [[{art_wl}|{f.name}]] "
            f"| {f.suffix.lstrip('.').upper() or 'FILE'} "
            f"| {size} | {mod} |"
        )

    subdir_block = "\n".join(subdir_lines) if subdir_lines else "*None*"
    if file_rows:
        file_block = (
            "| File | Type | Size | Last Modified |\n"
            "|------|------|------|---------------|\n"
            + "\n".join(file_rows)
        )
    else:
        file_block = "*No files.*"

    index_md = f"""---
source_folder: {source_dir}
wiki_updated: {today}
file_count: {len(files)}
subdir_count: {len(subdirs)}
tags: [folder-index]
---
{crumb_line}
# {source_dir.name}

> {len(files)} files · {len(subdirs)} subdirectories · [Open folder]({path_to_uri(source_dir)})

## Subdirectories

{subdir_block}

## Files

{file_block}
"""
    wiki_dir.mkdir(parents=True, exist_ok=True)
    folder_index_path(wiki_dir).write_text(index_md, encoding="utf-8")


def write_master_index(
    wiki_root: Path,
    folder_stats: list[dict],
    cfg: WikiConfig,
) -> None:
    """Write the root index.md — master catalog of all wiki content."""
    today = date.today().isoformat()

    rows = []
    for fs in sorted(folder_stats, key=lambda x: x["name"].lower()):
        idx_path = fs.get("index_path")
        if idx_path:
            wl = wikilink_name(wiki_root, Path(idx_path))
            rows.append(
                f"| [[{wl}|{fs['name']}]] "
                f"| {fs.get('files', '?')} "
                f"| {fs.get('subdirs', '?')} "
                f"| {fs.get('updated', today)} |"
            )

    table = (
        "| Folder | Files | Subdirs | Last Compiled |\n"
        "|--------|-------|---------|---------------|\n"
        + "\n".join(rows)
        if rows else "*No folders indexed yet.*"
    )

    master = f"""---
wiki_updated: {today}
tags: [index]
---

# {cfg.project.name} — Wiki Index

Generated: {today}

## Folders

{table}

---
*Built by `wikigen`. Run `wikigen ingest --incremental` to update.*
"""
    index_path = cfg.index_path()
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(master, encoding="utf-8")


def append_log(wiki_root: Path, cfg: WikiConfig, message: str) -> None:
    """Append an entry to log.md (append-only chronological record)."""
    log_path = cfg.log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    entry = f"\n## [{today}] {message}\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)
