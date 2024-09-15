import pygame
import sys
from model import *

if __name__ == "__main__":
    BOARD_ROWS = 3
    BOARD_COLS = 3
    BOARD_SIZE = BOARD_ROWS * BOARD_COLS


#init game UI
    pygame.init()
    width, height = 620, 620
    screen = pygame.display.set_mode((width, height))

    clock = pygame.time.Clock()

    BACKGROUND_PANEL = (112, 128, 144)
    background_panel = (0, 0, width, height)
    CELL_COLOR = (255, 245, 238)

    symbol_height = 150
    symbol_width = 150

    symbol_x = pygame.image.load("./assets/x.png")
    symbol_o = pygame.image.load("./assets/o.png")

    symbol_x = pygame.transform.scale(symbol_x, (symbol_width, symbol_height))
    symbol_o = pygame.transform.scale(symbol_o, (symbol_width, symbol_height))

    cells = []
    cell_vals = [-1, -1, -1, -1, -1, -1, -1, -1, -1]

    for i in range (0, 3):
        cell_width = (width - 20) // 3
        cell_height = (height - 20) // 3
        for j in range(0, 3):
            cell = pygame.Rect(j * (cell_width + 5) + 5, i * (cell_height + 5) + 5, cell_width, cell_height)
            cells.append(cell)
            
            
    #initialize the game
    player1 = HumanPlayer()
    player2 = Player(epsilon=0)
    judger = Judger(player1, player2)
    player2.load_policy()

    alternator = judger.alternate()
    judger.reset()
    current_state = State()
    judger.p1.set_state(current_state)
    judger.p2.set_state(current_state)

    human_turn = True
    is_end = False
     
    # game loop
    running = True
    while running:
        pygame.draw.rect(screen, BACKGROUND_PANEL, background_panel)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if human_turn and not is_end:
                    x, y = pygame.mouse.get_pos()
                    for index, cell in enumerate(cells):
                        if cell.collidepoint((x, y)):
                            if (cell_vals[index] == -1):
                                cell_vals[index] = 1
                                #next turn
                                i = index // BOARD_COLS
                                j = index % BOARD_COLS
                                symbol = player1.symbol
                                next_state_hash = current_state.next_state(i, j, symbol).hash()
                                current_state, is_end = all_states[next_state_hash]
                                judger.p1.set_state(current_state)
                                judger.p2.set_state(current_state)
                                human_turn = not human_turn
        
        if not human_turn and not is_end:
            i, j, symbol = judger.p2.act()
            index = i * BOARD_COLS + j
            cell_vals[index] = 0
            next_state_hash = current_state.next_state(i, j, symbol).hash()
            current_state, is_end = all_states[next_state_hash]
            judger.p1.set_state(current_state)
            judger.p2.set_state(current_state)
            human_turn = not human_turn

        for cell in cells:
            pygame.draw.rect(screen, CELL_COLOR, cell)
            
        for index, val in enumerate(cell_vals):
            if val == 1:
                symbol_pos = pygame.Rect(cells[index].centerx - (symbol_width // 2), cells[index].centery - (symbol_height // 2), symbol_width, symbol_height)
                screen.blit(symbol_x, symbol_pos)
            if val == 0:
                symbol_pos = pygame.Rect(cells[index].centerx - (symbol_width // 2), cells[index].centery - (symbol_height // 2), symbol_width, symbol_height)
                screen.blit(symbol_o, symbol_pos)
        
        pygame.display.update()
        clock.tick(60)

        if is_end:
            winner = judger.current_state.winner
            if winner == player2.symbol:
                print("You lose!")
            elif winner == player1.symbol:
                print("You win!")
            else:
                print("It is a tie!")