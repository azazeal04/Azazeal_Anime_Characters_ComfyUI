# Performance Improvement + Node 2.0 Migration Plan

## Current bottleneck (from current implementation)

The current implementation dynamically creates one Python class per anime JSON file during import (`discover_anime_nodes()` is executed at module load). This means startup work scales with the total number of anime files. In addition:

1. `create_anime_class(...).INPUT_TYPES()` opens/parses the anime JSON file.
2. Node `__init__` opens/parses the same file again.
3. ComfyUI has to register and render a very large node catalog (one node per anime).

With thousands of files, this causes large import-time overhead and UI catalog bloat.

## Recommended architecture

### 1) Replace per-anime node explosion with a single data-driven node (Node 2.0 path)

Create one primary node, e.g. `AnimeCharacterPromptSelectorV2`, that supports:

- `anime_title` input (dropdown from a lightweight index)
- `character_name` input (dropdown/string, resolved per selected anime)
- outputs:
  - `character_prompt`
  - optional `character_name_normalized`
  - optional `anime_title_normalized`

This changes startup complexity from **O(number_of_anime_nodes_registered)** to **O(1) node registrations**.

### 2) Introduce an on-disk index/cache

Add a generated cache file (e.g. `anime_data/.index.json`) containing:

- anime title -> file path
- anime title -> character name list
- source file mtime/hash metadata

Behavior:

- At startup: load only the cache (fast JSON read)
- On cache miss/stale entries: rebuild only changed anime files
- Load full prompt maps lazily only when a specific anime is selected

### 3) Lazy prompt loading + in-memory LRU cache

Only parse full prompt bodies for selected anime at execution time, with an LRU cache for active titles.

- Keeps memory bounded
- Avoids parsing prompts for titles the user never touches

### 4) Separate discovery from registration

Refactor startup so import-time work only registers a tiny fixed set of nodes. Move expensive file discovery into runtime utility methods.

## Backward compatibility strategy (Node 1.0 + old workflows)

### Compatibility goals

- Existing workflows that reference old node names should still load.
- New installations should default to the fast Node 2.0 experience.

### Practical approach

1. **Default mode (fast)**
   - Register only V2 nodes.

2. **Legacy compatibility mode (opt-in)**
   - Enable via env var, e.g. `AZAZEAL_ENABLE_LEGACY_NODES=1`.
   - Register legacy per-anime node names so old graphs deserialize.
   - Legacy adapters should delegate to shared V2 data backend (no duplicate file parsing logic).

3. **Migration helper node/script**
   - Provide a tool to replace legacy node types in workflow JSON with V2 node equivalents.
   - Optionally emit a migration report (how many nodes replaced, unresolved titles, etc.).

4. **Deprecation timeline**
   - N release cycles with warning banner when legacy mode is enabled.
   - Keep loader forever if maintenance cost is low; otherwise sunset only after explicit major release notes.

## Suggested implementation phases

### Phase 1 (quick win)

- Build shared `AnimeDataStore` abstraction.
- Move JSON parsing into this store.
- Ensure current nodes use the shared store to remove duplicate reads.

### Phase 2 (Node 2.0 rollout)

- Add `AnimeCharacterPromptSelectorV2` single-node UX.
- Add cache/index builder.
- Make V2 default in `NODE_CLASS_MAPPINGS`.

### Phase 3 (backward compatibility)

- Add legacy adapter registration behind env flag.
- Add workflow migration utility and docs.

### Phase 4 (hardening)

- Add timing telemetry logs for:
  - import time
  - index load/rebuild time
  - prompt lookup latency
- Add tests:
  - cache invalidation correctness
  - legacy node deserialization
  - V2 prompt parity with legacy output

## Concrete code-level refactor targets

- `anime_character_prompt_selector.py`
  - split into:
    - `data_store.py` (index + lazy loading)
    - `nodes_v2.py` (new single/few nodes)
    - `nodes_legacy.py` (adapter classes)
    - `__init__.py` (small, mode-based registration)

## Expected impact

- Substantially faster ComfyUI startup by avoiding thousands of node registrations by default.
- Better maintainability through one shared backend.
- Safe migration path for users with old workflows.
