# two player chess in python with Pygame!
# Board rotates 180° when turn switches between players

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
    'background': '#17212B',
    'panel': '#233243',
    'panel_dark': '#1B2734',
    'panel_light': '#314559',
    'border': '#E0B15C',
    'light_square': '#F3E7D0',
    'dark_square': '#B07D56',
    'hover': '#F8E16C',
    'selected_white': '#E85D75',
    'selected_black': '#60A5FA',
    'last_move': '#8BE9FD',
    'valid_white': '#FF6B6B',
    'valid_black': '#4D96FF',
    'capture': '#0F1720',
    'text': '#EEF2F7',
    'text_muted': '#BCC8D6',
    'text_dark': '#111827',
    'text_light': '#F9FAFB',
}

# ── Rotation state ────────────────────────────────────────────────────────────
# board_flipped = True means white is at bottom (board rotated 180°)
board_flipped = True

# Animation variables
rotating = False
rotation_angle = 0.0        # current angle in degrees (0 or 180)
rotation_target = 0.0       # target angle
ROTATION_DURATION_MS = 450  # lower is faster, higher is slower

# ── Helper: convert logical (col, row) → screen pixel rect ───────────────────
def board_to_screen(col, row):
    """Return top-left pixel coords for a logical square, respecting flip."""
    if board_flipped:
        screen_col = 7 - col
        screen_row = 7 - row
    else:
        screen_col = col
        screen_row = row
    return screen_col * SQUARE_SIZE, screen_row * SQUARE_SIZE

def screen_to_board(sx, sy):
    """Convert screen pixel position → logical board (col, row)."""
    sc = sx // SQUARE_SIZE
    sr = sy // SQUARE_SIZE
    if not (0 <= sc < 8 and 0 <= sr < 8):
        return None
    if board_flipped:
        return 7 - sc, 7 - sr
    return sc, sr

# ── Game variables ────────────────────────────────────────────────────────────
white_pieces    = ['rook','knight','bishop','king','queen','bishop','knight','rook',
                   'pawn','pawn','pawn','pawn','pawn','pawn','pawn','pawn']
white_locations = [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),
                   (0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1)]
black_pieces    = ['rook','knight','bishop','king','queen','bishop','knight','rook',
                   'pawn','pawn','pawn','pawn','pawn','pawn','pawn','pawn']
black_locations = [(0,7),(1,7),(2,7),(3,7),(4,7),(5,7),(6,7),(7,7),
                   (0,6),(1,6),(2,6),(3,6),(4,6),(5,6),(6,6),(7,6)]
captured_pieces_white = []
captured_pieces_black = []
turn_step  = 0      # 0=white no sel, 1=white sel, 2=black no sel, 3=black sel
selection  = 100
valid_moves = []
counter    = 0
winner     = ''
game_over  = False
hover_square  = None
last_move     = []
selected_piece = ''

white_moved = [False]*16
black_moved = [False]*16
white_ep = (100,100)
black_ep = (100,100)
white_promote = False
black_promote = False
promo_index   = 100
check         = False
castling_moves = []

white_promotions = ['bishop','knight','rook','queen']
black_promotions = ['bishop','knight','rook','queen']

# ── Images ───────────────────────────────────────────────────────────────────
def load(path, size):
    img = pygame.image.load(path)
    return pygame.transform.scale(img, size)

black_queen  = load('assets/images/black queen.png',  (80,80))
black_queen_small  = pygame.transform.scale(black_queen,  (45,45))
black_king   = load('assets/images/black king.png',   (80,80))
black_king_small   = pygame.transform.scale(black_king,   (45,45))
black_rook   = load('assets/images/black rook.png',   (80,80))
black_rook_small   = pygame.transform.scale(black_rook,   (45,45))
black_bishop = load('assets/images/black bishop.png', (80,80))
black_bishop_small = pygame.transform.scale(black_bishop, (45,45))
black_knight = load('assets/images/black knight.png', (80,80))
black_knight_small = pygame.transform.scale(black_knight, (45,45))
black_pawn   = load('assets/images/black pawn.png',   (65,65))
black_pawn_small   = pygame.transform.scale(black_pawn,   (45,45))

white_queen  = load('assets/images/white queen.png',  (80,80))
white_queen_small  = pygame.transform.scale(white_queen,  (45,45))
white_king   = load('assets/images/white king.png',   (80,80))
white_king_small   = pygame.transform.scale(white_king,   (45,45))
white_rook   = load('assets/images/white rook.png',   (80,80))
white_rook_small   = pygame.transform.scale(white_rook,   (45,45))
white_bishop = load('assets/images/white bishop.png', (80,80))
white_bishop_small = pygame.transform.scale(white_bishop, (45,45))
white_knight = load('assets/images/white knight.png', (80,80))
white_knight_small = pygame.transform.scale(white_knight, (45,45))
white_pawn   = load('assets/images/white pawn.png',   (65,65))
white_pawn_small   = pygame.transform.scale(white_pawn,   (45,45))

white_images = [white_pawn, white_queen, white_king, white_knight, white_rook, white_bishop]
small_white_images = [white_pawn_small, white_queen_small, white_king_small,
                      white_knight_small, white_rook_small, white_bishop_small]
black_images = [black_pawn, black_queen, black_king, black_knight, black_rook, black_bishop]
small_black_images = [black_pawn_small, black_queen_small, black_king_small,
                      black_knight_small, black_rook_small, black_bishop_small]
piece_list = ['pawn','queen','king','knight','rook','bishop']

# ── Move-checking functions (unchanged logic) ─────────────────────────────────
def check_options(pieces, locations, turn):
    global castling_moves
    all_moves = []
    castling_moves = []
    for i in range(len(pieces)):
        loc   = locations[i]
        piece = pieces[i]
        if   piece == 'pawn':   moves = check_pawn(loc, turn)
        elif piece == 'rook':   moves = check_rook(loc, turn)
        elif piece == 'knight': moves = check_knight(loc, turn)
        elif piece == 'bishop': moves = check_bishop(loc, turn)
        elif piece == 'queen':  moves = check_queen(loc, turn)
        elif piece == 'king':   moves, castling_moves = check_king(loc, turn)
        else: moves = []
        all_moves.append(moves)
    return all_moves

def check_king(position, color):
    moves = []
    castle = check_castling()
    friends = white_locations if color == 'white' else black_locations
    targets = [(1,0),(1,1),(1,-1),(-1,0),(-1,1),(-1,-1),(0,1),(0,-1)]
    for dx,dy in targets:
        t = (position[0]+dx, position[1]+dy)
        if t not in friends and 0<=t[0]<=7 and 0<=t[1]<=7:
            moves.append(t)
    return moves, castle

def check_queen(position, color):
    return check_bishop(position, color) + check_rook(position, color)

def check_bishop(position, color):
    moves = []
    friends = white_locations if color=='white' else black_locations
    enemies = black_locations if color=='white' else white_locations
    for dx,dy in [(1,-1),(-1,-1),(1,1),(-1,1)]:
        chain = 1
        while True:
            t = (position[0]+chain*dx, position[1]+chain*dy)
            if t not in friends and 0<=t[0]<=7 and 0<=t[1]<=7:
                moves.append(t)
                if t in enemies: break
                chain += 1
            else: break
    return moves

def check_rook(position, color):
    moves = []
    friends = white_locations if color=='white' else black_locations
    enemies = black_locations if color=='white' else white_locations
    for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]:
        chain = 1
        while True:
            t = (position[0]+chain*dx, position[1]+chain*dy)
            if t not in friends and 0<=t[0]<=7 and 0<=t[1]<=7:
                moves.append(t)
                if t in enemies: break
                chain += 1
            else: break
    return moves

def check_pawn(position, color):
    moves = []
    if color == 'white':
        if (position[0],position[1]+1) not in white_locations and \
           (position[0],position[1]+1) not in black_locations and position[1]<7:
            moves.append((position[0],position[1]+1))
            if (position[0],position[1]+2) not in white_locations and \
               (position[0],position[1]+2) not in black_locations and position[1]==1:
                moves.append((position[0],position[1]+2))
        if (position[0]+1,position[1]+1) in black_locations: moves.append((position[0]+1,position[1]+1))
        if (position[0]-1,position[1]+1) in black_locations: moves.append((position[0]-1,position[1]+1))
        if (position[0]+1,position[1]+1) == black_ep: moves.append((position[0]+1,position[1]+1))
        if (position[0]-1,position[1]+1) == black_ep: moves.append((position[0]-1,position[1]+1))
    else:
        if (position[0],position[1]-1) not in white_locations and \
           (position[0],position[1]-1) not in black_locations and position[1]>0:
            moves.append((position[0],position[1]-1))
            if (position[0],position[1]-2) not in white_locations and \
               (position[0],position[1]-2) not in black_locations and position[1]==6:
                moves.append((position[0],position[1]-2))
        if (position[0]+1,position[1]-1) in white_locations: moves.append((position[0]+1,position[1]-1))
        if (position[0]-1,position[1]-1) in white_locations: moves.append((position[0]-1,position[1]-1))
        if (position[0]+1,position[1]-1) == white_ep: moves.append((position[0]+1,position[1]-1))
        if (position[0]-1,position[1]-1) == white_ep: moves.append((position[0]-1,position[1]-1))
    return moves

def check_knight(position, color):
    moves = []
    friends = white_locations if color=='white' else black_locations
    for dx,dy in [(1,2),(1,-2),(2,1),(2,-1),(-1,2),(-1,-2),(-2,1),(-2,-1)]:
        t = (position[0]+dx, position[1]+dy)
        if t not in friends and 0<=t[0]<=7 and 0<=t[1]<=7:
            moves.append(t)
    return moves

def check_valid_moves():
    opts = white_options if turn_step < 2 else black_options
    return opts[selection]

def check_ep(old, new):
    if turn_step <= 1:
        idx   = white_locations.index(old)
        ep    = (new[0], new[1]-1)
        piece = white_pieces[idx]
    else:
        idx   = black_locations.index(old)
        ep    = (new[0], new[1]+1)
        piece = black_pieces[idx]
    if piece != 'pawn' or abs(old[1]-new[1]) <= 1:
        ep = (100,100)
    return ep

def check_castling():
    castle = []
    rook_idx = []
    rook_locs = []
    king_i = 0
    king_pos = (0,0)
    if turn_step > 1:   # white's castling check (shown during black's turn? kept original logic)
        for i,p in enumerate(white_pieces):
            if p == 'rook':  rook_idx.append(white_moved[i]); rook_locs.append(white_locations[i])
            if p == 'king':  king_i = i; king_pos = white_locations[i]
        if not white_moved[king_i] and False in rook_idx and not check:
            for i in range(len(rook_idx)):
                ok = True
                sq = [(king_pos[0]+1,king_pos[1]),(king_pos[0]+2,king_pos[1]),(king_pos[0]+3,king_pos[1])] \
                     if rook_locs[i][0] > king_pos[0] else \
                     [(king_pos[0]-1,king_pos[1]),(king_pos[0]-2,king_pos[1])]
                for s in sq:
                    if s in white_locations or s in black_locations or s in black_options or rook_idx[i]:
                        ok = False
                if ok: castle.append((sq[1], sq[0]))
    else:
        for i,p in enumerate(black_pieces):
            if p == 'rook':  rook_idx.append(black_moved[i]); rook_locs.append(black_locations[i])
            if p == 'king':  king_i = i; king_pos = black_locations[i]
        if not black_moved[king_i] and False in rook_idx and not check:
            for i in range(len(rook_idx)):
                ok = True
                sq = [(king_pos[0]+1,king_pos[1]),(king_pos[0]+2,king_pos[1]),(king_pos[0]+3,king_pos[1])] \
                     if rook_locs[i][0] > king_pos[0] else \
                     [(king_pos[0]-1,king_pos[1]),(king_pos[0]-2,king_pos[1])]
                for s in sq:
                    if s in white_locations or s in black_locations or s in white_options or rook_idx[i]:
                        ok = False
                if ok: castle.append((sq[1], sq[0]))
    return castle

def check_promotion():
    wi = bi = False
    pi = 100
    for i,p in enumerate(white_pieces):
        if p=='pawn' and white_locations[i][1]==7: wi=True; pi=i
    for i,p in enumerate(black_pieces):
        if p=='pawn' and black_locations[i][1]==0: bi=True; pi=i
    return wi, bi, pi

# ── Draw functions ────────────────────────────────────────────────────────────
def get_selection_outline():
    return BOARD_COLORS['selected_white'] if turn_step < 2 else BOARD_COLORS['selected_black']

def draw_coordinate_labels():
    """Draw file/rank labels that always show from the current player's perspective."""
    files = 'ABCDEFGH' if board_flipped else 'HGFEDCBA'
    ranks = '12345678' if board_flipped else '87654321'
    for i, label in enumerate(files):
        text = font.render(label, True, BOARD_COLORS['text_muted'])
        screen.blit(text, (i * SQUARE_SIZE + 40, BOARD_SIZE - 25))
    for i, label in enumerate(ranks):
        text = font.render(label, True, BOARD_COLORS['text_muted'])
        screen.blit(text, (8, i * SQUARE_SIZE + 8))

def draw_board():
    screen.fill(BOARD_COLORS['background'])
    for row in range(8):
        for col in range(8):
            color = BOARD_COLORS['light_square'] if (row+col)%2==0 else BOARD_COLORS['dark_square']
            pygame.draw.rect(screen, color, [col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE])

    pygame.draw.rect(screen, BOARD_COLORS['panel'], [0, BOARD_SIZE, WIDTH, HEIGHT-BOARD_SIZE])
    pygame.draw.rect(screen, BOARD_COLORS['panel_dark'], [12, 812, 776, 76], border_radius=24)
    pygame.draw.rect(screen, BOARD_COLORS['border'], [0, BOARD_SIZE, WIDTH, HEIGHT-BOARD_SIZE], 3)
    pygame.draw.rect(screen, BOARD_COLORS['border'], [SIDEBAR_X, 0, WIDTH-SIDEBAR_X, HEIGHT], 3)

    status_text = ['White: Select a Piece', 'White: Choose Destination',
                   'Black: Select a Piece', 'Black: Choose Destination']
    screen.blit(big_font.render(status_text[turn_step], True, BOARD_COLORS['text']), (28, 823))

    for i in range(9):
        pygame.draw.line(screen, BOARD_COLORS['capture'], (0, SQUARE_SIZE*i), (BOARD_SIZE, SQUARE_SIZE*i), 2)
        pygame.draw.line(screen, BOARD_COLORS['capture'], (SQUARE_SIZE*i, 0), (SQUARE_SIZE*i, BOARD_SIZE), 2)

    draw_coordinate_labels()

    # Sidebar cards
    draw_sidebar_card(20,  110, 'Match Dashboard',   'Local two-player chess')
    draw_sidebar_card(145, 160, 'Captured Pieces',   'Black left, white right')
    draw_sidebar_card(320, 135, 'Controls',          'Forfeit button below')
    pygame.draw.rect(screen, BOARD_COLORS['panel_dark'], [820, 815, 160, 58], border_radius=18)
    pygame.draw.rect(screen, BOARD_COLORS['border'],     [820, 815, 160, 58], 2, border_radius=18)
    screen.blit(medium_font.render('FORFEIT', True, BOARD_COLORS['text']), (828, 823))
    draw_selection_panel()

    # Rotation indicator
    perspective = 'White' if board_flipped else 'Black'
    ind = font.render(f'Perspective: {perspective}', True, BOARD_COLORS['border'])
    screen.blit(ind, (820, 460))

def draw_sidebar_card(top, height, title, subtitle=''):
    pygame.draw.rect(screen, BOARD_COLORS['panel_dark'], [815, top, 170, height], border_radius=18)
    pygame.draw.rect(screen, BOARD_COLORS['panel_light'], [822, top+8, 156, height-16], border_radius=14)
    screen.blit(font.render(title, True, BOARD_COLORS['text']), (830, top+18))
    if subtitle:
        screen.blit(font.render(subtitle, True, BOARD_COLORS['text_muted']), (830, top+48))

def draw_selection_panel():
    title = 'No Piece Selected'
    sub   = 'Pick a piece to see moves.'
    if selection != 100:
        team  = 'White' if turn_step < 2 else 'Black'
        title = f'{team} {selected_piece.title()}'
        sub   = 'Click a move or click again to cancel.'
    draw_sidebar_card(700, 110, title, sub)

def draw_pieces():
    for i,piece in enumerate(white_pieces):
        px, py = board_to_screen(white_locations[i][0], white_locations[i][1])
        idx = piece_list.index(piece)
        if piece == 'pawn':
            img = white_pawn
            screen.blit(img, (px+22, py+30))
        else:
            screen.blit(white_images[idx], (px+10, py+10))
        if turn_step < 2 and selection == i:
            pygame.draw.rect(screen, get_selection_outline(),
                             [px+2, py+2, SQUARE_SIZE-4, SQUARE_SIZE-4], 4, border_radius=8)

    for i,piece in enumerate(black_pieces):
        px, py = board_to_screen(black_locations[i][0], black_locations[i][1])
        idx = piece_list.index(piece)
        if piece == 'pawn':
            screen.blit(black_pawn, (px+22, py+30))
        else:
            screen.blit(black_images[idx], (px+10, py+10))
        if turn_step >= 2 and selection == i:
            pygame.draw.rect(screen, get_selection_outline(),
                             [px+2, py+2, SQUARE_SIZE-4, SQUARE_SIZE-4], 4, border_radius=8)

def draw_valid(moves):
    color  = BOARD_COLORS['valid_white'] if turn_step < 2 else BOARD_COLORS['valid_black']
    enemies = black_locations if turn_step < 2 else white_locations
    for move in moves:
        px, py = board_to_screen(move[0], move[1])
        cx, cy = px+50, py+50
        if move in enemies:
            pygame.draw.circle(screen, BOARD_COLORS['capture'], (cx,cy), 26, 4)
            pygame.draw.circle(screen, color, (cx,cy), 18, 3)
        else:
            pygame.draw.circle(screen, color, (cx,cy), 12)

def draw_castling(moves):
    color = BOARD_COLORS['valid_white'] if turn_step < 2 else BOARD_COLORS['valid_black']
    for m in moves:
        px0,py0 = board_to_screen(m[0][0], m[0][1])
        px1,py1 = board_to_screen(m[1][0], m[1][1])
        pygame.draw.circle(screen, color, (px0+50, py0+70), 8)
        screen.blit(font.render('king', True, BOARD_COLORS['text']), (px0+30, py0+70))
        pygame.draw.circle(screen, color, (px1+50, py1+70), 8)
        screen.blit(font.render('rook', True, BOARD_COLORS['text']), (px1+30, py1+70))
        pygame.draw.line(screen, color, (px0+50, py0+70), (px1+50, py1+70), 2)

def draw_captured():
    for i,piece in enumerate(captured_pieces_white):
        idx = piece_list.index(piece)
        screen.blit(small_black_images[idx], (825, 5+50*i))
    for i,piece in enumerate(captured_pieces_black):
        idx = piece_list.index(piece)
        screen.blit(small_white_images[idx], (925, 5+50*i))

def draw_check():
    global check
    check = False
    if turn_step < 2 and 'king' in white_pieces:
        ki  = white_pieces.index('king')
        kloc = white_locations[ki]
        for opts in black_options:
            if kloc in opts:
                check = True
                if counter < 15:
                    px,py = board_to_screen(kloc[0], kloc[1])
                    pygame.draw.rect(screen, 'dark red',
                                     [px+2,py+2,SQUARE_SIZE-4,SQUARE_SIZE-4], 5, border_radius=8)
    elif 'king' in black_pieces:
        ki  = black_pieces.index('king')
        kloc = black_locations[ki]
        for opts in white_options:
            if kloc in opts:
                check = True
                if counter < 15:
                    px,py = board_to_screen(kloc[0], kloc[1])
                    pygame.draw.rect(screen, 'dark blue',
                                     [px+2,py+2,SQUARE_SIZE-4,SQUARE_SIZE-4], 5, border_radius=8)

def draw_hover_highlight():
    if hover_square:
        px,py = board_to_screen(hover_square[0], hover_square[1])
        pygame.draw.rect(screen, BOARD_COLORS['hover'],
                         [px+6, py+6, SQUARE_SIZE-12, SQUARE_SIZE-12], 3, border_radius=10)

def draw_last_move():
    for sq in last_move:
        px,py = board_to_screen(sq[0], sq[1])
        pygame.draw.rect(screen, BOARD_COLORS['last_move'],
                         [px+10, py+10, SQUARE_SIZE-20, SQUARE_SIZE-20], 3, border_radius=10)

def draw_promotion():
    pygame.draw.rect(screen, BOARD_COLORS['panel_dark'], [805, 0, 190, 420], border_radius=18)
    promotions = white_promotions if white_promote else black_promotions
    images     = white_images     if white_promote else black_images
    for i,piece in enumerate(promotions):
        idx = piece_list.index(piece)
        screen.blit(images[idx], (860, 5+100*i))
    pygame.draw.rect(screen, BOARD_COLORS['border'], [805, 0, 190, 420], 3, border_radius=18)

def check_promo_select():
    mx,my = pygame.mouse.get_pos()
    left  = pygame.mouse.get_pressed()[0]
    xp,yp = mx//100, my//100
    if white_promote and left and xp > 7 and yp < 4:
        white_pieces[promo_index] = white_promotions[yp]
    elif black_promote and left and xp > 7 and yp < 4:
        black_pieces[promo_index] = black_promotions[yp]

def draw_game_over():
    pygame.draw.rect(screen, 'black', [200, 200, 400, 70])
    screen.blit(font.render(f'{winner} won the game!', True, 'white'), (210, 210))
    screen.blit(font.render('Press ENTER to Restart!', True, 'white'), (210, 240))

# ── Rotation animation ────────────────────────────────────────────────────────
def draw_rotating_board(angle):
    """
    Render the board into a temp surface and draw it rotated around the centre
    of the board area.  Called only while rotating=True.
    """
    # Build the board frame into a temp surface
    board_surf = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
    board_surf.fill(BOARD_COLORS['background'])
    for row in range(8):
        for col in range(8):
            c = BOARD_COLORS['light_square'] if (row+col)%2==0 else BOARD_COLORS['dark_square']
            pygame.draw.rect(board_surf, c, [col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE])
    for i in range(9):
        pygame.draw.line(board_surf, BOARD_COLORS['capture'], (0,SQUARE_SIZE*i),(BOARD_SIZE,SQUARE_SIZE*i),2)
        pygame.draw.line(board_surf, BOARD_COLORS['capture'], (SQUARE_SIZE*i,0),(SQUARE_SIZE*i,BOARD_SIZE),2)

    # Rotate and blit
    rotated = pygame.transform.rotate(board_surf, angle % 360)
    rx = BOARD_SIZE//2 - rotated.get_width()//2
    ry = BOARD_SIZE//2 - rotated.get_height()//2
    screen.blit(rotated, (rx, ry))

def start_rotation():
    """Begin a 180° rotation animation."""
    global rotating, rotation_angle, rotation_target
    rotating         = True
    rotation_angle   = 0.0
    rotation_target  = 180.0

def update_rotation():
    """Advance rotation animation; flip board_flipped when done."""
    global rotating, rotation_angle, board_flipped
    if not rotating:
        return
    degrees_per_ms = 180 / ROTATION_DURATION_MS
    rotation_angle += degrees_per_ms * frame_time_ms
    if rotation_angle >= rotation_target:
        rotation_angle = rotation_target
        rotating       = False
        board_flipped  = not board_flipped

# ── Initial option calculation ────────────────────────────────────────────────
black_options = check_options(black_pieces, black_locations, 'black')
white_options = check_options(white_pieces, white_locations, 'white')

# ── Main game loop ────────────────────────────────────────────────────────────
run = True
while run:
    frame_time_ms = timer.tick(fps)
    counter = (counter + 1) % 30

    # Hover square (in logical board coords)
    mouse_pos = pygame.mouse.get_pos()
    raw = screen_to_board(mouse_pos[0], mouse_pos[1])
    hover_square = raw if raw and not rotating else None
    pygame.mouse.set_cursor(
        pygame.SYSTEM_CURSOR_HAND if hover_square else pygame.SYSTEM_CURSOR_ARROW)

    # ── Draw ──────────────────────────────────────────────────────────────────
    if rotating:
        # During rotation: draw static UI + animated board
        screen.fill(BOARD_COLORS['background'])
        # Progress angle: go 0→180
        draw_rotating_board(rotation_angle)
        # Draw sidebar / status on top
        pygame.draw.rect(screen, BOARD_COLORS['panel'], [0, BOARD_SIZE, WIDTH, HEIGHT-BOARD_SIZE])
        pygame.draw.rect(screen, BOARD_COLORS['panel_dark'], [12, 812, 776, 76], border_radius=24)
        screen.blit(big_font.render('Rotating board...', True, BOARD_COLORS['border']), (28, 823))
        pygame.draw.rect(screen, BOARD_COLORS['border'], [SIDEBAR_X, 0, WIDTH-SIDEBAR_X, HEIGHT], 3)
        update_rotation()
    else:
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

    # ── Events ────────────────────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                and not game_over and not rotating:
            click = screen_to_board(event.pos[0], event.pos[1])
            # Sidebar click (outside board area)
            if click is None:
                xc = event.pos[0] // SQUARE_SIZE
                yc = event.pos[1] // SQUARE_SIZE
                click = (xc, yc)

            # ── White's turn ──────────────────────────────────────────────────
            if turn_step <= 1:
                if click in ((8,8),(9,8)):
                    winner = 'black'
                if click in white_locations:
                    si = white_locations.index(click)
                    if selection == si and turn_step == 1:
                        selection = 100; valid_moves = []; selected_piece = ''; turn_step = 0
                    else:
                        selection = si; selected_piece = white_pieces[si]
                        if turn_step == 0: turn_step = 1
                if click in valid_moves and selection != 100:
                    start = white_locations[selection]
                    white_ep = check_ep(white_locations[selection], click)
                    white_locations[selection] = click
                    white_moved[selection] = True
                    last_move = [start, click]
                    if click in black_locations:
                        bi = black_locations.index(click)
                        captured_pieces_white.append(black_pieces[bi])
                        if black_pieces[bi] == 'king': winner = 'white'
                        black_pieces.pop(bi); black_locations.pop(bi); black_moved.pop(bi)
                    if click == black_ep:
                        bi = black_locations.index((black_ep[0], black_ep[1]-1))
                        captured_pieces_white.append(black_pieces[bi])
                        black_pieces.pop(bi); black_locations.pop(bi); black_moved.pop(bi)
                    black_options = check_options(black_pieces, black_locations, 'black')
                    white_options = check_options(white_pieces, white_locations, 'white')
                    turn_step = 2; selection = 100; selected_piece = ''; valid_moves = []
                    start_rotation()   # ← rotate to black's perspective
                elif selection != 100 and selected_piece == 'king':
                    for q,cm in enumerate(castling_moves):
                        if click == cm[0]:
                            start = white_locations[selection]
                            white_locations[selection] = click
                            white_moved[selection] = True
                            rc = (0,0) if click==(1,0) else (7,0)
                            ri = white_locations.index(rc)
                            white_locations[ri] = castling_moves[q][1]
                            last_move = [start, click]
                            black_options = check_options(black_pieces, black_locations, 'black')
                            white_options = check_options(white_pieces, white_locations, 'white')
                            turn_step = 2; selection = 100; selected_piece = ''; valid_moves = []
                            start_rotation()   # ← rotate

            # ── Black's turn ──────────────────────────────────────────────────
            if turn_step > 1:
                if click in ((8,8),(9,8)):
                    winner = 'white'
                if click in black_locations:
                    si = black_locations.index(click)
                    if selection == si and turn_step == 3:
                        selection = 100; valid_moves = []; selected_piece = ''; turn_step = 2
                    else:
                        selection = si; selected_piece = black_pieces[si]
                        if turn_step == 2: turn_step = 3
                if click in valid_moves and selection != 100:
                    start = black_locations[selection]
                    black_ep = check_ep(black_locations[selection], click)
                    black_locations[selection] = click
                    black_moved[selection] = True
                    last_move = [start, click]
                    if click in white_locations:
                        wi = white_locations.index(click)
                        captured_pieces_black.append(white_pieces[wi])
                        if white_pieces[wi] == 'king': winner = 'black'
                        white_pieces.pop(wi); white_locations.pop(wi); white_moved.pop(wi)
                    if click == white_ep:
                        wi = white_locations.index((white_ep[0], white_ep[1]+1))
                        captured_pieces_black.append(white_pieces[wi])
                        white_pieces.pop(wi); white_locations.pop(wi); white_moved.pop(wi)
                    black_options = check_options(black_pieces, black_locations, 'black')
                    white_options = check_options(white_pieces, white_locations, 'white')
                    turn_step = 0; selection = 100; selected_piece = ''; valid_moves = []
                    start_rotation()   # ← rotate back to white's perspective
                elif selection != 100 and selected_piece == 'king':
                    for q,cm in enumerate(castling_moves):
                        if click == cm[0]:
                            start = black_locations[selection]
                            black_locations[selection] = click
                            black_moved[selection] = True
                            rc = (0,7) if click==(1,7) else (7,7)
                            ri = black_locations.index(rc)
                            black_locations[ri] = castling_moves[q][1]
                            last_move = [start, click]
                            black_options = check_options(black_pieces, black_locations, 'black')
                            white_options = check_options(white_pieces, white_locations, 'white')
                            turn_step = 0; selection = 100; selected_piece = ''; valid_moves = []
                            start_rotation()   # ← rotate

        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_RETURN:
                # Full reset
                game_over = False; winner = ''
                white_pieces    = ['rook','knight','bishop','king','queen','bishop','knight','rook',
                                   'pawn','pawn','pawn','pawn','pawn','pawn','pawn','pawn']
                white_locations = [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),
                                   (0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1)]
                white_moved     = [False]*16
                black_pieces    = ['rook','knight','bishop','king','queen','bishop','knight','rook',
                                   'pawn','pawn','pawn','pawn','pawn','pawn','pawn','pawn']
                black_locations = [(0,7),(1,7),(2,7),(3,7),(4,7),(5,7),(6,7),(7,7),
                                   (0,6),(1,6),(2,6),(3,6),(4,6),(5,6),(6,6),(7,6)]
                black_moved     = [False]*16
                captured_pieces_white = []; captured_pieces_black = []
                turn_step = 0; selection = 100; selected_piece = ''
                last_move = []; valid_moves = []
                board_flipped = True; rotating = False
                white_ep = (100,100); black_ep = (100,100)
                black_options = check_options(black_pieces, black_locations, 'black')
                white_options = check_options(white_pieces, white_locations, 'white')

    if winner != '':
        game_over = True
        draw_game_over()

    pygame.display.flip()

pygame.quit()
