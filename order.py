#!/usr/bin/env python3

import curses
import sys
import os
import math
import re

def draw_menu(stdscr, items, current_idx, first_selection, message=""):
    """
    Draws the list of items to the stdscr window.
    Highlights the current selection with reverse video.
    If `first_selection` is set, it will be indicated as well.
    `message` can be used to show a status/error message at the bottom.
    """
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    for idx, item in enumerate(items):
        display_text = item
        if idx == first_selection:
            # Mark the first selected item differently (e.g., prefix with '* ')
            display_text = f"* {display_text}"

        if idx == current_idx:
            # Highlight the current row
            stdscr.addstr(idx, 0, display_text, curses.A_REVERSE)
        else:
            stdscr.addstr(idx, 0, display_text)

    help_text = (
        "Up/Down or j/k to move cusor | J/K to move up down | Space/Enter to select/move | x to bulk enumerate | r to rename | S to Strip pattern | q to quit"
    )
    stdscr.addstr(h - 2, 0, help_text[: w - 1])

    # Show any status/error message on the last line
    stdscr.addstr(h - 1, 0, message[: w - 1])
    stdscr.clrtoeol()

    stdscr.refresh()

def prompt_user(stdscr, prompt, default_value):
    """
    Prompts the user for input.
    Returns:
      - The input if user confirms with Enter
      - None if the user cancels
    """
    curses.curs_set(1)  # Show the cursor while editing
    h, w = stdscr.getmaxyx()

    # Start with the old_name as default text
    buffer = list(default_value)
    cursor_pos = len(buffer)

    # We'll draw this prompt on the last line
    # For multi-line safety, we do h - 1
    prompt_y = h - 1
    prompt_x = 0

    while True:
        # Clear the line for fresh prompt
        stdscr.move(prompt_y, 0)
        stdscr.clrtoeol()

        # Show prompt + typed text
        display_text = prompt + "".join(buffer)
        stdscr.addstr(prompt_y, prompt_x, display_text)

        # Position the cursor after the typed text
        stdscr.move(prompt_y, prompt_x + len(prompt) + cursor_pos)
        stdscr.refresh()

        key = stdscr.getch()

        if key in (curses.KEY_ENTER, 10, 13):
            # Enter pressed: confirm
            value = "".join(buffer).strip()
            curses.curs_set(0)
            if value:
                return value
            else:
                return None
        elif key == 1: # Ctrl-A (Start of line)
            cursor_pos = 0
        elif key == 4: # Ctrl-D (Delete)
            if len(buffer) > 0:
                buffer.pop(cursor_pos)
        elif key == 5: # Ctrl-E (End)
            cursor_pos = len(buffer) - 1
        elif key in (27, 3, 7):
            # Esc (27), Ctrl-C (3), Ctrl-G (7) => Cancel
            curses.curs_set(0)
            return None
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            # Backspace
            if cursor_pos > 0:
                buffer.pop(cursor_pos - 1)
                cursor_pos -= 1
        elif key in (2, curses.KEY_LEFT):
            if cursor_pos > 0:
                cursor_pos -= 1
        elif key in (6, curses.KEY_RIGHT):
            if cursor_pos < len(buffer):
                cursor_pos += 1
        elif 32 <= key <= 126:
            # Printable ASCII range
            buffer.insert(cursor_pos, chr(key))
            cursor_pos += 1
        else:
            # Ignore other keys
            pass


def main(stdscr, files):
    curses.curs_set(0)  # Initially hide the cursor
    current_idx = 0     # The row currently highlighted
    first_selection = None  # Index of first selected item for swapping
    message = ""

    # Main loop
    while True:
        draw_menu(stdscr, files, current_idx, first_selection, message)
        message = ""  # Clear message after each draw

        key = stdscr.getch()

        if key == curses.KEY_UP or key == ord('k'):
            current_idx = (current_idx - 1) % len(files) if files else 0
        elif key == curses.KEY_DOWN or key == ord('j'):
            current_idx = (current_idx + 1) % len(files) if files else 0
        elif key in (27, 3, 7):
            first_selection = None
        elif key == ord('K'):
            old_idx = current_idx
            current_idx = (current_idx - 1) % len(files) if files else 0
            files[old_idx], files[current_idx] = (
                files[current_idx],
                files[old_idx],
            )
            if current_idx == first_selection:
                first_selection = min(first_selection+1, len(files)-1)
        elif key == ord('J'):
            old_idx = current_idx
            current_idx = (current_idx + 1) % len(files) if files else 0
            files[old_idx], files[current_idx] = (
                files[current_idx],
                files[old_idx],
            )
            if current_idx == first_selection:
                first_selection = max(first_selection-1, 0)
        elif key in (curses.KEY_ENTER, 10, 13, ord(' ')):
            # Space or Enter
            if first_selection is None:
                # Mark the first selected item
                first_selection = current_idx
            else:
                if first_selection != current_idx:
                    selected_value = files[first_selection]
                    files.pop(first_selection)
                    files.insert(current_idx, selected_value)
                first_selection = None
        elif key in (3, ord('q'), ord('Q')):
            return None
        elif key in (ord('x'), ord('X')):
            pattern = f'%0{math.ceil(math.log(len(files), 10))}d'
            pattern = prompt_user(stdscr, "Rename prefix: ", pattern)
            return pattern
        elif key == ord('S'):
            pattern = prompt_user(stdscr, f"Strip pattern: ", r'^')
            count = 0
            for i, v in enumerate(files):
                new_name = re.sub(pattern, '', v)
                if new_name != v:
                    os.rename(v, new_name)
                    files[i] = re.sub(pattern, '', v)
                    count += 1
            message = f"Renamed {count} files"
        elif key == ord('r'):
            # Rename the currently highlighted file
            old_name = files[current_idx]
            new_name = prompt_user(stdscr, f"Rename '{old_name}': ", old_name)
            if new_name and new_name != old_name:
                # Try renaming on the filesystem
                try:
                    os.rename(old_name, new_name)
                    files[current_idx] = new_name
                    message = f"Renamed '{old_name}' to '{new_name}'"
                except Exception as e:
                    message = f"Error: {e}"
            # else: either canceled or empty => do nothing


if __name__ == "__main__":
    files = sys.argv[1:]
    if not files:
        print("Usage: python order.py [FILE1] [FILE2] ...")
        sys.exit(1)

    pattern = curses.wrapper(main, files)
    if pattern is not None:
        # Once the user quits, 'files' may have been reordered
        for i, f in enumerate(files):
            new_name = f"{pattern%(i+1)} {f}"
            os.rename(f, new_name)
