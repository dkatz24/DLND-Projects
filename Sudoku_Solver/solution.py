assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'
reversed_cols = cols[::-1]

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s + t for s in A for t in B]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
col_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
diagonal_units = [[r + c for r, c in zip(rows, cols)], [r + c for r, c in zip(rows, reversed_cols)]]

unit_list = row_units + col_units + square_units + diagonal_units

units = dict((s, [u for u in unit_list if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)

#print(units)
#print(peers)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values

    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def make_dictionary(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    values = []
    all_digits = '123456789'
    grid = list(grid)

    for char in grid:
        if char == '.':
            values.append(all_digits)
        elif char in all_digits:
            values.append(char)

    #print(len(values))
    assert len(values) == 81

    g_dict = (dict(zip(boxes, values)))

    return g_dict

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    print(values)
    width = 1 + max(len(values[square]) for square in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)

    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF' : print(line)

    print()
    print

def eliminate(values):
    """
        Iterate through all boxes and whenever there is a box with a single value,
        eliminate that value from its peers.
        Args:
            Sudoku in dictionary form.
        Returns:
            Reduced sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]

    for box in solved_values:
        digit = values[box]

        for peer in peers[box]:
            values[peer] = values[peer].replace(digit, '')

    return values

def only_choice(values):
    """
    Iterate through all units, and if there is a unit with only one possible value left,
    assign the value to this box.
    Args:
        Sudoku in dictionary form.
    Returns:
        Reduced sudoku in dictionary form.
    """
    for unit in unit_list:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values = assign_value(values, dplaces[0], digit)

    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        the values dictionary with the naked twins eliminated from peers
    """

    no_more_twins = False
    while not no_more_twins:

        board_before = values

        for unit in unit_list:
            maybe_naked = {}
            naked_count = 1

            for box in unit:
                if len(values[box]) == 2:
                    for label, possibilities in maybe_naked.items():
                        if possibilities == values[box]:
                            naked_count += 1
                            naked_values = list(possibilities)
                            naked_twins = [label, box]
                    maybe_naked[box] = values[box]

            if naked_count == 2:
                #print()
                #print(naked_values)
                #print()
                for box in unit:
                    if (box != naked_twins[0]) and (box != naked_twins[1]):
                        #print(values[box])
                        values[box] = values[box].replace(naked_values[0], '')
                        values[box] = values[box].replace(naked_values[1], '')
                        #print(values[box])

            naked_count = 1

        board_after = values
        if board_before == board_after:
            no_more_twins = True
    return values

def reduce_puzzle(values):
    """
       Reduces sudoku grid using constraint propagation of
       eliminate, only_choice, and naked_twins
       Args:
           values: a sudoku grid in dictionary form
       Returns:
           The dictionary representation of the reduced sudoku grid. False if no solution exists.
       """
    solved_values = [box for box in values.keys()]

    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)

        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])

        stalled = solved_values_before == solved_values_after
        # sanity check - no box should ever have zero possibilities unless unsolvable
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values

def search(values):
    """
    Reduces sudoku grid using constraint propagation (reduce puzzle)
    then tests values for squares with fewest possible values remaining
    Args:
        values: a sudoku grid in dictionary form
    Returns:
        The dictionary representation of the solved sudoku grid. False if no solution exists.
    """

    values = reduce_puzzle(values)

    if values == False:
        return False # previous failed test

    if all(len(values[s]) == 1 for s in boxes):
        print("Solved!")
        return values # puzzle solved :)

    # choose square to search with fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)

    # use recurrence to solve each of the resulting sudokus - if it returns a value (i.e. not False), return that answer
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    sudoku_grid = make_dictionary(grid)
    solved_sudoku = search(sudoku_grid)

    return solved_sudoku

if __name__ == '__main__':
    diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'

    diag_sudoku_solved = solve(diag_sudoku_grid)
    #print(type(diag_sudoku_grid))
    display(diag_sudoku_solved)

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
