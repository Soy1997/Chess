# two player chess in python with Pygame!
# pawn double space checking
# castling
# en passant
# pawn promotion

import pygame
from constants import *

pygame.init()


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
        label = str(8 - index)
        text = font.render(label, True, BOARD_COLORS['text_muted'])
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
        subtitle = 'Click a highlighted square or click again to cancel.'
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
    if white_promote or black_promote:
        pygame.draw.rect(screen, BOARD_COLORS['panel'], [0, BOARD_SIZE, WIDTH - 200, HEIGHT - BOARD_SIZE])
        pygame.draw.rect(screen, BOARD_COLORS['panel_dark'], [12, 812, 776, 76], border_radius=24)
        pygame.draw.rect(screen, BOARD_COLORS['border'], [0, BOARD_SIZE, WIDTH - 200, HEIGHT - BOARD_SIZE], 3)
        screen.blit(big_font.render('Select Piece to Promote Pawn', True, BOARD_COLORS['text']), (20, 820))


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
    global castling_moves
    moves_list = []
    all_moves_list = []
    castling_moves = []
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
            moves_list, castling_moves = check_king(location, turn)
        all_moves_list.append(moves_list)
    return all_moves_list


# check king valid moves
def check_king(position, color):
    moves_list = []
    castle_moves = check_castling()
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
    return moves_list, castle_moves


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
            # indent the check for two spaces ahead, so it is only checked if one space ahead is also open
            if (position[0], position[1] + 2) not in white_locations and \
                    (position[0], position[1] + 2) not in black_locations and position[1] == 1:
                moves_list.append((position[0], position[1] + 2))
        if (position[0] + 1, position[1] + 1) in black_locations:
            moves_list.append((position[0] + 1, position[1] + 1))
        if (position[0] - 1, position[1] + 1) in black_locations:
            moves_list.append((position[0] - 1, position[1] + 1))
        # add en passant move checker
        if (position[0] + 1, position[1] + 1) == black_ep:
            moves_list.append((position[0] + 1, position[1] + 1))
        if (position[0] - 1, position[1] + 1) == black_ep:
            moves_list.append((position[0] - 1, position[1] + 1))
    else:
        if (position[0], position[1] - 1) not in white_locations and \
                (position[0], position[1] - 1) not in black_locations and position[1] > 0:
            moves_list.append((position[0], position[1] - 1))
            # indent the check for two spaces ahead, so it is only checked if one space ahead is also open
            if (position[0], position[1] - 2) not in white_locations and \
                    (position[0], position[1] - 2) not in black_locations and position[1] == 6:
                moves_list.append((position[0], position[1] - 2))
        if (position[0] + 1, position[1] - 1) in white_locations:
            moves_list.append((position[0] + 1, position[1] - 1))
        if (position[0] - 1, position[1] - 1) in white_locations:
            moves_list.append((position[0] - 1, position[1] - 1))
        # add en passant move checker
        if (position[0] + 1, position[1] - 1) == white_ep:
            moves_list.append((position[0] + 1, position[1] - 1))
        if (position[0] - 1, position[1] - 1) == white_ep:
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
    global check
    check = False
    if turn_step < 2:
        if 'king' in white_pieces:
            king_index = white_pieces.index('king')
            king_location = white_locations[king_index]
            for i in range(len(black_options)):
                if king_location in black_options[i]:
                    check = True
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
                    check = True
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


# check en passant because people on the internet won't stop bugging me for it
def check_ep(old_coords, new_coords):
    if turn_step <= 1:
        index = white_locations.index(old_coords)
        ep_coords = (new_coords[0], new_coords[1] - 1)
        piece = white_pieces[index]
    else:
        index = black_locations.index(old_coords)
        ep_coords = (new_coords[0], new_coords[1] + 1)
        piece = black_pieces[index]
    if piece == 'pawn' and abs(old_coords[1] - new_coords[1]) > 1:
        # if piece was pawn and moved two spaces, return EP coords as defined above
        pass
    else:
        ep_coords = (100, 100)
    return ep_coords


# add castling
def check_castling():
    # king must not currently be in check, neither the rook nor king has moved previously, nothing between
    # and the king does not pass through or finish on an attacked piece
    castle_moves = []  # store each valid castle move as [((king_coords), (castle_coords))]
    rook_indexes = []
    rook_locations = []
    king_index = 0
    king_pos = (0, 0)
    if turn_step > 1:
        for i in range(len(white_pieces)):
            if white_pieces[i] == 'rook':
                rook_indexes.append(white_moved[i])
                rook_locations.append(white_locations[i])
            if white_pieces[i] == 'king':
                king_index = i
                king_pos = white_locations[i]
        if not white_moved[king_index] and False in rook_indexes and not check:
            for i in range(len(rook_indexes)):
                castle = True
                if rook_locations[i][0] > king_pos[0]:
                    empty_squares = [(king_pos[0] + 1, king_pos[1]), (king_pos[0] + 2, king_pos[1]),
                                     (king_pos[0] + 3, king_pos[1])]
                else:
                    empty_squares = [(king_pos[0] - 1, king_pos[1]), (king_pos[0] - 2, king_pos[1])]
                for j in range(len(empty_squares)):
                    if empty_squares[j] in white_locations or empty_squares[j] in black_locations or \
                            empty_squares[j] in black_options or rook_indexes[i]:
                        castle = False
                if castle:
                    castle_moves.append((empty_squares[1], empty_squares[0]))
    else:
        for i in range(len(black_pieces)):
            if black_pieces[i] == 'rook':
                rook_indexes.append(black_moved[i])
                rook_locations.append(black_locations[i])
            if black_pieces[i] == 'king':
                king_index = i
                king_pos = black_locations[i]
        if not black_moved[king_index] and False in rook_indexes and not check:
            for i in range(len(rook_indexes)):
                castle = True
                if rook_locations[i][0] > king_pos[0]:
                    empty_squares = [(king_pos[0] + 1, king_pos[1]), (king_pos[0] + 2, king_pos[1]),
                                     (king_pos[0] + 3, king_pos[1])]
                else:
                    empty_squares = [(king_pos[0] - 1, king_pos[1]), (king_pos[0] - 2, king_pos[1])]
                for j in range(len(empty_squares)):
                    if empty_squares[j] in white_locations or empty_squares[j] in black_locations or \
                            empty_squares[j] in white_options or rook_indexes[i]:
                        castle = False
                if castle:
                    castle_moves.append((empty_squares[1], empty_squares[0]))
    return castle_moves


def draw_castling(moves):
    color = BOARD_COLORS['valid_white'] if turn_step < 2 else BOARD_COLORS['valid_black']
    for i in range(len(moves)):
        pygame.draw.circle(screen, color, (moves[i][0][0] * SQUARE_SIZE + 50, moves[i][0][1] * SQUARE_SIZE + 70), 8)
        screen.blit(font.render('king', True, BOARD_COLORS['text']),
                    (moves[i][0][0] * SQUARE_SIZE + 30, moves[i][0][1] * SQUARE_SIZE + 70))
        pygame.draw.circle(screen, color, (moves[i][1][0] * SQUARE_SIZE + 50, moves[i][1][1] * SQUARE_SIZE + 70), 8)
        screen.blit(font.render('rook', True, BOARD_COLORS['text']),
                    (moves[i][1][0] * SQUARE_SIZE + 30, moves[i][1][1] * SQUARE_SIZE + 70))
        pygame.draw.line(screen, color, (moves[i][0][0] * SQUARE_SIZE + 50, moves[i][0][1] * SQUARE_SIZE + 70),
                         (moves[i][1][0] * SQUARE_SIZE + 50, moves[i][1][1] * SQUARE_SIZE + 70), 2)


# add pawn promotion
def check_promotion():
    pawn_indexes = []
    white_promotion = False
    black_promotion = False
    promote_index = 100
    for i in range(len(white_pieces)):
        if white_pieces[i] == 'pawn':
            pawn_indexes.append(i)
    for i in range(len(pawn_indexes)):
        if white_locations[pawn_indexes[i]][1] == 7:
            white_promotion = True
            promote_index = pawn_indexes[i]
    pawn_indexes = []
    for i in range(len(black_pieces)):
        if black_pieces[i] == 'pawn':
            pawn_indexes.append(i)
    for i in range(len(pawn_indexes)):
        if black_locations[pawn_indexes[i]][1] == 0:
            black_promotion = True
            promote_index = pawn_indexes[i]
    return white_promotion, black_promotion, promote_index


def draw_promotion():
    pygame.draw.rect(screen, BOARD_COLORS['panel_dark'], [805, 0, 190, 420], border_radius=18)
    if white_promote:
        color = BOARD_COLORS['text_light']
        for i in range(len(white_promotions)):
            piece = white_promotions[i]
            index = piece_list.index(piece)
            screen.blit(white_images[index], (860, 5 + 100 * i))
    elif black_promote:
        color = BOARD_COLORS['text_light']
        for i in range(len(black_promotions)):
            piece = black_promotions[i]
            index = piece_list.index(piece)
            screen.blit(black_images[index], (860, 5 + 100 * i))
    pygame.draw.rect(screen, BOARD_COLORS['border'], [805, 0, 190, 420], 3, border_radius=18)


def check_promo_select():
    mouse_pos = pygame.mouse.get_pos()
    left_click = pygame.mouse.get_pressed()[0]
    x_pos = mouse_pos[0] // 100
    y_pos = mouse_pos[1] // 100
    if white_promote and left_click and x_pos > 7 and y_pos < 4:
        white_pieces[promo_index] = white_promotions[y_pos]
    elif black_promote and left_click and x_pos > 7 and y_pos < 4:
        black_pieces[promo_index] = black_promotions[y_pos]


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
    if not game_over:
        white_promote, black_promote, promo_index = check_promotion()
        if white_promote or black_promote:
            draw_promotion()
            check_promo_select()
    if selection != 100:
        valid_moves = check_valid_moves()
        draw_valid(valid_moves)
        if selected_piece == 'king':
            draw_castling(castling_moves)
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
                    white_ep = check_ep(white_locations[selection], click_coords)
                    white_locations[selection] = click_coords
                    white_moved[selection] = True
                    last_move = [start_square, click_coords]
                    if click_coords in black_locations:
                        black_piece = black_locations.index(click_coords)
                        captured_pieces_white.append(black_pieces[black_piece])
                        if black_pieces[black_piece] == 'king':
                            winner = 'white'
                        black_pieces.pop(black_piece)
                        black_locations.pop(black_piece)
                        black_moved.pop(black_piece)
                    # adding check if en passant pawn was captured
                    if click_coords == black_ep:
                        black_piece = black_locations.index((black_ep[0], black_ep[1] - 1))
                        captured_pieces_white.append(black_pieces[black_piece])
                        black_pieces.pop(black_piece)
                        black_locations.pop(black_piece)
                        black_moved.pop(black_piece)
                    black_options = check_options(black_pieces, black_locations, 'black')
                    white_options = check_options(white_pieces, white_locations, 'white')
                    turn_step = 2
                    selection = 100
                    selected_piece = ''
                    valid_moves = []
                # add option to castle
                elif selection != 100 and selected_piece == 'king':
                    for q in range(len(castling_moves)):
                        if click_coords == castling_moves[q][0]:
                            start_square = white_locations[selection]
                            white_locations[selection] = click_coords
                            white_moved[selection] = True
                            if click_coords == (1, 0):
                                rook_coords = (0, 0)
                            else:
                                rook_coords = (7, 0)
                            rook_index = white_locations.index(rook_coords)
                            white_locations[rook_index] = castling_moves[q][1]
                            last_move = [start_square, click_coords]
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
                    black_ep = check_ep(black_locations[selection], click_coords)
                    black_locations[selection] = click_coords
                    black_moved[selection] = True
                    last_move = [start_square, click_coords]
                    if click_coords in white_locations:
                        white_piece = white_locations.index(click_coords)
                        captured_pieces_black.append(white_pieces[white_piece])
                        if white_pieces[white_piece] == 'king':
                            winner = 'black'
                        white_pieces.pop(white_piece)
                        white_locations.pop(white_piece)
                        white_moved.pop(white_piece)
                    if click_coords == white_ep:
                        white_piece = white_locations.index((white_ep[0], white_ep[1] + 1))
                        captured_pieces_black.append(white_pieces[white_piece])
                        white_pieces.pop(white_piece)
                        white_locations.pop(white_piece)
                        white_moved.pop(white_piece)
                    black_options = check_options(black_pieces, black_locations, 'black')
                    white_options = check_options(white_pieces, white_locations, 'white')
                    turn_step = 0
                    selection = 100
                    selected_piece = ''
                    valid_moves = []
                # add option to castle
                elif selection != 100 and selected_piece == 'king':
                    for q in range(len(castling_moves)):
                        if click_coords == castling_moves[q][0]:
                            start_square = black_locations[selection]
                            black_locations[selection] = click_coords
                            black_moved[selection] = True
                            if click_coords == (1, 7):
                                rook_coords = (0, 7)
                            else:
                                rook_coords = (7, 7)
                            rook_index = black_locations.index(rook_coords)
                            black_locations[rook_index] = castling_moves[q][1]
                            last_move = [start_square, click_coords]
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
                white_moved = [False, False, False, False, False, False, False, False,
                               False, False, False, False, False, False, False, False]
                black_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
                black_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                                   (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]
                black_moved = [False, False, False, False, False, False, False, False,
                               False, False, False, False, False, False, False, False]
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
