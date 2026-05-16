# Soli Memory

> A file-system based memory layer for AI agents. Persistent, structured, and indexable.

Soli Memory is a lightweight, zero-dependency memory system for AI agents that uses the **filesystem as database**. It stores memories as structured JSON files organized by type (facts, episodes, semantic), with three-layer indexing for fast retrieval.

## Philosophy

Most AI memory systems rely on vector databases or graph databases. Soli Memory takes a different approach — the **filesystem is the database**.

Why filesystem-based:
- **No context limits** — each file is small; load only what you need
- **Instant access** — filesystem I/O is faster than querying external databases
- **Parallel friendly** — independent files = no locking contention
- **Flexible schema** — JSON allows per-memory-type structures
- **Debuggable** — open any file in a text editor to see what's stored
- **Backup friendly** — just `cp -r` the whole directory

## Architecture

```
memory_root/
├── facts/                    # Factual memory (long-term)
│   └── *.json                  user preferences, project conventions, technical decisions
├── episodes/                 # Episodic memory (short-to-medium term)
│   └── YYYY-MM-DD.json        daily event records
├── semantic/                 # Semantic memory (topic-organized knowledge)
│   └── *.json                  cross-session topic summaries
├── index/                    # Indexes
│   ├── master_index.json       master index with statistics
│   ├── keyword_index.json      keyword-to-file mapping
│   └── temporal_index.json     time-based index
└── config.json               # system configuration
```

## Three Memory Types

| Type | Description | Storage | Example Use |
|------|-------------|---------|-------------|
| **Facts** | Long-term, stable knowledge | `facts/*.json` | User preferences, project rules, technical decisions |
| **Episodes** | Time-based events | `episodes/YYYY-MM-DD.json` | Tasks completed, problems solved, emotional moments |
| **Semantic** | Topic-organized knowledge | `semantic/*.json` | Discussion conclusions, technical insights, best practices |

## Quick Start

```python
from soli_memory import SoliMemory

# Initialize with custom root path
mem = SoliMemory("./my_memory")

# Save a fact
mem.save_fact("user_preferences", "communication_style", 
              "Concise and direct", source="setup")

# Save an episode
mem.save_episode("2026-05-17", {
    "date": "2026-05-17",
    "events": [
        {"time": "09:00", "type": "task_completed", 
         "description": "Finished project setup"}
    ]
})

# Save semantic knowledge
mem.save_semantic("architecture_decisions", {
    "topic": "architecture_decisions",
    "key_points": ["Filesystem as database is suitable for AI agents"],
    "conclusions": ["Keep it simple"]
})

# Search
results = mem.search_by_keyword("database")
# -> ["facts/technical_decisions.json", "episodes/2026-05-17.json"]

# Search by time range
results = mem.search_by_timerange("2026-05-01", "2026-05-17")
# -> ["episodes/2026-05-17.json"]
```

## CLI Usage

```bash
# Save a fact
python soli_memory.py save-fact user_preferences language "English"

# Load facts
python soli_memory.py load-fact user_preferences
python soli_memory.py load-fact user_preferences language

# Save an episode from JSON file
python soli_memory.py save-episode 2026-05-17 episode_data.json

# Load an episode
python soli_memory.py load-episode 2026-05-17

# Search by keyword
python soli_memory.py search "database"

# Search by time range
python soli_memory.py search-timerange 2026-05-01 2026-05-17
```

## Configuration

See [config.json](config.json) for the full configuration schema.

## How It Compares

| Feature | Vector DB (Mem0, etc.) | Filesystem DB (Soli Memory) |
|---------|----------------------|---------------------------|
| Setup | Install Qdrant/Pinecone + SDK | Just create a directory |
| Query speed | ~150ms (network) | ~1ms (local I/O) |
| Semantic search | ✅ Built-in (embeddings) | ❌ (keyword only, but planned) |
| Schema flexibility | Fixed collection schema | Per-file JSON flexibility |
| Debug visibility | Hidden behind API | Open in any text editor |
| Dependency | Heavy (vector DB + embeddings) | Zero (Python stdlib only) |

## License

MIT
