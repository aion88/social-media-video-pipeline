"""Efface le trou et les fissures du plafond (en haut à gauche) sur une prise face caméra.

Caméra posée : la zone ne bouge que de quelques px, suivie par template matching.
Le masque des dégâts est détecté une fois sur une image de référence. Chaque image :
la zone est remplie par un dégradé lisse (polynôme 2D ajusté sur un anneau de plafond
propre AUTOUR, donc suit l'expo) + un grain statique pris sur du plafond propre.
Un pixel n'est remplacé que s'il ressemble à la référence (dégât) : une main ou des
cheveux devant restent intacts. Travaille en YUV420 (aucune conversion de couleur).

Usage : plafond.py mask  in.mp4 t_ref out_dir     -> écrit mask.png + preview.png
        plafond.py render in.mp4 out_dir out.mp4  -> rend la vidéo (audio copié)
"""

import subprocess, sys, json, os
import cv2
import numpy as np

W, H = 1080, 1920
YS, CW, CH = W * H, W // 2, H // 2
FS = YS + 2 * CW * CH
RX, RY, RW, RH = 0, 0, 520, 360  # zone de travail (coin haut gauche)


def frame_at(src, t):
    b = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-ss",
            str(t),
            "-i",
            src,
            "-frames:v",
            "1",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "yuv420p",
            "-",
        ],
        capture_output=True,
    ).stdout
    return np.frombuffer(b[:FS], np.uint8)


def planes(f):
    Y = f[:YS].reshape(H, W)
    U = f[YS : YS + CW * CH].reshape(CH, CW)
    V = f[YS + CW * CH :].reshape(CH, CW)
    return Y, U, V


def poly_basis(h, w, deg=3):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xx /= w
    yy /= h
    return np.stack(
        [xx**i * yy**j for i in range(deg + 1) for j in range(deg + 1 - i)], -1
    )


def cmd_mask(src, t, out):
    os.makedirs(out, exist_ok=True)
    Y, U, V = planes(frame_at(src, t))
    roi = Y[RY : RY + RH, RX : RX + RW].astype(np.float32)
    bg = cv2.medianBlur(roi.astype(np.uint8), 61).astype(np.float32)
    dark = (bg - roi) > 7
    u = cv2.resize(
        U[RY // 2 : (RY + RH) // 2, RX // 2 : (RX + RW) // 2], (RW, RH)
    ).astype(np.float32)
    v = cv2.resize(
        V[RY // 2 : (RY + RH) // 2, RX // 2 : (RX + RW) // 2], (RW, RH)
    ).astype(np.float32)
    tan = (
        np.abs(u - cv2.medianBlur(u.astype(np.uint8), 61))
        + np.abs(v - cv2.medianBlur(v.astype(np.uint8), 61))
    ) > 5
    m = (dark | tan).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    keep = np.zeros_like(m)
    for i in range(1, n):
        # dégâts seulement : petits morceaux dans la zone du trou, jamais une tête qui entre par le bas
        if st[i, cv2.CC_STAT_AREA] >= 12 and cen[i][0] < 400 and cen[i][1] < 250:
            keep[lab == i] = 1
    keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    cs, _ = cv2.findContours(keep, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(keep, cs, -1, 1, cv2.FILLED)  # bouche l'intérieur uni du trou
    keep = cv2.dilate(keep, np.ones((11, 11), np.uint8))
    cv2.imwrite(f"{out}/mask.png", keep * 255)
    np.save(f"{out}/ref.npy", np.frombuffer(frame_at(src, t), np.uint8))
    prev = cv2.cvtColor(roi.astype(np.uint8), cv2.COLOR_GRAY2BGR)
    prev[keep > 0] = (0.5 * prev[keep > 0] + [0, 0, 127]).astype(np.uint8)
    cv2.imwrite(f"{out}/preview.png", prev)
    ys, xs = np.nonzero(keep)
    print(
        "mask px",
        int(keep.sum()),
        "bbox x",
        xs.min(),
        xs.max(),
        "y",
        ys.min(),
        ys.max(),
    )


def cmd_render(src, d, dst):
    mask0 = (cv2.imread(f"{d}/mask.png", 0) > 0).astype(np.uint8)
    ref = np.load(f"{d}/ref.npy")
    rY, rU, rV = planes(ref)
    ys, xs = np.nonzero(mask0)
    # template = dégâts + marge, en coordonnées ROI
    tx0, tx1, ty0, ty1 = (
        max(xs.min() - 10, 0),
        min(xs.max() + 10, RW),
        max(ys.min() - 10, 0),
        min(ys.max() + 10, RH),
    )
    tpl = rY[ty0:ty1, tx0:tx1]
    S = 24
    # grain : haute fréquence d'une zone de plafond propre (sous le masque, décalée)
    clean = rY[RY : RY + RH, RX : RX + RW].astype(np.float32)
    hp = clean - cv2.GaussianBlur(clean, (0, 0), 3)
    grain = hp.copy()
    far = cv2.dilate(mask0, np.ones((41, 41), np.uint8)) > 0
    pool = hp[~far]
    rng = np.random.default_rng(0)
    grain[:] = rng.choice(pool, size=hp.shape)
    grain = cv2.GaussianBlur(grain, (0, 0), 0.7) * 1.3

    dec = subprocess.Popen(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            src,
            "-map",
            "0:v",
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
            "-i",
            src,
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:a",
            "copy",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "17",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            dst,
        ],
        stdin=subprocess.PIPE,
    )
    X, Y0, sc_ = tx0, ty0, 1.0
    WW, WH = W, 1100  # zone de travail dans l'image (le trou peut s'y déplacer)
    GH = 520  # recherche globale : bande du plafond
    n = lost = 0
    log = []
    while True:
        b = dec.stdout.read(FS)
        if len(b) < FS:
            break
        f = np.frombuffer(b, np.uint8).copy()
        Y, U, V = planes(f)
        # 1. localiser : local à l'échelle courante, sinon global multi-échelle
        #    (elle se penche : le plafond recule, le trou rapetisse, bouge de 100+ px)
        ts = cv2.resize(tpl, None, fx=sc_, fy=sc_) if sc_ != 1 else tpl
        sx0, sy0 = max(int(X - S), 0), max(int(Y0 - S), 0)
        win = Y[sy0 : min(int(Y0 + ts.shape[0] + S), WH), sx0 : min(int(X + ts.shape[1] + S), WW)]
        sc = -1
        if win.shape[0] >= ts.shape[0] and win.shape[1] >= ts.shape[1]:
            r = cv2.matchTemplate(win, ts, cv2.TM_CCOEFF_NORMED)
            _, sc, _, loc = cv2.minMaxLoc(r)
        if sc > 0.75:
            X, Y0 = sx0 + loc[0], sy0 + loc[1]
        else:
            # plafond seulement (haut de l'image), et proche de la dernière position :
            # sans ça la recherche « trouve » le trou dans ses cheveux
            small = cv2.resize(Y[:GH, :WW], None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            best = (-9, 0, 0, 1, -1)
            for k in np.arange(0.4, 1.95, 0.1):
                t2 = cv2.resize(tpl, None, fx=k / 2, fy=k / 2, interpolation=cv2.INTER_AREA)
                if t2.shape[0] >= small.shape[0]:
                    continue
                r = cv2.matchTemplate(small, t2, cv2.TM_CCOEFF_NORMED)
                gy, gx = np.mgrid[0 : r.shape[0], 0 : r.shape[1]]
                pen = r - 0.0008 * np.hypot(gx * 2 - X, gy * 2 - Y0)
                _, pv, _, l2 = cv2.minMaxLoc(pen)
                if pv > best[0]:
                    best = (pv, l2[0] * 2, l2[1] * 2, k, r[l2[1], l2[0]])
            sc = best[4]
            if sc > 0.4:
                X, Y0, sc_ = best[1], best[2], round(float(best[3]), 2)
            else:
                lost += 1
        log.append((n, int(X), int(Y0), sc_, round(float(sc), 3)))
        # 2. fenêtre = zone du masque de référence projetée + marge
        M = np.float32([[sc_, 0, X - sc_ * tx0], [0, sc_, Y0 - sc_ * ty0]])
        mref = cv2.warpAffine(mask0, M, (WW, WH), flags=cv2.INTER_NEAREST)
        if mref.sum() == 0:
            enc.stdin.write(f.tobytes()); n += 1; continue
        zone = cv2.dilate(mref, np.ones((71, 71), np.uint8))
        yy, xx = np.nonzero(cv2.dilate(zone, np.ones((61, 61), np.uint8)))
        bx0, bx1, by0, by1 = xx.min(), xx.max() + 1, yy.min(), yy.max() + 1
        fy = Y[by0:by1, bx0:bx1].astype(np.float32)
        u = cv2.resize(U[by0 // 2 : (by1 + 1) // 2, bx0 // 2 : (bx1 + 1) // 2], (bx1 - bx0, by1 - by0)).astype(np.float32)
        v = cv2.resize(V[by0 // 2 : (by1 + 1) // 2, bx0 // 2 : (bx1 + 1) // 2], (bx1 - bx0, by1 - by0)).astype(np.float32)
        # 3. dégâts détectés SUR CETTE image : plus sombre que le plafond ou teinte du plâtre
        # cheveux = grande masse sombre ; un bout de fissure très sombre reste un dégât
        dk = (fy < 85).astype(np.uint8)
        nc, lab, st, _ = cv2.connectedComponentsWithStats(dk)
        big = np.isin(lab, [i for i in range(1, nc) if st[i, cv2.CC_STAT_AREA] > 600 * sc_ * sc_])
        hair = cv2.dilate(big.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
        bg = cv2.medianBlur(fy.astype(np.uint8), 61).astype(np.float32)
        ub = cv2.medianBlur(u.astype(np.uint8), 61).astype(np.float32)
        vb = cv2.medianBlur(v.astype(np.uint8), 61).astype(np.float32)
        dmg = (((bg - fy) > 7) | ((np.abs(u - ub) + np.abs(v - vb)) > 5)) & ~hair & (zone[by0:by1, bx0:bx1] > 0)
        dmg = dmg.astype(np.uint8)
        dmg = cv2.morphologyEx(dmg, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
        dmg = cv2.dilate(dmg, np.ones((11, 11), np.uint8)) & (~hair).astype(np.uint8)
        if dmg.sum() < 30:
            enc.stdin.write(f.tobytes()); n += 1; continue
        # 4. remplissage : polynôme ajusté sur l'anneau de plafond propre (pas de cheveux) + grain
        ring = (cv2.dilate(dmg, np.ones((41, 41), np.uint8)) > 0) & ~(cv2.dilate(dmg, np.ones((13, 13), np.uint8)) > 0)
        ringok = ring & ~hair & (np.abs(fy - bg) < 12)
        if ringok.sum() < 300:
            enc.stdin.write(f.tobytes()); n += 1; continue
        wgt = np.clip(cv2.GaussianBlur(dmg.astype(np.float32), (0, 0), 3) * 1.6, 0, 1) * (~hair)
        B = poly_basis(by1 - by0, bx1 - bx0)
        coef, *_ = np.linalg.lstsq(B[ringok], fy[ringok], rcond=None)
        gr = cv2.warpAffine(grain, M, (WW, WH), borderMode=cv2.BORDER_REFLECT)[by0:by1, bx0:bx1]
        fy = fy * (1 - wgt) + (B @ coef + gr) * wgt
        Y[by0:by1, bx0:bx1] = np.clip(fy, 0, 255).astype(np.uint8)
        cx0, cx1, cy0, cy1 = bx0 // 2, (bx1 + 1) // 2, by0 // 2, (by1 + 1) // 2
        wc = cv2.resize(wgt, (cx1 - cx0, cy1 - cy0), interpolation=cv2.INTER_AREA)
        rc = cv2.resize(ringok.astype(np.uint8), (cx1 - cx0, cy1 - cy0), interpolation=cv2.INTER_NEAREST) > 0
        Bc = poly_basis(cy1 - cy0, cx1 - cx0, 2)
        for P in (U, V):
            fc = P[cy0:cy1, cx0:cx1].astype(np.float32)
            cc, *_ = np.linalg.lstsq(Bc[rc], fc[rc], rcond=None)
            P[cy0:cy1, cx0:cx1] = np.clip(fc * (1 - wc) + (Bc @ cc) * wc, 0, 255).astype(np.uint8)
        enc.stdin.write(f.tobytes())
        n += 1
        if n % 1000 == 0:
            print(n, "images", flush=True)
    enc.stdin.close()
    enc.wait()
    dec.wait()
    json.dump(log, open(f"{d}/track.json", "w"))
    print("done", n, "images, suivi perdu sur", lost)


if __name__ == "__main__":
    if sys.argv[1] == "mask":
        cmd_mask(sys.argv[2], float(sys.argv[3]), sys.argv[4])
    else:
        cmd_render(sys.argv[2], sys.argv[3], sys.argv[4])
