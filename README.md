# Focus Timer

A terminal Pomodoro timer with big ASCII countdown digits and streak tracking.

## Features

- 25-minute focus blocks followed by 5-minute short breaks
- 15-minute long break after every 4 focus sessions
- ASCII block-digit countdown display
- Progress bar with percentage
- Daily streak and all-time session counter persisted in `~/.focus_timer.json`

## Usage

```bash
python3 timer.py
```

**Controls**

| Key | Action |
|-----|--------|
| `Enter` | Skip current phase |
| `Ctrl-C` | Quit and save progress |

## Session cycle

| Phase | Duration |
|-------|----------|
| Focus | 25 min |
| Short break | 5 min |
| Focus | 25 min |
| Short break | 5 min |
| Focus | 25 min |
| Short break | 5 min |
| Focus | 25 min |
| Long break | 15 min |

After the long break the cycle repeats from the beginning.

## Requirements

Python 3.6+ — no third-party packages required.
