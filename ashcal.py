import tkinter as tk
from tkinter import font as tkfont
import math
import tkinter.messagebox


# ─── Colour Palette ──────────────────────────────────────────────────────────
BG_DARK        = "#0a0a0f"        # near-black base
BG_PANEL       = "#12121e"        # card / panel
BG_DISPLAY     = "#0d0d1a"        # display background

# Neon accent gradients simulated via discrete colours
NEON_CYAN      = "#00f5ff"
NEON_PINK      = "#ff2d78"
NEON_LIME      = "#39ff14"
NEON_ORANGE    = "#ff7700"
NEON_PURPLE    = "#bf00ff"
NEON_YELLOW    = "#ffe600"

# Button families
CLR_NUM        = "#1c1c2e"        # number bg
CLR_NUM_FG     = "#e0e0ff"
CLR_NUM_HL     = "#2e2e50"        # hover / 3d-raise

CLR_OP         = "#1a0a2e"        # operator bg
CLR_OP_FG      = "#c77dff"        # violet text
CLR_OP_HL      = "#2a0a4e"

CLR_SCI        = "#001a2e"        # scientific bg
CLR_SCI_FG     = "#00d4ff"        # cyan text
CLR_SCI_HL     = "#002a4e"

CLR_EQ         = "#ff2d78"        # equals — hot pink
CLR_EQ_HL      = "#ff6ba8"
CLR_EQ_FG      = "#ffffff"

CLR_CLEAR      = "#ff7700"        # C — orange
CLR_CLEAR_HL   = "#ffa040"
CLR_CLEAR_FG   = "#ffffff"

CLR_DEL        = "#ffe600"        # DEL — yellow
CLR_DEL_HL     = "#fff060"
CLR_DEL_FG     = "#0a0a0f"

CLR_CONV       = "#39ff14"        # Rad/Deg toggle — lime
CLR_CONV_HL    = "#80ff50"
CLR_CONV_FG    = "#0a0a0f"

CLR_CONST      = "#bf00ff"        # π, e — purple
CLR_CONST_HL   = "#d966ff"
CLR_CONST_FG   = "#ffffff"

SHADOW_DARK    = "#000000"
SHADOW_LIGHT   = "#2a2a3a"

TEXT_DISPLAY   = "#00f5ff"        # cyan display digits
TEXT_EXPR      = "#6e6e9e"        # expression sub-text
TEXT_RESULT    = "#ffffff"

# ─── State ───────────────────────────────────────────────────────────────────
switch   = None          # None = Rad mode, True = Deg mode
history  = []            # list of (expression, result)


# ─── Root Window Setup ───────────────────────────────────────────────────────
root = tk.Tk()
root.geometry("780x560+200+80")
root.title("✦ Scientific Calculator — Ashley Gem")
root.resizable(False, False)
root.configure(bg=BG_DARK)

# Try to set a nice icon colour in the title bar (Windows only, silent fail)
try:
    root.iconbitmap(default='')
except Exception:
    pass

# ─── Fonts ───────────────────────────────────────────────────────────────────
FONT_DISPLAY   = tkfont.Font(family="Consolas",  size=30, weight="bold")
FONT_EXPR      = tkfont.Font(family="Consolas",  size=12)
FONT_BTN_LG    = tkfont.Font(family="Consolas",  size=18, weight="bold")
FONT_BTN_MD    = tkfont.Font(family="Consolas",  size=13, weight="bold")
FONT_BTN_SM    = tkfont.Font(family="Consolas",  size=11, weight="bold")
FONT_TITLE     = tkfont.Font(family="Consolas",  size=11, weight="bold")

# ─── Helpers ─────────────────────────────────────────────────────────────────
def get_display():
    return disp_var.get()

def set_display(val):
    disp_var.set(str(val))
    update_cursor_glow()

def append_display(char):
    cur = get_display()
    if cur == "0":
        set_display(char)
    else:
        set_display(cur + char)

def set_expr(val):
    expr_var.set(str(val))

def update_cursor_glow():
    """Flash the display glow strip briefly."""
    glow_strip.configure(bg=NEON_CYAN)
    root.after(80, lambda: glow_strip.configure(bg="#005566"))

def err(msg="Check your values and operators"):
    tkinter.messagebox.showerror("Value Error", msg)


# ─── Animated Button Press ───────────────────────────────────────────────────
def press_anim(btn, normal_bg, hover_bg, callback):
    """3-D press: darken → restore, then run callback."""
    btn.configure(bg=SHADOW_DARK, relief=tk.SUNKEN)
    root.after(80, lambda: btn.configure(bg=hover_bg, relief=tk.FLAT))
    root.after(160, lambda: btn.configure(bg=normal_bg, relief=tk.FLAT))
    root.after(80, callback)

def make_btn(parent, text, bg, fg, hover, cmd,
             fnt=None, padx=0, pady=0, col=1):
    """Create a styled 3D button with hover + press effects."""
    if fnt is None:
        fnt = FONT_BTN_LG

    # Outer shadow frame (creates 3D depth illusion)
    shadow = tk.Frame(parent, bg=SHADOW_DARK, bd=0)

    btn = tk.Button(
        shadow,
        text=text,
        font=fnt,
        bg=bg,
        fg=fg,
        activebackground=hover,
        activeforeground=fg,
        relief=tk.FLAT,
        bd=0,
        cursor="hand2",
        padx=padx,
        pady=pady,
    )
    btn.pack(padx=(0, 2), pady=(0, 3), expand=True, fill=tk.BOTH)

    # Hover effects
    btn.bind("<Enter>",  lambda e, b=btn, h=hover: b.configure(bg=h))
    btn.bind("<Leave>",  lambda e, b=btn, n=bg:    b.configure(bg=n))
    btn.bind("<ButtonPress-1>",   lambda e, b=btn, n=bg, h=hover, c=cmd:
             press_anim(b, n, h, c))

    if col > 1:
        shadow.grid_configure(columnspan=col)

    return shadow, btn


# ──────────────────────────────────────────────────────────────────────────────
#  DISPLAY PANEL
# ──────────────────────────────────────────────────────────────────────────────
display_frame = tk.Frame(root, bg=BG_PANEL,
                         highlightbackground=NEON_CYAN,
                         highlightthickness=2,
                         bd=0)
display_frame.pack(fill=tk.X, padx=14, pady=(14, 6))

# Title bar inside panel
title_bar = tk.Frame(display_frame, bg="#0f0f20", height=28)
title_bar.pack(fill=tk.X)

mode_var = tk.StringVar(value="RAD")
tk.Label(title_bar, text="✦ SCIENTIFIC CALCULATOR",
         font=FONT_TITLE, bg="#0f0f20",
         fg=NEON_PURPLE).pack(side=tk.LEFT, padx=12, pady=4)

mode_lbl = tk.Label(title_bar, textvariable=mode_var,
                    font=FONT_TITLE, bg="#0f0f20",
                    fg=NEON_LIME)
mode_lbl.pack(side=tk.RIGHT, padx=12, pady=4)

tk.Label(title_bar, text="  by Ashley Gem  ",
         font=FONT_EXPR, bg="#0f0f20",
         fg="#3a3a5a").pack(side=tk.RIGHT, padx=0)

# Glow strip (animated)
glow_strip = tk.Frame(display_frame, bg="#005566", height=3)
glow_strip.pack(fill=tk.X)

# Expression (secondary)
expr_var = tk.StringVar(value="")
expr_lbl = tk.Label(display_frame, textvariable=expr_var,
                    font=FONT_EXPR, bg=BG_DISPLAY,
                    fg=TEXT_EXPR, anchor="e", padx=16)
expr_lbl.pack(fill=tk.X, ipady=4)

# Main display
disp_var = tk.StringVar(value="0")
disp_lbl = tk.Label(display_frame, textvariable=disp_var,
                    font=FONT_DISPLAY, bg=BG_DISPLAY,
                    fg=TEXT_DISPLAY, anchor="e",
                    padx=16, pady=8,
                    wraplength=740, justify=tk.RIGHT)
disp_lbl.pack(fill=tk.X)

# Bottom glow line
tk.Frame(display_frame, bg=NEON_PINK, height=2).pack(fill=tk.X)


# ──────────────────────────────────────────────────────────────────────────────
#  BUTTON GRID
# ──────────────────────────────────────────────────────────────────────────────
btn_outer = tk.Frame(root, bg=BG_DARK)
btn_outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4, 10))

grid = tk.Frame(btn_outer, bg=BG_DARK)
grid.pack(fill=tk.BOTH, expand=True)

# Make all columns & rows equal weight
for c in range(9):
    grid.columnconfigure(c, weight=1, uniform="col")
for r in range(5):
    grid.rowconfigure(r, weight=1, uniform="row")


# ─── Button Actions ──────────────────────────────────────────────────────────
def digit(d):
    cur = get_display()
    if cur == "0":
        set_display(d)
    else:
        set_display(cur + d)

def operator(op):
    set_display(get_display() + op)

def btn_clear():
    set_display("0")
    set_expr("")

def btn_del():
    cur = get_display()
    if len(cur) <= 1 or cur in ("Error",):
        set_display("0")
    else:
        set_display(cur[:-1] or "0")

def btn_eq():
    expr = get_display()
    try:
        result = eval(expr.replace("^", "**"))
        set_expr(expr + "  =")
        set_display(result if isinstance(result, str) else
                    (int(result) if float(result).is_integer() else round(result, 10)))
        history.append((expr, result))
    except Exception:
        set_display("Error")
        set_expr("")
        root.after(1200, lambda: set_display("0"))

def sci_op(fn):
    try:
        val = float(get_display())
        result = fn(val)
        set_expr(get_display() + "  =")
        set_display(int(result) if isinstance(result, float) and result.is_integer()
                    else round(result, 10))
    except Exception as ex:
        err(str(ex))

def btn_sin():
    sci_op(lambda v: math.sin(math.radians(v)) if switch else math.sin(v))
def btn_cos():
    sci_op(lambda v: math.cos(math.radians(v)) if switch else math.cos(v))
def btn_tan():
    sci_op(lambda v: math.tan(math.radians(v)) if switch else math.tan(v))
def btn_asin():
    sci_op(lambda v: math.degrees(math.asin(v)) if switch else math.asin(v))
def btn_acos():
    sci_op(lambda v: math.degrees(math.acos(v)) if switch else math.acos(v))
def btn_atan():
    sci_op(lambda v: math.degrees(math.atan(v)) if switch else math.atan(v))
def btn_sqrt():
    sci_op(math.sqrt)
def btn_log():
    sci_op(math.log10)
def btn_ln():
    sci_op(math.log)
def btn_fact():
    sci_op(lambda v: math.factorial(int(v)))
def btn_round():
    sci_op(round)

def btn_conv():
    global switch
    if switch is None:
        switch = True
        mode_var.set("DEG")
        mode_lbl.configure(fg=NEON_ORANGE)
        conv_btn.configure(text="DEG", bg=NEON_ORANGE, fg="#0a0a0f")
    else:
        switch = None
        mode_var.set("RAD")
        mode_lbl.configure(fg=NEON_LIME)
        conv_btn.configure(text="RAD", bg=CLR_CONV, fg=CLR_CONV_FG)

def btn_pi():
    append_display(str(round(math.pi, 10)))
def btn_e():
    append_display(str(round(math.e, 10)))
def btn_pow():
    set_display(get_display() + "**")
def btn_dot():
    cur = get_display()
    # avoid double dot in the last number token
    tokens = cur.replace("+","|").replace("-","|").replace("*","|").replace("/","|")
    last = tokens.split("|")[-1]
    if "." not in last:
        set_display(cur + ".")
def btn_lbracket():
    append_display("(")
def btn_rbracket():
    append_display(")")
def btn_mod():
    set_display(get_display() + "%")
def btn_neg():
    cur = get_display()
    try:
        val = float(cur)
        set_display(-val if not cur.startswith("-") else abs(val))
    except Exception:
        set_display("(" + cur + ")*-1")


# ──────────────────────────────────────────────────────────────────────────────
#   ROW 0  —  Scientific row 1  (π  e  sin  cos  tan  ←  C  ( ) )
# ──────────────────────────────────────────────────────────────────────────────
def place(widget, row, col, **kw):
    widget.grid(row=row, column=col, sticky="nsew",
                padx=3, pady=3, **kw)

P = 4    # inner padx on buttons
Q = 2    # inner pady on buttons

# ROW 0
r0 = [
    make_btn(grid, "π",     CLR_CONST, CLR_CONST_FG, CLR_CONST_HL,  btn_pi,      FONT_BTN_LG, P, Q),
    make_btn(grid, "e",     CLR_CONST, CLR_CONST_FG, CLR_CONST_HL,  btn_e,       FONT_BTN_LG, P, Q),
    make_btn(grid, "sin",   CLR_SCI,   CLR_SCI_FG,   CLR_SCI_HL,    btn_sin,     FONT_BTN_MD, P, Q),
    make_btn(grid, "cos",   CLR_SCI,   CLR_SCI_FG,   CLR_SCI_HL,    btn_cos,     FONT_BTN_MD, P, Q),
    make_btn(grid, "tan",   CLR_SCI,   CLR_SCI_FG,   CLR_SCI_HL,    btn_tan,     FONT_BTN_MD, P, Q),
    make_btn(grid, "x!",    CLR_SCI,   CLR_SCI_FG,   CLR_SCI_HL,    btn_fact,    FONT_BTN_MD, P, Q),
    make_btn(grid, "√",     CLR_SCI,   CLR_SCI_FG,   CLR_SCI_HL,    btn_sqrt,    FONT_BTN_LG, P, Q),
    make_btn(grid, "⌫",     CLR_DEL,   CLR_DEL_FG,   CLR_DEL_HL,    btn_del,     FONT_BTN_LG, P, Q),
    make_btn(grid, "C",     CLR_CLEAR, CLR_CLEAR_FG, CLR_CLEAR_HL,  btn_clear,   FONT_BTN_LG, P, Q),
]
for i, (shadow, _) in enumerate(r0):
    place(shadow, 0, i)

# ROW 1
r1 = [
    make_btn(grid, "sin⁻¹", CLR_SCI,   CLR_SCI_FG,   CLR_SCI_HL,   btn_asin,   FONT_BTN_SM, P, Q),
    make_btn(grid, "cos⁻¹", CLR_SCI,   CLR_SCI_FG,   CLR_SCI_HL,   btn_acos,   FONT_BTN_SM, P, Q),
    make_btn(grid, "tan⁻¹", CLR_SCI,   CLR_SCI_FG,   CLR_SCI_HL,   btn_atan,   FONT_BTN_SM, P, Q),
    make_btn(grid, "log",   CLR_SCI,   CLR_SCI_FG,   CLR_SCI_HL,   btn_log,    FONT_BTN_MD, P, Q),
    make_btn(grid, "ln",    CLR_SCI,   CLR_SCI_FG,   CLR_SCI_HL,   btn_ln,     FONT_BTN_MD, P, Q),
    make_btn(grid, "x^y",   CLR_OP,    CLR_OP_FG,    CLR_OP_HL,    btn_pow,    FONT_BTN_MD, P, Q),
    make_btn(grid, "rnd",   CLR_SCI,   CLR_SCI_FG,   CLR_SCI_HL,   btn_round,  FONT_BTN_SM, P, Q),
    make_btn(grid, "(",     CLR_OP,    CLR_OP_FG,    CLR_OP_HL,    btn_lbracket, FONT_BTN_LG, P, Q),
    make_btn(grid, ")",     CLR_OP,    CLR_OP_FG,    CLR_OP_HL,    btn_rbracket, FONT_BTN_LG, P, Q),
]
for i, (shadow, _) in enumerate(r1):
    place(shadow, 1, i)

# ROW 2  —  7 8 9  /  %  +/-  and RAD toggle
r2 = [
    make_btn(grid, "7",     CLR_NUM, CLR_NUM_FG, CLR_NUM_HL,  lambda: digit("7"),       FONT_BTN_LG, P, Q),
    make_btn(grid, "8",     CLR_NUM, CLR_NUM_FG, CLR_NUM_HL,  lambda: digit("8"),       FONT_BTN_LG, P, Q),
    make_btn(grid, "9",     CLR_NUM, CLR_NUM_FG, CLR_NUM_HL,  lambda: digit("9"),       FONT_BTN_LG, P, Q),
    make_btn(grid, "÷",     CLR_OP,  CLR_OP_FG,  CLR_OP_HL,   lambda: operator("/"),   FONT_BTN_LG, P, Q),
    make_btn(grid, "%",     CLR_OP,  CLR_OP_FG,  CLR_OP_HL,   btn_mod,                  FONT_BTN_LG, P, Q),
    make_btn(grid, "+/−",   CLR_OP,  CLR_OP_FG,  CLR_OP_HL,   btn_neg,                  FONT_BTN_MD, P, Q),
]
for i, (shadow, _) in enumerate(r2):
    place(shadow, 2, i)

# RAD/DEG toggle spans cols 6-8
conv_shadow, conv_btn = make_btn(grid, "RAD", CLR_CONV, CLR_CONV_FG, CLR_CONV_HL, btn_conv, FONT_BTN_MD, P, Q, col=3)
conv_shadow.grid(row=2, column=6, columnspan=3, sticky="nsew", padx=3, pady=3)

# ROW 3  —  4 5 6  *  and right ops
r3 = [
    make_btn(grid, "4",  CLR_NUM, CLR_NUM_FG, CLR_NUM_HL,  lambda: digit("4"),       FONT_BTN_LG, P, Q),
    make_btn(grid, "5",  CLR_NUM, CLR_NUM_FG, CLR_NUM_HL,  lambda: digit("5"),       FONT_BTN_LG, P, Q),
    make_btn(grid, "6",  CLR_NUM, CLR_NUM_FG, CLR_NUM_HL,  lambda: digit("6"),       FONT_BTN_LG, P, Q),
    make_btn(grid, "×",  CLR_OP,  CLR_OP_FG,  CLR_OP_HL,   lambda: operator("*"),   FONT_BTN_LG, P, Q),
    make_btn(grid, "−",  CLR_OP,  CLR_OP_FG,  CLR_OP_HL,   lambda: operator("-"),   FONT_BTN_LG, P, Q),
    make_btn(grid, "+",  CLR_OP,  CLR_OP_FG,  CLR_OP_HL,   lambda: operator("+"),   FONT_BTN_LG, P, Q),
]
for i, (shadow, _) in enumerate(r3):
    place(shadow, 3, i)

# = button spans 3 columns on the right
eq_shadow, eq_btn = make_btn(grid, "=", CLR_EQ, CLR_EQ_FG, CLR_EQ_HL, btn_eq, FONT_BTN_LG, P, Q, col=3)
eq_shadow.grid(row=3, column=6, columnspan=3, sticky="nsew", padx=3, pady=3)
# Make the = label bigger & glow
eq_btn.configure(font=tkfont.Font(family="Consolas", size=22, weight="bold"))

# ROW 4  —  1 2 3 0 . (wide)
r4 = [
    make_btn(grid, "1",   CLR_NUM, CLR_NUM_FG, CLR_NUM_HL,  lambda: digit("1"),  FONT_BTN_LG, P, Q),
    make_btn(grid, "2",   CLR_NUM, CLR_NUM_FG, CLR_NUM_HL,  lambda: digit("2"),  FONT_BTN_LG, P, Q),
    make_btn(grid, "3",   CLR_NUM, CLR_NUM_FG, CLR_NUM_HL,  lambda: digit("3"),  FONT_BTN_LG, P, Q),
    make_btn(grid, "0",   CLR_NUM, CLR_NUM_FG, CLR_NUM_HL,  lambda: digit("0"),  FONT_BTN_LG, P, Q),
    make_btn(grid, ".",   CLR_NUM, CLR_NUM_FG, CLR_NUM_HL,  btn_dot,              FONT_BTN_LG, P, Q),
]
for i, (shadow, _) in enumerate(r4):
    place(shadow, 4, i)

# History area (cols 5-8, row 4)
hist_frame = tk.Frame(grid, bg="#0f0f1e",
                      highlightbackground="#2a2a3a",
                      highlightthickness=1)
hist_frame.grid(row=4, column=5, columnspan=4, sticky="nsew", padx=3, pady=3)

hist_title = tk.Label(hist_frame, text="HISTORY",
                      font=FONT_BTN_SM, bg="#0f0f1e",
                      fg="#3a3a6a")
hist_title.pack(anchor="w", padx=8, pady=(4, 0))

hist_var = tk.StringVar(value="—")
hist_lbl = tk.Label(hist_frame, textvariable=hist_var,
                    font=FONT_EXPR, bg="#0f0f1e",
                    fg="#5a5a8a", anchor="e",
                    justify=tk.RIGHT, wraplength=200)
hist_lbl.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)


# ─── Keyboard Bindings ───────────────────────────────────────────────────────
def on_key(event):
    k = event.keysym
    char = event.char

    if char.isdigit():
        digit(char)
    elif char == '+':
        operator("+")
    elif char == '-':
        operator("-")
    elif char == '*':
        operator("*")
    elif char == '/':
        operator("/")
    elif char == '.':
        btn_dot()
    elif char == '%':
        btn_mod()
    elif char in ('=', '\r'):
        btn_eq()
    elif k == 'BackSpace':
        btn_del()
    elif k == 'Delete' or char.lower() == 'c':
        btn_clear()
    elif char == '(':
        btn_lbracket()
    elif char == ')':
        btn_rbracket()

root.bind("<Key>", on_key)


# ─── History updater ─────────────────────────────────────────────────────────
def refresh_history():
    if history:
        last = history[-3:][::-1]
        lines = "\n".join(f"{e} = {r}" for e, r in last)
        hist_var.set(lines)
    root.after(500, refresh_history)

refresh_history()


# ─── Ambient glow pulsation ──────────────────────────────────────────────────
_glow_toggle = [True]
_glow_colors = [NEON_CYAN, NEON_PINK, NEON_PURPLE, NEON_LIME, NEON_ORANGE]
_glow_idx    = [0]

def pulse_border():
    """Cycle the display border colour for a living-neon effect."""
    c = _glow_colors[_glow_idx[0] % len(_glow_colors)]
    display_frame.configure(highlightbackground=c)
    _glow_idx[0] += 1
    root.after(1800, pulse_border)

pulse_border()


# ─── Startup flash animation ─────────────────────────────────────────────────
def startup_flash(step=0):
    colors = [NEON_CYAN, NEON_PINK, NEON_LIME, NEON_ORANGE, NEON_PURPLE, TEXT_DISPLAY]
    if step < len(colors):
        disp_lbl.configure(fg=colors[step])
        root.after(110, lambda: startup_flash(step + 1))
    else:
        disp_lbl.configure(fg=TEXT_DISPLAY)

root.after(200, startup_flash)


# ─── Equal-button glow pulse ─────────────────────────────────────────────────
_eq_bright = [True]
def pulse_eq():
    eq_btn.configure(bg=CLR_EQ if _eq_bright[0] else "#cc2260")
    _eq_bright[0] = not _eq_bright[0]
    root.after(900, pulse_eq)

pulse_eq()


# ─── Run ─────────────────────────────────────────────────────────────────────
root.mainloop()
