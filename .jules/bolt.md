## 2024-05-23 - [Python List Comp Performance] **Learning:** List comprehensions with complex logic (e.g. walrus operator assignments) can be slower than explicit loops. **Action:** Benchmark before assuming list comprehensions are always faster.

## 2024-05-23 - [Loop Fusion & Object Overhead] **Learning:** Merging loops and avoiding intermediate DTOs (like `NarrativeChunk`) can significantly improve performance (e.g. 3x speedup in this case) by reducing allocation and iteration overhead. **Action:** Look for opportunities to stream processing instead of building intermediate lists.

## 2024-10-24 - [String Parsing Efficiency] **Learning:** Using `splitlines()` and `partition()` is significantly faster (~10-15%) and more memory efficient than `split('\n')` and `split(separator)` for parsing line-based data like git logs, as it avoids creating intermediate list objects for every line. **Action:** Prefer `partition` over `split` when the separator count is known and small.
