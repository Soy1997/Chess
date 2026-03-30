# two player chess in python with Pygame!
# part one, set up variables images and game loop

import pygame

pygame.init()
WIDTH = 1000
HEIGHT = 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Two-Player Pygame Chess!')
font = pygame.font.Font('freesansbold.ttf', 20)
medium_font = pygame.font.Font('freesansbold.ttf', 40)
big_font = pygame.font.Font('freesansbold.ttf', 50)
timer = pygame.time.Clock()
fps = 60
BOARD_SIZE = 800
SQUARE_SIZE = 100
SIDEBAR_X = 800
BOARD_COLORS = {
    'background': '#2F3640',
    'panel': '#5C6773',
    'border': '#C9A227',
    'light_square': '#F0D9B5',
    'dark_square': '#B58863',
    'hover': '#F6F669',
    'selected_white': '#D7263D',
    'selected_black': '#1D4ED8',
    'last_move': '#7DD3FC',
    'valid_white': '#D7263D',
    'valid_black': '#2563EB',
    'capture': '#111827',
    'text': '#111111',
}
# game variables and images
white_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
white_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                   (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
black_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
black_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                   (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]
captured_pieces_white = []
captured_pieces_black = []
# 0 - whites turn no selection: 1-whites turn piece selected: 2- black turn no selection, 3 - black turn piece selected
turn_step = 0
selection = 100
valid_moves = []
# load in game piece images (queen, king, rook, bishop, knight, pawn) x 2
black_queen = pygame.image.load('assets/images/black queen.png')
black_queen = pygame.transform.scale(black_queen, (80, 80))
black_queen_small = pygame.transform.scale(black_queen, (45, 45))
black_king = pygame.image.load('assets/images/black king.png')
black_king = pygame.transform.scale(black_king, (80, 80))
black_king_small = pygame.transform.scale(black_king, (45, 45))
black_rook = pygame.image.load('assets/images/black rook.png')
black_rook = pygame.transform.scale(black_rook, (80, 80))
black_rook_small = pygame.transform.scale(black_rook, (45, 45))
black_bishop = pygame.image.load('assets/images/black bishop.png')
black_bishop = pygame.transform.scale(black_bishop, (80, 80))
black_bishop_small = pygame.transform.scale(black_bishop, (45, 45))
black_knight = pygame.image.load('assets/images/black knight.png')
black_knight = pygame.transform.scale(black_knight, (80, 80))
black_knight_small = pygame.transform.scale(black_knight, (45, 45))
black_pawn = pygame.image.load('assets/images/black pawn.png')
black_pawn = pygame.transform.scale(black_pawn, (65, 65))
black_pawn_small = pygame.transform.scale(black_pawn, (45, 45))
white_queen = pygame.image.load('assets/images/white queen.png')
white_queen = pygame.transform.scale(white_queen, (80, 80))
white_queen_small = pygame.transform.scale(white_queen, (45, 45))
white_king = pygame.image.load('assets/images/white king.png')
white_king = pygame.transform.scale(white_king, (80, 80))
white_king_small = pygame.transform.scale(white_king, (45, 45))
white_rook = pygame.image.load('assets/images/white rook.png')
white_rook = pygame.transform.scale(white_rook, (80, 80))
white_rook_small = pygame.transform.scale(white_rook, (45, 45))
white_bishop = pygame.image.load('assets/images/white bishop.png')
white_bishop = pygame.transform.scale(white_bishop, (80, 80))
white_bishop_small = pygame.transform.scale(white_bishop, (45, 45))
white_knight = pygame.image.load('assets/images/white knight.png')
white_knight = pygame.transform.scale(white_knight, (80, 80))
white_knight_small = pygame.transform.scale(white_knight, (45, 45))
white_pawn = pygame.image.load('assets/images/white pawn.png')
white_pawn = pygame.transform.scale(white_pawn, (65, 65))
white_pawn_small = pygame.transform.scale(white_pawn, (45, 45))
white_images = [white_pawn, white_queen, white_king, white_knight, white_rook, white_bishop]
small_white_images = [white_pawn_small, white_queen_small, white_king_small, white_knight_small,
                      white_rook_small, white_bishop_small]
black_images = [black_pawn, black_queen, black_king, black_knight, black_rook, black_bishop]
small_black_images = [black_pawn_small, black_queen_small, black_king_small, black_knight_small,
                      black_rook_small, black_bishop_small]
piece_list = ['pawn', 'queen', 'king', 'knight', 'rook', 'bishop']
# check variables/ flashing counter
counter = 0
winner = ''
game_over = False
hover_square = None
last_move = []
selected_piece = ''


def get_board_square(mouse_pos):
    x_pos = mouse_pos[0] // SQUARE_SIZE
    y_pos = mouse_pos[1] // SQUARE_SIZE
    if 0 <= x_pos < 8 and 0 <= y_pos < 8:
        return x_pos, y_pos
    return None


def get_selection_outline():
    if turn_step < 2:
        return BOARD_COLORS['selected_white']
    return BOARD_COLORS['selected_black']


def draw_coordinate_labels():
    files = 'ABCDEFGH'
    for index, label in enumerate(files):
        text = font.render(label, True, BOARD_COLORS['text_muted'])
        screen.blit(text, (index * SQUARE_SIZE + 40, BOARD_SIZE - 25))
    for index in range(8):
        text = font.render(str(8 - index), True, BOARD_COLORS['text_muted'])
        screen.blit(text, (8, index * SQUARE_SIZE + 8))


def draw_sidebar_card(top, height, title, subtitle=''):
    pygame.draw.rect(screen, BOARD_COLORS['panel_dark'], [815, top, 170, height], border_radius=18)
    pygame.draw.rect(screen, BOARD_COLORS['panel_light'], [822, top + 8, 156, height - 16], border_radius=14)
    screen.blit(font.render(title, True, BOARD_COLORS['text']), (830, top + 18))
    if subtitle:
        screen.blit(font.render(subtitle, True, BOARD_COLORS['text_muted']), (830, top + 48))


def draw_selection_panel():
    title = 'No Piece Selected'
    subtitle = 'Pick a piece to see moves.'
    if selection != 100:
        piece_name = selected_piece.title()
        team_name = 'White' if turn_step < 2 else 'Black'
        title = f'{team_name} {piece_name}'
        subtitle = 'Click a move marker or click again to cancel.'
    draw_sidebar_card(700, 110, title, subtitle)


# draw main game board
def draw_board():
    screen.fill(BOARD_COLORS['background'])
    for row in range(8):
        for column in range(8):
            square_color = BOARD_COLORS['light_square'] if (row + column) % 2 == 0 else BOARD_COLORS['dark_square']
            pygame.draw.rect(screen, square_color, [column * SQUARE_SIZE, row * SQUARE_SIZE,
                                                    SQUARE_SIZE, SQUARE_SIZE])
    pygame.draw.rect(screen, BOARD_COLORS['panel'], [0, BOARD_SIZE, WIDTH, HEIGHT - BOARD_SIZE])
    pygame.draw.rect(screen, BOARD_COLORS['panel_dark'], [12, 812, 776, 76], border_radius=24)
    pygame.draw.rect(screen, BOARD_COLORS['border'], [0, BOARD_SIZE, WIDTH, HEIGHT - BOARD_SIZE], 3)
    pygame.draw.rect(screen, BOARD_COLORS['border'], [SIDEBAR_X, 0, WIDTH - SIDEBAR_X, HEIGHT], 3)
    status_text = ['White: Select a Piece to Move', 'White: Choose a Destination',
                   'Black: Select a Piece to Move', 'Black: Choose a Destination']
    screen.blit(big_font.render(status_text[turn_step], True, BOARD_COLORS['text']), (28, 823))
    for i in range(9):
        pygame.draw.line(screen, BOARD_COLORS['capture'], (0, SQUARE_SIZE * i), (BOARD_SIZE, SQUARE_SIZE * i), 2)
        pygame.draw.line(screen, BOARD_COLORS['capture'], (SQUARE_SIZE * i, 0), (SQUARE_SIZE * i, BOARD_SIZE), 2)
    draw_coordinate_labels()
    draw_sidebar_card(20, 110, 'Match Dashboard', 'Local two-player chess')
    draw_sidebar_card(145, 160, 'Captured Pieces', 'Black on left, white on right')
    draw_sidebar_card(320, 135, 'Controls', 'Forfeit button below')
    pygame.draw.rect(screen, BOARD_COLORS['panel_dark'], [820, 815, 160, 58], border_radius=18)
    pygame.draw.rect(screen, BOARD_COLORS['border'], [820, 815, 160, 58], 2, border_radius=18)
    screen.blit(medium_font.render('FORFEIT', True, BOARD_COLORS['text']), (828, 823))
    draw_selection_panel()


# draw pieces onto board
def draw_pieces():
    for i in range(len(white_pieces)):
        index = piece_list.index(white_pieces[i])
        if white_pieces[i] == 'pawn':
            screen.blit(white_pawn, (white_locations[i][0] * SQUARE_SIZE + 22, white_locations[i][1] * SQUARE_SIZE + 30))
        else:
            screen.blit(white_images[index], (white_locations[i][0] * SQUARE_SIZE + 10,
                                              white_locations[i][1] * SQUARE_SIZE + 10))
        if turn_step < 2:
            if selection == i:
                pygame.draw.rect(screen, get_selection_outline(),
                                 [white_locations[i][0] * SQUARE_SIZE + 2, white_locations[i][1] * SQUARE_SIZE + 2,
                                  SQUARE_SIZE - 4, SQUARE_SIZE - 4], 4, border_radius=8)

    for i in range(len(black_pieces)):
        index = piece_list.index(black_pieces[i])
        if black_pieces[i] == 'pawn':
            screen.blit(black_pawn, (black_locations[i][0] * SQUARE_SIZE + 22, black_locations[i][1] * SQUARE_SIZE + 30))
        else:
            screen.blit(black_images[index], (black_locations[i][0] * SQUARE_SIZE + 10,
                                              black_locations[i][1] * SQUARE_SIZE + 10))
        if turn_step >= 2:
            if selection == i:
                pygame.draw.rect(screen, get_selection_outline(),
                                 [black_locations[i][0] * SQUARE_SIZE + 2, black_locations[i][1] * SQUARE_SIZE + 2,
                                  SQUARE_SIZE - 4, SQUARE_SIZE - 4], 4, border_radius=8)


# function to check all pieces valid options on board
def check_options(pieces, locations, turn):
    moves_list = []
    all_moves_list = []
    for i in range((len(pieces))):
        location = locations[i]
        piece = pieces[i]
        if piece == 'pawn':
            moves_list = check_pawn(location, turn)
        elif piece == 'rook':
            moves_list = check_rook(location, turn)
        elif piece == 'knight':
            moves_list = check_knight(location, turn)
        elif piece == 'bishop':
            moves_list = check_bishop(location, turn)
        elif piece == 'queen':
            moves_list = check_queen(location, turn)
        elif piece == 'king':
            moves_list = check_king(location, turn)
        all_moves_list.append(moves_list)
    return all_moves_list


# check king valid moves
def check_king(position, color):
    moves_list = []
    if color == 'white':
        enemies_list = black_locations
        friends_list = white_locations
    else:
        friends_list = black_locations
        enemies_list = white_locations
    # 8 squares to check for kings, they can go one square any direction
    targets = [(1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1)]
    for i in range(8):
        target = (position[0] + targets[i][0], position[1] + targets[i][1])
        if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
            moves_list.append(target)
    return moves_list


# check queen valid moves
def check_queen(position, color):
    moves_list = check_bishop(position, color)
    second_list = check_rook(position, color)
    for i in range(len(second_list)):
        moves_list.append(second_list[i])
    return moves_list


# check bishop moves
def check_bishop(position, color):
    moves_list = []
    if color == 'white':
        enemies_list = black_locations
        friends_list = white_locations
    else:
        friends_list = black_locations
        enemies_list = white_locations
    for i in range(4):  # up-right, up-left, down-right, down-left
        path = True
        chain = 1
        if i == 0:
            x = 1
            y = -1
        elif i == 1:
            x = -1
            y = -1
        elif i == 2:
            x = 1
            y = 1
        else:
            x = -1
            y = 1
        while path:
            if (position[0] + (chain * x), position[1] + (chain * y)) not in friends_list and \
                    0 <= position[0] + (chain * x) <= 7 and 0 <= position[1] + (chain * y) <= 7:
                moves_list.append((position[0] + (chain * x), position[1] + (chain * y)))
                if (position[0] + (chain * x), position[1] + (chain * y)) in enemies_list:
                    path = False
                chain += 1
            else:
                path = False
    return moves_list


# check rook moves
def check_rook(position, color):
    moves_list = []
    if color == 'white':
        enemies_list = black_locations
        friends_list = white_locations
    else:
        friends_list = black_locations
        enemies_list = white_locations
    for i in range(4):  # down, up, right, left
        path = True
        chain = 1
        if i == 0:
            x = 0
            y = 1
        elif i == 1:
            x = 0
            y = -1
        elif i == 2:
            x = 1
            y = 0
        else:
            x = -1
            y = 0
        while path:
            if (position[0] + (chain * x), position[1] + (chain * y)) not in friends_list and \
                    0 <= position[0] + (chain * x) <= 7 and 0 <= position[1] + (chain * y) <= 7:
                moves_list.append((position[0] + (chain * x), position[1] + (chain * y)))
                if (position[0] + (chain * x), position[1] + (chain * y)) in enemies_list:
                    path = False
                chain += 1
            else:
                path = False
    return moves_list


# check valid pawn moves
def check_pawn(position, color):
    moves_list = []
    if color == 'white':
        if (position[0], position[1] + 1) not in white_locations and \
                (position[0], position[1] + 1) not in black_locations and position[1] < 7:
            moves_list.append((position[0], position[1] + 1))
        if (position[0], position[1] + 2) not in white_locations and \
                (position[0], position[1] + 2) not in black_locations and position[1] == 1:
            moves_list.append((position[0], position[1] + 2))
        if (position[0] + 1, position[1] + 1) in black_locations:
            moves_list.append((position[0] + 1, position[1] + 1))
        if (position[0] - 1, position[1] + 1) in black_locations:
            moves_list.append((position[0] - 1, position[1] + 1))
    else:
        if (position[0], position[1] - 1) not in white_locations and \
                (position[0], position[1] - 1) not in black_locations and position[1] > 0:
            moves_list.append((position[0], position[1] - 1))
        if (position[0], position[1] - 2) not in white_locations and \
                (position[0], position[1] - 2) not in black_locations and position[1] == 6:
            moves_list.append((position[0], position[1] - 2))
        if (position[0] + 1, position[1] - 1) in white_locations:
            moves_list.append((position[0] + 1, position[1] - 1))
        if (position[0] - 1, position[1] - 1) in white_locations:
            moves_list.append((position[0] - 1, position[1] - 1))
    return moves_list


# check valid knight moves
def check_knight(position, color):
    moves_list = []
    if color == 'white':
        enemies_list = black_locations
        friends_list = white_locations
    else:
        friends_list = black_locations
        enemies_list = white_locations
    # 8 squares to check for knights, they can go two squares in one direction and one in another
    targets = [(1, 2), (1, -2), (2, 1), (2, -1), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]
    for i in range(8):
        target = (position[0] + targets[i][0], position[1] + targets[i][1])
        if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
            moves_list.append(target)
    return moves_list


# check for valid moves for just selected piece
def check_valid_moves():
    if turn_step < 2:
        options_list = white_options
    else:
        options_list = black_options
    valid_options = options_list[selection]
    return valid_options


# draw valid moves on screen
def draw_valid(moves):
    move_color = BOARD_COLORS['valid_white'] if turn_step < 2 else BOARD_COLORS['valid_black']
    enemy_locations = black_locations if turn_step < 2 else white_locations
    for move in moves:
        center = (move[0] * SQUARE_SIZE + 50, move[1] * SQUARE_SIZE + 50)
        if move in enemy_locations:
            pygame.draw.circle(screen, BOARD_COLORS['capture'], center, 26, 4)
            pygame.draw.circle(screen, move_color, center, 18, 3)
        else:
            pygame.draw.circle(screen, move_color, center, 12)


# draw captured pieces on side of screen
def draw_captured():
    for i in range(len(captured_pieces_white)):
        captured_piece = captured_pieces_white[i]
        index = piece_list.index(captured_piece)
        screen.blit(small_black_images[index], (825, 5 + 50 * i))
    for i in range(len(captured_pieces_black)):
        captured_piece = captured_pieces_black[i]
        index = piece_list.index(captured_piece)
        screen.blit(small_white_images[index], (925, 5 + 50 * i))


# draw a flashing square around king if in check
def draw_check():
    if turn_step < 2:
        if 'king' in white_pieces:
            king_index = white_pieces.index('king')
            king_location = white_locations[king_index]
            for i in range(len(black_options)):
                if king_location in black_options[i]:
                    if counter < 15:
                        pygame.draw.rect(screen, 'dark red', [white_locations[king_index][0] * SQUARE_SIZE + 2,
                                                              white_locations[king_index][1] * SQUARE_SIZE + 2,
                                                              SQUARE_SIZE - 4, SQUARE_SIZE - 4], 5, border_radius=8)
    else:
        if 'king' in black_pieces:
            king_index = black_pieces.index('king')
            king_location = black_locations[king_index]
            for i in range(len(white_options)):
                if king_location in white_options[i]:
                    if counter < 15:
                        pygame.draw.rect(screen, 'dark blue', [black_locations[king_index][0] * SQUARE_SIZE + 2,
                                                               black_locations[king_index][1] * SQUARE_SIZE + 2,
                                                               SQUARE_SIZE - 4, SQUARE_SIZE - 4], 5, border_radius=8)


def draw_hover_highlight():
    if hover_square is None:
        return
    pygame.draw.rect(screen, BOARD_COLORS['hover'],
                     [hover_square[0] * SQUARE_SIZE + 6, hover_square[1] * SQUARE_SIZE + 6,
                      SQUARE_SIZE - 12, SQUARE_SIZE - 12], 3, border_radius=10)


def draw_last_move():
    for square in last_move:
        pygame.draw.rect(screen, BOARD_COLORS['last_move'],
                         [square[0] * SQUARE_SIZE + 10, square[1] * SQUARE_SIZE + 10,
                          SQUARE_SIZE - 20, SQUARE_SIZE - 20], 3, border_radius=10)


def draw_game_over():
    pygame.draw.rect(screen, 'black', [200, 200, 400, 70])
    screen.blit(font.render(f'{winner} won the game!', True, 'white'), (210, 210))
    screen.blit(font.render(f'Press ENTER to Restart!', True, 'white'), (210, 240))


# main game loop
black_options = check_options(black_pieces, black_locations, 'black')
white_options = check_options(white_pieces, white_locations, 'white')
run = True
while run:
    timer.tick(fps)
    if counter < 30:
        counter += 1
    else:
        counter = 0
    hover_square = get_board_square(pygame.mouse.get_pos())
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if hover_square else pygame.SYSTEM_CURSOR_ARROW)
    draw_board()
    draw_last_move()
    draw_hover_highlight()
    draw_pieces()
    draw_captured()
    draw_check()
    if selection != 100:
        valid_moves = check_valid_moves()
        draw_valid(valid_moves)
    # event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
            click_coords = get_board_square(event.pos)
            if click_coords is None:
                x_coord = event.pos[0] // SQUARE_SIZE
                y_coord = event.pos[1] // SQUARE_SIZE
                click_coords = (x_coord, y_coord)
            if turn_step <= 1:
                if click_coords == (8, 8) or click_coords == (9, 8):
                    winner = 'black'
                if click_coords in white_locations:
                    selected_index = white_locations.index(click_coords)
                    if selection == selected_index and turn_step == 1:
                        selection = 100
                        valid_moves = []
                        selected_piece = ''
                        turn_step = 0
                    else:
                        selection = selected_index
                        selected_piece = white_pieces[selection]
                        if turn_step == 0:
                            turn_step = 1
                if click_coords in valid_moves and selection != 100:
                    start_square = white_locations[selection]
                    white_locations[selection] = click_coords
                    last_move = [start_square, click_coords]
                    if click_coords in black_locations:
                        black_piece = black_locations.index(click_coords)
                        captured_pieces_white.append(black_pieces[black_piece])
                        if black_pieces[black_piece] == 'king':
                            winner = 'white'
                        black_pieces.pop(black_piece)
                        black_locations.pop(black_piece)
                    black_options = check_options(black_pieces, black_locations, 'black')
                    white_options = check_options(white_pieces, white_locations, 'white')
                    turn_step = 2
                    selection = 100
                    selected_piece = ''
                    valid_moves = []
            if turn_step > 1:
                if click_coords == (8, 8) or click_coords == (9, 8):
                    winner = 'white'
                if click_coords in black_locations:
                    selected_index = black_locations.index(click_coords)
                    if selection == selected_index and turn_step == 3:
                        selection = 100
                        valid_moves = []
                        selected_piece = ''
                        turn_step = 2
                    else:
                        selection = selected_index
                        selected_piece = black_pieces[selection]
                        if turn_step == 2:
                            turn_step = 3
                if click_coords in valid_moves and selection != 100:
                    start_square = black_locations[selection]
                    black_locations[selection] = click_coords
                    last_move = [start_square, click_coords]
                    if click_coords in white_locations:
                        white_piece = white_locations.index(click_coords)
                        captured_pieces_black.append(white_pieces[white_piece])
                        if white_pieces[white_piece] == 'king':
                            winner = 'black'
                        white_pieces.pop(white_piece)
                        white_locations.pop(white_piece)
                    black_options = check_options(black_pieces, black_locations, 'black')
                    white_options = check_options(white_pieces, white_locations, 'white')
                    turn_step = 0
                    selection = 100
                    selected_piece = ''
                    valid_moves = []
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_RETURN:
                game_over = False
                winner = ''
                white_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
                white_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                                   (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
                black_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
                black_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                                   (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]
                captured_pieces_white = []
                captured_pieces_black = []
                turn_step = 0
                selection = 100
                selected_piece = ''
                last_move = []
                valid_moves = []
                black_options = check_options(black_pieces, black_locations, 'black')
                white_options = check_options(white_pieces, white_locations, 'white')

    if winner != '':
        game_over = True
        draw_game_over()

    pygame.display.flip()
pygame.quit()
