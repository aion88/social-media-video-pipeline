"""Remove rolling-shutter light banding (50 Hz mains, 30 fps -> 3-frame cycle).

Per frame: row luma profile P_t(y). Reference = mean of P over t-1,t,t+1 (one full
flicker cycle, so flicker cancels). Gain(y) = ref/P, fitted with a low-order cosine
basis (bands are ~1 cycle per frame height, motion is not) and clamped. Applied to Y.
Usage: deband.py in.MOV out.mov
"""

import subprocess, sys
import numpy as np

src, dst = sys.argv[1], sys.argv[2]
W, H = 1920, 1080
YS, CS = W * H, (W // 2) * (H // 2)
FS = YS + 2 * CS
K = 8  # cosine terms 0..7 (K=4 left 2-5x floor on IMG_4632)
y = (np.arange(H) + 0.5) / H
B = np.stack([np.cos(np.pi * k * y) for k in range(K)], 1)
Bp = np.linalg.pinv(B)

dec = subprocess.Popen(
    [
        "ffmpeg",
        "-v",
        "error",
        "-noautorotate",
        "-i",
        src,
        "-map",
        "0:v",
        "-fps_mode",
        "cfr",
        "-r",
        "30",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "yuv420p",
        "-",
    ],
    stdout=subprocess.PIPE,
    bufsize=FS * 4,
)
enc = subprocess.Popen(
    [
        "ffmpeg",
        "-v",
        "error",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "yuv420p",
        "-s",
        f"{W}x{H}",
        "-r",
        "30",
        # tag the INPUT: tagging only the output makes ffmpeg convert the matrix
        "-color_range",
        "tv",
        "-color_primaries",
        "bt709",
        "-color_trc",
        "bt709",
        "-colorspace",
        "bt709",
        "-i",
        "-",
        "-vf",
        "transpose=clock",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "17",
        "-pix_fmt",
        "yuv420p",
        dst,
    ],
    stdin=subprocess.PIPE,
)


def read():
    b = dec.stdout.read(FS)
    return np.frombuffer(b, np.uint8) if len(b) == FS else None


def prof(f):
    return f[:YS].reshape(H, W).astype(np.float32).mean(1) - 16.0


def fix(f, p, ref):
    r = np.clip(ref / np.maximum(p, 1.0), 0.85, 1.15)
    g = np.clip(B @ (Bp @ r), 0.92, 1.08).astype(np.float32)
    out = f.copy()
    Y = out[:YS].reshape(H, W).astype(np.float32)
    Y = (Y - 16.0) * g[:, None] + 16.0
    out[:YS] = np.clip(Y, 0, 255).astype(np.uint8).ravel()
    return out


def nextp():
    f = read()
    return (f, prof(f)) if f is not None else (None, None)


prev, cur, nxt = (None, None), nextp(), nextp()
n = 0
while cur[0] is not None:
    if prev[0] is not None and nxt[0] is not None:
        enc.stdin.write(fix(cur[0], cur[1], (prev[1] + cur[1] + nxt[1]) / 3).tobytes())
    else:
        enc.stdin.write(cur[0].tobytes())
    n += 1
    if n % 1000 == 0:
        print(n, "frames", flush=True)
    prev, cur, nxt = cur, nxt, nextp()

enc.stdin.close()
enc.wait()
dec.wait()
print("done", n, "frames")
