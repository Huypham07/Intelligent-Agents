import time
from numpy import rec
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

    font = pygame.font.SysFont("mv boli", 80)
    start_text = font.render("Start", True, (50, 70, 80))
    font = pygame.font.SysFont("mv boli", 65)
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
    cell_vals = [0, 0, 0, 0, 0, 0, 0, 0, 0]

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

    # game loop
    is_begin = True
    is_end = False
    running = True
    end_time = 0
    end_timer_start = False
    while running:
        pygame.draw.rect(screen, BACKGROUND_PANEL, background_panel)
        # print(human_turn)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if is_begin or is_end:
                    rect = pygame.Rect(width // 2 - start_text.get_width() // 2, height // 2 - start_text.get_height() // 2, start_text.get_width(), start_text.get_height())
                    if rect.collidepoint(x, y):
                        print("Game start!")
                        cell_vals = [0, 0, 0, 0, 0, 0, 0, 0, 0]
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
                        end_timer_start = False
                        if is_begin:
                            is_begin = False
                        if is_end:
                            is_end = False
                        
                
                elif human_turn:
                    for index, cell in enumerate(cells):
                        if cell.collidepoint((x, y)):
                            if (cell_vals[index] == 0):
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
        
        if not human_turn and not is_end and not is_begin:
            i, j, symbol = judger.p2.act()
            index = i * BOARD_COLS + j
            cell_vals[index] = symbol
            print(symbol)
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
            if val == -1:
                symbol_pos = pygame.Rect(cells[index].centerx - (symbol_width // 2), cells[index].centery - (symbol_height // 2), symbol_width, symbol_height)
                screen.blit(symbol_o, symbol_pos)
        
        if is_begin:
            pygame.draw.rect(screen, CELL_COLOR, (0, 0, width, height))
            screen.blit(start_text, (width // 2 - start_text.get_width() // 2, height // 2 - start_text.get_height() // 2))
            
        if is_end:
            if not end_timer_start:
                end_timer_start = True
                end_time = time.time_ns()
            if time.time_ns() - end_time > 2e9:
                pygame.draw.rect(screen, CELL_COLOR, (0, 0, width, height))
                screen.blit(start_text, (width // 2 - start_text.get_width() // 2, height // 2 - start_text.get_height() // 2))
                winner = current_state.winner
                print(winner)
                if winner == judger.p2.symbol:
                    print("You lose!")
                    text = font.render("You lose!", True, (125, 0, 0))
                    screen.blit(text, (width // 2 - text.get_width() // 2, height // 4 - text.get_height() // 2))
                elif winner == judger.p1.symbol:
                    print("You win!")
                    text = font.render("You win!", True, (125, 0, 0))
                    screen.blit(text, (width // 2 - text.get_width() // 2, height // 4 - text.get_height() // 2))
                else:
                    print("It is a tie!")
                    text = font.render("It is a tie!", True, (125, 0, 0))       
                    screen.blit(text, (width // 2 - text.get_width() // 2, height // 4 - text.get_height() // 2))           
            
        pygame.display.update()
        clock.tick(60)
            