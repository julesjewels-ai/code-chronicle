# Implementation Plan - CodeChronicle

## Phase 1: Foundation & Reliability [Current]
- [x] **Enhance Git Service for Richer Data**
    - [x] Update `Commit` model (author, date, body).
    - [x] Robust `git log` parsing (handle delimiters, multi-line).
- [ ] **Integrate Diff Extraction**
    - [ ] Add `diff` to `Commit` model.
    - [ ] Fetch diffs (file changes) for each commit.
- [ ] **Real LLM Integration**
    - [ ] Implement `OpenAILLMService`.
    - [ ] Add configuration for API keys.

## Phase 2: Core Analysis Features
- [ ] **Architectural Change Detection**
    - [ ] Analyze diffs for significant structural changes.
- [ ] **Story Generation**
    - [ ] Improve prompt engineering for "narrative" mode.

## Phase 3: CLI & Usability
- [ ] **CLI Arguments**
    - [ ] Support custom repo paths, limits, model selection.
