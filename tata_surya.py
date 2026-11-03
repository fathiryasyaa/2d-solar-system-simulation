import array as _arr
import pygame
import pygame.gfxdraw
import math
import sys
import random

pygame.init()

try:
    pygame.mixer.pre_init(22050, -16, 1, 512)
    pygame.mixer.init()
    def _mksnd(freq, dur, vol=0.3, decay=5.0):
        n = int(22050 * dur)
        buf = _arr.array('h', [0]*n)
        for i in range(n):
            t = i / 22050.0
            env = math.exp(-decay * t)
            buf[i] = int(32767 * vol * env * math.sin(2*math.pi*freq*t))
        return pygame.mixer.Sound(buffer=buf)
    def _mknoise(dur, vol=0.4, decay=8.0):
        import random as _r
        n = int(22050 * dur)
        buf = _arr.array('h', [0]*n)
        for i in range(n):
            t = i / 22050.0
            env = math.exp(-decay * t)
            buf[i] = int(32767 * vol * env * (_r.random()*2-1))
        return pygame.mixer.Sound(buffer=buf)
    SND_IMPACT  = _mknoise(0.25, 0.35, 10)
    SND_EXPLODE = _mknoise(0.5,  0.5,  4)
    SND_SELECT  = _mksnd(600, 0.07, 0.15, 20)
    SND_ABSORB  = _mksnd(200, 0.4,  0.3,  3)
    _SND_OK = True
except Exception:
    _SND_OK = False

W, H    = 1280, 720
PANEL_W = 380
screen  = pygame.display.set_mode((W, H))
pygame.display.set_caption("Tata Surya 2D — Transformasi Geometri 2D | Kelompok 3")
clock   = pygame.time.Clock()

def fnt(name, size, bold=False):
    try:    return pygame.font.SysFont(name, size, bold=bold)
    except: return pygame.font.Font(None, size + 4)

f_ttl = fnt("Consolas", 15, bold=True)
f_bdy = fnt("Consolas", 13)
f_sml = fnt("Consolas", 11)
f_lbl = fnt("Arial",    12)

# warna
BG     = (5,   8,  20)
PBG    = (8,  14,  30)
PBD    = (40,  80, 160)
SEC    = (18,  28,  52)
ORBC   = (38,  50,  80)
WHITE  = (255, 255, 255)
DIM    = (140, 145, 165)
GOLD   = (255, 215,  50)
GREEN  = (70,  210, 110)
CYAN   = (70,  195, 230)
ORANGE = (255, 155,  60)
PURPLE = (175,  95, 255)
RED    = (255,  80,  80)

# data planet  (hardness = massa relatif, menentukan daya tahan terhadap meteor)
PDATA = [
    {"name":"Merkurius","r": 5,"orbit": 80, "spd":4.15, "col":(185,185,185),"angle":0.0,"srot":0.0,"sspd":0.05,"desc":"Planet terkecil & terdekat matahari","kind":"mercury","hardness":  4,
     "ptype":"Batuan",     "grav":0.38,"diam":"4.879 km",   "period":"88 hari",  "moons":0},
    {"name":"Venus",    "r": 9,"orbit":130, "spd":1.62, "col":(237,180,100),"angle":0.8,"srot":0.0,"sspd":0.02,"desc":"Planet terpanas di tata surya",      "kind":"venus",  "hardness": 14,
     "ptype":"Batuan",     "grav":0.91,"diam":"12.104 km",  "period":"225 hari", "moons":0},
    {"name":"Bumi",     "r":10,"orbit":190, "spd":1.0,  "col":(70, 130,200),"angle":1.6,"srot":0.0,"sspd":0.10,"desc":"Satu-satunya planet berpenghuni",   "kind":"earth",  "hardness": 20,"moon_angle":0.0,"moon_orbit":24,"moon_spd":5.0,
     "ptype":"Batuan",     "grav":1.00,"diam":"12.742 km",  "period":"365 hari", "moons":1},
    {"name":"Mars",     "r": 7,"orbit":260, "spd":0.53, "col":(188, 74, 60),"angle":2.4,"srot":0.0,"sspd":0.09,"desc":"Planet Merah",                     "kind":"mars",   "hardness":  8,
     "ptype":"Batuan",     "grav":0.38,"diam":"6.779 km",   "period":"687 hari", "moons":2},
    {"name":"Jupiter",  "r":22,"orbit":360, "spd":0.084,"col":(210,170,120),"angle":0.5,"srot":0.0,"sspd":0.25,"desc":"Planet terbesar di tata surya",    "kind":"jupiter","hardness":150,
     "ptype":"Raksasa Gas","grav":2.34,"diam":"139.820 km", "period":"12 tahun", "moons":79},
    {"name":"Saturnus", "r":18,"orbit":460, "spd":0.034,"col":(210,190,140),"angle":1.2,"srot":0.0,"sspd":0.22,"desc":"Dikenal dengan cincin es-nya",     "kind":"saturn", "hardness":100,"has_rings":True,
     "ptype":"Raksasa Gas","grav":0.93,"diam":"116.460 km", "period":"29 tahun", "moons":83},
    {"name":"Uranus",   "r":14,"orbit":545, "spd":0.012,"col":(135,210,220),"angle":3.0,"srot":0.0,"sspd":0.14,"desc":"Planet dengan sumbu miring ~98 derajat","kind":"uranus","hardness": 50,
     "ptype":"Raksasa Es", "grav":0.92,"diam":"50.724 km",  "period":"84 tahun", "moons":27},
    {"name":"Neptunus", "r":13,"orbit":620, "spd":0.006,"col":(60,  80,200),"angle":4.5,"srot":0.0,"sspd":0.15,"desc":"Planet terjauh dari matahari",      "kind":"neptune","hardness": 45,
     "ptype":"Raksasa Es", "grav":1.12,"diam":"49.244 km",  "period":"165 tahun","moons":16},
]
planets = [dict(p) for p in PDATA]
for p in planets: p["trail"] = []

# ukuran meteor: mass menentukan apakah bisa hancurkan planet (vs planet.hardness)
METEOR_SIZES = [
    {"name": "Kecil",   "size": 2.5, "mass":  3, "col": (220, 220, 160)},  # gak bisa hancurkan siapapun
    {"name": "Sedang",  "size": 5.0, "mass": 20, "col": (230, 170,  70)},  # bisa hancurkan Merkurius & Mars
    {"name": "Besar",   "size": 8.5, "mass": 60, "col": (220,  90,  30)},  # bisa hancurkan sampai Uranus
    {"name": "Raksasa", "size":13.0, "mass":200, "col": (180,  40,  15)},  # hancurkan semua termasuk Jupiter
]
meteor_size_sel = 1   # default: Sedang

# sabuk asteroid antara Mars dan Jupiter
random.seed(999)
ASTEROIDS = [
    {
        "orbit": random.uniform(290, 338),
        "angle": random.uniform(0, math.pi * 2),
        "spd":   random.uniform(0.22, 0.42),
        "size":  random.randint(1, 2),
        "col":   random.choice([(160,155,145),(145,140,130),(170,165,158)]),
    }
    for _ in range(200)
]

# komet Halley: orbit elips eksentrik, matahari di salah satu fokus
COMET_A    = 700
COMET_B    = 200
COMET_C    = math.sqrt(COMET_A**2 - COMET_B**2)   # ~670.8
COMET_PERI = COMET_A - COMET_C                     # perihelion ~29.2
COMET_SPD  = 1.2                                   # kecepatan dasar di perihelion (rad/s)

# state
cam_x, cam_y = float(W // 2), float(H // 2)
scale        = 0.82
paused       = False
tspd         = 1.0
tspd_saved   = 1.0   # simpan speed sebelum slomo
slomo        = False  # S: toggle slomo 0.05x
sel          = None
dragging     = False
drag_from    = (0, 0)
cam_from     = (0.0, 0.0)
show_orbit   = True
show_label   = True
show_grid    = False
show_trails  = False
show_grav_lines = True
hide_panel   = False
show_help    = False  # F1: overlay panduan kontrol
tracking     = False   # F: kamera mengikuti planet terpilih
step_once    = False   # →: maju 1 frame saat pause

sun_time     = 0.0     # untuk efek pulsing matahari
comet_angle  = math.pi * 0.75
comet_trail  = []      # [(wx, wy), ...] rekam jejak komet

random.seed(2024)
stars = [(random.randint(0, W), random.randint(0, H),
          random.uniform(0.3, 1.0), random.randint(1, 2)) for _ in range(260)]

# meteor & ledakan
meteors      = []       # list dict meteor aktif
expl_parts   = []       # partikel ledakan
shockwaves   = []       # shockwave ring
sling_start  = None     # titik awal slingshot
sling_cur    = None     # posisi cursor saat drag
METEOR_G     = 800000   # konstanta gravitasi (tuned ke skala world)
APPROACH_DST = 60       # jarak warning (world units dari permukaan planet)


# ── TRANSFORMASI ────────────────────────────────────────────

def w2s(wx, wy):
    # translasi + scaling: world -> screen
    return int(cam_x + wx * scale), int(cam_y + wy * scale)

def rot2d(R, theta):
    # rotasi 2D: x' = R*cos(t), y' = R*sin(t)
    return R * math.cos(theta), R * math.sin(theta)

def p_wpos(p):
    return rot2d(p["orbit"], p["angle"])

def p_spos(p):
    return w2s(*p_wpos(p))

def comet_wpos():
    # posisi komet: elips dengan matahari di fokus
    wx = COMET_A * math.cos(comet_angle) - COMET_C
    wy = COMET_B * math.sin(comet_angle)
    return wx, wy


# ── DRAW UTILS ──────────────────────────────────────────────

def circ(surf, col, pos, r):
    x, y, r = int(pos[0]), int(pos[1]), max(int(r), 1)
    try:
        pygame.gfxdraw.aacircle(surf, x, y, r, col)
        pygame.gfxdraw.filled_circle(surf, x, y, r, col)
    except:
        pygame.draw.circle(surf, col, (x, y), r)

def glow(surf, col, pos, r, n=4):
    for i in range(n, 0, -1):
        gr = r + i * 5
        s  = pygame.Surface((gr*2+4, gr*2+4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*col, int(55/i)), (gr+2, gr+2), gr)
        surf.blit(s, (pos[0]-gr-2, pos[1]-gr-2))

def put_text(surf, text, pos, font, col=WHITE, align="left"):
    r = font.render(text, True, col)
    x, y = pos
    if align == "center": x -= r.get_width() // 2
    elif align == "right": x -= r.get_width()
    surf.blit(r, (x, y))

def box(surf, rect, col, brd=8, alpha=220):
    s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(s, (*col, alpha), (0, 0, rect[2], rect[3]), border_radius=brd)
    surf.blit(s, (rect[0], rect[1]))

def make_ellipse(w, h, col, alpha=220):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (*col, alpha), (0, 0, w, h))
    return s

def dashed_line(surf, col, p1, p2, dash=5, gap=4):
    # gambar garis putus-putus
    dx, dy = p2[0]-p1[0], p2[1]-p1[1]
    dist = math.hypot(dx, dy)
    if dist == 0: return
    nx, ny = dx/dist, dy/dist
    pos, on = 0.0, True
    while pos < dist:
        end = min(pos + (dash if on else gap), dist)
        if on:
            x1 = int(p1[0] + nx*pos);  y1 = int(p1[1] + ny*pos)
            x2 = int(p1[0] + nx*end);  y2 = int(p1[1] + ny*end)
            pygame.draw.line(surf, col, (x1, y1), (x2, y2), 1)
        pos = end
        on  = not on

def draw_angle_arc(surf, center, r, angle):
    # busur sudut dari 0 sampai angle (world→screen: sin positif = bawah)
    steps = max(8, int(abs(angle) * 20))
    pts   = []
    for i in range(steps + 1):
        a  = (angle / steps) * i
        px = center[0] + r * math.cos(a)
        py = center[1] + r * math.sin(a)
        pts.append((int(px), int(py)))
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, GOLD, pts[i], pts[i+1], 1)


# ── DETAIL PLANET ───────────────────────────────────────────

def draw_bands(surf, cx, cy, r, bands):
    # scanline: warnai tiap baris horizontal sesuai band
    for py in range(cy - r, cy + r + 1):
        dy = py - cy
        if abs(dy) >= r: continue
        chord = int(math.sqrt(r*r - dy*dy))
        rel   = dy / r
        col   = bands[-1][2]
        for y0, y1, bc in bands:
            if y0 <= rel < y1:
                col = bc
                break
        pygame.draw.line(surf, col, (cx - chord, py), (cx + chord, py))

def planet_detail(surf, kind, cx, cy, r):
    if r < 2: return

    if kind == "mercury":
        circ(surf, (185, 185, 185), (cx, cy), r)
        if r >= 4:
            rng = random.Random(42)
            for _ in range(6):
                a  = rng.uniform(0, math.pi * 2)
                d  = rng.uniform(0.2, 0.7) * r
                cr = max(1, int(r * rng.uniform(0.08, 0.16)))
                circ(surf, (155, 155, 155),
                     (int(cx + d*math.cos(a)), int(cy + d*math.sin(a))), cr)

    elif kind == "venus":
        draw_bands(surf, cx, cy, r, [
            (-1.0, -0.60, (230, 175,  90)),
            (-0.60,-0.30, (240, 188, 108)),
            (-0.30, 0.00, (235, 180,  98)),
            ( 0.00, 0.40, (242, 190, 112)),
            ( 0.40, 0.70, (232, 172,  88)),
            ( 0.70, 1.00, (226, 166,  82)),
        ])

    elif kind == "earth":
        draw_bands(surf, cx, cy, r, [
            (-1.00,-0.78, (210, 225, 255)),
            (-0.78,-0.50, ( 58, 118, 198)),
            (-0.50,-0.20, ( 65, 132, 210)),
            (-0.20, 0.12, ( 68, 130, 202)),
            ( 0.12, 0.45, ( 60, 124, 195)),
            ( 0.45, 0.72, ( 62, 120, 190)),
            ( 0.72, 1.00, (210, 225, 255)),
        ])
        if r >= 5:
            rng = random.Random(7)
            for _ in range(4):
                a  = rng.uniform(0, math.pi * 2)
                d  = rng.uniform(0.1, 0.5) * r
                gr = max(2, int(r * rng.uniform(0.22, 0.40)))
                circ(surf, (55, 148, 70),
                     (int(cx + d*math.cos(a)), int(cy + d*math.sin(a)*0.65)), gr)
        if r >= 5:
            rng = random.Random(13)
            for _ in range(3):
                a  = rng.uniform(0, math.pi * 2)
                d  = rng.uniform(0.15, 0.65) * r
                wr = max(1, int(r * 0.22))
                wx = int(cx + d * math.cos(a))
                wy = int(cy + d * math.sin(a) * 0.5)
                cs = pygame.Surface((wr*3, wr+2), pygame.SRCALPHA)
                pygame.draw.ellipse(cs, (255, 255, 255, 110), (0, 0, wr*3, wr+2))
                surf.blit(cs, (wx - wr, wy - wr//2))

    elif kind == "mars":
        draw_bands(surf, cx, cy, r, [
            (-1.00,-0.72, (215, 215, 225)),
            (-0.72,-0.40, (185,  68,  52)),
            (-0.40, 0.30, (190,  74,  56)),
            ( 0.30, 0.68, (176,  62,  48)),
            ( 0.68, 1.00, (210, 210, 220)),
        ])
        if r >= 5:
            rng = random.Random(3)
            for _ in range(3):
                a  = rng.uniform(0.2, math.pi * 1.8)
                d  = rng.uniform(0.15, 0.55) * r
                sr = max(1, int(r * 0.14))
                circ(surf, (158, 52, 40),
                     (int(cx + d*math.cos(a)), int(cy + d*math.sin(a)*0.7)), sr)

    elif kind == "jupiter":
        draw_bands(surf, cx, cy, r, [
            (-1.00,-0.82, (228, 198, 158)),
            (-0.82,-0.62, (192, 148,  92)),
            (-0.62,-0.42, (220, 183, 128)),
            (-0.42,-0.22, (178, 128,  78)),
            (-0.22,-0.02, (224, 188, 138)),
            (-0.02, 0.18, (182, 132,  82)),
            ( 0.18, 0.38, (218, 183, 128)),
            ( 0.38, 0.58, (192, 148,  92)),
            ( 0.58, 0.78, (222, 188, 138)),
            ( 0.78, 1.00, (228, 198, 158)),
        ])
        if r >= 10:
            gw = max(int(r * 0.58), 5)
            gh = max(int(r * 0.30), 3)
            gx = int(cx + r * 0.22) - gw // 2
            gy = int(cy + r * 0.12) - gh // 2
            surf.blit(make_ellipse(gw, gh, (198, 65, 45), 230), (gx, gy))
            hw = max(gw // 3, 2)
            hh = max(gh // 3, 1)
            surf.blit(make_ellipse(hw, hh, (225, 110, 85), 180),
                      (gx + gw//2 - hw//2, gy + gh//2 - hh//2))

    elif kind == "saturn":
        draw_bands(surf, cx, cy, r, [
            (-1.00,-0.65, (218, 198, 148)),
            (-0.65,-0.35, (198, 178, 128)),
            (-0.35,-0.05, (212, 192, 142)),
            (-0.05, 0.25, (202, 182, 132)),
            ( 0.25, 0.60, (208, 188, 138)),
            ( 0.60, 1.00, (198, 178, 128)),
        ])

    elif kind == "uranus":
        draw_bands(surf, cx, cy, r, [
            (-1.00,-0.55, (158, 218, 228)),
            (-0.55,-0.20, (128, 208, 218)),
            (-0.20, 0.25, (122, 202, 216)),
            ( 0.25, 0.65, (128, 208, 220)),
            ( 0.65, 1.00, (152, 215, 226)),
        ])

    elif kind == "neptune":
        draw_bands(surf, cx, cy, r, [
            (-1.00,-0.45, (48,  68, 188)),
            (-0.45, 0.15, (52,  72, 198)),
            ( 0.15, 0.58, (42,  62, 182)),
            ( 0.58, 1.00, (48,  68, 192)),
        ])
        if r >= 5:
            sw  = max(int(r * 0.45), 3)
            sh  = max(int(r * 0.25), 2)
            npx = int(cx - r * 0.25) - sw // 2
            npy = int(cy - r * 0.12) - sh // 2
            surf.blit(make_ellipse(sw, sh, (195, 212, 255), 200), (npx, npy))

    # highlight cahaya di semua planet
    if r >= 3:
        hl = max(int(r * 0.28), 1)
        hs = pygame.Surface((hl*2+2, hl*2+2), pygame.SRCALPHA)
        pygame.draw.circle(hs, (255, 255, 255, 75), (hl+1, hl+1), hl)
        surf.blit(hs, (cx - r//3 - hl - 1, cy - r//3 - hl - 1))

def draw_night_shadow(surf, planet_angle, sx, sy, r):
    # bayangan malam: sisi planet yang membelakangi matahari
    size = (r + 4) * 2
    s    = pygame.Surface((size, size), pygame.SRCALPHA)
    lx, ly    = size // 2, size // 2
    shadow_dir = planet_angle + math.pi  # menjauhi matahari
    pts = [(lx, ly)]
    for i in range(21):
        a  = (shadow_dir - math.pi/2) + i * (math.pi / 20)
        pts.append((int(lx + r*math.cos(a)), int(ly + r*math.sin(a))))
    if len(pts) >= 3:
        pygame.draw.polygon(s, (0, 0, 20, 145), pts)
    surf.blit(s, (sx - size//2, sy - size//2))


# ── SCENE ───────────────────────────────────────────────────

def draw_grid(surf):
    # grid koordinat Kartesius, scale dengan kamera
    GRID_STEP = 100  # world units
    cw = W - PANEL_W
    # hitung range world x/y yang terlihat
    wx_min = int((-cam_x) / scale / GRID_STEP) - 1
    wx_max = int((cw - cam_x) / scale / GRID_STEP) + 1
    wy_min = int((-cam_y) / scale / GRID_STEP) - 1
    wy_max = int((H - cam_y) / scale / GRID_STEP) + 1
    for ix in range(wx_min, wx_max + 1):
        wx = ix * GRID_STEP
        sx = int(cam_x + wx * scale)
        if sx < 0 or sx >= cw: continue
        is_axis = (ix == 0)
        col  = (60, 100, 180) if is_axis else (30, 50, 90)
        w_ln = 2 if is_axis else 1
        pygame.draw.line(surf, col, (sx, 0), (sx, H), w_ln)
        if ix != 0:
            put_text(surf, str(wx), (sx + 2, 2), f_sml, (40, 65, 110))
    for iy in range(wy_min, wy_max + 1):
        wy = iy * GRID_STEP
        sy = int(cam_y + wy * scale)
        if sy < 0 or sy >= H: continue
        is_axis = (iy == 0)
        col  = (60, 100, 180) if is_axis else (30, 50, 90)
        w_ln = 2 if is_axis else 1
        pygame.draw.line(surf, col, (0, sy), (cw, sy), w_ln)
        if iy != 0:
            put_text(surf, str(wy), (2, sy + 2), f_sml, (40, 65, 110))

def draw_stars(surf):
    for x, y, b, sz in stars:
        c = int(b * 210)
        pygame.draw.circle(surf, (c, c, min(255, c+25)), (x, y), sz)

def draw_asteroids(surf):
    for a in ASTEROIDS:
        ax, ay = w2s(*rot2d(a["orbit"], a["angle"]))
        if 0 <= ax < W - PANEL_W and 0 <= ay < H:
            pygame.draw.circle(surf, a["col"], (ax, ay), a["size"])

def draw_comet(surf):
    cwx, cwy = comet_wpos()
    csx, csy = w2s(cwx, cwy)

    # trail (rekam jejak: semakin tua semakin transparan & kecil)
    for i, (twx, twy) in enumerate(comet_trail):
        tsx, tsy = w2s(twx, twy)
        if tsx < -50 or tsx > W+50 or tsy < -50 or tsy > H+50:
            continue
        ratio = i / max(len(comet_trail), 1)
        alpha = int(180 * ratio)
        tr    = max(1, int(2 * ratio))
        ts    = pygame.Surface((tr*2+2, tr*2+2), pygame.SRCALPHA)
        pygame.draw.circle(ts, (200, 220, 255, alpha), (tr+1, tr+1), tr)
        surf.blit(ts, (tsx - tr - 1, tsy - tr - 1))

    # ekor angin surya: selalu mengarah menjauhi matahari
    dist = math.hypot(cwx, cwy)
    if dist > 5:
        tail_dx = cwx / dist
        tail_dy = cwy / dist
        # makin panjang saat dekat matahari (Kepler visual effect)
        tail_world_len = max(40, int(250 * COMET_PERI / dist))
        for j in range(0, tail_world_len, 6):
            ratio  = j / tail_world_len
            twx_   = cwx + tail_dx * j
            twy_   = cwy + tail_dy * j
            tsx_, tsy_ = w2s(twx_, twy_)
            if tsx_ < -50 or tsx_ > W+50 or tsy_ < -50 or tsy_ > H+50:
                break
            alpha  = max(0, int(140 * (1 - ratio)))
            tr_    = max(1, int(2 * (1 - ratio * 0.6)))
            ts     = pygame.Surface((tr_*2+2, tr_*2+2), pygame.SRCALPHA)
            pygame.draw.circle(ts, (180, 210, 255, alpha), (tr_+1, tr_+1), tr_)
            surf.blit(ts, (tsx_ - tr_ - 1, tsy_ - tr_ - 1))

    # kepala komet
    comet_r = max(int(3 * scale), 1)
    glow(surf, (180, 210, 255), (csx, csy), comet_r, n=2)
    circ(surf, (220, 235, 255), (csx, csy), comet_r)
    if show_label:
        put_text(surf, "Komet Halley", (csx + comet_r + 4, csy - 6), f_sml, (180, 210, 255))

def draw_sun(surf):
    sx, sy = w2s(0, 0)
    # pulsing: ukuran berubah dengan gelombang sinus
    pulse = 1.0 + 0.06 * math.sin(sun_time * 1.5)
    sr    = max(int(28 * scale * pulse), 8)
    glow(surf, (255, 200, 50), (sx, sy), sr, n=5)
    circ(surf, (255, 225, 70), (sx, sy), sr)
    circ(surf, (255, 255, 190), (sx, sy), max(sr // 2, 4))
    if show_label:
        put_text(surf, "Matahari", (sx + sr + 4, sy - 7), f_lbl, GOLD)

def draw_saturn_rings(surf, sx, sy, planet_r):
    ra = int(planet_r * 2.3 * scale)
    rb = int(planet_r * 0.55 * scale)
    if ra < 4: return
    for th, alpha, sh in [(5, 80, 0), (3, 50, 4), (2, 30, 7)]:
        rs = pygame.Surface((ra*2+6, rb*2+6), pygame.SRCALPHA)
        pygame.draw.ellipse(rs, (210, 185, 130, alpha),
                            (sh, sh, ra*2+6-sh*2, rb*2+6-sh*2), th)
        surf.blit(rs, (sx - ra - 3, sy - rb - 3))

def draw_vector_viz(surf, p):
    # segitiga siku-siku komponen vektor rotasi
    sun_sx, sun_sy = w2s(0, 0)
    psx, psy       = p_spos(p)
    wx, wy         = p_wpos(p)

    # vektor R (kuning): matahari ke planet
    pygame.draw.line(surf, (*GOLD, 200), (sun_sx, sun_sy), (psx, psy), 2)

    # komponen x (cyan): garis horizontal dari matahari ke bawah planet
    dashed_line(surf, CYAN, (sun_sx, sun_sy), (psx, sun_sy))

    # komponen y (hijau): garis vertikal dari titik (wx,0) ke planet
    dashed_line(surf, GREEN, (psx, sun_sy), (psx, psy))

    # kotak sudut siku di titik (psx, sun_sy)
    bsz = max(6, int(7 * scale))
    sq  = pygame.Surface((bsz+2, bsz+2), pygame.SRCALPHA)
    pygame.draw.rect(sq, (*WHITE, 80), (0, 0, bsz, bsz), 1)
    surf.blit(sq, (psx - bsz - 1, sun_sy - bsz - 1 if wy < 0 else sun_sy))

    # busur sudut theta di matahari
    arc_r = max(int(38 * scale), 15)
    draw_angle_arc(surf, (sun_sx, sun_sy), arc_r, p["angle"] % (2*math.pi))

    # label
    R         = p["orbit"]
    theta_deg = math.degrees(p["angle"]) % 360
    mid_x     = (sun_sx + psx) // 2
    mid_y     = (sun_sy + psy) // 2
    put_text(surf, f"R={R}",          (mid_x + 5, mid_y - 12),               f_sml, GOLD)
    put_text(surf, f"x'={wx:.0f}",   ((sun_sx+psx)//2 - 20, sun_sy + 4),    f_sml, CYAN)
    put_text(surf, f"y'={wy:.0f}",   (psx + 5, (sun_sy+psy)//2),            f_sml, GREEN)
    put_text(surf, f"t={theta_deg:.1f}", (sun_sx + arc_r + 5, sun_sy - 8),  f_sml, GOLD)

def draw_planets(surf):
    # garis orbit
    if show_orbit:
        cx_, cy_ = w2s(0, 0)
        for p in planets:
            r_ = int(p["orbit"] * scale)
            if r_ > 5:
                pygame.draw.circle(surf, ORBC, (cx_, cy_), r_, 1)

    # visualisasi vektor untuk planet terpilih
    if sel is not None and scale > 0.3 and not planets[sel].get("dead"):
        draw_vector_viz(surf, planets[sel])

    for i, p in enumerate(planets):
        if p.get("dead"): continue   # planet hancur, skip render
        sx, sy = p_spos(p)
        r      = max(int(p["r"] * scale), 2)

        if sel == i:
            pygame.draw.circle(surf, CYAN, (sx, sy), r + 7, 2)
            glow(surf, CYAN, (sx, sy), r, n=2)

        if p.get("has_rings"):
            draw_saturn_rings(surf, sx, sy, p["r"])

        planet_detail(surf, p["kind"], sx, sy, r)
        draw_night_shadow(surf, p["angle"], sx, sy, r)  # efek siang-malam

        # bulan mengorbit bumi
        if "moon_angle" in p:
            ewx, ewy = p_wpos(p)
            ma  = p["moon_angle"]
            mo  = p["moon_orbit"]
            msx, msy = w2s(ewx + mo*math.cos(ma), ewy + mo*math.sin(ma))
            mr  = max(int(3 * scale), 1)
            if show_orbit:
                mor = int(mo * scale)
                if mor > 3:
                    pygame.draw.circle(surf, (28, 38, 58), (sx, sy), mor, 1)
            circ(surf, (200, 200, 210), (msx, msy), mr)
            if show_label and scale > 0.6:
                put_text(surf, "Bulan", (msx + mr + 3, msy - 5), f_sml, (120, 125, 145))

        if show_label and scale > 0.35:
            put_text(surf, p["name"], (sx + r + 5, sy - 6), f_lbl, CYAN if sel == i else DIM)


# ── PANEL ALGORITMA ─────────────────────────────────────────

def draw_panel(surf):
    px = W - PANEL_W
    x0 = px + 10
    xr = W - 10
    lh = 17
    y  = 10

    box(surf, (px-2, 0, PANEL_W+2, H), PBG, brd=0, alpha=235)
    pygame.draw.line(surf, PBD, (px-2, 0), (px-2, H), 2)

    put_text(surf, "TRANSFORMASI GEOMETRI 2D", (px + PANEL_W//2, y), f_ttl, GOLD, align="center")
    y += 20
    put_text(surf, "Kelompok 3 -- Tata Surya Interaktif", (px + PANEL_W//2, y), f_sml, DIM, align="center")
    y += 16
    pygame.draw.line(surf, PBD, (x0, y), (xr, y), 1); y += 10

    # 1. SCALING
    box(surf, (x0-4, y-2, PANEL_W-12, 84), SEC, brd=6)
    put_text(surf, "1. SCALING  (Scroll = Zoom)", (x0, y), f_ttl, ORANGE)
    y += lh + 2
    put_text(surf, "Rumus:", (x0, y), f_sml, DIM); y += lh
    put_text(surf, f"  x' = x * s  =  x * {scale:.3f}", (x0, y), f_bdy, WHITE); y += lh
    put_text(surf, f"  y' = y * s  =  y * {scale:.3f}", (x0, y), f_bdy, WHITE); y += lh
    if scale > 1.02:   zt, zc = f"  [ZOOM IN   x{scale:.2f}]", GREEN
    elif scale < 0.98: zt, zc = f"  [ZOOM OUT  x{scale:.2f}]", RED
    else:              zt, zc = f"  [NORMAL    x{scale:.2f}]", DIM
    put_text(surf, zt, (x0, y), f_sml, zc); y += lh + 12

    # 2. TRANSLASI
    dx = int(cam_x) - W // 2
    dy = int(cam_y) - H // 2
    box(surf, (x0-4, y-2, PANEL_W-12, 100), SEC, brd=6)
    put_text(surf, "2. TRANSLASI  (Drag Kamera)", (x0, y), f_ttl, PURPLE)
    y += lh + 2
    put_text(surf, "Rumus:", (x0, y), f_sml, DIM); y += lh
    put_text(surf, f"  x' = x + dx  =  x + ({dx:+d})", (x0, y), f_bdy, WHITE); y += lh
    put_text(surf, f"  y' = y + dy  =  y + ({dy:+d})", (x0, y), f_bdy, WHITE); y += lh
    put_text(surf, f"  Pusat layar : ({W//2}, {H//2})", (x0, y), f_sml, DIM); y += lh
    put_text(surf, f"  Pos matahari: ({int(cam_x)}, {int(cam_y)})", (x0, y), f_sml, DIM); y += lh
    put_text(surf, f"  Offset (dx,dy): ({dx:+d}, {dy:+d})", (x0, y), f_sml, CYAN); y += lh + 12

    # 3. ROTASI
    rot_h = 162 if sel is None else 212
    box(surf, (x0-4, y-2, PANEL_W-12, rot_h), SEC, brd=6)
    put_text(surf, "3. ROTASI  (Orbit Planet)", (x0, y), f_ttl, GREEN)
    y += lh + 2
    put_text(surf, "Matriks Rotasi 2D:", (x0, y), f_sml, DIM); y += lh
    put_text(surf, " [cos t  -sin t]   [R]   [x']", (x0, y), f_bdy, WHITE); y += lh
    put_text(surf, " [sin t   cos t] * [0] = [y']", (x0, y), f_bdy, WHITE); y += lh + 2
    put_text(surf, "Penyederhanaan:", (x0, y), f_sml, DIM); y += lh
    put_text(surf, "  x' = R * cos(t)", (x0, y), f_bdy, WHITE); y += lh
    put_text(surf, "  y' = R * sin(t)", (x0, y), f_bdy, WHITE); y += lh + 4

    if sel is not None:
        p     = planets[sel]
        theta = p["angle"]
        deg   = math.degrees(theta) % 360
        ct    = math.cos(theta)
        st    = math.sin(theta)
        R     = p["orbit"]
        xp    = R * ct
        yp    = R * st
        scx, scy = w2s(xp, yp)
        pygame.draw.line(surf, GREEN, (x0, y), (xr, y), 1); y += 6
        put_text(surf, f"  Planet : {p['name']} (R={R})", (x0, y), f_bdy, CYAN);  y += lh
        put_text(surf, f"  theta  = {deg:.1f} deg",       (x0, y), f_bdy, GOLD);  y += lh
        if p.get("dead"):
            put_text(surf, f"  STATUS : HANCUR (Meteor)",  (x0, y), f_bdy, RED);   y += lh
            put_text(surf, f"  Tekan R untuk reset",      (x0, y), f_sml, DIM);   y += lh * 4
        else:
            put_text(surf, f"  cos(t) = {ct:+.4f}",           (x0, y), f_sml, WHITE); y += lh
            put_text(surf, f"  sin(t) = {st:+.4f}",           (x0, y), f_sml, WHITE); y += lh
            put_text(surf, f"  x'= {R}*{ct:.3f} = {xp:.1f}", (x0, y), f_sml, GREEN); y += lh
            put_text(surf, f"  y'= {R}*{st:.3f} = {yp:.1f}", (x0, y), f_sml, GREEN); y += lh
            put_text(surf, f"  Screen = ({scx}, {scy})",      (x0, y), f_sml, ORANGE);y += lh
    else:
        put_text(surf, "  -> Klik planet untuk detail rotasi", (x0, y), f_sml, DIM)
        y += lh * 8

    y += 12
    pygame.draw.line(surf, PBD, (x0, y), (xr, y), 1); y += 8

    # status
    put_text(surf, "STATUS", (x0, y), f_ttl, GOLD); y += lh + 2
    put_text(surf, f"  Simulasi  : {'|| PAUSED' if paused else '> BERJALAN'}", (x0, y), f_bdy, RED if paused else GREEN); y += lh
    spd_col = (100, 180, 255) if slomo else WHITE
    spd_lbl = f"{tspd:.2f}x  [SLOMO]" if slomo else f"{tspd:.2f}x"
    put_text(surf, f"  Kecepatan : {spd_lbl}", (x0, y), f_bdy, spd_col); y += lh
    put_text(surf, f"  Skala     : x{scale:.3f}", (x0, y), f_bdy, WHITE); y += lh
    follow_txt = f"ON - {planets[sel]['name']}" if (tracking and sel is not None) else "OFF"
    put_text(surf, f"  Follow    : {follow_txt}", (x0, y), f_bdy, CYAN if tracking else DIM); y += lh

    if sel is not None:
        p   = planets[sel]
        deg = math.degrees(p["angle"]) % 360
        y  += 4
        put_text(surf, f"  Planet  : {p['name']}",  (x0, y), f_bdy, CYAN); y += lh
        put_text(surf, f"  Orbit t : {deg:.1f} deg",(x0, y), f_bdy, CYAN); y += lh
        put_text(surf, f"  Info    : {p['desc']}",  (x0, y), f_sml, DIM);  y += lh

    y += 8
    pygame.draw.line(surf, PBD, (x0, y), (xr, y), 1); y += 8

    # kontrol
    put_text(surf, "KONTROL", (x0, y), f_ttl, GOLD); y += lh + 2
    ctrls = [
        ("Scroll",     "Zoom In/Out (Scaling)"),
        ("Drag",       "Geser kamera (Translasi)"),
        ("Klik",       "Pilih planet (Rotasi)"),
        ("Klik Kanan", "Slingshot meteor (tahan+tarik)"),
        ("SPASI",      "Pause / Resume"),
        ("->",         "Step 1 frame (saat pause)"),
        ("S",          "Slow-mo toggle (0.05x)"),
        ("F",          "Follow / Lepas planet"),
        ("[ / ]",      "Lambat / Cepat (step 0.1)"),
        ("O",          "Toggle orbit"),
        ("L",          "Toggle label"),
        ("G",          "Toggle grid koordinat"),
        ("T",          "Toggle orbit trail"),
        ("V",          "Toggle garis gravitasi"),
        ("H",          "Sembunyikan/tampil panel"),
        ("R",          "Reset tampilan + meteor"),
        ("F1",         "Panduan kontrol (menu ini)"),
        ("ESC",        "Keluar"),
    ]
    for key, act in ctrls:
        if y + lh > H - 5: break
        put_text(surf, f"  {key:<8}", (x0, y), f_sml, ORANGE)
        put_text(surf, f"        {act}", (x0, y), f_sml, DIM)
        y += lh


# ── METEOR ──────────────────────────────────────────────────

def screen_to_world(sx, sy):
    return (sx - cam_x) / scale, (sy - cam_y) / scale

def spawn_meteor(sx, sy):
    wx, wy = screen_to_world(sx, sy)
    ms = METEOR_SIZES[meteor_size_sel]
    bc = ms["col"]
    col = (
        min(255, max(0, bc[0] + random.randint(-20, 20))),
        min(255, max(0, bc[1] + random.randint(-20, 20))),
        min(255, max(0, bc[2] + random.randint(-20, 20))),
    )
    meteors.append({
        "wx": wx, "wy": wy,
        "vx": 0.0, "vy": 0.0,
        "trail": [],
        "alive": True,
        "size": ms["size"],
        "mass": ms["mass"],
        "col":  col,
    })

def spawn_explosion(wx, wy):
    for _ in range(28):
        ang = random.uniform(0, math.pi * 2)
        spd = random.uniform(25, 100)
        expl_parts.append({
            "wx": wx, "wy": wy,
            "vx": math.cos(ang) * spd,
            "vy": math.sin(ang) * spd,
            "life": 1.0,
            "col": random.choice([(255, 100, 30), (255, 210, 60), (255, 255, 150), (200, 60, 10)]),
            "size": random.uniform(1.5, 3.5),
        })

def spawn_impact(wx, wy, col):
    # efek benturan kecil: meteor mental, planet selamat
    for _ in range(14):
        ang = random.uniform(0, math.pi * 2)
        spd = random.uniform(10, 40)
        expl_parts.append({
            "wx": wx, "wy": wy,
            "vx": math.cos(ang) * spd,
            "vy": math.sin(ang) * spd,
            "life": random.uniform(0.3, 0.6),
            "col": col,
            "size": random.uniform(0.8, 2.0),
        })

def spawn_sun_absorb(wx, wy):
    # efek meteor terserap matahari
    for _ in range(20):
        ang = random.uniform(0, math.pi * 2)
        spd = random.uniform(15, 70)
        expl_parts.append({
            "wx": wx, "wy": wy,
            "vx": math.cos(ang) * spd,
            "vy": math.sin(ang) * spd,
            "life": random.uniform(0.4, 0.8),
            "col": random.choice([(255,255,150),(255,220,80),(255,255,220),(255,180,50)]),
            "size": random.uniform(1.0, 3.0),
        })
    if _SND_OK: SND_ABSORB.play()

def spawn_planet_explosion(wx, wy, planet_r):
    # ledakan planet: lebih besar, lebih banyak, lebih lama
    n = int(40 + planet_r * 2)
    for _ in range(n):
        ang = random.uniform(0, math.pi * 2)
        spd = random.uniform(30, planet_r * 8)
        expl_parts.append({
            "wx": wx + random.uniform(-planet_r*0.5, planet_r*0.5),
            "wy": wy + random.uniform(-planet_r*0.5, planet_r*0.5),
            "vx": math.cos(ang) * spd,
            "vy": math.sin(ang) * spd,
            "life": random.uniform(0.8, 1.5),
            "col": random.choice([(255, 80, 20), (255, 200, 50), (255, 255, 180),
                                  (200, 50, 10), (255, 140, 0), (180, 180, 180)]),
            "size": random.uniform(planet_r * 0.15, planet_r * 0.5),
        })

def update_meteors(sp):
    to_remove = []
    for m in meteors:
        if not m["alive"]:
            to_remove.append(m)
            continue
        for p in planets:
            if p.get("dead"): continue
            pwx, pwy = p_wpos(p)
            dx = pwx - m["wx"]
            dy = pwy - m["wy"]
            dist = max(math.hypot(dx, dy), 5)
            # gravitasi min-boost biar planet kecil tetap punya pull wajar
            grav_r = max(p["r"], 8)
            acc = METEOR_G * grav_r / (dist * dist)
            m["vx"] += (dx / dist) * acc * sp
            m["vy"] += (dy / dist) * acc * sp
            hit_r = max(p["r"], 7)  # hitbox minimum 7 unit biar planet kecil tetap bisa kena
            if dist < hit_r:
                if m["mass"] >= p.get("hardness", 999):
                    # meteor cukup besar → planet hancur
                    spawn_explosion(m["wx"], m["wy"])
                    spawn_planet_explosion(pwx, pwy, p["r"])
                    spawn_shockwave(pwx, pwy, p["r"] * 5)
                    p["dead"] = True
                    if _SND_OK: SND_EXPLODE.play()
                else:
                    # meteor terlalu kecil → cuma benturan, planet selamat
                    spawn_impact(m["wx"], m["wy"], m["col"])
                    if _SND_OK: SND_IMPACT.play()
                m["alive"] = False
                break
        if not m["alive"]:
            to_remove.append(m)
            continue
        spd_val = math.hypot(m["vx"], m["vy"])
        if spd_val > 600:
            m["vx"] = m["vx"] / spd_val * 600
            m["vy"] = m["vy"] / spd_val * 600
        m["wx"] += m["vx"] * sp
        m["wy"] += m["vy"] * sp
        # gravitasi matahari
        sdx, sdy = -m["wx"], -m["wy"]
        sdist = max(math.hypot(sdx, sdy), 5)
        sacc = METEOR_G * 40 / (sdist * sdist)
        m["vx"] += (sdx / sdist) * sacc * sp
        m["vy"] += (sdy / sdist) * sacc * sp
        if sdist < 30:   # terserap matahari
            spawn_sun_absorb(m["wx"], m["wy"])
            m["alive"] = False
            to_remove.append(m)
            continue
        m["trail"].append((m["wx"], m["wy"]))
        if len(m["trail"]) > 30:
            m["trail"].pop(0)
    for m in to_remove:
        if m in meteors:
            meteors.remove(m)

def update_expl_parts(sp):
    for ep in expl_parts:
        ep["wx"] += ep["vx"] * sp
        ep["wy"] += ep["vy"] * sp
        ep["life"] -= sp * 1.8
        ep["vx"] *= 0.95
        ep["vy"] *= 0.95
    expl_parts[:] = [ep for ep in expl_parts if ep["life"] > 0]

def draw_meteors(surf):
    for m in meteors:
        if not m["alive"]: continue
        # ekor api
        for i, (twx, twy) in enumerate(m["trail"]):
            ratio = (i + 1) / max(len(m["trail"]), 1)
            alpha = int(200 * ratio)
            tr = max(1, int(m["size"] * scale * 0.6 * ratio))
            tsx, tsy = w2s(twx, twy)
            ts = pygame.Surface((tr*2+2, tr*2+2), pygame.SRCALPHA)
            pygame.draw.circle(ts, (*m["col"], alpha), (tr+1, tr+1), tr)
            surf.blit(ts, (tsx-tr-1, tsy-tr-1))
        # kepala meteor
        msx, msy = w2s(m["wx"], m["wy"])
        mr = max(int(m["size"] * scale), 2)
        glow(surf, m["col"], (msx, msy), mr, n=2)
        circ(surf, (255, 240, 200), (msx, msy), mr)

def draw_approach_effects(surf):
    # ring peringatan saat meteor mendekati planet
    for m in meteors:
        if not m["alive"]: continue
        for p in planets:
            if p.get("dead"): continue
            pwx, pwy = p_wpos(p)
            dist = math.hypot(m["wx"] - pwx, m["wy"] - pwy)
            # threshold min 20 unit extra biar ring Mercury tetap keliatan
            threshold = max(p["r"], 7) + max(APPROACH_DST, 30)
            if dist < threshold:
                sx, sy = w2s(pwx, pwy)
                ratio = 1 - dist / threshold
                ring_r = max(int((max(p["r"], 7) + 20) * scale), 6)
                alpha = int(220 * ratio)
                rs = pygame.Surface((ring_r*2+4, ring_r*2+4), pygame.SRCALPHA)
                pygame.draw.circle(rs, (255, 80, 30, alpha), (ring_r+2, ring_r+2), ring_r, 2)
                surf.blit(rs, (sx-ring_r-2, sy-ring_r-2))

def draw_expl_parts(surf):
    for ep in expl_parts:
        esx, esy = w2s(ep["wx"], ep["wy"])
        er = max(int(ep["size"] * scale * min(ep["life"], 1.0)), 1)
        alpha = int(255 * min(ep["life"], 1.0))
        es = pygame.Surface((er*2+2, er*2+2), pygame.SRCALPHA)
        pygame.draw.circle(es, (*ep["col"], alpha), (er+1, er+1), er)
        surf.blit(es, (esx-er-1, esy-er-1))

def get_help_btn_rect():
    # tombol "?" pojok kiri bawah
    return pygame.Rect(10, H - 42, 80, 30)

def draw_help_btn(surf):
    rect = get_help_btn_rect()
    pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.002)) * 40)
    col_bg = (10, 20 + pulse//3, 60 + pulse, 200)
    col_bd = (80, 140, 255, 220) if not show_help else (255, 200, 50, 220)
    s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(s, col_bg, (0, 0, rect.w, rect.h), border_radius=8)
    pygame.draw.rect(s, col_bd, (0, 0, rect.w, rect.h), 2, border_radius=8)
    surf.blit(s, (rect.x, rect.y))
    label = "✕ Tutup" if show_help else "? Panduan"
    put_text(surf, label, (rect.centerx, rect.y + 8), f_sml,
             (255, 200, 50) if show_help else (150, 210, 255), align="center")

def get_size_btn_rects():
    bw, bh, gap = 70, 36, 6
    return [pygame.Rect(12 + i*(bw+gap), 42, bw, bh) for i in range(len(METEOR_SIZES))]

def draw_meteor_size_ui(surf):
    rects = get_size_btn_rects()
    total_w = len(METEOR_SIZES) * (70+6) - 6 + 18
    bg = pygame.Surface((total_w, 62), pygame.SRCALPHA)
    pygame.draw.rect(bg, (10, 15, 30, 200), (0, 0, total_w, 62), border_radius=8)
    pygame.draw.rect(bg, (40, 80, 160, 180), (0, 0, total_w, 62), 1, border_radius=8)
    surf.blit(bg, (6, 20))
    put_text(surf, "UKURAN METEOR (Klik / Tombol 1-4):", (12, 24), f_sml, GOLD)
    for i, (rect, ms) in enumerate(zip(rects, METEOR_SIZES)):
        selected = (i == meteor_size_sel)
        col = ms["col"]
        alpha = 230 if selected else 80
        s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(s, (*col, alpha), (0, 0, rect.w, rect.h), border_radius=6)
        if selected:
            pygame.draw.rect(s, (255, 255, 255), (0, 0, rect.w, rect.h), 2, border_radius=6)
        surf.blit(s, (rect.x, rect.y))
        put_text(surf, f"{i+1}. {ms['name']}", (rect.centerx, rect.y + 4), f_sml, WHITE, align="center")
        put_text(surf, f"M={ms['mass']}", (rect.centerx, rect.y + 19), f_sml, (220, 220, 220), align="center")

def draw_planet_info_card(surf):
    if sel is None: return
    p = planets[sel]
    sx, sy = p_spos(p)
    # jangan gambar kalau planet di luar canvas atau planet hancur
    if sx < 0 or sx > W - PANEL_W or sy < 0 or sy > H: return

    cw, lh = 210, 16
    dead = p.get("dead", False)

    # baris konten kartu
    rows = [
        ("Tipe",      p.get("ptype", "-"),          CYAN),
        ("Diameter",  p.get("diam",  "-"),           WHITE),
        ("Gravitasi", f"{p.get('grav', 0):.2f}g",   (120, 220, 120)),
        ("Periode",   p.get("period","-"),           WHITE),
        ("Bulan",     str(p.get("moons", 0)),        (200, 200, 100)),
        ("Ketahanan", str(p.get("hardness", "-")),   ORANGE),
        ("Status",    "HANCUR" if dead else "Normal",RED if dead else (80, 220, 80)),
    ]
    ch = 14 + len(rows) * lh + 10   # tinggi kartu

    # posisi: kanan planet, kalau kepotong panel → kiri planet
    pr = max(int(p["r"] * scale), 5) + 10
    cx = sx + pr
    if cx + cw > W - PANEL_W - 4:
        cx = sx - pr - cw
    cy = sy - ch // 2
    cy = max(6, min(H - ch - 6, cy))

    # background kartu
    bg = pygame.Surface((cw, ch), pygame.SRCALPHA)
    pygame.draw.rect(bg, (8, 14, 35, 220), (0, 0, cw, ch), border_radius=8)
    col_border = RED if dead else p["col"]
    pygame.draw.rect(bg, (*col_border, 200), (0, 0, cw, ch), 2, border_radius=8)
    surf.blit(bg, (cx, cy))

    # judul nama planet
    y = cy + 5
    put_text(surf, p["name"].upper(), (cx + cw//2, y), f_bdy, GOLD if not dead else RED, align="center")
    y += lh + 2
    pygame.draw.line(surf, (*p["col"], 180), (cx + 6, y), (cx + cw - 6, y), 1)
    y += 5

    for label, val, vcol in rows:
        put_text(surf, f"  {label}:", (cx + 4, y), f_sml, DIM)
        put_text(surf, val, (cx + cw - 6, y), f_sml, vcol, align="right")
        y += lh



# ── GRID & EFEK TAMBAHAN ─────────────────────────────────────

def draw_grid(surf):
    if not show_grid: return
    cw = W - PANEL_W
    step = 100   # jarak antar garis dalam world units
    sp_px = step * scale
    if sp_px < 15: return  # terlalu kecil, skip
    ox, oy = w2s(0, 0)
    # range world yang terlihat
    wx0 = int((-cam_x) / scale / step) * step - step
    wx1 = int((cw - cam_x) / scale / step) * step + step
    wy0 = int((-cam_y) / scale / step) * step - step
    wy1 = int((H - cam_y) / scale / step) * step + step
    for wx in range(wx0, wx1 + step, step):
        sx, _ = w2s(wx, 0)
        if not (0 <= sx <= cw): continue
        is_axis = (wx == 0)
        col = (60, 100, 180) if is_axis else (28, 45, 80)
        pygame.draw.line(surf, col, (sx, 0), (sx, H), 2 if is_axis else 1)
        if sp_px > 30 and not is_axis:
            put_text(surf, str(wx), (sx + 2, max(oy, 2) + 2), f_sml, (50, 80, 130))
    for wy in range(wy0, wy1 + step, step):
        _, sy = w2s(0, wy)
        if not (0 <= sy <= H): continue
        is_axis = (wy == 0)
        col = (60, 100, 180) if is_axis else (28, 45, 80)
        pygame.draw.line(surf, col, (0, sy), (cw, sy), 2 if is_axis else 1)
        if sp_px > 30 and not is_axis:
            put_text(surf, str(wy), (max(ox, 2) + 2, sy - 14), f_sml, (50, 80, 130))

def draw_help_overlay(surf):
    if not show_help: return
    # background gelap semi-transparan
    cw = W - PANEL_W
    ow, oh = min(cw - 40, 820), 520
    ox = (cw - ow) // 2
    oy = (H - oh) // 2
    bg = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(bg, (5, 10, 28, 235), (0, 0, ow, oh), border_radius=14)
    pygame.draw.rect(bg, (40, 80, 160, 220), (0, 0, ow, oh), 2, border_radius=14)
    surf.blit(bg, (ox, oy))

    lh = 18
    y = oy + 14
    # judul
    put_text(surf, "PANDUAN KONTROL", (ox + ow//2, y), f_ttl, GOLD, align="center"); y += 24
    pygame.draw.line(surf, (40, 80, 160), (ox+12, y), (ox+ow-12, y), 1); y += 10

    # dua kolom
    col_w = ow // 2 - 16
    lx1 = ox + 12
    lx2 = ox + ow//2 + 4

    mouse_rows = [
        ("MOUSE", None),
        ("Scroll",            "Zoom In / Out"),
        ("Klik kiri + Drag",  "Geser kamera"),
        ("Klik kiri planet",  "Pilih planet"),
        ("Klik kanan + Tarik","Slingshot meteor"),
        ("Tombol 1-4",        "Pilih ukuran meteor"),
    ]
    key_rows = [
        ("KEYBOARD", None),
        ("SPASI",    "Pause / Resume"),
        ("→",        "Step 1 frame (saat pause)"),
        ("S",        "Slow-mo 0.05x"),
        ("F",        "Follow planet"),
        ("[ / ]",    "Lambat / Cepat"),
        ("O",        "Toggle orbit"),
        ("L",        "Toggle label"),
        ("G",        "Toggle grid koordinat"),
        ("T",        "Toggle orbit trail"),
        ("V",        "Toggle garis gravitasi"),
        ("H",        "Sembunyikan panel"),
        ("R",        "Reset semua"),
        ("F1",       "Menu ini"),
        ("ESC",      "Keluar"),
    ]

    def draw_col(rows, x, start_y):
        cy = start_y
        for key, act in rows:
            if act is None:  # header
                put_text(surf, key, (x, cy), f_bdy, GOLD); cy += lh + 4
                pygame.draw.line(surf, (40, 60, 120), (x, cy), (x + col_w, cy), 1); cy += 6
            else:
                put_text(surf, f"  {key}", (x, cy), f_sml, ORANGE)
                put_text(surf, act, (x + col_w, cy), f_sml, WHITE, align="right")
                cy += lh
        return cy

    draw_col(mouse_rows, lx1, y)
    draw_col(key_rows,   lx2, y)

    # footer
    fy = oy + oh - 22
    pygame.draw.line(surf, (40, 80, 160), (ox+12, fy-6), (ox+ow-12, fy-6), 1)
    put_text(surf, "Tekan F1 untuk menutup", (ox + ow//2, fy), f_sml, DIM, align="center")

# ── UPDATE ──────────────────────────────────────────────────

def update_trails():
    # tambah posisi ke trail planet jika tidak paused
    if paused: return
    for p in planets:
        if p.get("dead"): continue
        p["trail"].append(p_wpos(p))
        if len(p["trail"]) > 400:
            p["trail"].pop(0)

def draw_trails(surf):
    if not show_trails: return
    cw = W - PANEL_W
    for p in planets:
        if p.get("dead") or len(p["trail"]) < 2: continue
        bc = p["col"]
        n  = len(p["trail"])
        for i in range(n - 1):
            ax, ay = w2s(*p["trail"][i])
            bx, by = w2s(*p["trail"][i+1])
            # kedua titik harus di dalam canvas
            on_a = 0 <= ax < cw and 0 <= ay < H
            on_b = 0 <= bx < cw and 0 <= by < H
            if not (on_a or on_b): continue
            ratio = (i + 1) / n
            col = (int(bc[0]*ratio), int(bc[1]*ratio), int(bc[2]*ratio))
            pygame.draw.line(surf, col, (ax, ay), (bx, by), 1)

def spawn_shockwave(wx, wy, max_r):
    shockwaves.append({"wx": wx, "wy": wy, "r": 0.0, "max_r": max_r, "life": 1.0})

def update_shockwaves(sp):
    for sw in shockwaves:
        sw["r"]    += sw["max_r"] * sp * 2.5
        sw["life"] -= sp * 2.0
    shockwaves[:] = [sw for sw in shockwaves if sw["life"] > 0]

def draw_shockwaves(surf):
    for sw in shockwaves:
        sx, sy = w2s(sw["wx"], sw["wy"])
        sr = max(int(sw["r"] * scale), 2)
        alpha = int(255 * max(sw["life"], 0))
        rs = pygame.Surface((sr*2+4, sr*2+4), pygame.SRCALPHA)
        pygame.draw.circle(rs, (255, 200, 80, alpha), (sr+2, sr+2), sr, 2)
        surf.blit(rs, (sx - sr - 2, sy - sr - 2))

def draw_gravity_lines(surf):
    if not show_grav_lines: return
    cw = W - PANEL_W
    for m in meteors:
        if not m["alive"]: continue
        msx, msy = w2s(m["wx"], m["wy"])
        if not (0 <= msx < cw and 0 <= msy < H): continue
        for p in planets:
            if p.get("dead"): continue
            pwx, pwy = p_wpos(p)
            d = math.hypot(m["wx"] - pwx, m["wy"] - pwy)
            if d > 400: continue
            psx, psy = w2s(pwx, pwy)
            if not (0 <= psx < cw and 0 <= psy < H): continue
            strength = min(1.0, 80 / max(d, 1))
            col = (int(30*strength), int(80*strength), int(200*strength))
            pygame.draw.line(surf, col, (msx, msy), (psx, psy), 1)
        # garis ke matahari
        d_sun = math.hypot(m["wx"], m["wy"])
        if d_sun < 300:
            ssx, ssy = w2s(0, 0)
            strength = min(1.0, 80 / max(d_sun, 1))
            col_sun = (int(100*strength), int(80*strength), 0)
            pygame.draw.line(surf, col_sun, (msx, msy), (ssx, ssy), 1)

def draw_sling_preview(surf):
    if sling_start is None: return
    pygame.draw.line(surf, (255, 220, 0), sling_start, sling_cur, 2)
    # hitung vx/vy di world space
    dx = sling_start[0] - sling_cur[0]
    dy = sling_start[1] - sling_cur[1]
    vx = dx * 3.0 / scale
    vy = dy * 3.0 / scale
    # posisi world titik awal
    wx, wy = screen_to_world(sling_start[0], sling_start[1])
    tvx, tvy = vx, vy
    cw = W - PANEL_W
    for step in range(60):
        # gravity dari planet
        for p in planets:
            if p.get("dead"): continue
            pwx, pwy = p_wpos(p)
            ddx = pwx - wx
            ddy = pwy - wy
            dist = max(math.hypot(ddx, ddy), 5)
            grav_r = max(p["r"], 8)
            acc = METEOR_G * grav_r / (dist * dist)
            sp_sim = 1.0/60.0
            tvx += (ddx/dist) * acc * sp_sim
            tvy += (ddy/dist) * acc * sp_sim
        # gravity matahari
        sdx, sdy = -wx, -wy
        sdist = max(math.hypot(sdx, sdy), 5)
        sacc = METEOR_G * 40 / (sdist * sdist)
        sp_sim = 1.0/60.0
        tvx += (sdx/sdist) * sacc * sp_sim
        tvy += (sdy/sdist) * sacc * sp_sim
        wx += tvx * sp_sim
        wy += tvy * sp_sim
        tsx, tsy = w2s(wx, wy)
        if 0 <= tsx < cw and 0 <= tsy < H:
            ratio = step / 60.0
            alpha = int(200 * (1 - ratio))
            r = max(int(2 * (1 - ratio * 0.5)), 1)
            ts = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
            pygame.draw.circle(ts, (255, 220, 80, alpha), (r+1, r+1), r)
            surf.blit(ts, (tsx - r - 1, tsy - r - 1))

def update(dt):
    global sun_time, comet_angle, comet_trail, cam_x, cam_y, step_once, tracking

    if paused and not step_once:
        return

    # kalau step mode: pakai 1 frame tetap, bukan dt asli
    sp        = (1.0 / 60.0) * tspd if paused else (dt / 1000.0) * tspd
    step_once = False

    for p in planets:
        p["angle"] += p["spd"] * sp
        p["srot"]   = (p["srot"] + p["sspd"] * sp) % (2 * math.pi)
        if "moon_angle" in p:
            p["moon_angle"] += p["moon_spd"] * sp

    for a in ASTEROIDS:
        a["angle"] += a["spd"] * sp

    # komet: kecepatan proporsional dengan 1/jarak (Kepler)
    cwx, cwy = comet_wpos()
    dist_sun  = max(math.hypot(cwx, cwy), 5)
    comet_angle += COMET_SPD * (COMET_PERI / dist_sun) * sp

    # rekam posisi trail setelah update
    nwx, nwy = comet_wpos()
    comet_trail.append((nwx, nwy))
    if len(comet_trail) > 120:
        comet_trail.pop(0)

    # sun time terus jalan (tidak dipengaruhi tspd)
    if not paused:
        sun_time += dt / 1000.0

    # smooth camera follow
    if tracking and sel is not None:
        if planets[sel].get("dead"):
            tracking = False
        else:
            wx, wy = p_wpos(planets[sel])
            target_x = W / 2.0 - wx * scale
            target_y = H / 2.0 - wy * scale
            cam_x   += (target_x - cam_x) * 0.1
            cam_y   += (target_y - cam_y) * 0.1

    update_meteors(sp)
    update_expl_parts(sp)
    update_trails()
    update_shockwaves(sp)


# ── MAIN ────────────────────────────────────────────────────

def handle_click(pos):
    global sel
    mx, my = pos
    if mx >= W - PANEL_W: return
    best, bdist = None, float("inf")
    for i, p in enumerate(planets):
        if p.get("dead"): continue   # planet hancur, skip render
        sx, sy = p_spos(p)
        d  = math.hypot(mx - sx, my - sy)
        cr = max(p["r"] * scale + 8, 14)
        if d < cr and d < bdist:
            bdist, best = d, i
    sel = best if best != sel else None

def main():
    global cam_x, cam_y, scale, paused, tspd, tspd_saved, slomo
    global sel, dragging, drag_from, cam_from
    global show_orbit, show_label, tracking, step_once, meteor_size_sel
    global show_grid, show_trails, show_grav_lines, hide_panel, show_help
    global sling_start, sling_cur

    running = True
    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if   event.key == pygame.K_ESCAPE:        running = False
                elif event.key == pygame.K_SPACE:          paused = not paused
                elif event.key == pygame.K_r:
                    cam_x, cam_y, scale, tspd, sel = float(W//2), float(H//2), 0.82, 1.0, None
                    tracking, slomo, tspd_saved = False, False, 1.0
                    meteor_size_sel = 1
                    meteors.clear()
                    expl_parts.clear()
                    for i, p in enumerate(planets):   # restore planet yang hancur
                        planets[i] = dict(PDATA[i])
                    shockwaves.clear()
                    for p in planets: p["trail"] = []
                    sling_start = sling_cur = None
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    meteor_size_sel = event.key - pygame.K_1
                elif event.key == pygame.K_RIGHT:
                    if paused: step_once = True
                elif event.key == pygame.K_f:
                    if sel is not None: tracking = not tracking
                elif event.key == pygame.K_s:
                    # toggle slomo: 0.05x <-> speed sebelumnya
                    if slomo:
                        tspd, slomo = tspd_saved, False
                    else:
                        tspd_saved, tspd, slomo = tspd, 0.05, True
                elif event.key == pygame.K_LEFTBRACKET:
                    tspd = max(0.02, round(tspd - 0.1, 2))
                    if not slomo: tspd_saved = tspd
                elif event.key == pygame.K_RIGHTBRACKET:
                    tspd = min(8.0, round(tspd + 0.2, 1))
                    if not slomo: tspd_saved = tspd
                elif event.key == pygame.K_o:              show_orbit = not show_orbit
                elif event.key == pygame.K_l:              show_label = not show_label
                elif event.key == pygame.K_g:              show_grid = not show_grid
                elif event.key == pygame.K_t:              show_trails = not show_trails
                elif event.key == pygame.K_v:              show_grav_lines = not show_grav_lines
                elif event.key == pygame.K_h:              hide_panel = not hide_panel
                elif event.key == pygame.K_F1:             show_help = not show_help
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    hit_btn = False
                    # cek tombol panduan "?" dulu
                    if get_help_btn_rect().collidepoint(event.pos):
                        show_help = not show_help
                        hit_btn = True
                    if not hit_btn:
                        for i, rect in enumerate(get_size_btn_rects()):
                            if rect.collidepoint(event.pos):
                                meteor_size_sel = i
                                hit_btn = True
                                break
                    if not hit_btn and event.pos[0] < W - PANEL_W and not tracking:
                        dragging  = True
                        drag_from = event.pos
                        cam_from  = (cam_x, cam_y)
                elif event.button == 3:  # klik kanan → slingshot meteor
                    if event.pos[0] < W - PANEL_W:
                        sling_start = event.pos
                        sling_cur   = event.pos
                elif event.button == 4: scale = min(4.0, scale * 1.12)
                elif event.button == 5: scale = max(0.18, scale / 1.12)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if dragging:
                        ddx = event.pos[0] - drag_from[0]
                        ddy = event.pos[1] - drag_from[1]
                        if abs(ddx) < 5 and abs(ddy) < 5:
                            handle_click(event.pos)
                    dragging = False
                elif event.button == 3:  # lepas klik kanan → lempar meteor
                    if sling_start is not None and event.pos[0] < W - PANEL_W:
                        dx = sling_start[0] - sling_cur[0]
                        dy = sling_start[1] - sling_cur[1]
                        ms = METEOR_SIZES[meteor_size_sel]
                        bc = ms["col"]
                        col = (
                            min(255, max(0, bc[0] + random.randint(-20, 20))),
                            min(255, max(0, bc[1] + random.randint(-20, 20))),
                            min(255, max(0, bc[2] + random.randint(-20, 20))),
                        )
                        wx, wy = screen_to_world(sling_start[0], sling_start[1])
                        meteors.append({
                            "wx": wx, "wy": wy,
                            "vx": dx * 3.0 / scale,
                            "vy": dy * 3.0 / scale,
                            "trail": [], "alive": True,
                            "size": ms["size"], "mass": ms["mass"], "col": col,
                        })
                    sling_start = sling_cur = None
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    cam_x = cam_from[0] + (event.pos[0] - drag_from[0])
                    cam_y = cam_from[1] + (event.pos[1] - drag_from[1])
                if sling_start is not None:
                    sling_cur = event.pos

        update(dt)

        screen.fill(BG)
        draw_grid(screen)
        draw_stars(screen)
        draw_trails(screen)
        draw_asteroids(screen)
        draw_comet(screen)
        draw_approach_effects(screen)
        draw_gravity_lines(screen)
        draw_meteors(screen)
        draw_expl_parts(screen)
        draw_shockwaves(screen)
        draw_sun(screen)
        draw_planets(screen)
        draw_sling_preview(screen)
        draw_planet_info_card(screen)
        draw_meteor_size_ui(screen)
        if not hide_panel:
            draw_panel(screen)
        else:
            put_text(screen, "H = Tampilkan Panel", (W - 175, H - 18), f_sml, (50, 60, 90))

        # hint saat pause
        if paused:
            put_text(screen, "|| PAUSED   ->  = step 1 frame", (10, H - 24), f_sml, (200, 80, 80))

        put_text(screen, f"FPS: {int(clock.get_fps())}", (8, 8), f_sml, (65, 70, 95))
        draw_help_btn(screen)           # tombol ? pojok kiri bawah
        draw_help_overlay(screen)       # overlay paling atas
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
