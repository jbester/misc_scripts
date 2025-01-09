Order.py
-----

A Python script that uses ncurses to provide a simple text-based interface
to bulk renaming and prefixing files.

Example usage: you may have a list of pdfs which are named by chapter.  This will allow you to order the chapters then bulk insert a numeric prefix (e.g. 001, 002).

Features:

 - Keyboard Navigation: Use the Up and Down, j/k arrow keys to select a file
 - Use J/K to move the current file up or down in order
 - Repostion - Press Space (or Enter) once to select a file,  use j/k or up down to select a new position, press space again to move the file to that position
 - Rename: Press r to open a rename prompt for the currently highlighted file. You can edit its name, then press Enter to confirm and rename on the actual filesystem (via os.rename), or press Esc (or **Ctrl-G`) to cancel.
 - S - strip a regex from the filenames
 - x - bulk add the specified prefix
