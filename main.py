import pygame, random
from pathlib import Path
from collections import Counter

WIDTH, HEIGHT = 1280, 900
FPS = 60

CARD_OFFSET_Y = 100
CARD_SPACING = 35
CARD_HOLDER_PADDING = 8

BUTTON_OFFSET_Y = 69
BUTTON_SPACING = 280

RESULT_OFFSET_Y = 200

DECK_OFFSET_X = 85
DECK_OFFSET_Y = -50

TITLE_OFFSET_Y = 40

HUD_OFFSET_Y = 120
HUD_CREDITS_X = 40
HUD_BET_X = 260

CARD_CREAM = (245, 235, 220)
CARD_CREAM_BORDER = (220, 205, 190)

GOLD = (212, 175, 55)
VELVET = (100, 10, 20)
WHITE = (255, 255, 255)
DARK = (40, 30, 30)
BTN_BG = (40, 40, 40)
BTN_HOVER = (80, 80, 80)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Luxury Royale — 5-Card Draw")
clock = pygame.time.Clock()

title_font = pygame.font.Font(None, 90)
hud_font   = pygame.font.Font(None, 38)
btn_font   = pygame.font.Font(None, 38)
res_font   = pygame.font.Font(None, 54)

BASE = Path(__file__).parent
ASSETS = BASE / "assets"
CARD_DIR = ASSETS / "cards"
SND_DIR = ASSETS / "sounds"

CARD_W, CARD_H = 150, 218

VALUES = ["2","3","4","5","6","7","8","9","10","jack","queen","king","ace"]
SUITS = ["clubs","diamonds","hearts","spades"]

def load_card(name):
    p = CARD_DIR / name
    if not p.exists():
        raise FileNotFoundError(f"Missing card asset: {p}")
    img = pygame.image.load(str(p)).convert_alpha()
    return pygame.transform.smoothscale(img, (CARD_W, CARD_H))

CARD_IMAGES = {(v,s): load_card(f"{v}_of_{s}.png") for v in VALUES for s in SUITS}
CARD_BACK = load_card("back.png")

DECK_BACK = CARD_BACK.copy()
DECK_BACK.fill(CARD_CREAM, special_flags=pygame.BLEND_RGBA_MULT)

def load_sound(name):
    p = SND_DIR / name
    if p.exists():
        try: return pygame.mixer.Sound(str(p))
        except: return None
    return None

SND_DEAL = load_sound("deal.wav")
SND_FLIP = load_sound("flip.wav")
SND_CLICK = load_sound("click.wav")
SND_WIN = load_sound("win.wav")

def play(snd):
    if snd:
        try: snd.play()
        except: pass

class CardObj:
    def __init__(self, v, s):
        self.value = v
        self.suit = s
        self.image = CARD_IMAGES[(v,s)]
        self.flipped = False
        self.held = False

class DeckObj:
    def __init__(self):
        self.reset()
    def reset(self):
        self.cards = [CardObj(v,s) for v in VALUES for s in SUITS]
        random.shuffle(self.cards)
    def draw(self, n):
        out = self.cards[-n:]
        self.cards = self.cards[:-n]
        return out

def rank_val(v):
    if v=="jack": return 11
    if v=="queen": return 12
    if v=="king": return 13
    if v=="ace": return 14
    return int(v)

def evaluate(hand):
    vals = sorted([rank_val(c.value) for c in hand], reverse=True)
    suits = [c.suit for c in hand]
    c = Counter(vals)
    cnts = sorted(c.values(), reverse=True)

    def is_straight(vs):
        s = sorted(set(vs))
        if len(s)!=5: return (False,0)
        if max(s)-min(s)==4: return (True,max(s))
        if set(s)=={14,5,4,3,2}: return (True,5)
        return (False,0)

    straight, top = is_straight(vals)
    flush = len(set(suits))==1

    if straight and flush and top==14: return "Royal Flush"
    if straight and flush: return "Straight Flush"
    if cnts[0]==4: return "Four of a Kind"
    if cnts[0]==3 and cnts[1]==2: return "Full House"
    if flush: return "Flush"
    if straight: return "Straight"
    if cnts[0]==3: return "Three of a Kind"
    if cnts[0]==2 and cnts[1]==2: return "Two Pair"
    if cnts[0]==2: return "One Pair"
    return "High Card"

REWARD = {
    "Royal Flush":500,
    "Straight Flush":250,
    "Four of a Kind": 100,
    "Full House": 60,
    "Flush": 40,
    "Straight": 20,
    "Three of a Kind": 30,
    "Two Pair": 20,
    "One Pair": 10,
    "High Card": 0
}

TOTAL_W = 5 * CARD_W + 4 * CARD_SPACING
START_X = (WIDTH - TOTAL_W)//2
CARD_Y = HEIGHT//2 + CARD_OFFSET_Y
POS = [(START_X + i*(CARD_W+CARD_SPACING), CARD_Y) for i in range(5)]
DECK_POS = (WIDTH - CARD_W - DECK_OFFSET_X, HEIGHT//2 - CARD_H//2 + DECK_OFFSET_Y)

class Button:
    def __init__(self, text, x, y):
        self.text = text
        self.rect = pygame.Rect(x, y, 170, 60)
        self.hover = False
    def draw(self):
        col = BTN_HOVER if self.hover else BTN_BG
        pygame.draw.rect(screen, col, self.rect, border_radius=12)
        pygame.draw.rect(screen, GOLD, self.rect, 3, border_radius=12)
        if self.hover:
            glow = pygame.Surface((self.rect.w+14, self.rect.h+14), pygame.SRCALPHA)
            pygame.draw.rect(glow,(255,215,0,60), glow.get_rect(), border_radius=14)
            screen.blit(glow,(self.rect.x-7,self.rect.y-7))
        txt = btn_font.render(self.text, True, WHITE)
        screen.blit(txt, txt.get_rect(center=self.rect.center))
    # separate hover update & click test to avoid double-processing
    def update_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)
    def test_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover:
            play(SND_CLICK)
            return True
        return False

btn_deal = Button("DEAL", WIDTH//2 - BUTTON_SPACING, HEIGHT - BUTTON_OFFSET_Y)
btn_restart = Button("Restart", WIDTH//2 - 2*BUTTON_SPACING, HEIGHT - BUTTON_OFFSET_Y)
btn_draw = Button("DRAW", WIDTH//2 - 80, HEIGHT - BUTTON_OFFSET_Y)
btn_new  = Button("NEW HAND", WIDTH//2 + BUTTON_SPACING, HEIGHT - BUTTON_OFFSET_Y)

def draw_scene(hand, state, credits, msg):
    screen.fill(VELVET)
    title = title_font.render("Luxury Royale Poker", True, GOLD)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, TITLE_OFFSET_Y))

    # HUD
    pygame.draw.rect(screen, DARK, (HUD_CREDITS_X, HUD_OFFSET_Y, 200, 55), border_radius=10)
    pygame.draw.rect(screen, GOLD, (HUD_CREDITS_X, HUD_OFFSET_Y, 200, 55), 3, border_radius=10)
    pygame.draw.rect(screen, DARK, (HUD_BET_X, HUD_OFFSET_Y, 150, 55), border_radius=10)
    pygame.draw.rect(screen, GOLD, (HUD_BET_X, HUD_OFFSET_Y, 150, 55), 3, border_radius=10)
    screen.blit(hud_font.render(f"Credits: {credits}", True, WHITE), (HUD_CREDITS_X+15, HUD_OFFSET_Y+15))
    screen.blit(hud_font.render(f"Bet: {10+count}", True, WHITE), (HUD_BET_X+15, HUD_OFFSET_Y+15))

    if msg:
        txt = res_font.render(msg, True, GOLD)
        shadow = res_font.render(msg, True, (20,10,10))
        screen.blit(shadow,(WIDTH//2 - txt.get_width()//2 +2, RESULT_OFFSET_Y+2))
        screen.blit(txt,(WIDTH//2 - txt.get_width()//2, RESULT_OFFSET_Y))

    screen.blit(DECK_BACK, DECK_POS)

    for i,c in enumerate(hand):
        x,y = POS[i]
        holder = pygame.Rect(x-CARD_HOLDER_PADDING, y-CARD_HOLDER_PADDING,
                             CARD_W+2*CARD_HOLDER_PADDING, CARD_H+2*CARD_HOLDER_PADDING)
        pygame.draw.rect(screen, CARD_CREAM, holder, border_radius=12)
        pygame.draw.rect(screen, CARD_CREAM_BORDER, holder, 2, border_radius=12)
        img = c.image if c.flipped else CARD_BACK
        screen.blit(img,(x,y))
        if c.held:
            pygame.draw.rect(screen, GOLD,(x-10,y-10,CARD_W+20,CARD_H+20),4,border_radius=12)

    if state=="START":
        if credits < 10+count:
            btn_restart.draw()
        else:
            btn_deal.draw()
    elif state=="DEALT":
        btn_draw.draw(); 
        btn_new.draw()
    elif state=="RESULT":
        btn_new.draw()

def animate_deal(hand):
    for i,c in enumerate(hand):
        tx,ty = POS[i]
        sx,sy = DECK_POS
        steps = 22
        for k in range(steps):
            t=(k+1)/steps
            draw_scene(hand, "DEALT", credits, result_msg)
            x=sx+(tx-sx)*t; y=sy+(ty-sy)*t
            screen.blit(CARD_BACK,(x,y))
            pygame.display.flip()
            clock.tick(FPS)
        play(SND_DEAL)

def flip_card(c, idx):
    x,y = POS[idx]
    cx,cy = x+CARD_W//2, y+CARD_H//2
    for w in range(CARD_W,0,-20):
        draw_scene(current_hand,"DEALT",credits,result_msg)
        img = pygame.transform.scale(CARD_BACK,(w,CARD_H))
        screen.blit(img,img.get_rect(center=(cx,cy)))
        pygame.display.flip(); clock.tick(FPS)
    play(SND_FLIP)
    for w in range(0,CARD_W+1,20):
        draw_scene(current_hand,"DEALT",credits,result_msg)
        img = pygame.transform.scale(c.image,(w,CARD_H))
        screen.blit(img,img.get_rect(center=(cx,cy)))
        pygame.display.flip(); clock.tick(FPS)
    c.flipped = True

deck = DeckObj()
current_hand = []
state = "START"
credits = 100
count = 0
result_msg = ""
draw_enabled = False

running = True
while running:
    events = pygame.event.get()
    mx,my = pygame.mouse.get_pos()
    btn_deal.update_hover((mx,my))
    btn_draw.update_hover((mx,my))
    btn_new.update_hover((mx,my))
    btn_restart.update_hover((mx,my))


    for ev in events:
        if ev.type == pygame.QUIT:
            running = False
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            running = False
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if state == "DEALT":
                for i,c in enumerate(current_hand):
                    if pygame.Rect(POS[i][0], POS[i][1], CARD_W, CARD_H).collidepoint(ev.pos):
                        c.held = not c.held
                        play(SND_CLICK)

            if state == "START" and btn_restart.test_click(ev):
                current_hand = []
                state = "START"
                credits = 100
                count = 0
                result_msg = ""
                draw_enabled = False

            if state == "START" and btn_deal.test_click(ev):
                if credits < 10+count:
                    result_msg = "Not enough credits"
                else:
                    credits -= 10+count
                    if len(deck.cards) < 5:
                        deck = DeckObj()
                    current_hand = deck.draw(5)
                    for c in current_hand:
                        c.flipped = False; c.held = False
                    draw_enabled = False
                    animate_deal(current_hand)
                    for i,c in enumerate(current_hand):
                        flip_card(c,i)
                    draw_enabled = True
                    state = "DEALT"
                    result_msg = "Select cards to HOLD, then DRAW"

            if state == "DEALT" and draw_enabled and btn_draw.test_click(ev):
                repl = [i for i,c in enumerate(current_hand) if not c.held]
                n = len(repl)
                if n > 0:
                    new_cards = deck.draw(n)
                    for idx in repl:
                        x,y = POS[idx]; cx,cy = x+CARD_W//2, y+CARD_H//2
                        for w in range(CARD_W,0,-20):
                            draw_scene(current_hand,"DEALT",credits,result_msg)
                            img = pygame.transform.scale(current_hand[idx].image,(w,CARD_H))
                            screen.blit(img,img.get_rect(center=(cx,cy)))
                            pygame.display.flip(); clock.tick(FPS)
                        current_hand[idx] = new_cards.pop()
                        current_hand[idx].flipped = False; current_hand[idx].held = False
                        sx,sy = DECK_POS; tx,ty = POS[idx]
                        for k in range(18):
                            t = (k+1)/18
                            draw_scene(current_hand,"DEALT",credits,result_msg)
                            x2 = sx + (tx - sx) * t; y2 = sy + (ty - sy) * t
                            screen.blit(CARD_BACK,(x2,y2))
                            pygame.display.flip(); clock.tick(FPS)
                        flip_card(current_hand[idx], idx)
                        play(SND_DEAL)
                draw_enabled = False
                name = evaluate(current_hand)
                reward = REWARD[name]
                credits += reward
                if reward > 0: play(SND_WIN)
                result_msg = f"{name} (+{reward})"
                state = "RESULT"

            if state == "RESULT" and btn_new.test_click(ev):
                count += 2
                draw_enabled = False
                state = "START"
                if credits < 10+count:
                    result_msg = """Not enough Credits, Want to Restart The Game ?!"""
                else:
                    result_msg = ""
                if len(deck.cards) < 10:
                    deck = DeckObj()

    draw_scene(current_hand if current_hand else [], state, credits, result_msg)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
