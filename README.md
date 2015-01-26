Crossword
=========

About
-----
Crossword is a local network multiplayer crossword application. It is written in vanilla Python 3.

Controls
--------
* **Left click on cell** - selects the cell and highlights the word
* **Right click on cell** - spawn the options menu for the cell, word, and board
* **Repeated click on selected cell** - switches the highlight direction
* **Click on clue** - selects the first letter of the corresponding word and highlights the word
<br><br>
* **Arrow keys** - move the current selection
* **Type letter** - insert the letter into the selected cell and move to the next
* **Shift and type letter** - appends the letter to the contents of the cell for rebus mode
* **Space** - remove the letter from the cell and move forward
* **Backspace** - remove the letter from the cell and move back

Mechanics
---------
* When the user clicks on the chat entry the focus is switched to it
* The user must click on the board to switch focus back to it before being able to select cells
* When the user enters a letter the end of a word the selection will go to the first letter of the next word
* When the user backspaces at the beginning of the word it will go to the last letter of the previous word
* Behavior at word changes can be changed in the settings file