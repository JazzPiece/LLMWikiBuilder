"""
state.py — Hash-based incremental state management.

Two JSON files are maintained alongside the wiki:
  _wiki_state.json     — per-file extraction state (hash, mtime, wiki_path, llm metadata)
  _wiki_llm_cache.json — LLM responses keyed by content hash (survives full rebuilds)
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class FileState:
    hash: str                   # MD5 of source file
    mtime: float                # mtime timestamp
    wiki_path: str              # Absolute path of output .md
    llm_cache_key: str = ""     # sha256(content) for LLM response lookup
    summarized_at: str = ""     # ISO date of last LLM summarization
    llm_model: str = ""         # Model used for summarization


@dataclass
class LLMCacheEntry:
    summary: str = ""
    key_entities: list[str] = field(default_factory=list)
    suggested_tags: list[str] = field(default_factory=list)
    related_topics: list[str] = field(default_factory=list)
    wikilinks: list[dict] = field(default_factory=list)   # cross-reference results
    timestamp: str = ""


# ---------------------------------------------------------------------------
# WikiState
# ---------------------------------------------------------------------------

class WikiState:
    """Manages the two state files for a wiki project."""

    def __init__(self, wiki_root: Path) -> None:
        self._wiki_root = wiki_root
        self._state_file = wiki_root / "_wiki_state.json"
        self._cache_file = wiki_root / "_wiki_llm_cache.json"
        self._state: dict[str, FileState] = {}
        self._llm_cache: dict[str, LLMCacheEntry] = {}

    # --- Loading ---

    def load(self) -> None:
        """Load both state files from disk."""
        if self._state_file.exists():
            try:
                raw = json.loads(self._state_file.read_text(encoding="utf-8"))
                self._state = {
                    k: FileState(**{f: v.get(f, "") for f in FileState.__dataclass_fields__})
                    for k, v in raw.items()
                }
            except Exception:
                self._state = {}

        if self._cache_file.exists():
            try:
                raw = json.loads(self._cache_file.read_text(encoding="utf-8"))
                self._llm_cache = {
                    k: LLMCacheEntry(**{
                        f: v.get(f, LLMCacheEntry.__dataclass_fields__[f].default
                                 if not hasattr(LLMCacheEntry.__dataclass_fields__[f].default_factory, '__call__')
                                 else LLMCacheEntry.__dataclass_fields__[f].default_factory())
                        for f in LLMCacheEntry.__dataclass_fields__
                    })
                    for k, v in raw.items()
                }
            except Exception:
                self._llm_cache = {}

    # --- Saving ---

    def save(self) -> None:
        """Persist both state files to disk."""
        self._wiki_root.mkdir(parents=True, exist_ok=True)
        self._state_file.write_text(
            json.dumps({k: asdict(v) for k, v in self._state.items()}, indent=2),
            encoding="utf-8",
        )
        self._cache_file.write_text(
            json.dumps({k: asdict(v) for k, v in self._llm_cache.items()}, indent=2),
            encoding="utf-8",
        )

    # --- Extraction state ---

    def needs_extraction(self, source_file: Path, wiki_file: Path, incremental: bool) -> bool:
        """Return True if the source file's wiki article needs to be (re)generated."""
        if not incremental:
            return True
        key = str(source_file)
        if key not in self._state:
            return True
        if not wiki_file.exists():
            return True
        try:
            current_mtime = source_file.stat().st_mtime
            entry = self._state[key]
            if entry.mtime != current_mtime:
                from .extractor import file_hash
                current_hash = file_hash(source_file)
                if entry.hash != current_hash:
                    return True
                # mtime changed but content identical — just update mtime
                self._state[key].mtime = current_mtime
                return False
        except Exception:
            return True
        return False

    def needs_summarization(self, source_file: Path, content_hash: str, model: str) -> bool:
        """Return True if the file needs a fresh LLM summarization call."""
        key = str(source_file)
        if key not in self._state:
            return True
        entry = self._state[key]
        if entry.llm_cache_key != content_hash:
            return True
        if entry.llm_model != model:
            return True
        # Check LLM cache has the result
        return content_hash not in self._llm_cache

    def update_extraction(
        self,
        source_file: Path,
        wiki_file: Path,
        file_hash: str,
        content_hash: str,
    ) -> None:
        """Record that a file has been extracted."""
        try:
            mtime = source_file.stat().st_mtime
        except Exception:
            mtime = 0.0
        key = str(source_file)
        existing = self._state.get(key)
        self._state[key] = FileState(
            hash=file_hash,
            mtime=mtime,
            wiki_path=str(wiki_file),
            llm_cache_key=existing.llm_cache_key if existing else content_hash,
            summarized_at=existing.summarized_at if existing else "",
            llm_model=existing.llm_model if existing else "",
        )

    def update_summarization(
        self,
        source_file: Path,
        content_hash: str,
        model: str,
        llm_result: LLMCacheEntry,
    ) -> None:
        """Record that a file has been LLM-summarized and cache the result."""
        key = str(source_file)
        if key in self._state:
            self._state[key].llm_cache_key = content_hash
            self._state[key].summarized_at = date.today().isoformat()
            self._state[key].llm_model = model
        llm_result.timestamp = date.today().isoformat()
        self._llm_cache[content_hash] = llm_result

    # --- LLM cache ---

    def get_llm_cache(self, content_hash: str) -> LLMCacheEntry | None:
        return self._llm_cache.get(content_hash)

    def set_llm_cache(self, content_hash: str, entry: LLMCacheEntry) -> None:
        self._llm_cache[content_hash] = entry

    # --- File state access ---

    def get_file_state(self, source_file: Path) -> FileState | None:
        return self._state.get(str(source_file))

    def all_wiki_paths(self) -> list[str]:
        """Return all known wiki article paths (for lint orphan detection)."""
        return [s.wiki_path for s in self._state.values() if s.wiki_path]

    def remove_file(self, source_file: Path) -> str | None:
        """Remove a file from state (called when source is deleted). Returns old wiki_path."""
        key = str(source_file)
        if key in self._state:
            old_wiki = self._state[key].wiki_path
            del self._state[key]
            return old_wiki
        return None

    def all_source_keys(self) -> set[str]:
        return set(self._state.keys())
