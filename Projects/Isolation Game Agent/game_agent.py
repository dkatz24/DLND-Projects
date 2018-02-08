"""Finish all TODO items in this file to complete the isolation project, then
test your agent's strength against a set of known agents using tournament.py
and include the results in your report.
"""
import random


class SearchTimeout(Exception):
    """Subclass base exception for code clarity. """
    pass


def opp_diff(game, player):
    """
    Heuristic evaluation function that calculates the difference between the number of legal moves available
    to our player and the number legal moves available to our opponent

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    # Check for win/loss
    if game.is_winner(player):
        return float('inf')
    elif game.is_loser(player):
        return float('-inf')

    # Heuristic evaluation
    return float(len(game.get_legal_moves(player)) - len(game.get_legal_moves(game.get_opponent(player))))


def opp_diff_defensive(game, player):
    """
    Similar mathematical structure to opp_diff, except the number of legal moves available to our player is weighted by a
    factor of theta (> 1), giving our agent a defensive orientation

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    # Check for win/loss
    if game.is_winner(player):
        return float('inf')
    elif game.is_loser(player):
        return float('-inf')

    # Initialize variable for heuristic evaluation
    player_moves = game.get_legal_moves(player)
    opponent_moves = game.get_legal_moves(game.get_opponent(player))
    theta = 2

    # Heuristic evaluation
    return float(theta * len(player_moves) - len(opponent_moves))


def opp_diff_aggressive(game, player):
    """
    Similar mathematical structure to opp_diff, except the number of legal moves available to our opponent is weighted by
    a factor of 'theta' (> 1), giving our agent an aggressive orientation

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    # Check for win/loss
    if game.is_winner(player):
        return float('inf')
    elif game.is_loser(player):
        return ('-inf')

    # Initialize variable for heuristic evaluation
    player_moves = game.get_legal_moves(player)
    opponent_moves = game.get_legal_moves(game.get_opponent(player))
    theta = 2

    # Heuristic evaluation
    return float(len(player_moves) - theta * len(opponent_moves))


def opp_diff_decay(game, player):
    """
    Similar mathematical structure to opp_diff aggressive / defensive variations, except we incorporate a "game_ratio"
    variable that reflects how much of the game has been completed.  In the beginning of the game, our player puts
    more value on its own mobility; however, as the game progresses, the player becomes more aggressive in limiting
    its opponents moves.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    # Check for win/loss
    if game.is_winner(player):
        return float('inf')
    elif game.is_loser(player):
        return float('-inf')

    # Initialize variables for heuristic evaluation
    player_moves = len(game.get_legal_moves(player))
    opponent_moves = len(game.get_legal_moves(game.get_opponent(player)))
    game_ratio = float(((game.height * game.width) - len(game.get_blank_spaces())) / (game.height * game.width))
    theta = 3

    # Heuristic evaluation
    return float(((1 - game_ratio) * theta * player_moves) - (game_ratio * opponent_moves))


def custom_score(game, player):
    """
    This is the best performing heuristic:

    Oppositional Difference Between Open Moves - Forward-Thinking Orientation

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    return opp_diff_defensive(game, player)


def custom_score_2 (game, player):
    return opp_diff(game, player)


def custom_score_3 (game, player):
    return opp_diff_decay(game, player)

class IsolationPlayer:
    """Base class for minimax and alphabeta agents -- this class is never
    constructed or tested directly.

    ********************  DO NOT MODIFY THIS CLASS  ********************

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """
    def __init__(self, search_depth=3, score_fn=custom_score, timeout=10.):
        self.search_depth = search_depth
        self.score = score_fn
        self.time_left = None
        self.TIMER_THRESHOLD = timeout


class MinimaxPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using depth-limited minimax
    search. You must finish and test this player to make sure it properly uses
    minimax to return a good move before the search time limit expires.
    """

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left

        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout
        best_move = (-1, -1)

        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            return self.minimax(game, self.search_depth)

        except SearchTimeout:
            pass  # Handle any actions required after timeout as needed

        # Return the best move from the last completed search iteration
        return best_move

    def minimax(self, game, depth):
        """
        Implement depth-limited minimax search algorithm as described in
        the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        """

        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        # Record all legal moves available to our player
        legal_moves = game.get_legal_moves()

        # If no legal moves are available, return (-1, -1)
        if not legal_moves:
            return (-1, -1)

        # Initialize best_score and best_move
        best_score = float('-inf')
        best_move = legal_moves[0]

        for move in legal_moves:
            future_state = game.forecast_move(move)
            score = self.min_play(future_state, depth - 1)
            if score > best_score:
                best_score = score
                best_move = move

        return best_move


    def min_play(self, future_state, depth):
        """
        Minimizing player in minimax game

        Parameters
        ----------
        future_state : isolation.Board
            An instance of the Isolation game `Board` class representing a
            future game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        Returns
        -------
        lowest_score : int
            An integer reflecting the lowest score of a forecasted move
            given the evaluation function custom_score
        """

        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        legal_moves = future_state.get_legal_moves()
        lowest_score = float('inf')

        # Base case for recursion in depth-limited search- return score of current position
        if depth == 0 or not legal_moves:
            return self.score(future_state, self)

        for move in legal_moves:
            future_state_min = future_state.forecast_move(move)
            lowest_score = min(lowest_score, float(self.max_play(future_state_min, depth - 1)))

        return lowest_score


    def max_play(self, future_state, depth):
        """
        Maximizing player in minimax game

        Parameters
        ----------
        future_state : isolation.Board
            An instance of the Isolation game `Board` class representing a
            future game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        Returns
        -------
        highest_score : int
            An integer reflecting the highest score of a forecasted move
            given the evaluation function custom_score
        """

        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        legal_moves = future_state.get_legal_moves()
        highest_score = float('-inf')

        # Base case for recursion in depth-limited search- return score of current position
        if depth == 0 or not legal_moves:
            return self.score(future_state, self)

        for move in legal_moves:
            future_state_max = future_state.forecast_move(move)
            highest_score = max(highest_score, float(self.min_play(future_state_max, depth - 1)))

        return float(highest_score)


class AlphaBetaPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using iterative deepening minimax
    search with alpha-beta pruning. You must finish and test this player to
    make sure it returns a good move before the search time limit expires.
    """

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """

        self.time_left = time_left

        legal_moves = game.get_legal_moves(self)

        if not legal_moves:
            return (-1, -1)

        best_move = legal_moves[0]

        # The try/except block will automatically catch the exception
        # raised when the timer is about to expire.
        depth = 1
        try:
            while True:
                best_move = self.alphabeta(game, depth)
                depth += 1

        except SearchTimeout:
            pass  # Handle any actions required after timeout as needed

        # Return the best move if maximum depth reached
        return best_move

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf")):
        """Implement depth-limited minimax search with alpha-beta pruning as
        described in the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves
        """

        # Make sure we return move before time runs out
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        # Record all legal moves available to our player
        legal_moves = game.get_legal_moves()

        # If no legal moves are available, return (-1, -1)
        if not legal_moves:
            return (-1, -1)

        # Initialize best_score and best_move
        best_score = float('-inf')
        best_move = legal_moves[0]

        for move in legal_moves:
            future_state = game.forecast_move(move)
            score = self.ab_min_play(future_state, depth - 1, alpha, beta)

            if score > beta:
                return move
            alpha = max(alpha, score)

            if score > best_score:
                best_score = score
                best_move = move

        return best_move


    def ab_min_play(self, future_state, depth, alpha, beta):
        """
        Minimizing player in minimax game with alphabeta pruning

        Parameters
        ----------
        future_state : isolation.Board
            An instance of the Isolation game `Board` class representing a
            future game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        Returns
        -------
        lowest_score : int
            An integer reflecting the lowest score of a forecasted move
            given the evaluation function custom_score
        """

        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        legal_moves = future_state.get_legal_moves()
        lowest_score = float('inf')

        # Base case for recursion in depth-limited search - return score of current position
        if depth == 0 or not legal_moves:
            return self.score(future_state, self)

        for move in legal_moves:
            future_state_min = future_state.forecast_move(move)
            lowest_score = min(lowest_score, float(self.ab_max_play(future_state_min, depth - 1, alpha, beta)))

            beta = min(beta, lowest_score)

            if beta <= alpha:
                break

        return beta


    def ab_max_play(self, future_state, depth, alpha, beta):
        """
        Maximizing player in minimax game

        Parameters
        ----------
        future_state : isolation.Board
            An instance of the Isolation game `Board` class representing a
            future game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        Returns
        -------
        highest_score : int
            An integer reflecting the highest score of a forecasted move
            given the evaluation function custom_score
        """

        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        legal_moves = future_state.get_legal_moves()
        highest_score = float('-inf')

        # Base case for recursion in depth-limited search - return score of current position
        if depth == 0 or not legal_moves:
            return self.score(future_state, self)

        for move in legal_moves:
            future_state_max = future_state.forecast_move(move)
            highest_score = max(highest_score, float(self.ab_min_play(future_state_max, depth - 1, alpha, beta)))

            alpha = max(alpha, highest_score)

            if alpha >= beta:
                break

        return alpha
