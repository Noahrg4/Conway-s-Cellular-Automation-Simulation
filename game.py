import copy
import pygame
import pygame_gui
import random

# Constant for board size.  GUI is optimized for 20.
SIZE = 20


class Game:
    """Game handles the core loop (events, updating, and drawing).  Game keeps an instance of a Board
    that is the world the cells "live" in.  All operations that directly modify the world are encapsulated
    in Board.  Game layout is not flexible; it is optimized for a 20x20 world.
    """

    def __init__(self):
        # A Board is the cells' world
        self._board = Board(SIZE)
        # We will represent a cell with a rectangle from the pygame library.  This function
        # creates them.
        self._rects = self.__make_rects__()
        # Startup pygame
        pygame.init()
        # Create a screen
        self._screen = pygame.display.set_mode([1024, 768])
        pygame.display.set_caption('Life')
        # GUI manager manages buttons, labels, sliders, etc.
        self._manager = pygame_gui.UIManager((1024, 768), "theme.json")
        # Create a play/pause button
        self._play_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((700, 75), (100, 50)),
                                                         text='Paused',
                                                         manager=self._manager)
        # Create a label for the generation number
        self._generations_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((700, 150), (250, 50)),
                                                              text='Generations: 0',
                                                              manager=self._manager)
        # Create a button for random board layout
        self._random_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((700, 225), (250, 50)),
                                                              text='Randomize',
                                                              manager=self._manager)
        # Create a button to reset generations and the world
        self._reset_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((700, 300), (250, 50)),
                                                              text='Reset',
                                                              manager=self._manager)
        # Create a label for the speed slider
        self._speed_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((700, 375), (250, 50)),
                                                              text='Speed: 250ms',
                                                              manager=self._manager)
        # Create a slider to control sim speed
        self._speed_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((700, 450), (250, 50)),
                                                                    start_value=250,
                                                                    value_range=(0, 1000),
                                                                    manager=self._manager)
        # Track if the simulation is running or not
        self._running = False
        # Track if the application should be finished and close
        self._finished = False
        # Number of generations
        self._generations = 0
        # Default delay in milliseconds (ms)
        self._delay = 250

    def loop(self):
        """Main simulation loop.  Checks for events and handles them.  Updates world accordingly.  Redraws
        world.  Starts over if no QUIT event has occurred.  Notice that _delay is a blocking delay; it
        will make the GUI less responsive.  It shouldn't be too hard to change this, but I didn't really care
        that much.
        """

        # Keep a clock for frame limiting
        clock = pygame.time.Clock()
        # Keep going until this changes; will change when a user clicks the close button.
        while not self._finished:
            # Ensure 60 frames per second
            time_delta = clock.tick(60)/1000.0
            # Ask pygame for events
            for event in pygame.event.get():
                # If window close event happens, set _finished to True
                if event.type == pygame.QUIT:
                    self._finished = True
                # Left mouse click events
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Find coordinate of click
                    coords = pygame.mouse.get_pos()
                    # See if that coordinate is in a cell.  If it is, this function returns which one.
                    i, j, rectangle = self.__select_rectangle__(coords)
                    # If function returned None it means we didn't click a cell
                    if rectangle is not None:
                        # We clicked a cell.  Change its color.
                        self._board.change_color(i, j)
                # Did the user click a button?  If so, figure out which and call the
                # appropriate function.
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self._play_button:
                        self.toggle()
                    if event.ui_element == self._reset_button:
                        self.reset()
                    if event.ui_element == self._random_button:
                        self.randomize()
                # Speed slider moved.  Update the label.
                if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    self._speed_label.set_text("Speed: " + str(self._speed_slider.get_current_value()) + "ms")
                    self._delay = int(self._speed_slider.get_current_value())
                # Have the GUI manager handle GUI events
                self._manager.process_events(event)

            # Let the GUI manager know the time change since last frame
            self._manager.update(time_delta)
            # If we aren't paused, calculate the next generation
            if self._running:
                # Cell updates happen in the Board class.  Call it.
                self._board.update()
                # Increment generations.
                self._generations = self._generations + 1
                # Update generations label
                self._generations_label.set_text("Generations: " + str(self._generations))
                # Wait to delay.  Not the best method, but eh.
                pygame.time.wait(self._delay)

            # Fill the screen with white
            self._screen.fill((255, 255, 255))
            # Redraw the world
            self.__draw_board__()
            # Redraw the GUI elements
            self._manager.draw_ui(self._screen)
            # Flip buffers
            pygame.display.update()

        # Loop is over (user clicked quit).  Shutdown pygame.
        pygame.quit()

    def reset(self):
        """Set the simulation back to its starting point values (blank world, zero generations)."""

        self._board = Board()
        self._generations = 0

    def randomize(self):
        """Create a random world.  Would be neat to expand it to accept values for density of cells,
        but I didn't want to today.  Fill level at about 20% works pretty well."""

        self._board = Board()
        for i in range(SIZE):
            for j in range (SIZE):
                if random.randint(1, 100) <= 20:
                    self._board.change_color(i, j)

    def toggle(self):
        """Play/pause the sim."""

        self._running = not self._running
        if self._running:
            self._play_button.set_text("Running")
        else:
            self._play_button.set_text("Paused")

    def __select_rectangle__(self, coords: [int, int]) -> (int, int, pygame.Rect):
        """Given a set of coordinates, determine if they lie in one of our rectangles
        that represent our cells.  If so, return coordinates and the rectangle.  Otherwise
        return a triple of None."""

        for i in range(SIZE):
            for j in range(SIZE):
                if self._rects[i][j].collidepoint(coords):
                    return i, j, self._rects[i][j]
        return None, None, None

    def __make_rects__(self):
        """Make and return an SIZE x SIZE list of pygame Rectangles.  These will be
        used to visually represent our cells."""

        rectangles = []
        for i in range(SIZE):
            rectangles.append([])
            for j in range(SIZE):
                rectangles[i].append(pygame.Rect(i * 34, j * 34, 32, 32))
        return rectangles

    def __draw_board__(self):
        """Loop over the board and draw each rectangle with the appropriate color."""

        board = self._board.get_board()
        for i in range(SIZE):
            for j in range(SIZE):
                pygame.draw.rect(self._screen, board[i][j], self._rects[i][j])

# Write your code to complete the project below this line.
