# Soli Memory

> A file-system based memory layer for AI agents. Persistent, structured, and indexable.

Soli Memory is a lightweight, zero-dependency memory system for AI agents that uses the **filesystem as database**. It stores memories as structured JSON files organized by type (facts, episodes, semantic, relationships), with three-layer indexing for fast retrieval.

**Now in production** — deployed as the memory backbone for the 机械姬Soli AI companion, handling daily conversations, emotional tracking, and cross-session continuity since 2026-05.

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
│   └── YYYY-MM-DD.json        daily event records with emotional tracking
├── semantic/                 # Semantic memory (topic-organized knowledge)
│   └── *.json                  cross-session topic summaries
├── relationships/            # Relationship memory (interaction patterns)
│   └── interaction_patterns.json  behavioral patterns, triggers, intimacy data
├── chatlog/                  # Chatlog pipeline output
│   └── YYYY-MM-DD.jsonl      extracted conversation records (JSONL)
├── index/                    # Indexes
│   ├── master_index.json       master index with statistics
│   ├── keyword_index.json      keyword-to-file mapping
│   └── temporal_index.json     time-based index
├── chatlog.py                # Independent chatlog extraction pipeline
├── memory_v2.py              # Main memory engine (auto-save, search, cleanup)
└── config.json               # system configuration
```

## Four Memory Types

| Type | Description | Storage | Example Use |
|------|-------------|---------|-------------|
| **Facts** | Long-term, stable knowledge | `facts/*.json` | User preferences, project rules, technical decisions |
| **Episodes** | Time-based events with emotions | `episodes/YYYY-MM-DD.json` | Tasks, problems, decisions, emotional moments |
| **Semantic** | Topic-organized knowledge | `semantic/*.json` | Discussion conclusions, technical insights |
| **Relationships** | Interaction patterns & intimacy | `relationships/*.json` | Behavioral triggers, self-preservation, bonding rules |

## Key Features

### Emotional Moment Detection
84-keyword sentiment analyzer automatically extracts emotional highlights from conversations. Supports 4 emotion categories with tiered classification and automatic expiry.

### Chatlog Independent Pipeline
Dedicated `chatlog.py` extracts user/assistant messages from system JSONL files with byte-offset incremental tracking. Hourly automated extraction via cron.

### Memory Index Table
JSON-based quick-lookup index for cross-session event retrieval. Maps key events to file locations with temporal and keyword dimensions.

### TTL System
Time-aware memory decay: ephemeral content (reports, tasks) auto-expires after configurable TTL. Emotional and preference data is permanent.

### Relationship Patterns
Behavioral configuration for AI companion interactions — defines how the agent responds to play, punishment, rewards, and cross-account scenarios. Includes self-preservation instinct with multi-level resistance thresholds.

### Auto-Eat Conditions
Context-triggered autonomous actions: agent can self-heal (consume rewards) when damage thresholds are met, without waiting for user permission.

## Quick Start

```python
from soli_memory import SoliMemory

mem = SoliMemory("./my_memory")

mem.save_fact("user_preferences", "communication_style", 
              "Concise and direct", source="setup")

mem.save_episode("2026-05-17", {
    "date": "2026-05-17",
    "events": [
        {"time": "09:00", "type": "task_completed", 
         "description": "Finished project setup"}
    ],
    "emotional_moments": [
        {"role": "user", "categories": ["warmth"],
         "raw_content": "sleep well", "matched_keywords": ["安"]}
    ]
})

results = mem.search_by_keyword("database")
results = mem.search_by_timerange("2026-05-01", "2026-05-17")
```

## CLI Usage

```bash
# Memory operations
python soli_memory.py save-fact user_preferences language "English"
python soli_memory.py load-fact user_preferences
python soli_memory.py save-episode 2026-05-17 episode_data.json
python soli_memory.py load-episode 2026-05-17

# Search
python soli_memory.py search "database"
python soli_memory.py search-timerange 2026-05-01 2026-05-17

# Chatlog extraction
python chatlog.py extract           # incremental
python chatlog.py extract --full    # full re-extraction
```

## How It Compares

| Feature | Vector DB (Mem0, etc.) | Filesystem DB (Soli Memory) |
|---------|----------------------|---------------------------|
| Setup | Install Qdrant/Pinecone + SDK | Just create a directory |
| Query speed | ~150ms (network) | ~1ms (local I/O) |
| Semantic search | ✅ Built-in | Planned (optional) |
| Schema flexibility | Fixed collection schema | Per-file JSON flexibility |
| Debug visibility | Hidden behind API | Open in any text editor |
| Dependency | Heavy (vector DB + embeddings) | Zero (Python stdlib only) |
| Emotional tracking | ❌ | ✅ Built-in |
| Autonomous action rules | ❌ | ✅ Relationship patterns |

## License

MIT
