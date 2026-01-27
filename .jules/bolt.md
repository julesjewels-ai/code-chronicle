## 2024-05-23 - [Python List Comp Performance] **Learning:** List comprehensions with complex logic (e.g. walrus operator assignments) can be slower than explicit loops. **Action:** Benchmark before assuming list comprehensions are always faster.

## 2024-05-23 - [Loop Fusion & Object Overhead] **Learning:** Merging loops and avoiding intermediate DTOs (like `NarrativeChunk`) can significantly improve performance (e.g. 3x speedup in this case) by reducing allocation and iteration overhead. **Action:** Look for opportunities to stream processing instead of building intermediate lists.

## 2024-05-24 - [Generator vs List in Join] **Learning:** Using a generator expression with `str.join` yielded a ~30% speedup over list appending for large datasets (100k items), likely due to avoiding `list.append` overhead and list resizing. Memory impact was masked by input data size. **Action:** Prefer generator expressions for `join` when processing large sequences.

## 2024-05-25 - [Streaming Subprocess I/O] **Learning:** Streaming `git log` output via `subprocess.Popen` and `yield` reduced end-to-end latency by ~30% compared to `subprocess.run` (blocking) when coupled with parallel downstream processing. **Action:** Prefer `Popen` with generators for large CLI outputs to enable pipeline parallelism.

## 2024-05-26 - [Concurrent Futures Overhead] **Learning:** Importing `concurrent.futures` can introduce significant startup latency (~25-50ms+). While custom threading is faster, it sacrifices readability. **Action:** Use lazy imports for heavy modules like `concurrent.futures` to optimize CLI startup time without compromising code quality.

## 2024-05-27 - [Standard Lib Import Cost] **Learning:** Even standard library modules like `subprocess` can have measurable import cost (~20ms). **Action:** Apply lazy loading to `subprocess` in CLI tools where startup time is critical.

## 2024-05-27 - [Static Method vs Function] **Learning:** Extracting tight-loop static methods to module-level functions can reduce overhead by ~35% (approx 40ns per call) by avoiding attribute lookup. **Action:** Consider extracting helpers in hot loops.

## 2024-05-28 - [Subprocess Import Cost] **Learning:** Lazy importing 'subprocess' in 'LocalGitService' reduced module import time by ~95ms (from ~150ms to ~55ms). Standard library imports can be significant bottlenecks in CLI tools. **Action:** Profile standard library imports in hot paths or CLI startup.

## 2026-01-27 - [Subprocess Buffering] **Learning:** `subprocess.Popen` with `bufsize=1` (line buffering) increases syscall overhead significantly compared to default buffering (`bufsize=-1`). Switching to default buffering improved throughput by ~7% for large outputs while still supporting line iteration via `TextIOWrapper`. **Action:** Use `bufsize=-1` for `subprocess` streaming unless interactive line-by-line control (deadlock prevention) is strictly required.
