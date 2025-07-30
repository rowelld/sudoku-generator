from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from math import ceil
import random
import copy

# -- Sudoku generation code (same as before) --
GRID_SIZE = 9
SUBGRID_SIZE = 3

def is_safe(grid, row, col, num):
    for x in range(GRID_SIZE):
        if grid[row][x] == num or grid[x][col] == num:
            return False
    start_row, start_col = row - row % SUBGRID_SIZE, col - col % SUBGRID_SIZE
    for i in range(SUBGRID_SIZE):
        for j in range(SUBGRID_SIZE):
            if grid[start_row + i][start_col + j] == num:
                return False
    return True

def solve_sudoku(grid):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if grid[row][col] == 0:
                for num in range(1, 10):
                    if is_safe(grid, row, col, num):
                        grid[row][col] = num
                        if solve_sudoku(grid):
                            return True
                        grid[row][col] = 0
                return False
    return True

def fill_diagonal(grid):
    for i in range(0, GRID_SIZE, SUBGRID_SIZE):
        fill_box(grid, i, i)

def fill_box(grid, row, col):
    nums = list(range(1, 10))
    random.shuffle(nums)
    for i in range(SUBGRID_SIZE):
        for j in range(SUBGRID_SIZE):
            grid[row + i][col + j] = nums.pop()

def remove_cells(grid, difficulty):
    levels = {'easy': 35, 'medium': 45, 'hard': 55}
    cells_to_remove = levels.get(difficulty, 45)
    attempts = cells_to_remove
    while attempts > 0:
        row = random.randint(0, GRID_SIZE - 1)
        col = random.randint(0, GRID_SIZE - 1)
        if grid[row][col] != 0:
            grid[row][col] = 0
            attempts -= 1
    return grid

def generate_sudoku(difficulty='medium'):
    grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    fill_diagonal(grid)
    solve_sudoku(grid)
    solution = copy.deepcopy(grid)
    puzzle = remove_cells(grid, difficulty)
    return puzzle, solution

# -- PDF Generation Part --

def draw_sudoku_grid(c, puzzle, x=72, y=760, cell_size=18):
    c.setFont("Helvetica", 9)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            xpos = x + col * cell_size
            ypos = y - row * cell_size
            c.rect(xpos, ypos - cell_size, cell_size, cell_size)

            if puzzle[row][col] != 0:
                c.drawCentredString(
                    xpos + cell_size / 2,
                    ypos - cell_size + cell_size * 0.3,
                    str(puzzle[row][col])
                )

    # Draw bold lines every 3 cells (for 3x3 boxes)
    c.setLineWidth(3)
    for i in range(0, GRID_SIZE + 1, 3):
        # Vertical
        c.line(x + i * cell_size, y,
               x + i * cell_size, y - cell_size * GRID_SIZE)
        # Horizontal
        c.line(x, y - i * cell_size,
               x + cell_size * GRID_SIZE, y - i * cell_size)
    c.setLineWidth(1)  # reset



def generate_pdf(filename="sudoku_book.pdf", total_puzzles=27):
    from math import ceil

    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("Helvetica", 10)
    width, height = A4

    puzzles_per_page = 6
    cell_size = 23
    margin_x = 57
    margin_y = 790
    x_spacing = 260
    y_spacing = 265
    cols  = 2
    difficulty = ['easy', 'medium', 'hard']

    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height / 2, "Sudoku Puzzle Book - Generated Puzzles")

    c.showPage()

    for i in range(len(difficulty)):
        # Step 1: Generate all puzzles and solutions first
        all_puzzles = []
        all_solutions = []
        for _ in range(total_puzzles):
            puzzle, solution = generate_sudoku(difficulty[i])
            all_puzzles.append(puzzle)
            all_solutions.append(solution)

        # Step 2: Draw puzzle pages
        for page_start in range(0, total_puzzles, puzzles_per_page):
            for i in range(page_start, min(page_start + puzzles_per_page, total_puzzles)):
                index_on_page = i % puzzles_per_page
                
                row = index_on_page // cols
                col = index_on_page % cols

                x = margin_x + col * x_spacing
                y = margin_y - row * y_spacing            

                c.drawString(x, y + 10, f"Puzzle {i + 1}")
                draw_sudoku_grid(c, all_puzzles[i], x=x, y=y, cell_size=cell_size)

            c.showPage()

        # Step 3: Draw solution pages
        for page_start in range(0, total_puzzles, puzzles_per_page):
            for i in range(page_start, min(page_start + puzzles_per_page, total_puzzles)):
                index_on_page = i % puzzles_per_page
                cols  = 2
                row = index_on_page // cols
                col = index_on_page % cols

                x = margin_x + col * x_spacing
                y = margin_y - row * y_spacing

                c.drawString(x, y + 10, f"Solution {i + 1}")
                draw_sudoku_grid(c, all_solutions[i], x=x, y=y, cell_size=cell_size)

            c.showPage()

    c.save()
    print(f"PDF saved with puzzles and solutions: {filename}")


# Run this to create the PDF
generate_pdf(filename="sudoku.pdf", total_puzzles=12)
# generate_pdf(filename="sudoku_medium.pdf", total_puzzles=36, difficulty='medium')
# generate_pdf(filename="sudoku_hard.pdf", total_puzzles=36, difficulty='hard')
