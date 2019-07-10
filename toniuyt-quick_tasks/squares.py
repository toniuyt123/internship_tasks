import math
from copy import deepcopy

def squares(grid, symbols):
    side = len(symbols)
    small_side = int(math.sqrt(side))

    solved = False
    extreme = False
    while not solved:
        solved = True
        found = False

        for i in range(side):
            for j in range(side):
                if grid[i][j] == '0':
                    solved = False

                    symbols_left = symbols[:]
                    for c in range(side):
                        #check row
                        symbols_left = check_symbol(symbols_left, grid[i][c])
                        #check col
                        symbols_left = check_symbol(symbols_left, grid[c][j])

                    #check small box
                    box_index = (int(i / small_side), int(j / small_side))
                    for row in range(small_side * box_index[0], small_side * box_index[0] + small_side):
                        for col in range(small_side * box_index[1], small_side * box_index[1] + small_side):
                            symbols_left = check_symbol(symbols_left, grid[row][col])


                    if len(symbols_left) == 1:
                        found = True
                        grid[i][j] = symbols_left[0]


                    if len(symbols_left) == 2 and extreme:
                        secondary = deepcopy(grid)
                        secondary[i][j] = symbols_left[1]
                        secondary = squares(secondary, symbols)
                        if not secondary:
                            grid[i][j] = symbols_left[0]
                        else:
                            return secondary
                        

                    if len(symbols_left) == 0:
                        return False

        if not found:
            extreme = True

    return grid

def check_symbol(symbols_left, symbol):
    if symbol != '0' and symbol in symbols_left:
        symbols_left.remove(symbol)
    return symbols_left

if __name__ == '__main__':
    try:
        n = int(input())
        if n < 2 or n > 3:
            raise ValueError('invalid data')

        square_side = n**2
        symbols = []
        grid = [['0' for j in range(square_side)] for i in range(square_side)]
        start_count = 0
        for i in range(square_side):
            row = input().split()
            for j in range(square_side):
                if row[j] != '0':
                    start_count += 1
                    grid[i][j] = row[j]
                    if row[j] not in symbols:
                        symbols.append(row[j])

        if start_count < square_side or start_count > square_side**2:
            raise ValueError('inavlid starting grid')
    
        solution = squares(grid, symbols)
        
        for row in solution:
            print(' '.join(row))
        
    except ValueError as e:
        print(e)