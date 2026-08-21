# THE WHITENING ADVANTAGE — PROJECT SPECIFICATION & CONSTRAINTS

@AGENTS.md

---

## Codebase Navigation & Token Conservation (Graphify Protocol)

A precomputed AST structural knowledge graph is maintained in `graphify-out/`.

### Mandatory Exploration Workflow:
1. **Never perform blind, recursive `grep` or `view_file` calls across `experiments/` or `data/`** during initial architectural exploration.
2. **First consult `graphify-out/GRAPH_REPORT.md`** to understand component boundaries, community clusters, and god nodes.
3. **Use `/graphify query <concept>`** (or execute `graphify query "<concept>"` in bash) to locate exact file paths and function definitions.
4. **Use `/graphify path <source_symbol> <target_symbol>`** when tracing cross-stream dependencies or determinism harness invocations.
5. Inspect individual source files **only** after isolating target symbols via the graph index.

### Graph Synchronization:
- If code changes modify function signatures or import topologies across `experiments/`, refresh the index with:
  `graphify . --update`