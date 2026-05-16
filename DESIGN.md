# Soli Memory Design Document

## Design Goals

1. **Persistent memory** — maintain context across AI agent sessions
2. **Zero dependencies** — Python stdlib only, no external databases
3. **Structured storage** — JSON format, easy to query and debug
4. **On-demand loading** — only load relevant memories, waste no tokens
5. **Indexed retrieval** — keyword, temporal, and (planned) semantic search

## Why Filesystem as Database

Inspired by the observation that **filesystems are the original database** — directories are collections, files are records, and hierarchies are indexing. For AI agents specifically:

| AI Agent Need | Filesystem Advantage |
|---------------|---------------------|
| No context limits | Each memory is its own file; load only what's needed |
| Fast access | Local filesystem I/O (ms) vs network DB queries (100ms+) |
| Parallel safety | Independent files = no locking contention |
| Schema flexibility | JSON allows per-record structure |
| Debug visibility | Open any file in a text editor |
| Backup simplicity | One `cp -r` command |

## Memory Classification

### 1. Facts (Long-term)
Stable knowledge that rarely changes:
- User preferences and communication style
- Project conventions and rules
- Technical decisions and their rationale
- Important configuration values

**Schema**: `facts/{category}.json` with `{key: {value, source, date_added}}`

### 2. Episodes (Short-to-medium term)
Time-bound events that capture what happened:
- Tasks completed with outcomes
- Problems solved and solutions applied
- Decisions made with context
- Emotional moments and user feedback

**Schema**: `episodes/YYYY-MM-DD.json` with `{date, events[], tasks_completed[], decisions_made[]}`

### 3. Semantic (Medium-to-long term)
Cross-session knowledge organized by topic:
- Technical insights and best practices
- Discussion conclusions and lessons learned
- Architecture decisions and their evolution
- Domain-specific knowledge

**Schema**: `semantic/{topic}.json` with `{topic, key_points[], conclusions[]}`

## Storage Strategy

### Write Path
1. Memory event is captured (manually or auto-extracted)
2. Classified into facts/episodes/semantic
3. Written to the appropriate JSON file
4. Index files are updated (keyword + temporal)

### Read Path
1. Identify what memory is needed (facts for session start, episodes for recent context, semantic for topic queries)
2. Look up index for relevant file paths
3. Read only the needed JSON files
4. Return structured memory data

## Retrieval Mechanisms

### Keyword Search
Full-text search across all memory files. Simple, predictable, no dependencies.

### Time Range Search
Filter episodes by date range. Efficient using filename-based indexing.

### Semantic Search (Planned)
Vector similarity search using embeddings. Will be optional and pluggable.

## Indexing

### Master Index
Tracks all memory files with statistics and file locations.

### Keyword Index
Maps topic keywords to their file locations. Built automatically on save.

### Temporal Index
Maps months to episode files. Enables efficient time-range queries.

## Future Roadmap

- [x] Phase 1: Basic architecture (directory structure, JSON I/O, indexing)
- [ ] Phase 2: Auto-extraction (extract memory elements from conversations)
- [ ] Phase 3: Search optimization (multi-keyword, ranked results)
- [ ] Phase 4: Semantic search (optional vector DB integration)
- [ ] Phase 5: Compression and archiving for long-running deployments
