import math

def squares(grid, symbols):
    side = len(symbols)
    small_side = int(math.sqrt(side))

    solved = False

    while not solved:
        solved = True
        for i in range(side):
            for j in range(side):
                if grid[i][j] == '0':
                    solved = False

                    symbols_left = symbols[:]
                    for c in range(side):
                        #check row
                        col_symbol = grid[i][c]
                        if col_symbol != '0' and col_symbol in symbols_left:
                            symbols_left.remove(col_symbol)

                        #check col
                        row_symbol = grid[c][j]
                        if row_symbol != '0' and row_symbol in symbols_left:
                            symbols_left.remove(row_symbol)

                    #print(symbols_left)
                    #check small box
                    box_index = (int(i / small_side), int(j / small_side))
                    for row in range(small_side * box_index[0], small_side * box_index[0] + small_side):
                        for col in range(small_side * box_index[1], small_side * box_index[1] + small_side):
                            symbol = grid[row][col]
                            if symbol != '0' and symbol in symbols_left:
                                symbols_left.remove(symbol)

                    #print(i,j)
                    print(symbols_left)
                    if len(symbols_left) == 1:
                        grid[i][j] = symbols_left[0]

    return grid

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

'''
2
0 0 # $
0 0 0 0
* 0 0 0
0 # 0 5


3 
B Y 0 0 P 0 0 0 0
L 0 0 R E B 0 0 0
0 E W 0 0 0 0 L 0 
W 0 0 0 L 0 0 0 Y 
G 0 0 W 0 Y 0 0 R 
P 0 0 0 O 0 0 0 L 
0 L 0 0 0 0 O W 0 
0 0 0 G R E 0 0 B
0 0 0 0 W 0 0 P E
'''