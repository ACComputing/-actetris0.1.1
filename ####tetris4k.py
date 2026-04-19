import pygame
import random
import sys
import numpy as np

# Initialize Pygame and Mixer
pygame.init()
pygame.mixer.quit()
# channels=1 ensures mono sound, required for our 1D numpy arrays
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

WIDTH, HEIGHT = 800, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AC's 8-Bit Tetris")
clock = pygame.time.Clock()
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

COLORS = {
    'I': CYAN, 'O': YELLOW, 'T': PURPLE,
    'S': GREEN, 'Z': RED, 'J': BLUE, 'L': ORANGE
}

# Game grid
GRID_W = 10
GRID_H = 20
CELL = 32
GRID_X = (WIDTH - GRID_W * CELL) // 2
GRID_Y = 80

# Tetromino shapes
tetrominoes = {
    'I': [
        [[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]],
        [[0,0,1,0], [0,0,1,0], [0,0,1,0], [0,0,1,0]],
        [[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]],
        [[0,0,1,0], [0,0,1,0], [0,0,1,0], [0,0,1,0]]
    ],
    'O': [
        [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
        [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
        [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
        [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]]
    ],
    'T': [
        [[0,1,0,0], [1,1,1,0], [0,0,0,0], [0,0,0,0]],
        [[0,1,0,0], [0,1,1,0], [0,1,0,0], [0,0,0,0]],
        [[0,0,0,0], [1,1,1,0], [0,1,0,0], [0,0,0,0]],
        [[0,1,0,0], [1,1,0,0], [0,1,0,0], [0,0,0,0]]
    ],
    'S': [
        [[0,0,0,0], [0,1,1,0], [1,1,0,0], [0,0,0,0]],
        [[0,1,0,0], [0,1,1,0], [0,0,1,0], [0,0,0,0]],
        [[0,0,0,0], [0,1,1,0], [1,1,0,0], [0,0,0,0]],
        [[0,1,0,0], [0,1,1,0], [0,0,1,0], [0,0,0,0]]
    ],
    'Z': [
        [[0,0,0,0], [1,1,0,0], [0,1,1,0], [0,0,0,0]],
        [[0,0,1,0], [0,1,1,0], [0,1,0,0], [0,0,0,0]],
        [[0,0,0,0], [1,1,0,0], [0,1,1,0], [0,0,0,0]],
        [[0,0,1,0], [0,1,1,0], [0,1,0,0], [0,0,0,0]]
    ],
    'J': [
        [[0,1,0,0], [0,1,0,0], [1,1,0,0], [0,0,0,0]],
        [[1,0,0,0], [1,1,1,0], [0,0,0,0], [0,0,0,0]],
        [[0,1,1,0], [0,1,0,0], [0,1,0,0], [0,0,0,0]],
        [[0,0,0,0], [1,1,1,0], [0,0,1,0], [0,0,0,0]]
    ],
    'L': [
        [[0,1,0,0], [0,1,0,0], [0,1,1,0], [0,0,0,0]],
        [[0,0,0,0], [1,1,1,0], [1,0,0,0], [0,0,0,0]],
        [[1,1,0,0], [0,1,0,0], [0,1,0,0], [0,0,0,0]],
        [[0,0,1,0], [1,1,1,0], [0,0,0,0], [0,0,0,0]]
    ]
}

# Game state
grid = [[0 for _ in range(GRID_W)] for _ in range(GRID_H)]
score = 0
level = 1
lines_cleared = 0
current_type = None
current_x = 0
current_y = 0
current_rot = 0
next_type = None
last_fall = 0
fall_delay = 500
game_state = "menu"

# --- FULL KOROBEINIKI MELODY (GAME BOY TYPE A OST) ---
# Frequencies (Adjusted slightly for chip-tune tuning)
E5, B4, C5, D5 = 659.25, 493.88, 523.25, 587.33
A4, F5, G5, A5 = 440.00, 698.46, 783.99, 880.00
Ab4 = 415.30 # Used in the classic transition

# Timing in milliseconds (Authentic fast tempo)
Q = 360  # Quarter note
E = 180  # Eighth note

part_a = [
    (E5, Q), (B4, E), (C5, E), (D5, Q), (C5, E), (B4, E),
    (A4, Q), (A4, E), (C5, E), (E5, Q), (D5, E), (C5, E),
    (B4, Q+E), (C5, E), (D5, Q), (E5, Q),
    (C5, Q), (A4, Q), (A4, Q), (0, Q)
]

part_b = [
    (D5, Q+E), (F5, E), (A5, Q), (G5, E), (F5, E),
    (E5, Q+E), (C5, E), (E5, Q), (D5, E), (C5, E),
    (B4, Q), (B4, E), (C5, E), (D5, Q), (E5, Q),
    (C5, Q), (A4, Q), (A4, Q), (0, Q)
]

# The complete song structure: Part A plays twice, then Part B, then loops.
melody = part_a + part_a + part_b

note_event = pygame.USEREVENT + 1
current_note_idx = 0

def play_note():
    """Generate and play a harsh 90s Game Boy style square wave."""
    global current_note_idx
    if game_state != "playing":
        return
    
    freq, duration = melody[current_note_idx]
    
    if freq > 0:
        sample_rate = 44100
        # Play for 85% of duration for the discrete, bouncy 8-bit separation
        play_dur = (duration * 0.85) / 1000.0 
        n_samples = int(sample_rate * play_dur)
        t = np.linspace(0, play_dur, n_samples, endpoint=False)
        
        # 8-BIT MAGIC: Using np.sign to turn the smooth sine into a harsh SQUARE WAVE
        # Volume is kept very low (0.10) because square waves are inherently loud
        wave = np.sign(np.sin(2 * np.pi * freq * t)) * 0.10
        
        # Audio Envelope: Fade in slightly and fade out to prevent speaker clicking
        fade_in = int(n_samples * 0.05)
        fade_out = int(n_samples * 0.15)
        envelope = np.ones(n_samples)
        
        if fade_in > 0:
            envelope[:fade_in] = np.linspace(0, 1, fade_in)
        if fade_out > 0:
            envelope[-fade_out:] = np.linspace(1, 0, fade_out)
            
        wave = wave * envelope
        
        # Convert to 16-bit integer array matching Pygame mixer requirements
        audio_data = np.int16(wave * 32767)
        sound = pygame.mixer.Sound(buffer=np.ascontiguousarray(audio_data))
        sound.play()
    
    # Schedule the next note event precisely based on the current note's full duration
    pygame.time.set_timer(note_event, int(duration))
    
    # Advance to the next note. When it hits the end of the full OST array, it loops.
    current_note_idx += 1
    if current_note_idx >= len(melody):
        current_note_idx = 0

def start_tetris_theme():
    global current_note_idx
    current_note_idx = 0
    play_note()

def stop_tetris_theme():
    pygame.time.set_timer(note_event, 0)
    pygame.mixer.stop()

def draw_tetromino(typ, rot, start_x, start_y):
    if typ not in tetrominoes:
        return
    shape = tetrominoes[typ][rot]
    color = COLORS[typ]
    for i in range(4):
        for j in range(4):
            if shape[i][j]:
                rect_x = start_x + j * CELL
                rect_y = start_y + i * CELL
                pygame.draw.rect(screen, color, (rect_x, rect_y, CELL, CELL))
                pygame.draw.rect(screen, WHITE, (rect_x, rect_y, CELL, CELL), 2)

def draw_board():
    for y in range(GRID_H):
        for x in range(GRID_W):
            cell_x = GRID_X + x * CELL
            cell_y = GRID_Y + y * CELL
            if grid[y][x] != 0:
                pygame.draw.rect(screen, COLORS[grid[y][x]], (cell_x, cell_y, CELL, CELL))
                pygame.draw.rect(screen, WHITE, (cell_x, cell_y, CELL, CELL), 2)
            pygame.draw.rect(screen, DARK_GRAY, (cell_x, cell_y, CELL, CELL), 1)

def check_collision(x, y, rot):
    shape = tetrominoes[current_type][rot]
    for i in range(4):
        for j in range(4):
            if shape[i][j]:
                gx = x + j
                gy = y + i
                if gx < 0 or gx >= GRID_W or gy >= GRID_H:
                    return True
                if gy >= 0 and grid[gy][gx] != 0:
                    return True
    return False

def new_piece():
    global current_type, current_x, current_y, current_rot, next_type, game_state
    current_type = next_type
    next_type = random.choice(list(tetrominoes.keys()))
    current_rot = 0
    current_x = GRID_W // 2 - 2
    current_y = -2
    if check_collision(current_x, current_y, current_rot):
        game_state = "gameover"
        stop_tetris_theme()

def lock_piece():
    global score
    shape = tetrominoes[current_type][current_rot]
    for i in range(4):
        for j in range(4):
            if shape[i][j]:
                gx = current_x + j
                gy = current_y + i
                if gy >= 0:
                    grid[gy][gx] = current_type
    clear_lines()
    new_piece()

def clear_lines():
    global score, lines_cleared, level, grid
    full_lines = [y for y in range(GRID_H) if all(grid[y])]
    if full_lines:
        for y in sorted(full_lines, reverse=True):
            del grid[y]
            grid.insert(0, [0] * GRID_W)
        num = len(full_lines)
        lines_cleared += num
        score_table = {1: 40, 2: 100, 3: 300, 4: 1200}
        score += score_table.get(num, 0) * level
        level = lines_cleared // 10 + 1

def reset_game():
    global grid, score, level, lines_cleared, last_fall, fall_delay, next_type, game_state
    grid = [[0 for _ in range(GRID_W)] for _ in range(GRID_H)]
    score = 0
    level = 1
    lines_cleared = 0
    next_type = random.choice(list(tetrominoes.keys()))
    new_piece()
    last_fall = pygame.time.get_ticks()
    fall_delay = 500
    game_state = "playing"
    start_tetris_theme()

def draw_menu():
    screen.fill(BLACK)
    font_title = pygame.font.SysFont("arial", 72, bold=True)
    title_surf = font_title.render("AC's 8-Bit Tetris", True, CYAN)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, 180))
    screen.blit(title_surf, title_rect)
    
    draw_tetromino('I', 1, 80, 120)
    draw_tetromino('T', 0, WIDTH - 180, 140)
    draw_tetromino('O', 0, 100, 560)
    draw_tetromino('L', 0, WIDTH - 200, 560)
    
    font_sub = pygame.font.SysFont("arial", 28, bold=True)
    sub_surf = font_sub.render("CLASSIC BLOCK STACKING ACTION", True, WHITE)
    sub_rect = sub_surf.get_rect(center=(WIDTH // 2, 260))
    screen.blit(sub_surf, sub_rect)
    
    font_ctrl_head = pygame.font.SysFont("arial", 22, bold=True)
    font_ctrl = pygame.font.SysFont("arial", 18)
    ctrl_lines = [
        "CONTROLS",
        "Left / Right : Move",
        "Up : Rotate",
        "Down : Soft drop (+1 score)",
        "Space : Hard drop (+2 per cell dropped)",
        "Esc : Back to this menu (from game or game over)",
        "Esc here : Quit the program",
        "Full 8-Bit Korobeiniki plays while in-game.",
    ]
    cy = 300
    for i, line in enumerate(ctrl_lines):
        col = CYAN if i == 0 else (WHITE if i <= 6 else GRAY)
        f = font_ctrl_head if i == 0 else font_ctrl
        surf = f.render(line, True, col)
        screen.blit(surf, surf.get_rect(center=(WIDTH // 2, cy)))
        cy += 26 if i == 0 else 24

    font_prompt = pygame.font.SysFont("arial", 36)
    prompt_surf = font_prompt.render("PRESS SPACE TO START", True, WHITE)
    prompt_rect = prompt_surf.get_rect(center=(WIDTH // 2, 560))
    screen.blit(prompt_surf, prompt_rect)

    font_small = pygame.font.SysFont("arial", 16)
    credit = font_small.render("60 FPS • Pure Pygame • No Audio Files Used", True, DARK_GRAY)
    credit_rect = credit.get_rect(center=(WIDTH // 2, HEIGHT - 28))
    screen.blit(credit, credit_rect)

def draw_game():
    screen.fill(BLACK)
    draw_board()
    if current_type:
        draw_tetromino(current_type, current_rot, GRID_X + current_x * CELL, GRID_Y + current_y * CELL)
    
    next_label_font = pygame.font.SysFont("arial", 24, bold=True)
    next_label = next_label_font.render("NEXT", True, WHITE)
    screen.blit(next_label, (GRID_X + GRID_W * CELL + 40, GRID_Y - 30))
    if next_type:
        draw_tetromino(next_type, 0, GRID_X + GRID_W * CELL + 40, GRID_Y)
    
    panel_x = 50
    font_ui = pygame.font.SysFont("arial", 28, bold=True)
    screen.blit(font_ui.render("SCORE", True, GRAY), (panel_x, 120))
    screen.blit(font_ui.render(str(score), True, WHITE), (panel_x, 155))
    screen.blit(font_ui.render("LEVEL", True, GRAY), (panel_x, 220))
    screen.blit(font_ui.render(str(level), True, CYAN), (panel_x, 255))
    screen.blit(font_ui.render("LINES", True, GRAY), (panel_x, 320))
    screen.blit(font_ui.render(str(lines_cleared), True, WHITE), (panel_x, 355))
    
    inst_font = pygame.font.SysFont("arial", 18)
    for i, line in enumerate(["CONTROLS:", "← → : Move", "↑ : Rotate", "↓ : Soft Drop (+1 pt)", "SPACE : Hard Drop", "ESC : Menu"]):
        screen.blit(inst_font.render(line, True, WHITE if i == 0 else GRAY), (WIDTH - 180, 120 + i * 28))
    
    pygame.draw.line(screen, GRAY, (0, 60), (WIDTH, 60), 2)

def draw_gameover():
    screen.fill(BLACK)
    font_over = pygame.font.SysFont("arial", 64, bold=True)
    over_surf = font_over.render("GAME OVER", True, RED)
    screen.blit(over_surf, over_surf.get_rect(center=(WIDTH // 2, 220)))
    
    font_score = pygame.font.SysFont("arial", 36)
    score_surf = font_score.render(f"FINAL SCORE: {score}", True, WHITE)
    screen.blit(score_surf, score_surf.get_rect(center=(WIDTH // 2, 310)))
    
    font_stats = pygame.font.SysFont("arial", 24)
    stats_surf = font_stats.render(f"Level {level}  •  {lines_cleared} Lines Cleared", True, GRAY)
    screen.blit(stats_surf, stats_surf.get_rect(center=(WIDTH // 2, 360)))
    
    font_restart = pygame.font.SysFont("arial", 32)
    restart_surf = font_restart.render("PRESS SPACE TO PLAY AGAIN", True, CYAN)
    screen.blit(restart_surf, restart_surf.get_rect(center=(WIDTH // 2, 450)))
    
    font_hint = pygame.font.SysFont("arial", 20)
    hint_surf = font_hint.render("Or ESC to return to Menu", True, GRAY)
    screen.blit(hint_surf, hint_surf.get_rect(center=(WIDTH // 2, 500)))

# Main loop
running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Audio handler hooks right into the user event loop
        if event.type == note_event and game_state == "playing":
            play_note()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state in ("playing", "gameover"):
                    stop_tetris_theme()
                    game_state = "menu"
                else:
                    running = False
            
            if game_state == "menu" and event.key == pygame.K_SPACE:
                reset_game()
            
            elif game_state == "playing":
                if event.key == pygame.K_LEFT and not check_collision(current_x - 1, current_y, current_rot):
                    current_x -= 1
                elif event.key == pygame.K_RIGHT and not check_collision(current_x + 1, current_y, current_rot):
                    current_x += 1
                elif event.key == pygame.K_UP:
                    new_rot = (current_rot + 1) % 4
                    if not check_collision(current_x, current_y, new_rot):
                        current_rot = new_rot
                elif event.key == pygame.K_DOWN and not check_collision(current_x, current_y + 1, current_rot):
                    current_y += 1
                    score += 1
                elif event.key == pygame.K_SPACE:
                    drop_score = 0
                    while not check_collision(current_x, current_y + 1, current_rot):
                        current_y += 1
                        drop_score += 2
                    score += drop_score
                    lock_piece()
            
            elif game_state == "gameover" and event.key == pygame.K_SPACE:
                reset_game()
    
    if game_state == "playing":
        now = pygame.time.get_ticks()
        if now - last_fall >= fall_delay:
            if not check_collision(current_x, current_y + 1, current_rot):
                current_y += 1
            else:
                lock_piece()
            last_fall = now
        fall_delay = max(80, 500 - (level - 1) * 45)
    
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        draw_game()
    elif game_state == "gameover":
        draw_gameover()
    
    pygame.display.flip()

pygame.quit()
sys.exit()
