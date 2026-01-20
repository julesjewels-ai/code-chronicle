## 2024-05-23 - [Python List Comp Performance] **Learning:** List comprehensions with complex logic (e.g. walrus operator assignments) can be slower than explicit loops. **Action:** Benchmark before assuming list comprehensions are always faster.

## 2024-05-23 - [Loop Fusion & Object Overhead] **Learning:** Merging loops and avoiding intermediate DTOs (like `NarrativeChunk`) can significantly improve performance (e.g. 3x speedup in this case) by reducing allocation and iteration overhead. **Action:** Look for opportunities to stream processing instead of building intermediate lists.

## 2024-05-24 - [Generator vs List in Join] **Learning:** Using a generator expression with `str.join` yielded a ~30% speedup over list appending for large datasets (100k items), likely due to avoiding `list.append` overhead and list resizing. Memory impact was masked by input data size. **Action:** Prefer generator expressions for `join` when processing large sequences.

## 2024-05-25 - [Streaming Subprocess I/O] **Learning:** Streaming `git log` output via `subprocess.Popen` and `yield` reduced end-to-end latency by ~30% compared to `subprocess.run` (blocking) when coupled with parallel downstream processing. **Action:** Prefer `Popen` with generators for large CLI outputs to enable pipeline parallelism.

## 2024-05-26 - [Concurrent Futures Overhead] **Learning:** Importing `concurrent.futures` can introduce significant startup latency (~25-50ms+). While custom threading is faster, it sacrifices readability. **Action:** Use lazy imports for heavy modules like `concurrent.futures` to optimize CLI startup time without compromising code quality.
