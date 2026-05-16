#!/usr/bin/env python3
"""
Soli Memory — A file-system based memory layer for AI agents.

Persistent, structured, and indexable. Uses the filesystem as database.
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional


class SoliMemory:
    """Core memory engine with facts, episodes, semantic, and indexing."""

    def __init__(self, root_path: str = "./memory"):
        """
        Initialize memory at the given root path.
        
        Args:
            root_path: Directory path for storing all memory data
        """
        self.root = Path(root_path)
        self.facts_dir = self.root / "facts"
        self.episodes_dir = self.root / "episodes"
        self.semantic_dir = self.root / "semantic"
        self.index_dir = self.root / "index"
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Ensure all memory directories exist."""
        for d in [self.facts_dir, self.episodes_dir, self.semantic_dir, self.index_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def _load_json(self, file_path: Path) -> Optional[Dict]:
        """Load a JSON file, returning None if missing."""
        if not file_path.exists():
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_json(self, file_path: Path, data: Dict):
        """Save data to a JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ── Facts ──────────────────────────────────────────────

    def save_fact(self, category: str, key: str, value: Any,
                  source: str = "", date_added: str = "") -> bool:
        """Save a fact to the specified category."""
        file_path = self.facts_dir / f"{category}.json"

        data = self._load_json(file_path) or {
            "type": category,
            "last_updated": "",
            "items": {}
        }

        data["items"][key] = {
            "value": value,
            "source": source,
            "date_added": date_added or datetime.now().strftime("%Y-%m")
        }
        data["last_updated"] = datetime.now().isoformat()
        self._save_json(file_path, data)

        self._update_keyword_index(category, key, f"facts/{file_path.name}")
        return True

    def load_fact(self, category: str, key: Optional[str] = None) -> Any:
        """Load facts from a category. Returns all items or a single key."""
        data = self._load_json(self.facts_dir / f"{category}.json")
        if not data:
            return None
        if key:
            return data["items"].get(key)
        return data["items"]

    def load_all_facts(self) -> Dict:
        """Load all fact categories."""
        facts = {}
        for file in self.facts_dir.glob("*.json"):
            data = self._load_json(file)
            if data:
                facts[file.stem] = data["items"]
        return facts

    # ── Episodes ──────────────────────────────────────────

    def save_episode(self, date: str, episode_data: Dict) -> bool:
        """Save an episodic memory entry."""
        file_path = self.episodes_dir / f"{date}.json"
        self._save_json(file_path, episode_data)
        self._update_temporal_index(date, f"episodes/{file_path.name}")
        return True

    def load_episode(self, date: str) -> Optional[Dict]:
        """Load an episode by date string (YYYY-MM-DD)."""
        return self._load_json(self.episodes_dir / f"{date}.json")

    def load_recent_episodes(self, days: int = 2) -> List[Dict]:
        """Load episodes from the last N days."""
        episodes = []
        today = datetime.now().date()
        for i in range(days):
            date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            ep = self.load_episode(date_str)
            if ep:
                episodes.append(ep)
        return episodes

    # ── Semantic ──────────────────────────────────────────

    def save_semantic(self, topic: str, data: Dict) -> bool:
        """Save semantic knowledge under a topic."""
        file_path = self.semantic_dir / f"{topic}.json"
        self._save_json(file_path, data)
        return True

    def load_semantic(self, topic: str) -> Optional[Dict]:
        """Load semantic knowledge by topic."""
        return self._load_json(self.semantic_dir / f"{topic}.json")

    # ── Search ────────────────────────────────────────────

    def search_by_keyword(self, keyword: str) -> List[str]:
        """Search all memory files for a keyword."""
        results = []
        for directory in [self.facts_dir, self.episodes_dir, self.semantic_dir]:
            for file in directory.glob("*.json"):
                content = self._read_file_content(file)
                if keyword in content:
                    results.append(f"{directory.name}/{file.name}")
        return results

    def search_by_timerange(self, start_date: str, end_date: str) -> List[str]:
        """Search episodes within a date range (inclusive)."""
        results = []
        for file in self.episodes_dir.glob("*.json"):
            if start_date <= file.stem <= end_date:
                results.append(f"episodes/{file.name}")
        return results

    def _read_file_content(self, file_path: Path) -> str:
        """Read file content for keyword search."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (IOError, OSError):
            return ""

    # ── Indexing ─────────────────────────────────────────

    def _update_keyword_index(self, category: str, key: str, file_path: str):
        """Update the keyword index with a new entry."""
        index = self._load_json(self.index_dir / "keyword_index.json") or {
            "version": "1.0", "last_update": "", "keywords": {}
        }

        if category not in index["keywords"]:
            index["keywords"][category] = []
        if file_path not in index["keywords"][category]:
            index["keywords"][category].append(file_path)

        index["last_update"] = datetime.now().isoformat()
        self._save_json(self.index_dir / "keyword_index.json", index)

    def _update_temporal_index(self, date: str, file_path: str):
        """Update the temporal index with a new episode."""
        index = self._load_json(self.index_dir / "temporal_index.json") or {
            "version": "1.0", "last_update": "", "time_periods": {}
        }

        month = date[:7]  # YYYY-MM
        if month not in index["time_periods"]:
            index["time_periods"][month] = {"month": month, "episodes": []}
        if file_path not in index["time_periods"][month]["episodes"]:
            index["time_periods"][month]["episodes"].append(file_path)

        index["last_update"] = datetime.now().isoformat()
        self._save_json(self.index_dir / "temporal_index.json", index)

    def update_master_index(self):
        """Rebuild the master index from current data."""
        facts_count = len(list(self.facts_dir.glob("*.json")))
        episodes_count = len(list(self.episodes_dir.glob("*.json")))
        semantic_count = len(list(self.semantic_dir.glob("*.json")))

        index = {
            "version": "1.0",
            "last_update": datetime.now().isoformat(),
            "statistics": {
                "total_facts": facts_count,
                "total_episodes": episodes_count,
                "total_semantic_topics": semantic_count
            },
            "file_locations": {}
        }

        for directory, prefix in [
            (self.facts_dir, "facts"),
            (self.episodes_dir, "episodes"),
            (self.semantic_dir, "semantic")
        ]:
            for file in directory.glob("*.json"):
                index["file_locations"][file.stem] = f"{prefix}/{file.name}"

        self._save_json(self.index_dir / "master_index.json", index)

    # ── Auto-extraction (placeholder) ─────────────────────

    def extract_memory_elements(self, conversation_history: List[Dict]) -> Dict:
        """
        Extract memory elements from conversation history.
        
        This is a simplified rule-based extractor. Override or extend
        this method for more sophisticated extraction logic.
        """
        elements = {"facts": [], "episodes": [], "semantic": []}

        for message in conversation_history:
            content = message.get("content", "")

            # Detect preference expressions
            if any(kw in content for kw in ["I like", "I prefer", "don't"]):
                elements["facts"].append({
                    "type": "user_preference",
                    "content": content
                })

            # Detect completed tasks
            if any(kw in content for kw in ["completed", "finished", "done"]):
                elements["episodes"].append({
                    "type": "task_completed",
                    "content": content
                })

            # Detect conclusions
            if any(kw in content for kw in ["conclusion", "summary"]):
                elements["semantic"].append({
                    "type": "discussion_conclusion",
                    "content": content
                })

        return elements

    def auto_save_memory(self, conversation_history: List[Dict]) -> bool:
        """Auto-save memory from conversation (call at session end)."""
        elements = self.extract_memory_elements(conversation_history)

        for fact in elements["facts"]:
            pass  # Override for custom fact routing

        today = datetime.now().strftime("%Y-%m-%d")
        episode_data = {
            "date": today,
            "events": elements["episodes"],
            "tasks_completed": [],
            "decisions_made": []
        }
        self.save_episode(today, episode_data)
        self.update_master_index()
        return True


# ── CLI Entry Point ─────────────────────────────────────

def _cli():
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python soli_memory.py save-fact <category> <key> <value> [source]")
        print("  python soli_memory.py load-fact <category> [key]")
        print("  python soli_memory.py save-episode <date> <json_file>")
        print("  python soli_memory.py load-episode <date>")
        print("  python soli_memory.py search <keyword>")
        print("  python soli_memory.py search-timerange <start> <end>")
        sys.exit(1)

    mem = SoliMemory()
    cmd = sys.argv[1]

    if cmd == "save-fact":
        category, key, value = sys.argv[2], sys.argv[3], sys.argv[4]
        source = sys.argv[5] if len(sys.argv) > 5 else ""
        mem.save_fact(category, key, value, source)
        print(f"Fact saved: {category}.{key}")

    elif cmd == "load-fact":
        category = sys.argv[2]
        key = sys.argv[3] if len(sys.argv) > 3 else None
        result = mem.load_fact(category, key)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "save-episode":
        date = sys.argv[2]
        json_file = sys.argv[3]
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        mem.save_episode(date, data)
        print(f"Episode saved: {date}")

    elif cmd == "load-episode":
        date = sys.argv[2]
        result = mem.load_episode(date)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "search":
        keyword = sys.argv[2]
        results = mem.search_by_keyword(keyword)
        print(f"Found {len(results)} results:")
        for r in results:
            print(f"  - {r}")

    elif cmd == "search-timerange":
        start, end = sys.argv[2], sys.argv[3]
        results = mem.search_by_timerange(start, end)
        print(f"Found {len(results)} episodes from {start} to {end}:")
        for r in results:
            print(f"  - {r}")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    _cli()
