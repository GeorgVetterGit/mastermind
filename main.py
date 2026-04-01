#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mastermind – a Pygame implementation.

Rules:
  - A secret code of 4 coloured pegs (from 6 colours, repeats allowed) is generated.
  - The player has 10 attempts to guess the code.
  - After each guess, feedback is given:
      ● Black peg  – correct colour in the correct position.
      ○ White peg  – correct colour in the wrong position.
  - The player wins by guessing the exact code within 10 attempts.

Controls:
  - Click a colour in the palette to select it.
  - Click a peg slot in the active row to place the selected colour.
  - Right-click a filled peg to clear it.
  - Press 1–6 to select a colour by number.
  - Press Enter or click Submit to evaluate the current guess.
  - Press N or click New Game to start over.
  - Press Escape to quit.
"""

import random
import sys
import pygame

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
W, H = 620, 820
FPS  = 60

# UI Colours
BG         = (25,  25,  42)
PANEL      = (38,  38,  58)
HOLE_CLR   = (65,  65,  88)
WHITE      = (255, 255, 255)
NEAR_BLACK = (20,  20,  20)
GRAY       = (140, 140, 160)
LGRAY      = (200, 200, 218)
GOLD       = (218, 185,  50)
G_OK       = ( 60, 200, 100)
R_ERR      = (210,  70,  70)
HIGHLIGHT  = ( 60,  60,  85)
BTN_BLUE   = ( 65, 125, 200)
BTN_GREEN  = ( 55, 150,  75)
BTN_DGRAY  = ( 70,  70,  90)

# Game peg colours
PEG_PALETTE = [
    (218,  55,  55),   # 0 – Red
    ( 55, 195,  70),   # 1 – Green
    ( 65, 130, 228),   # 2 – Blue
    (228, 198,  45),   # 3 – Yellow
    (228, 122,  45),   # 4 – Orange
    (172,  62, 222),   # 5 – Purple
]
COLOR_NAMES = ["Red", "Green", "Blue", "Yellow", "Orange", "Purple"]

N_COLORS = len(PEG_PALETTE)
CODE_LEN  = 4
MAX_TRIES = 10

# Board geometry

ROW_H   = 50
PEG_R   = 17
COL_GAP = 52   # horizontal centre-to-centre distance between code pegs

# Feedback mini-pegs (2 × 2 grid per row)

FB_R       = 7
FB_GAP     = 17    # distance between feedback peg centres

board_w = COL_GAP * (CODE_LEN - 1) + PEG_R * 2 + FB_GAP + FB_R * 4 + 28
BOARD_X = (W - board_w) // 2
BOARD_Y = 100

FEEDBACK_X = BOARD_X + board_w - 28   # x of left feedback column centre

# Colour palette strip (bottom area)
PAL_Y   = 660
PAL_X   = 32
PAL_GAP = 65
PAL_R   = 22

# Buttons
buttons_width = 2 * 122 + 18
buttons_x = (W - buttons_width) // 2
SUBMIT_RECT  = pygame.Rect(buttons_x, 760, 122, 42)
NEWGAME_RECT = pygame.Rect(buttons_x + 122 + 18, 760, 122, 42)

# ---------------------------------------------------------------------------
# Game logic
# ---------------------------------------------------------------------------

def make_secret() -> list[int]:
    return [random.randint(0, N_COLORS - 1) for _ in range(CODE_LEN)]


def score(secret: list[int], guess: list[int]) -> tuple[int, int]:
    """Return (black_pegs, white_pegs) feedback for a guess."""
    black = sum(s == g for s, g in zip(secret, guess))
    white = (
        sum(min(secret.count(c), guess.count(c)) for c in range(N_COLORS)) - black
    )
    return black, white


class Game:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.secret: list[int] = make_secret()
        self.guesses: list[tuple[list[int], tuple[int, int]]] = []
        self.current: list[int | None] = [None] * CODE_LEN
        self.selected: int = 0          # currently selected palette colour
        self.state: str = "playing"     # "playing" | "won" | "lost"

    # ------------------------------------------------------------------
    def place(self, col: int) -> None:
        """Place the selected colour into the given column of the active row."""
        if self.state == "playing":
            self.current[col] = self.selected

    def clear(self, col: int) -> None:
        """Remove the colour from the given column of the active row."""
        if self.state == "playing":
            self.current[col] = None

    def submit(self) -> None:
        """Evaluate the current guess and record feedback."""
        if self.state != "playing" or None in self.current:
            return
        fb = score(self.secret, self.current)
        self.guesses.append((list(self.current), fb))
        if fb[0] == CODE_LEN:
            self.state = "won"
        elif len(self.guesses) >= MAX_TRIES:
            self.state = "lost"
        else:
            self.current = [None] * CODE_LEN

    @property
    def attempt(self) -> int:
        return len(self.guesses)


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def _highlight(colour: tuple[int, int, int], amount: int = 55) -> tuple[int, int, int]:
    return tuple(min(255, v + amount) for v in colour)  # type: ignore[return-value]


def draw_peg(
    surface: pygame.Surface,
    x: int,
    y: int,
    colour_idx: int | None,
    r: int = PEG_R,
) -> None:
    if colour_idx is None:
        pygame.draw.circle(surface, HOLE_CLR, (x, y), r)
        pygame.draw.circle(surface, (88, 88, 112), (x, y), r, 2)
    else:
        c = PEG_PALETTE[colour_idx]
        pygame.draw.circle(surface, c, (x, y), r)
        # Specular highlight (top-left glint)
        pygame.draw.circle(surface, _highlight(c), (x - r // 3, y - r // 3), r // 3)
        pygame.draw.circle(surface, NEAR_BLACK, (x, y), r, 2)


def draw_feedback_row(
    surface: pygame.Surface, cx: int, cy: int, black: int, white: int
) -> None:
    """Draw a 2×2 grid of feedback mini-pegs centred at (cx, cy)."""
    positions = [
        (cx,          cy - FB_GAP // 2),
        (cx + FB_GAP, cy - FB_GAP // 2),
        (cx,          cy + FB_GAP // 2),
        (cx + FB_GAP, cy + FB_GAP // 2),
    ]
    colours = [NEAR_BLACK] * black + [WHITE] * white
    for i, pos in enumerate(positions):
        if i < len(colours):
            pygame.draw.circle(surface, colours[i], pos, FB_R)
            pygame.draw.circle(surface, (105, 105, 125), pos, FB_R, 1)
        else:
            pygame.draw.circle(surface, HOLE_CLR, pos, FB_R - 2)
            pygame.draw.circle(surface, (90, 90, 110), pos, FB_R - 2, 1)


def draw_button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    font: pygame.font.Font,
    colour: tuple[int, int, int] = BTN_BLUE,
    active: bool = True,
) -> None:
    bg = colour if active else BTN_DGRAY
    pygame.draw.rect(surface, bg, rect, border_radius=9)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=9)
    lbl = font.render(text, True, WHITE if active else GRAY)
    surface.blit(lbl, lbl.get_rect(center=rect.center))


# ---------------------------------------------------------------------------
# Main draw function
# ---------------------------------------------------------------------------

def draw(
    surface: pygame.Surface,
    game: Game,
    font_big: pygame.font.Font,
    font_med: pygame.font.Font,
    font_sm: pygame.font.Font,
) -> None:
    surface.fill(BG)

    # ── Title ──────────────────────────────────────────────────────────────
    title = font_big.render("MASTERMIND", True, GOLD)
    surface.blit(title, title.get_rect(centerx=W // 2, y=14))

    # ── Board panel ────────────────────────────────────────────────────────
    board_rect = pygame.Rect(BOARD_X - 12, BOARD_Y - 8, board_w, ROW_H * MAX_TRIES + 16)
    pygame.draw.rect(surface, PANEL, board_rect, border_radius=10)

    for row in range(MAX_TRIES):
        row_cy = BOARD_Y + row * ROW_H + ROW_H // 2

        # Highlight active row
        if row == game.attempt and game.state == "playing":
            hl = pygame.Rect(
                BOARD_X - 10,
                BOARD_Y + row * ROW_H,
                board_w - 4,
                ROW_H - 1,
            )
            pygame.draw.rect(surface, HIGHLIGHT, hl, border_radius=7)

        # Row number
        num_lbl = font_sm.render(str(row + 1), True, GRAY)
        surface.blit(num_lbl, (BOARD_X - 30, row_cy - 9))

        # Code pegs
        for col in range(CODE_LEN):
            px = BOARD_X + col * COL_GAP + PEG_R
            if row < game.attempt:
                draw_peg(surface, px, row_cy, game.guesses[row][0][col])
            elif row == game.attempt and game.state == "playing":
                draw_peg(surface, px, row_cy, game.current[col])
            else:
                draw_peg(surface, px, row_cy, None)

        # Feedback pegs
        if row < game.attempt:
            b, w = game.guesses[row][1]
            draw_feedback_row(surface, FEEDBACK_X - 23, row_cy, b, w)

    # ── Feedback legend ────────────────────────────────────────────────────
    legend_x = FEEDBACK_X + FB_GAP + FB_R + 10
    pygame.draw.circle(surface, NEAR_BLACK, (legend_x, BOARD_Y + 13), 6)
    pygame.draw.circle(surface, (105, 105, 125), (legend_x, BOARD_Y + 13), 6, 1)
    surface.blit(font_sm.render("= right place", True, GRAY), (legend_x + 10, BOARD_Y + 1))
    pygame.draw.circle(surface, WHITE, (legend_x, BOARD_Y + 27), 6)
    pygame.draw.circle(surface, (105, 105, 125), (legend_x, BOARD_Y + 27), 6, 1)
    surface.blit(font_sm.render("= right colour", True, GRAY), (legend_x + 10, BOARD_Y + 15))

    # ── Separator ──────────────────────────────────────────────────────────
    sep_y = BOARD_Y + MAX_TRIES * ROW_H + 20
    pygame.draw.line(surface, (70, 70, 95), (22, sep_y), (W - 22, sep_y), 1)

    # ── Status message ─────────────────────────────────────────────────────
    if game.state == "won":
        msg = font_med.render(
            f"🎉  You cracked it in {game.attempt} guess{'es' if game.attempt != 1 else ''}!",
            True, G_OK,
        )
        surface.blit(msg, msg.get_rect(centerx=W // 2, y=sep_y + 6))
        # Reveal secret
        lbl = font_sm.render("Secret:", True, LGRAY)
        surface.blit(lbl, (BOARD_X + 2, sep_y + 34))
        for i, c in enumerate(game.secret):
            draw_peg(surface, BOARD_X + 75 + i * 44, sep_y + 42, c, r=13)

    elif game.state == "lost":
        msg = font_med.render("No more attempts! The secret was:", True, R_ERR)
        surface.blit(msg, msg.get_rect(centerx=W // 2, y=sep_y + 6))
        for i, c in enumerate(game.secret):
            draw_peg(surface, W // 2 - 75 + i * 44, sep_y + 38, c, r=13)

    # ── Colour palette ─────────────────────────────────────────────────────
    pal_label = font_sm.render("Colour palette  (1–6):", True, LGRAY)
    surface.blit(pal_label, (PAL_X, PAL_Y - 30))

    for i in range(N_COLORS):
        cx = PAL_X + i * PAL_GAP + PAL_R
        cy = PAL_Y + PAL_R + 10
        c  = PEG_PALETTE[i]
        pygame.draw.circle(surface, c, (cx, cy), PAL_R)
        pygame.draw.circle(surface, _highlight(c), (cx - PAL_R // 3, cy - PAL_R // 3), PAL_R // 3)
        if i == game.selected:
            pygame.draw.circle(surface, WHITE, (cx, cy), PAL_R + 4, 3)
        else:
            pygame.draw.circle(surface, (100, 100, 118), (cx, cy), PAL_R, 2)
        num = font_sm.render(str(i + 1), True, LGRAY)
        surface.blit(num, (cx - 4, cy + PAL_R + 3))

    # ── Selected colour preview ────────────────────────────────────────────
    sel_x = PAL_X + 6 * PAL_GAP + PAL_R + 18
    surface.blit(font_sm.render("Selected:", True, LGRAY), (sel_x, PAL_Y - 30))
    sc = PEG_PALETTE[game.selected]
    pygame.draw.circle(surface, sc, (sel_x + 24, PAL_Y + PAL_R + 10), PAL_R + 4)
    pygame.draw.circle(surface, _highlight(sc), (sel_x + 24 - (PAL_R + 4) // 3, PAL_Y + PAL_R + 10 - (PAL_R + 4) // 3), (PAL_R + 4) // 3)
    pygame.draw.circle(surface, WHITE, (sel_x + 24, PAL_Y + PAL_R + 10), PAL_R + 4, 3)
    sel_name = font_sm.render(COLOR_NAMES[game.selected], True, LGRAY)
    surface.blit(sel_name, sel_name.get_rect(centerx=sel_x + 24, y=(PAL_Y + PAL_R + 10) + PAL_R + 3))

    # ── Buttons ────────────────────────────────────────────────────────────
    can_submit = None not in game.current and game.state == "playing"
    draw_button(surface, SUBMIT_RECT, "Submit", font_med, BTN_BLUE, active=can_submit)
    draw_button(surface, NEWGAME_RECT, "New Game", font_sm, BTN_GREEN, active=True)

    pygame.display.flip()


# ---------------------------------------------------------------------------
# Hit-testing helpers
# ---------------------------------------------------------------------------

def peg_center(row: int, col: int) -> tuple[int, int]:
    x = BOARD_X + col * COL_GAP + PEG_R
    y = BOARD_Y + row * ROW_H + ROW_H // 2
    return x, y


def palette_index(mx: int, my: int) -> int | None:
    for i in range(N_COLORS):
        cx = PAL_X + i * PAL_GAP + PAL_R
        cy = PAL_Y + PAL_R
        if (mx - cx) ** 2 + (my - cy) ** 2 <= (PAL_R + 4) ** 2:
            return i
    return None


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Mastermind")
    clock = pygame.time.Clock()

    font_big = pygame.font.SysFont("segoeui", 38, bold=True)
    font_med = pygame.font.SysFont("segoeui", 21, bold=True)
    font_sm  = pygame.font.SysFont("segoeui", 15)

    game = Game()

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                # Select colour via number key
                if pygame.K_1 <= event.key <= pygame.K_6:
                    game.selected = event.key - pygame.K_1

                # Submit on Enter
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    game.submit()

                # New game
                if event.key == pygame.K_n:
                    game.reset()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # Palette selection (left or right click)
                pi = palette_index(mx, my)
                if pi is not None:
                    game.selected = pi
                    continue

                # Submit button
                if event.button == 1 and SUBMIT_RECT.collidepoint(mx, my):
                    game.submit()
                    continue

                # New game button
                if event.button == 1 and NEWGAME_RECT.collidepoint(mx, my):
                    game.reset()
                    continue

                # Peg slots in the active row
                if game.state == "playing":
                    row = game.attempt
                    for col in range(CODE_LEN):
                        px, py = peg_center(row, col)
                        if (mx - px) ** 2 + (my - py) ** 2 <= PEG_R ** 2:
                            if event.button == 1:
                                game.place(col)
                            elif event.button == 3:
                                game.clear(col)
                            break

        draw(screen, game, font_big, font_med, font_sm)


if __name__ == "__main__":
    main()
