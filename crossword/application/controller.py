import tkinter as tk
import tkinter.messagebox as mb
import string
import queue
from crossword.application import view as _view
from crossword.application import model as _model
from crossword.network import custom
from crossword.settings import settings
from crossword.constants import *


# Logging
class Controller:

    def __init__(self):
        """Initialize a crossword controller, its network connection, and its
        sub-controllers."""
        # Queue and bindings
        self.queue = queue.Queue()
        self.bindings = {}

        # Get the player
        result = {}
        # Try to join
        logging.info("%s: starting join process", self)
        while True:
            # Try to join a server
            result = _view.join_dialog(result)
            if not result:
                logging.info("%s: cancelled join", self)
                quit()
            try:
                # Network connection
                self.connection = custom.CrosswordConnection(result["address"])
            except OSError:
                logging.error("%s: failed to connect to %s:%i", self, *result["address"])
                mb.showerror("Error", "Could not connect to server")
            else:
                logging.info("%s: connected to %s:%i", self, *result["address"])
                break

        result.pop("address")

        # Queue bindings
        self.bind(CLIENT_JOINED, self.on_client_joined)
        self.bind(PUZZLE_REQUESTED, self.on_puzzle_requested)
        self.bind(PUZZLE_UPDATED, self.on_puzzle_updated)
        self.bind(SERVER_UPDATED, self.on_server_updated)
        self.bind(CLIENT_UPDATED, self.on_client_updated)
        logging.info("%s: bound events", self)

        # Connection
        self.connection.queue(self.queue)
        self.connection.start()
        self.connection.emit(CLIENT_JOINED, result)
        logging.info("%s: started server handshake", self)

        # Main contents
        self.player = _model.PlayerModel(**result)
        self.players = []
        self.view = _view.View()
        self.model = None
        logging.info("%s: created models and view", self)

        # Sub-controllers
        self.header = HeaderController(self)
        self.puzzle = PuzzleController(self)
        self.clues = CluesController(self)
        logging.info("%s: created worker controllers", self)

        # Hide until ready
        self.view.hide()

    def __repr__(self):
        """Represent the controller as a string."""
        return "Controller"

    def reload(self):
        """Reload the controller."""
        self.header.reload()
        self.puzzle.reload()
        self.clues.reload()
        logging.info("%s: reloaded", self)

    def load(self, model: _model.PuzzleModel):
        """Load the controller."""
        self.model = model
        self.header.load()
        self.puzzle.load()
        self.clues.load()
        # Clues also needs to be loaded for this to work
        self.puzzle.select_cell(0, 0)
        logging.info("%s: load", self)

    def update(self):
        """Update the controller."""
        if not self.queue.empty():
            event, data = self.queue.get()
            function = self.bindings.get(event)
            if function is None:
                logging.error("%s: caught event '%s' with no binding", self, event)
            else:
                function(data)
        self.view.root.after(50, self.update)

    def main(self):
        """Run the old application."""
        self.update()
        logging.info("%s: starting runtime", self)
        self.view.main()
        self.connection.stop()

    def bind(self, event, function):
        """Bind a function to a network event."""
        self.bindings[event] = function

    def get_player(self, pid):
        """Get a player by his idea."""
        for player in [self.player] + self.players:
            if player.id == pid:
                return player

    def on_client_joined(self, data):
        """Called when a client joins the server."""
        logging.info("%s: client '%s' joined server", self, data[NAME])

    def on_server_updated(self, data):
        """Called when the server sends out updates."""
        for key in data:
            if key == CLIENTS:
                print("Received clients: ", data[CLIENTS])
                self.players = data[CLIENTS]
            elif key == ID:
                self.player.id = data[ID]
                self.view.root.title("Joined as %s" % self.player[NAME])
                self.view.show()
            else:
                logging.error("%s: received invalid server update '%s'", self, key)

    def on_puzzle_requested(self, data):
        """Called when the server requests a puzzle."""
        path = _view.puzzle_dialog()
        if not path:
            # If none is chosen, pass the request to the next client
            self.connection.emit(PUZZLE_PASSED, None)
            logging.info("%s: passed on the puzzle request", self)
        else:
            # Read the puzzle and send the raw data to the server
            with open(path, "rb") as file:
                data = file.read()
            self.connection.emit(PUZZLE_SUBMITTED, data)
            logging.info("%s: sent puzzle to the server", self)

    def on_puzzle_updated(self, data):
        """Called when the server updates the puzzle directly."""
        self.load(data)
        logging.info("%s: updated the puzzle", self)

    def on_client_updated(self, data):
        """Called when a client is updated."""
        pid, data = data
        player = self.get_player(pid)

        if not player:
            logging.error("%s: could not find player %s", self, str(pid))
            return

        for key in data:
            if key == POSITION:
                position = data[POSITION]
                player.x, player.y = position
            elif key == DIRECTION:
                direction = data[DIRECTION]
                player.direction = direction
            elif key == LETTER:
                letter = data[LETTER]
                x, y, letters = letter
                self.model.cells[x, y].letters = letters
                self.model.cells[x, y].owner = player.id
                self.puzzle.draw(self.model.cells[x, y])
            else:
                logging.error("%s: received an invalid key '%s' from client update", self, key)


class SubController:

    def __init__(self, parent: Controller):
        """Initialize a crossword sub-controller."""
        self.parent = parent

    @property  # This is a property because the model is not permanent
    def model(self):
        """Get the model of the controller."""
        return self.parent.model

    @property  # This is a property because I'm unsure of how it will work
    def players(self):
        """Get the player of the controller."""
        return self.parent.players

    @property
    def player(self):
        """Get the controller player."""
        return self.parent.player


class HeaderController(SubController):

    def __init__(self, parent: Controller):
        """Initialize a header controller."""
        super().__init__(parent)
        self.view = self.parent.view.header

    def __repr__(self):
        return "HeaderController"

    def load(self):
        """Load the header."""
        self.view.title.set(self.model.title)
        self.view.author.set(self.model.author)
        logging.info("%s: loaded the header view", self)

    reload = load


class PuzzleController(SubController):

    def __init__(self, parent: Controller):
        """Initialize the puzzle controller."""
        super().__init__(parent)
        self.view = self.parent.view.puzzle
        # Bindings
        self.view.canvas.bind("<Button-1>", self.on_left_click)
        self.view.canvas.bind("<BackSpace>", self.on_backspace)
        self.view.canvas.bind("<space>", self.on_space)
        self.view.canvas.bind("<Tab>", self.on_tab)
        self.view.canvas.bind("<Shift-Tab>", self.on_shift_tab)
        self.view.canvas.bind("<Left>", self.on_arrow)
        self.view.canvas.bind("<Right>", self.on_arrow)
        self.view.canvas.bind("<Up>", self.on_arrow)
        self.view.canvas.bind("<Down>", self.on_arrow)
        self.view.canvas.bind("<Key>", self.on_key)
        self.view.canvas.focus_set()

    def __repr__(self):
        """Represent the puzzle controller as a string."""
        return "PuzzleController"

    def load(self):
        """Load the puzzle."""
        d = settings.appearance.puzzle.bg
        e = settings.appearance.puzzle.highlight.empty
        for cell in self.model.cells:
            cell.update(fill=d if cell.kind == LETTER else e)
            self.draw(cell)
        logging.info("%s: loaded the puzzle view", self)

    reload = load

    def draw(self, model: (_model.CellModel, _model.WordModel, _model.PlayerModel), **options):
        """Draw a model on the puzzle view."""
        # Draw a cell model
        if isinstance(model, _model.CellModel):
            # Delete the previous drawings
            self.view.canvas.delete(*list(model.drawings))
            # Get size and position
            x, y = model.x, model.y
            s = settings.appearance.puzzle.cell.size
            bbox = (x*s, y*s, (x+1)*s, (y+1)*s)
            # Draw a rectangle
            model.drawings.box = self.view.canvas.create_rectangle(*bbox, fill=model.fill)
            # Draw the letters
            if model.letters:
                # Get the letters, position, font, and color
                h = s // 2 + 1
                pos = (x*s + h, y*s + h)
                letters = model.letters
                font = (settings.appearance.puzzle.font[0], int(s / (1.1 + 0.6*len(model.letters)))-3)
                player = self.parent.get_player(model.owner)
                color = settings.appearance.puzzle.fg if not player else player[COLOR]
                # Draw the letters
                model.drawings.letters = self.view.canvas.create_text(*pos, text=letters, font=font, fill=color)
            # Draw cell number
            if model.number:
                # Get position, number, and font
                pos = (x*s + NUMBER_PAD_LEFT, y*s + NUMBER_PAD_TOP)
                number = model.number
                font = (settings.appearance.puzzle.font[0], int(s / 3.5)-2)
                # Draw the number
                model.drawings.number = self.view.canvas.create_text(*pos, text=number, font=font, anchor=tk.W)
        # Draw a word by drawing each cell
        elif isinstance(model, _model.WordModel):
            for cell in model.cells:
                self.draw(cell)
        # Draw a player
        elif isinstance(model, _model.PlayerModel):
            # Ignore if the cell is empty
            cell = self.model.cells[model.x, model.y]
            if cell.kind == EMPTY:
                raise TypeError("Cannot select an empty cell")
            # Clear the current selection
            word = cell.word[model.direction]
            word.update(fill=settings.appearance.puzzle.bg)
            self.draw(word)
            # Change the fill of the word and selected cell
            if options.get("highlight") is not False:
                cell.word[model.direction].update(fill=settings.appearance.puzzle.highlight.word)
                cell.update(fill=settings.appearance.puzzle.highlight.letter)
            # Draw the word
            self.draw(cell.word[model.direction])

    def switch_direction(self):
        """Switch the direction of the player."""
        # Get the current cell and word
        cell = self.model.cells[self.player.x, self.player.y]
        word = cell.word[self.player.direction]
        word.update(fill=settings.appearance.puzzle.bg)
        # Draw the current word, switch the direction, and then draw the player
        self.draw(word)
        self.player.direction = [ACROSS, DOWN][self.player.direction == ACROSS]
        self.draw(self.player)
        # Change the clue and update the server
        self.parent.clues.set_clue(cell.word[self.player.direction])
        self.parent.connection.emit(CLIENT_UPDATED, {DIRECTION: self.player.direction})

    def select_cell(self, x: int, y: int):
        """Select a cell."""
        # Update and draw the player
        self.player.x, self.player.y = x, y
        self.draw(self.player)
        # Update the clues, change window focus, update server
        self.parent.clues.set_clue(self.model.cells[x, y].word[self.player.direction])
        self.view.canvas.focus_set()
        self.parent.connection.emit(CLIENT_UPDATED, {POSITION: (x, y)})

    def move_cell(self, distance: int=1, absolute: bool=False):
        """Move the current cell by a set distance."""
        # Set constants for access
        step = -1 if distance < 0 else 1
        across = self.player.direction == ACROSS
        down = self.player.direction == DOWN
        x, y = self.player.x, self.player.y
        # Move while not complete
        while distance != 0:
            x += step * across
            y += step * down
            # Fix bound issues
            while not (0 <= x < self.model.width and 0 <= y < self.model.height):
                # Bounding rules
                if x < 0:
                    x = self.model.width - 1
                    y = (y - (not absolute)) % self.model.height
                elif x >= self.model.width:
                    x = 0
                    y = (y + (not absolute)) % self.model.height
                elif y < 0:
                    y = self.model.height - 1
                    x = (x - (not absolute)) % self.model.width
                elif y >= self.model.height:
                    y = 0
                    x = (x + (not absolute)) % self.model.width
            # Subtract the step if the crossword cell is a letter cell
            if self.model.cells[x, y].kind == LETTER:
                distance -= step
        # Select a crossword cell
        self.select_cell(x, y)

    def move_word(self, count=1):
        """Move the currently selected word to the next in the list."""
        # Get the cell and direction
        cell = self.model.cells[self.player.x, self.player.y]
        direction = self.player.direction
        # Get the word index and add the count
        index = (self.model.words[direction].index(cell.word[direction]) + count)
        index %= len(self.model.words[direction])
        # Select a new cell
        cell = self.model.words[direction][index].cells[0]
        self.select_cell(cell.x, cell.y)

    def insert_letter(self, letter: str):
        """Insert a different letter in the currently selected cell."""
        # Change the owner
        cell = self.model.cells[self.player.x, self.player.y]
        cell.owner = self.player.id
        # If the letter is a space
        if letter == " ":
            cell.letters = ""
        # If the letter is lowercase change normally
        elif letter in string.ascii_lowercase:
            cell.letters = letter.upper()
        # Otherwise, add it
        elif letter in string.ascii_uppercase:
            cell.letters += letter.upper()
        # Update the server
        self.parent.connection.emit(CLIENT_UPDATED, {LETTER: (self.player.x, self.player.y,  cell.letters)})
        # Draw the cell
        self.draw(cell)

    def remove_letter(self):
        """Remove a letter from the current cell."""
        # Get the current cell
        cell = self.model.cells[self.player.x, self.player.y]
        # Remove a letter
        cell.letters = cell.letters[:-1]
        # Update the server
        self.parent.connection.emit(CLIENT_UPDATED, (self.player.x, self.player.y, cell.letters))
        # Draw the current cell
        self.draw(cell)

    def on_left_click(self, event):
        """Called when the user left clicks the puzzle."""
        # Get focus
        self.view.canvas.focus_set()
        # Efficiently access instance members
        s = settings.appearance.puzzle.cell.size
        x = (event.x - CANVAS_PAD - 1) // s
        y = (event.y - CANVAS_PAD - 1) // s
        cell = self.model.cells[x, y]
        # Ignore if the cell is empty
        if cell.kind == EMPTY:
            return
        # Change direction if the clicked cell is selected
        if (x, y) == (self.player.x, self.player.y):
            self.switch_direction()
        # Select the cell
        self.select_cell(x, y)

    def on_backspace(self, event):
        """Called when the user types backspace."""
        self.remove_letter()
        if settings.controls.behavior.on_backspace == "go to last cell":
            self.move_cell(-1)

    def on_space(self, event):
        """Called when the user types space."""
        on_space = settings.controls.behavior.on_space
        if on_space == "go to next cell":
            self.move_cell()
        elif on_space == "change direction":
            self.switch_direction()

    def on_tab(self, event):
        """Called when the user types tab."""
        self.move_word(1)
        return "break"

    def on_shift_tab(self, event):
        """Called when the user types shift tab."""
        self.move_word(-1)
        return "break"

    def on_arrow(self, event):
        """Called when the user types an arrow key."""
        # Get the arrow key behaviors
        on_arrow_key = settings.controls.behavior.on_double_arrow
        arrow_key_movement = settings.controls.behavior.on_arrow
        # Get the arrow key direction and distance
        direction = ACROSS if event.keysym in ACROSS_ARROWS else DOWN
        distance = -1 if event.keysym in NEGATIVE_ARROWS else 1
        # Switch direction
        if self.player.direction != direction:
            self.switch_direction()
            if on_arrow_key == "move in direction":
                self.move_cell(distance=distance, absolute=arrow_key_movement == "absolute")
        # Move otherwise
        elif on_arrow_key == "move in direction":
            self.move_cell(distance=distance, absolute=arrow_key_movement == "absolute")

    def on_key(self, event):
        """Called when the user types a key."""
        # If the key is a letter
        if event.keysym in string.ascii_letters:
            self.insert_letter(event.keysym)
            # Move on lowercase letter
            if event.keysym in string.ascii_lowercase:
                self.move_cell()


class CluesController(SubController):

    def __init__(self, parent: Controller):
        """Initialize the clues controller."""
        super().__init__(parent)
        # Get the view
        self.view = self.parent.view.clues
        # Bind controls
        self.view.across_listbox.bind("<Button-1>", self.on_across_left_click)
        self.view.down_listbox.bind("<Button-1>", self.on_down_left_click)

    def load(self):
        """Load the clues controller widget."""
        self.view.across.set(list(map(lambda word: word.clue, self.model.words.across)))
        self.view.down.set(list(map(lambda word: word.clue, self.model.words.down)))

    reload = load

    def set_clue(self, word):
        """Set the current clue based on a word."""
        if word in self.model.words.across:
            self.view.across_listbox.selection_clear(0, tk.END)
            index = self.model.words.across.index(word)
            self.view.across_listbox.selection_set(index)
            self.view.across_listbox.see(index)
        else:
            self.view.down_listbox.selection_clear(0, tk.END)
            index = self.model.words.down.index(word)
            self.view.down_listbox.selection_set(index)
            self.view.across_listbox.see(index)

    def on_across_left_click(self, event):
        """Called when the user left clicks on the across list."""
        index = self.view.across_listbox.nearest(event.y)
        cell = self.model.words.across[index].cells[0]
        if self.player.direction != ACROSS:
            self.parent.puzzle.switch_direction()
        self.parent.puzzle.select_cell(cell.x, cell.y)

    def on_down_left_click(self, event):
        """Called when the user left clicks on the down list."""
        index = self.view.down_listbox.nearest(event.y)
        cell = self.model.words.down[index].cells[0]
        if self.player.direction != DOWN:
            self.parent.puzzle.switch_direction()
        self.parent.puzzle.select_cell(cell.x, cell.y)
