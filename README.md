# CodeChronicle

An interactive documentation platform that transforms Git repository history into a visual narrative. It uses LLMs to analyze diffs and commit messages, creating a 'story mode' for codebases that helps onboard new developers by explaining not just what the code does, but how and why it evolved that way over time. It can generate video walkthroughs of code evolution for specific features.

## Tech Stack

- Electron
- React
- TypeScript
- Remotion
- Isomorphic-Git
- OpenAI API

## Features

- Automated Git history timeline visualization
- AI-generated summaries of major architectural changes
- Interactive file-tree playback scrubbing
- Video export capabilities for sprint demos
- Context-aware onboarding walkthroughs based on specific branches

## Usage

Run the CLI tool:

```bash
python main.py
```

### Options

- `-n, --limit`: Number of commits to analyze (default: 5)
- `-f, --format`: Output format (`console` or `markdown`)
- `--api-key`: OpenAI API Key (can also use `OPENAI_API_KEY` env var)
- `--model`: OpenAI model (default: `gpt-4o`)

Example:

```bash
export OPENAI_API_KEY=sk-...
python main.py -n 10 -f markdown
```
