#!/usr/bin/env python3
"""Les overlays d'une vidéo parlée :
- l'accroche au début (durée validée), puis UNE idée par phrase, pas chaque mot ;
- les mots clés de l'idée surlignés en vert clair (SURLIGNE ci-dessous, à changer), texte encre ;
- apparition en fondu court avec une montée de quelques pixels, le surlignage passe comme un
  feutre, disparition en fondu sur place : pas d'effet parallaxe, jamais deux idées à la fois ;
- sous le menton, pas collé au visage.
Le look (cube) passe sous le texte. Typo : Inter Display Medium et Light (OFL, outils/fonts/) ; `polices` dans overlays.json pour la tienne.

  overlays.py texte <dossier>   les phrases datées du montage, pour écrire les idées (transcrit
                                d'abord si besoin : transcribe.sh de /sm-motion, ~1 min)
  overlays.py essai <dossier>   le calendrier sans rendu : début, durée, largeur, TROP LARGE, COURT
  overlays.py <dossier>         le rendu : <STEM>.overlays.mp4, <STEM>.thumbnail.png,
                                overlays/sous-titres.json (quoi, quand) et overlays/check.jpg
overlays.json (exemple complet : example/overlays.json) :
  {"video": "IMG_4640.reel.mp4",     le montage exporté ; absent = <STEM>.reel.mp4
   "look": "look/essai-D.cube",      chemin depuis le dossier ; null = aucun ;
                                     absent = outils/looks/look.cube s'il est fixé
   "couleur": "blanc", "y": 1300,    blanc ou noir ; centre du texte (défaut 1300, sous le menton)
   "polices": {"medium": "/chemin/Ma-Medium.ttf", "book": "...", "ita": "..."},   facultatif
   "accroche": {"lignes": [["comment préserver", "book", 86], ["ta concentration", "medium", 140],
                           ["*en bossant avec l'IA", "ita", 46, 150]], "fin": 5.1},
   "idees": [["c'est **un carnet**", "c'est un carnet"],    affiché (**surligné**, « / » coupe
             ["1|les idées", "numéro 1 les idées"]]         la ligne), phrase dite ; N|titre : une section
  }
Le son est copié tel quel : la vidéo d'entrée doit déjà être à -14 LUFS (derush export)."""

import json, os, re, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H, IPS = 1080, 1920, 30
Y0, HC = 1000, 600  # le calque texte couvre y 1000 à 1600
REPOS, ACCROCHE_Y = (
    1300,
    1300,
)  # centres : sous le menton (bas du visage à 953, p90 1002)
FONTS = Path(__file__).resolve().parent / "fonts"  # Inter Display, licence OFL, redistribuable
POLICE = {
    "medium": "InterDisplay-Medium.ttf",
    "book": "InterDisplay-Light.ttf",
    "ita": "InterDisplay-Light.ttf",  # pas d'italique livré : donne le tien via « polices »
}
COULEURS = {
    "blanc": ((255, 255, 255), (0, 0, 0), 0.5),
    "noir": ((14, 22, 32), (255, 255, 255), 0.45),
}
SURLIGNE, ENCRE = (
    (183, 198, 181),
    (14, 22, 32),
)  # vert clair du surlignage, encre : tes couleurs à toi, en RVB
TRANSCRIBE = (
    Path(__file__).resolve().parent.parent / ".claude" / "skills" / "sm-motion" / "scripts" / "transcribe.sh"
)
# Le look fixé par look.py. Le jour où derush export posera le look (lot 3 du plan), ce défaut
# tombe, sinon l'image est étalonnée deux fois.
LOOK_FIXE = Path(__file__).resolve().parent / "looks" / "look.cube"
TAILLE, LARGEUR_MAX = 66, 960
ENTREE, MONTEE, FEUTRE, SORTIE = 0.2, 10, 0.3, 0.15


POLICES_PERSO = {}  # rempli depuis « polices » d'overlays.json


def police(cle, taille):
    chemin = POLICES_PERSO.get(cle) or FONTS / POLICE[cle]
    return ImageFont.truetype(str(chemin), taille)


def norme(t):
    return re.sub(r"[^\w']", "", t.lower().replace("’", "'"))


def mots_dits(aligned):
    """(début, fin, normé) ; « l 'IA » et « celui -ci » recollés."""
    out = []
    for s in json.load(open(aligned))["segments"]:
        for w in s.get("words", []):
            t = w["word"].strip().replace("’", "'")
            if t[:1] in "'-" and out:
                out[-1] = (out[-1][0], w["end"], out[-1][2] + norme(t))
            elif norme(t):
                out.append((w["start"], w["end"], norme(t)))
    return out


def cherche(mots, phrase, i0=0):
    cible = [norme(x) for x in phrase.split() if norme(x)]
    for i in range(i0, len(mots) - len(cible) + 1):
        if [m[2] for m in mots[i : i + len(cible)]] == cible:
            return i, i + len(cible)
    return None


def calendrier(mots, spec):
    """Chaque idée entre quand sa phrase commence, reste au moins 1 s, et sort avant la suivante."""
    if not spec.get("idees"):
        sys.exit(
            "pas d'idées : écris overlays/overlays.json (format : overlays.py sans argument)"
        )
    out, i0 = [], 0
    for texte, phrase in spec["idees"]:
        r = cherche(mots, phrase, i0)
        if r is None:
            sys.exit(f"phrase introuvable : « {phrase} »")
        out.append(
            {
                "texte": texte,
                "debut": round(mots[r[0]][0] - 0.05, 3),
                "dit_fin": mots[r[1] - 1][1],
            }
        )
        i0 = r[0] + 1
    for k, c in enumerate(out):
        nxt = out[k + 1]["debut"] if k + 1 < len(out) else c["dit_fin"] + 1.5
        c["sortie"] = round(
            max(
                c["debut"] + 0.45,
                min(nxt - SORTIE - 0.02, max(c["dit_fin"] + 0.5, c["debut"] + 1.0)),
            ),
            3,
        )
    return out


def morceaux(texte):
    """« c'est **un carnet** » -> lignes de (texte, police, taille, surligné) ; « / » coupe la
    ligne ; « 1|les idées » : une section."""
    if "|" in texte:
        num, titre = texte.split("|", 1)
        return [[(num, "medium", 120, False), (titre, "medium", 72, True)]]
    lignes = []
    for l in texte.split(" / "):
        segs = []
        for p in re.split(r"(\*\*[^*]+\*\*)", l):
            if p.strip():
                segs.append(
                    (p[2:-2], "medium", TAILLE, True)
                    if p.startswith("**")
                    else (p.strip(), "medium", TAILLE, False)
                )
        lignes.append(segs)
    return lignes


def sprite(lignes, couleur):
    """Deux calques plein large : le texte (avec ombre) et le surlignage (boîte + texte encre),
    plus l'étendue x du surlignage pour l'effet feutre. Les mots surlignés sont aussi écrits en
    blanc : on les lit avant que le feutre passe."""
    k = 1.0
    while True:
        poses = []
        for segs in lignes:
            fs = [police(p, int(z * k)) for _, p, z, _ in segs]
            esp = fs[0].getlength(" ")
            larg = [f.getlength(t) for f, (t, *_) in zip(fs, segs)]
            total = sum(larg) + esp * (len(segs) - 1)
            x, pose = (W - total) / 2, []
            for f, w, (t, _, _, s) in zip(fs, larg, segs):
                pose.append((f, t, x, w, s))
                x += w + esp
            poses.append((pose, total))
        if max(tot for _, tot in poses) <= LARGEUR_MAX or k < 0.7:
            break
        k *= 0.94
    bb = [[f.getbbox("Hg", anchor="ls") for f, *_ in pose] for pose, _ in poses]
    pas = int(max(z for segs in lignes for _, _, z, _ in segs) * k * 1.3)
    base0 = 40 + max(-b[1] for b in bb[0])
    hauteur = int(base0 + pas * (len(lignes) - 1) + max(b[3] for b in bb[-1]) + 40)
    txt, boite, encre = (Image.new("L", (W, hauteur), 0) for _ in range(3))
    dt, db, de = ImageDraw.Draw(txt), ImageDraw.Draw(boite), ImageDraw.Draw(encre)
    xb = [W, 0]
    for i, (pose, _) in enumerate(poses):
        base = base0 + i * pas
        for f, t, x, w, s in pose:
            dt.text((x, base), t, font=f, fill=255, anchor="ls")
            if s:
                cap = f.getbbox("H", anchor="ls")[1]
                db.rounded_rectangle(
                    [x - 14, base + cap - 13, x + w + 14, base + 15],
                    radius=10,
                    fill=255,
                )
                de.text((x, base), t, font=f, fill=255, anchor="ls")
                xb = [min(xb[0], x - 14), max(xb[1], x + w + 14)]
    teinte, teinte_ombre, force = COULEURS[couleur]
    calque = Image.new("RGBA", (W, hauteur), (0, 0, 0, 0))
    ombre = txt.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * force))
    calque.paste((*teinte_ombre, 255), mask=ombre)
    calque.paste((*teinte, 255), mask=txt)
    feutre = Image.new("RGBA", (W, hauteur), (0, 0, 0, 0))
    feutre.paste(
        (0, 0, 0, 255),
        mask=boite.filter(ImageFilter.GaussianBlur(12)).point(lambda v: int(v * 0.2)),
    )
    feutre.paste((*SURLIGNE, 255), mask=boite.point(lambda v: int(v * 0.95)))
    feutre.paste((*ENCRE, 255), mask=ImageChops.multiply(encre, boite))
    return calque, feutre, xb


def tableau(img):
    a = np.asarray(img, np.float32) / 255
    a[..., :3] *= a[..., 3:4]
    return a


def doux(p):
    return 1 - (1 - min(max(p, 0.0), 1.0)) ** 3


def elements(spec, idees, couleur):
    els = []
    acc = spec.get("accroche") or {"lignes": [], "fin": 0}
    lignes = []
    for ligne in acc["lignes"]:
        texte, p, taille = ligne[:3]
        calque, _, _ = sprite([[(texte, p, taille, False)]], couleur)
        if len(ligne) > 3:
            calque = calque.transform(
                calque.size, Image.Transform.AFFINE, (1, 0, -ligne[3], 0, 1, 0)
            )
        a = tableau(calque)
        rows = np.where(a[..., 3].max(1) > 0)[0]
        lignes.append(a[rows[0] : rows[-1] + 1])
    total = sum(x.shape[0] for x in lignes) - 30 * (len(lignes) - 1)
    y = spec.get("y", ACCROCHE_Y) - total / 2
    for k, a in enumerate(lignes):
        els.append(
            {
                "calque": a,
                "feutre": None,
                "centre": y + a.shape[0] / 2,
                "a": 0.1 * k,
                "b": acc["fin"] - 0.25,
            }
        )
        y += a.shape[0] - 30
    for c in idees:
        calque, feutre, xb = sprite(morceaux(c["texte"]), couleur)
        a, f = tableau(calque), tableau(feutre)
        rows = np.where(np.maximum(a[..., 3], f[..., 3]).max(1) > 0)[0]
        els.append(
            {
                "calque": a[rows[0] : rows[-1] + 1],
                "feutre": f[rows[0] : rows[-1] + 1],
                "xb": xb,
                "centre": spec.get("y", REPOS),
                "a": c["debut"],
                "b": c["sortie"],
            }
        )
    return els


def image(els, t):
    can, vide = np.zeros((HC, W, 4), np.float32), True
    for s in els:
        if t < s["a"] or t > s["b"] + SORTIE:
            continue
        op = doux((t - s["a"]) / ENTREE) if t < s["b"] else 1 - (t - s["b"]) / SORTIE
        dy = MONTEE * (1 - doux((t - s["a"]) / ENTREE))
        h = s["calque"].shape[0]
        y = int(round(s["centre"] + dy - h / 2)) - Y0
        y0, y1 = max(0, y), min(HC, y + h)
        if y1 <= y0:
            continue
        src = s["calque"][y0 - y : y1 - y] * op
        if s["feutre"] is not None:  # le feutre passe de gauche à droite
            x0, x1 = s["xb"]
            xr = x0 + (x1 - x0 + 30) * doux((t - s["a"] - 0.05) / FEUTRE)
            masque = np.clip((xr - np.arange(W)) / 30, 0, 1)[None, :, None]
            f = s["feutre"][y0 - y : y1 - y] * op * masque
            src = src + f * (1 - src[..., 3:4])
        can[y0:y1] = src + can[y0:y1] * (1 - src[..., 3:4])
        vide = False
    if vide:
        return None
    a = can[..., 3:4]
    can[..., :3] = np.where(a > 0, can[..., :3] / np.maximum(a, 1e-6), 0)
    return (np.clip(can, 0, 1) * 255 + 0.5).astype(np.uint8)


def ouvre(dossier):
    dossier = Path(dossier)
    if not dossier.is_dir():  # un STEM seul : videos/<STEM>
        dossier = Path(__file__).resolve().parent.parent / "videos" / dossier.name
    dossier = dossier.resolve()
    p = dossier / "overlays" / "overlays.json"
    spec = json.load(open(p)) if p.exists() else {}
    POLICES_PERSO.update(spec.get("polices") or {})
    return dossier, spec


def source(dossier, spec):
    """La vidéo sous le texte : "video" de overlays.json, sinon <STEM>.reel.mp4 (derush export)."""
    v = spec.get("video") or f"{dossier.name}.reel.mp4"
    if not (dossier / v).exists():
        sys.exit(
            f"pas de {v} dans {dossier} : derush export {dossier.name} d'abord, ou « video » dans overlays.json"
        )
    return v


def aligned(dossier, video):
    """Le transcript daté de la vidéo : overlays/_work, sinon motion/_work (vidéos d'avant), s'il est
    plus récent qu'elle ; sinon transcribe.sh de /sm-motion (whisper + alignement) dans overlays/_work."""
    t = (dossier / video).stat().st_mtime
    for w in ("overlays", "motion"):
        p = dossier / w / "_work" / "aligned.json"
        if p.exists() and p.stat().st_mtime >= t:
            return p
    work = dossier / "overlays" / "_work"
    work.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(TRANSCRIBE), video, str(work)], cwd=dossier, check=True)
    return work / "aligned.json"


def cube(dossier, spec):
    """Le look sous le texte : « look » d'overlays.json (chemin depuis le dossier vidéo, null =
    aucun), sinon outils/looks/look.cube. Aucun des deux : refus, le choix est à toi."""
    if "look" in spec:
        if not spec["look"]:
            return None
        p = (dossier / spec["look"]).resolve()
        if not p.exists():
            sys.exit(f"look introuvable : {p} (outils/look.py cube <lettre> <chemin> le refait)")
        return p
    if LOOK_FIXE.exists():
        return LOOK_FIXE
    sys.exit("aucun look choisi : outils/look.py planche <vidéo> puis outils/look.py fixe <lettre>, une fois "
             "pour toutes ; ou « look » dans overlays.json (un cube d'essai, ou null pour aucun)")


def phrases(dossier):
    dossier, spec = ouvre(dossier)
    for s in json.load(open(aligned(dossier, source(dossier, spec))))["segments"]:
        print(f"{s['start']:6.2f} {s['text'].strip()}")


def essai(dossier):
    """Le calendrier et la largeur de chaque idée, sans rendu."""
    dossier, spec = ouvre(dossier)
    idees = calendrier(mots_dits(aligned(dossier, source(dossier, spec))), spec)
    for c in idees:
        larg = []
        for segs in morceaux(c["texte"]):
            fs = [police(p, z) for _, p, z, _ in segs]
            larg.append(
                int(
                    sum(f.getlength(t) for f, (t, *_) in zip(fs, segs))
                    + fs[0].getlength(" ") * (len(segs) - 1)
                )
            )
        d = c["sortie"] - c["debut"]
        drapeaux = (" TROP LARGE (rétrécie)" if max(larg) > LARGEUR_MAX else "") + (
            " COURT" if d < 0.6 else ""
        )
        print(f"{c['debut']:6.2f} {d:4.2f}s {max(larg):4d}px{drapeaux}  {c['texte']}")
    lut = cube(dossier, spec)
    print(f"{len(idees)} idées ; look : {lut or 'aucun'}")


def main(dossier):
    dossier, spec = ouvre(dossier)
    stem, ov = dossier.name, dossier / "overlays"
    video = source(dossier, spec)
    couleur = spec.get("couleur", "blanc")
    idees = calendrier(mots_dits(aligned(dossier, video)), spec)
    json.dump(idees, open(ov / "sous-titres.json", "w"), ensure_ascii=False, indent=1)
    els = elements(spec, idees, couleur)
    n = int(
        subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=nb_frames",
                "-of",
                "csv=p=0",
                video,
            ],
            cwd=dossier,
            capture_output=True,
            text=True,
        ).stdout
    )
    base, lut = "[0:v]", cube(dossier, spec)
    print("look :", lut or "aucun")
    if lut:
        base = (
            f"[0:v]scale=in_color_matrix=bt709:in_range=tv,format=gbrp16le,"
            f"lut3d=file='{os.path.relpath(lut, dossier)}':interp=tetrahedral,"
            f"scale=out_color_matrix=bt709:out_range=tv,format=yuv420p[g];[g]"
        )
    # incrustation en yuv420 : en « auto », ffmpeg repasse l'image en RGBA 8 bits et l'assombrit
    # de 2 niveaux sur 255 (mesuré le 2026-10-17)
    fc = f"[1:v]scale=out_color_matrix=bt709:out_range=tv,format=yuva420p[c];{base}[c]overlay=x=0:y={Y0}:format=yuv420[v]"
    sortie = f"{stem}.overlays.mp4"
    # pas de -frames:v : il coupait les 3 derniers paquets de son ; le calque fait exactement n images
    ff = subprocess.Popen(
        [
            "ffmpeg",
            "-nostdin",
            "-v",
            "error",
            "-y",
            "-i",
            video,
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgba",
            "-s",
            f"{W}x{HC}",
            "-r",
            str(IPS),
            "-i",
            "-",
            "-filter_complex",
            fc,
            "-map",
            "[v]",
            "-map",
            "0:a",
            "-c:v",
            "libx264",
            "-crf",
            "17",
            "-preset",
            "medium",
            "-pix_fmt",
            "yuv420p",
            "-colorspace",
            "bt709",
            "-color_primaries",
            "bt709",
            "-color_trc",
            "bt709",
            "-c:a",
            "copy",
            "-movflags",
            "+faststart",
            sortie,
        ],
        cwd=dossier,
        stdin=subprocess.PIPE,
    )
    vide = bytes(HC * W * 4)
    for i in range(n):
        im = image(els, i / IPS)
        ff.stdin.write(vide if im is None else im.tobytes())
    ff.stdin.close()
    if ff.wait():
        sys.exit("ffmpeg a échoué")
    subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-v",
            "error",
            "-y",
            "-ss",
            "1.3",
            "-i",
            sortie,
            "-frames:v",
            "1",
            f"{stem}.thumbnail.png",
        ],
        cwd=dossier,
        check=True,
    )
    sect = [c for c in idees if "|" in c["texte"]]
    autres = [c for c in idees if "|" not in c["texte"]]
    ts = [1.3] + [c["debut"] + 0.6 for c in sect[:1]] + [c["debut"] + 0.15 for c in autres[1:2]]
    ts += [c["debut"] + 0.7 for c in autres[2 :: max(1, len(autres) // 5)]][:5]
    vignettes = []
    for t in ts:
        raw = subprocess.run(
            [
                "ffmpeg",
                "-nostdin",
                "-v",
                "error",
                "-ss",
                f"{t:.2f}",
                "-i",
                sortie,
                "-frames:v",
                "1",
                "-vf",
                "scale=270:480",
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                "-",
            ],
            cwd=dossier,
            capture_output=True,
            check=True,
        ).stdout
        vignettes.append(Image.frombytes("RGB", (270, 480), raw))
    planche = Image.new("RGB", (270 * len(vignettes), 480))
    for k, v in enumerate(vignettes):
        planche.paste(v, (270 * k, 0))
    planche.save(ov / "check.jpg", quality=85)
    print(dossier / sortie, f"{len(idees)} idées")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 2 and a[0] in ("texte", "essai"):
        (phrases if a[0] == "texte" else essai)(a[1])
    elif len(a) == 1:
        main(a[0])
    else:
        sys.exit(__doc__)
