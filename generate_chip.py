from PIL import Image, ImageDraw, ImageFont
import math
import random

WIDTH, HEIGHT = 840, 220
FRAMES = 40
FPS_DELAY = 80

# Dark mode colors
BG_DARK = (13, 17, 23)
CHIP_BODY = (22, 27, 34)
CHIP_BORDER = (48, 54, 61)
TRACE_COLOR = (48, 54, 61)
PIN_COLOR = (125, 133, 144)
PULSE_CYAN = (88, 166, 255)
PULSE_GREEN = (63, 185, 80)
TEXT_COLOR = (200, 210, 220)
DIM_TEXT = (125, 133, 144)

# Chip dimensions - centered in wide banner
CHIP_W, CHIP_H = 90, 90
CHIP_X = (WIDTH - CHIP_W) // 2
CHIP_Y = (HEIGHT - CHIP_H) // 2
PIN_LEN = 14
PIN_WIDTH = 4
PINS_PER_SIDE = 7

random.seed(42)


def generate_traces():
    traces = []
    spacing = CHIP_W // (PINS_PER_SIDE + 1)
    v_spacing = CHIP_H // (PINS_PER_SIDE + 1)

    # Left pins - traces extend far left
    for i in range(PINS_PER_SIDE):
        px = CHIP_X - PIN_LEN
        py = CHIP_Y + v_spacing * (i + 1)
        waypoints = [(px, py)]

        mid_x = px - 40 - random.randint(10, 40)
        mid_y = py + random.randint(-20, 20)
        mid_y = max(15, min(HEIGHT - 15, mid_y))
        waypoints.append((mid_x, mid_y))

        far_x = random.randint(60, 160)
        waypoints.append((far_x, mid_y))

        far_y = mid_y + random.randint(-30, 30)
        far_y = max(15, min(HEIGHT - 15, far_y))
        waypoints.append((far_x, far_y))

        if i % 2 == 0:
            edge_x = random.randint(5, 50)
            waypoints.append((edge_x, far_y))

        traces.append(waypoints)

    # Right pins - traces extend far right
    for i in range(PINS_PER_SIDE):
        px = CHIP_X + CHIP_W + PIN_LEN
        py = CHIP_Y + v_spacing * (i + 1)
        waypoints = [(px, py)]

        mid_x = px + 40 + random.randint(10, 40)
        mid_y = py + random.randint(-20, 20)
        mid_y = max(15, min(HEIGHT - 15, mid_y))
        waypoints.append((mid_x, mid_y))

        far_x = WIDTH - random.randint(60, 160)
        waypoints.append((far_x, mid_y))

        far_y = mid_y + random.randint(-30, 30)
        far_y = max(15, min(HEIGHT - 15, far_y))
        waypoints.append((far_x, far_y))

        if i % 2 == 0:
            edge_x = WIDTH - random.randint(5, 50)
            waypoints.append((edge_x, far_y))

        traces.append(waypoints)

    # Top pins - shorter vertical traces with horizontal runs
    for i in range(PINS_PER_SIDE):
        px = CHIP_X + spacing * (i + 1)
        py = CHIP_Y - PIN_LEN
        waypoints = [(px, py)]

        up_y = py - random.randint(15, 30)
        up_y = max(8, up_y)
        waypoints.append((px, up_y))

        direction = -1 if i < PINS_PER_SIDE // 2 else 1
        branch_x = px + direction * random.randint(40, 100 + i * 10)
        branch_x = max(10, min(WIDTH - 10, branch_x))
        waypoints.append((branch_x, up_y))

        end_y = random.randint(5, max(8, up_y - 5))
        waypoints.append((branch_x, end_y))

        traces.append(waypoints)

    # Bottom pins
    for i in range(PINS_PER_SIDE):
        px = CHIP_X + spacing * (i + 1)
        py = CHIP_Y + CHIP_H + PIN_LEN
        waypoints = [(px, py)]

        down_y = py + random.randint(15, 30)
        down_y = min(HEIGHT - 8, down_y)
        waypoints.append((px, down_y))

        direction = -1 if i < PINS_PER_SIDE // 2 else 1
        branch_x = px + direction * random.randint(40, 100 + i * 10)
        branch_x = max(10, min(WIDTH - 10, branch_x))
        waypoints.append((branch_x, down_y))

        end_y = min(HEIGHT - 5, down_y + random.randint(5, 15))
        waypoints.append((branch_x, end_y))

        traces.append(waypoints)

    return traces


def lerp_along_path(waypoints, t):
    if t <= 0:
        return waypoints[0]
    if t >= 1:
        return waypoints[-1]

    segments = []
    total_len = 0
    for i in range(len(waypoints) - 1):
        dx = waypoints[i+1][0] - waypoints[i][0]
        dy = waypoints[i+1][1] - waypoints[i][1]
        seg_len = math.sqrt(dx*dx + dy*dy)
        segments.append(seg_len)
        total_len += seg_len

    if total_len == 0:
        return waypoints[0]

    target_dist = t * total_len
    traveled = 0
    for i, seg_len in enumerate(segments):
        if traveled + seg_len >= target_dist:
            local_t = (target_dist - traveled) / seg_len if seg_len > 0 else 0
            x = waypoints[i][0] + local_t * (waypoints[i+1][0] - waypoints[i][0])
            y = waypoints[i][1] + local_t * (waypoints[i+1][1] - waypoints[i][1])
            return (x, y)
        traveled += seg_len
    return waypoints[-1]


def draw_pulses(img, draw, traces, t, pulse_colors):
    for idx, waypoints in enumerate(traces):
        phase = (idx * 0.06 + t) % 1.0
        pulse_color = pulse_colors[idx % len(pulse_colors)]

        pos = lerp_along_path(waypoints, phase)
        px, py = int(pos[0]), int(pos[1])

        for r in range(8, 2, -1):
            alpha = int(35 * (8 - r) / 6)
            glow_color = pulse_color + (alpha,)
            glow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_layer)
            glow_draw.ellipse([px-r, py-r, px+r, py+r], fill=glow_color)
            img = Image.alpha_composite(img, glow_layer)
            draw = ImageDraw.Draw(img)

        draw.ellipse([px-3, py-3, px+3, py+3], fill=pulse_color + (255,))

    return img, draw


def draw_base(draw, chip_body, chip_border, trace_color, pin_color, text_color, dim_text, traces):
    spacing = CHIP_W // (PINS_PER_SIDE + 1)
    v_spacing = CHIP_H // (PINS_PER_SIDE + 1)

    for waypoints in traces:
        for i in range(len(waypoints) - 1):
            draw.line([waypoints[i], waypoints[i+1]], fill=trace_color, width=2)
        end = waypoints[-1]
        draw.ellipse([end[0]-3, end[1]-3, end[0]+3, end[1]+3], fill=trace_color)

    for i in range(PINS_PER_SIDE):
        px = CHIP_X + spacing * (i + 1)
        draw.rectangle([px-PIN_WIDTH//2, CHIP_Y-PIN_LEN, px+PIN_WIDTH//2, CHIP_Y], fill=pin_color)
        draw.rectangle([px-PIN_WIDTH//2, CHIP_Y+CHIP_H, px+PIN_WIDTH//2, CHIP_Y+CHIP_H+PIN_LEN], fill=pin_color)

    for i in range(PINS_PER_SIDE):
        py = CHIP_Y + v_spacing * (i + 1)
        draw.rectangle([CHIP_X-PIN_LEN, py-PIN_WIDTH//2, CHIP_X, py+PIN_WIDTH//2], fill=pin_color)
        draw.rectangle([CHIP_X+CHIP_W, py-PIN_WIDTH//2, CHIP_X+CHIP_W+PIN_LEN, py+PIN_WIDTH//2], fill=pin_color)

    draw.rectangle([CHIP_X, CHIP_Y, CHIP_X+CHIP_W, CHIP_Y+CHIP_H], fill=chip_body, outline=chip_border, width=2)
    draw.arc([CHIP_X+CHIP_W//2-6, CHIP_Y-1, CHIP_X+CHIP_W//2+6, CHIP_Y+11], 0, 180, fill=chip_border, width=2)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 12)
        font_sm = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 9)
    except:
        font = ImageFont.load_default()
        font_sm = font

    label = "PACKETZ"
    bbox = draw.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((CHIP_X + (CHIP_W - tw) // 2, CHIP_Y + 28), label, fill=text_color, font=font)

    sub = "IC-2015"
    bbox2 = draw.textbbox((0, 0), sub, font=font_sm)
    tw2 = bbox2[2] - bbox2[0]
    draw.text((CHIP_X + (CHIP_W - tw2) // 2, CHIP_Y + 48), sub, fill=dim_text, font=font_sm)


# Generate traces once (shared across all frames)
traces = generate_traces()

# ── Dark mode ──
print("Generating dark mode frames...")
dark_frames = []
for i in range(FRAMES):
    img = Image.new("RGBA", (WIDTH, HEIGHT), BG_DARK + (255,))
    draw = ImageDraw.Draw(img)
    draw_base(draw, CHIP_BODY, CHIP_BORDER, TRACE_COLOR, PIN_COLOR, TEXT_COLOR, DIM_TEXT, traces)
    img, draw = draw_pulses(img, draw, traces, i / FRAMES, [PULSE_CYAN, PULSE_GREEN])
    dark_frames.append(img)
    if (i + 1) % 10 == 0:
        print(f"  Frame {i+1}/{FRAMES}")

print("Saving chip-dark.gif...")
dark_frames[0].save(
    "/Users/chipsteen/Code/Packetz/assets/chip-dark.gif",
    save_all=True,
    append_images=dark_frames[1:],
    duration=FPS_DELAY,
    loop=0,
    disposal=2,
)

# ── Light mode ──
print("Generating light mode frames...")
light_frames = []
for i in range(FRAMES):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw_base(draw, (240, 240, 245), (200, 205, 212), (200, 205, 212), (150, 158, 168), (36, 41, 47), (125, 133, 144), traces)
    img, draw = draw_pulses(img, draw, traces, i / FRAMES, [(9, 105, 218), (26, 127, 55)])
    light_frames.append(img)

print("Saving chip-light.gif...")
light_frames[0].save(
    "/Users/chipsteen/Code/Packetz/assets/chip-light.gif",
    save_all=True,
    append_images=light_frames[1:],
    duration=FPS_DELAY,
    loop=0,
    disposal=2,
)

print("Done!")
