## 2024-05-23 - [Python List Comp Performance] **Learning:** List comprehensions with complex logic (e.g. walrus operator assignments) can be slower than explicit loops. **Action:** Benchmark before assuming list comprehensions are always faster.

## 2024-05-23 - [Loop Fusion & Object Overhead] **Learning:** Merging loops and avoiding intermediate DTOs (like `NarrativeChunk`) can significantly improve performance (e.g. 3x speedup in this case) by reducing allocation and iteration overhead. **Action:** Look for opportunities to stream processing instead of building intermediate lists.

## 2024-05-24 - [Generator vs List in Join] **Learning:** Using a generator expression with `str.join` yielded a ~30% speedup over list appending for large datasets (100k items), likely due to avoiding `list.append` overhead and list resizing. Memory impact was masked by input data size. **Action:** Prefer generator expressions for `join` when processing large sequences.

## 2024-05-25 - [Subprocess Streaming] **Learning:** Using `subprocess.Popen` to stream `git log` output is significantly faster (~30% in benchmarks) and more memory-efficient than `subprocess.run(capture_output=True)` for large histories, as it avoids loading the entire output into a large string. **Action:** Prefer streaming `stdout` for potentially large subprocess outputs.
