#!/usr/bin/env python3
"""Focus Timer — terminal Pomodoro timer with big ASCII countdown and streak tracking."""

import json
import select
import sys
import time
from datetime import date, timedelta
from pathlib import Path

GREEN  = '\033[92m'
BLUE   = '\033[94m'
YELLOW = '\033[93m'
BOLD   = '\033[1m'
DIM    = '\033[2m'
RESET  = '\033[0m'

DIGITS = {
    '0': ['  ████  ', ' ██  ██ ', '██    ██', '██    ██', '██    ██', ' ██  ██ ', '  ████  '],
    '1': ['  ███   ', ' ████   ', '   ██   ', '   ██   ', '   ██   ', '   ██   ', ' ██████ '],
    '2': [' ██████ ', '██    ██', '     ██ ', '   ████ ', '  ██    ', ' ██     ', '████████'],
    '3': [' ██████ ', '██    ██', '      ██', '  █████ ', '      ██', '██    ██', ' ██████ '],
    '4': ['██    ██', '██    ██', '██    ██', '████████', '      ██', '      ██', '      ██'],
    '5': ['████████', '██      ', '███████ ', '      ██', '      ██', '██    ██', ' ██████ '],
    '6': [' ██████ ', '██      ', '██      ', '███████ ', '██    ██', '██    ██', ' ██████ '],
    '7': ['████████', '     ██ ', '    ██  ', '   ██   ', '  ██    ', ' ██     ', '██      '],
    '8': [' ██████ ', '██    ██', '██    ██', ' ██████ ', '██    ██', '██    ██', ' ██████ '],
    '9': [' ██████ ', '██    ██', '██    ██', ' ███████', '      ██', '██    ██', ' ██████ '],
    ':': ['        ', '   ██   ', '   ██   ', '        ', '   ██   ', '   ██   ', '        '],
}

CYCLE = [
    ('FOCUS',       25 * 60, GREEN),
    ('SHORT BREAK',  5 * 60, BLUE),
    ('FOCUS',       25 * 60, GREEN),
    ('SHORT BREAK',  5 * 60, BLUE),
    ('FOCUS',       25 * 60, GREEN),
    ('SHORT BREAK',  5 * 60, BLUE),
    ('FOCUS',       25 * 60, GREEN),
    ('LONG BREAK',  15 * 60, YELLOW),
]

STATE_FILE = Path.home() / '.focus_timer.json'


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {'streak': 0, 'last_date': None, 'total': 0, 'today': 0}


def save_state(s):
    STATE_FILE.write_text(json.dumps(s))


def record_session(s):
    today     = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    if s['last_date'] != today:
        s['today']  = 0
        s['streak'] = (s['streak'] + 1) if s['last_date'] == yesterday else 1
        s['last_date'] = today
    s['total'] += 1
    s['today'] += 1


def big_time(mm, ss, color):
    time_str = f'{mm:02d}:{ss:02d}'
    rows = [''] * 7
    for ch in time_str:
        for i, col in enumerate(DIGITS.get(ch, DIGITS['0'])):
            rows[i] += col + '  '
    return '\n'.join(f'{color}{r}{RESET}' for r in rows)


def progress_bar(elapsed, total, color, width=42):
    filled = int(width * elapsed / total) if total else 0
    pct    = int(100 * elapsed / total)   if total else 0
    bar    = f'{color}{"█" * filled}{RESET}{"░" * (width - filled)}'
    return f'[{bar}] {pct:3d}%'


def clear():
    sys.stdout.write('\033[2J\033[H')
    sys.stdout.flush()


def bell():
    sys.stdout.write('\a')
    sys.stdout.flush()


def key_pressed():
    return bool(select.select([sys.stdin], [], [], 0)[0])


def drain():
    if key_pressed():
        sys.stdin.readline()


def draw(phase, color, remaining, duration, pomo_num, state):
    clear()
    mm, ss  = divmod(remaining, 60)
    elapsed = duration - remaining
    pad     = '  '

    print()
    if phase == 'FOCUS':
        print(f'{pad}{color}{BOLD}● {phase}{RESET}   {DIM}Pomodoro #{pomo_num}{RESET}')
    else:
        print(f'{pad}{color}{BOLD}◌ {phase}{RESET}   {DIM}step away, rest your eyes{RESET}')
    print()

    for line in big_time(mm, ss, color).split('\n'):
        print(f'{pad}{line}')

    print()
    print(f'{pad}{progress_bar(elapsed, duration, color)}')
    print()

    hot = ' ***' if state['streak'] >= 3 else ''
    print(f'{DIM}{pad}Today {state["today"]} sessions  |  '
          f'Streak {state["streak"]} days{hot}  |  '
          f'Total {state["total"]}{RESET}')
    print(f'\n{DIM}{pad}Enter → skip   Ctrl-C → quit{RESET}')


def run_phase(phase, duration, color, pomo_num, state):
    remaining = duration
    while remaining >= 0:
        draw(phase, color, remaining, duration, pomo_num, state)
        if key_pressed():
            drain()
            return True   # skipped
        time.sleep(1)
        remaining -= 1
    return False          # completed naturally


def main():
    state = load_state()
    if state.get('last_date') != date.today().isoformat():
        state['today'] = 0

    clear()
    hot = ' ***' if state['streak'] >= 3 else ''
    print(f'\n  {BOLD}{GREEN}Focus Timer{RESET}')
    print(f'  {DIM}25m focus · 5m break · 15m long break after 4 rounds{RESET}')
    print(f'\n  Streak {state["streak"]} days{hot}  |  '
          f'Total {state["total"]} sessions  |  Today {state["today"]}')
    print(f'\n  {DIM}Press Enter to start ...{RESET}')
    input()

    pomo_num = 0
    idx      = 0

    while True:
        phase, duration, color = CYCLE[idx % len(CYCLE)]
        if phase == 'FOCUS':
            pomo_num += 1

        try:
            skipped = run_phase(phase, duration, color, pomo_num, state)
        except KeyboardInterrupt:
            clear()
            print(f'\n  {BOLD}Stopped.{RESET}  '
                  f'Today {state["today"]}  |  Streak {state["streak"]}d  |  Total {state["total"]}\n')
            save_state(state)
            sys.exit(0)

        if not skipped and phase == 'FOCUS':
            record_session(state)
            save_state(state)
            bell()
            bell()
        elif not skipped:
            bell()

        clear()
        if not skipped:
            msg = 'Focus session complete!' if phase == 'FOCUS' else 'Break over.'
            print(f'\n  {color}{BOLD}{msg}{RESET}\n')
        else:
            print(f'\n  {DIM}Skipped.{RESET}\n')

        print(f'  {DIM}Press Enter for next phase ...{RESET}')
        try:
            input()
        except KeyboardInterrupt:
            clear()
            save_state(state)
            sys.exit(0)

        idx += 1


if __name__ == '__main__':
    main()
