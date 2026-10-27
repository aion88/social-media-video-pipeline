#!/usr/bin/env python3
"""Le look : une planche de 4 versions sur des images de la prise, puis le cube choisi, une fois.

  look.py planche <video> [t1 t2 ...]   -> <dossier de la vidéo>/look/planche.jpg, ouverte dans Aperçu
                                          A neutre, B Kodak 2383, C Fuji 3513, D 2383 léger
  look.py fixe <lettre> [--force 0.6]   -> outils/looks/look.cube + LOOK.json, copie dans Resolve LUT/Perso/ si possible
  look.py cube <lettre> <sortie.cube>   -> le cube d'une lettre, sans rien fixer (pour un rendu d'essai)

Les Film Looks de Resolve attendent du Cineon Log (en-tête des .cube) : l'image Rec709 (gamma 2,4)
passe en linéaire puis en Cineon avant le LUT, sinon elle sort écrasée. L'exposition d'entrée est
calée pour qu'un gris moyen ressorte gris moyen."""

import datetime, json, os, shutil, subprocess, sys
from pathlib import Path
import cv2
import numpy as np

# Les LUT « Film Looks » livrés avec DaVinci Resolve (gratuit suffit), jamais copiés ici.
# Autre emplacement : export RESOLVE_FILM_LOOKS=/chemin/Film\ Looks
FILM = Path(
    os.environ.get("RESOLVE_FILM_LOOKS")
    or "/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/Film Looks"
)
RESOLVE_PERSO = FILM.parent / "Perso"
LOOKS = Path(__file__).resolve().parent / "looks"
N = 33
VERSIONS = {  # lettre : (nom, LUT de Resolve ou None, force par défaut)
    "A": ("neutre", None, 0.0),
    "B": ("Kodak 2383", "Rec709 Kodak 2383 D65.cube", 1.0),
    "C": ("Fuji 3513", "Rec709 Fujifilm 3513DI D65.cube", 1.0),
    "D": ("2383 léger", "Rec709 Kodak 2383 D65.cube", 0.5),
}


def disponibles():
    """Les lettres utilisables : A (neutre) toujours, B à D seulement si leur LUT Film Looks est là."""
    return {k: v for k, v in VERSIONS.items() if v[1] is None or (FILM / v[1]).is_file()}


def exiger(lettre):
    """La lettre, ou une sortie claire si elle n'existe pas ou si son LUT manque (pas de trace Python)."""
    if lettre not in VERSIONS:
        sys.exit(f"lettre inconnue « {lettre} » : {', '.join(VERSIONS)}")
    if lettre not in disponibles():
        sys.exit(f"{lettre} ({VERSIONS[lettre][0]}) demande le LUT « {VERSIONS[lettre][1]} » de DaVinci Resolve, "
                 f"absent de {FILM}. Installe DaVinci Resolve (gratuit), ou export RESOLVE_FILM_LOOKS=<dossier>. "
                 f"Sans lui, seul A (neutre) marche : {sys.argv[0]} fixe A")
    return lettre


def lire_cube(p):
    lignes = [l.split() for l in Path(p).read_text().splitlines()]
    n = next(int(l[1]) for l in lignes if l and l[0] == "LUT_3D_SIZE")
    data = np.array(
        [
            [float(x) for x in l]
            for l in lignes
            if len(l) == 3 and l[0][0] in "0123456789.-"
        ]
    )
    return data.reshape(n, n, n, 3)  # [b][g][r], le rouge varie le plus vite


def echantillonne(lut, rgb):
    n = lut.shape[0]
    x = np.clip(rgb, 0, 1) * (n - 1)
    i0 = np.minimum(x.astype(int), n - 2)
    f = x - i0
    out = 0
    for db in (0, 1):
        for dg in (0, 1):
            for dr in (0, 1):
                w = (
                    (f[..., 0] if dr else 1 - f[..., 0])
                    * (f[..., 1] if dg else 1 - f[..., 1])
                    * (f[..., 2] if db else 1 - f[..., 2])
                )
                out = (
                    out
                    + w[..., None]
                    * lut[i0[..., 2] + db, i0[..., 1] + dg, i0[..., 0] + dr]
                )
    return out


def vers_cineon(v, k):
    lin = np.clip(v, 0, 1) ** 2.4 * k
    off = 10 ** ((95 - 685) / 300)
    return (685 + 300 * np.log10(lin * (1 - off) + off)) / 1023


def expo(lut):
    """Gain d'entrée tel qu'un gris à 0,5 ressorte à 0,5 (bissection)."""
    lo, hi = 0.25, 8.0
    for _ in range(40):
        k = (lo * hi) ** 0.5
        y = echantillonne(lut, np.full((1, 3), vers_cineon(0.5, k)))[0].mean()
        lo, hi = (k, hi) if y < 0.5 else (lo, k)
    return k


def transforme(lettre, rgb, force=None):
    nom, fichier, f0 = VERSIONS[lettre]
    f = f0 if force is None else force
    if fichier is None or f == 0:
        return rgb
    lut = lire_cube(FILM / fichier)
    film = echantillonne(lut, vers_cineon(rgb, expo(lut)))
    return (1 - f) * rgb + f * film


def ecrire_cube(p, titre, lettre, force=None):
    g = np.linspace(0, 1, N)
    b, gg, r = np.meshgrid(g, g, g, indexing="ij")
    out = transforme(lettre, np.stack([r, gg, b], -1).reshape(-1, 3), force)
    with open(p, "w") as fh:
        fh.write(
            f'TITLE "{titre}"\n# Rec709 vers Rec709 (gamma 2,4), fait par outils/look.py\nLUT_3D_SIZE {N}\n'
        )
        fh.writelines(f"{x:.6f} {y:.6f} {z:.6f}\n" for x, y, z in np.clip(out, 0, 1))


def image(video, t):
    raw = subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-v",
            "error",
            "-ss",
            str(t),
            "-i",
            str(video),
            "-frames:v",
            "1",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ],
        capture_output=True,
        check=True,
    ).stdout
    w, h = (
        int(x)
        for x in subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "csv=p=0",
                str(video),
            ],
            capture_output=True,
            text=True,
        ).stdout.split(",")[:2]
    )
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3).astype(np.float64) / 255


def planche(video, temps):
    video = Path(video).resolve()
    if not temps:
        d = float(
            subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "csv=p=0",
                    str(video),
                ],
                capture_output=True,
                text=True,
            ).stdout
        )
        temps = [d * 0.3, d * 0.6]
    dispo = disponibles()
    absentes = [k for k in VERSIONS if k not in dispo]
    if absentes:
        print(f"LUT Film Looks de DaVinci Resolve absents ({FILM}) : planche sans {', '.join(absentes)}. "
              "Gratuit, à installer pour les looks film.", file=sys.stderr)
    lignes = []
    for t in temps:
        img = image(video, t)
        cases = []
        for lettre, (nom, _, _) in dispo.items():
            c = cv2.resize(
                (np.clip(transforme(lettre, img), 0, 1) * 255).astype(np.uint8),
                (405, 720),
                interpolation=cv2.INTER_AREA,
            )
            c = cv2.cvtColor(c, cv2.COLOR_RGB2BGR)
            cv2.rectangle(c, (0, 0), (405, 56), (20, 20, 20), -1)
            cv2.putText(
                c,
                f"{lettre}  {nom}",
                (14, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.1,
                (240, 240, 240),
                2,
                cv2.LINE_AA,
            )
            cases.append(c)
        lignes.append(np.hstack(cases))
    out = video.parent / "look" / "planche.jpg"
    out.parent.mkdir(exist_ok=True)
    cv2.imwrite(str(out), np.vstack(lignes), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(out)
    return out


def fixe(lettre, force=None):
    nom, fichier, f0 = VERSIONS[exiger(lettre)]
    LOOKS.mkdir(exist_ok=True)
    cube = LOOKS / "look.cube"
    ecrire_cube(cube, f"Look {lettre} {nom}", lettre, force)
    k = expo(lire_cube(FILM / fichier)) if fichier else None
    json.dump(
        {
            "lettre": lettre,
            "nom": nom,
            "lut_resolve": fichier,
            "force": f0 if force is None else force,
            "gain_entree": k,
            "date": datetime.date.today().isoformat(),
        },
        open(LOOKS / "LOOK.json", "w"),
        ensure_ascii=False,
        indent=1,
    )
    print(cube)
    try:  # facultatif : le rendre aussi disponible dans Resolve
        RESOLVE_PERSO.mkdir(exist_ok=True)
        shutil.copy(cube, RESOLVE_PERSO / "look.cube")
        print("copie dans", RESOLVE_PERSO / "look.cube")
    except OSError as e:
        print("copie Resolve sautée (DaVinci Resolve absent)")


if __name__ == "__main__":
    a = sys.argv[1:]
    force = float(a[a.index("--force") + 1]) if "--force" in a else None
    if a and a[0] == "planche":
        p = planche(a[1], [float(x) for x in a[2:]])
        if shutil.which("open"):  # macOS ; ailleurs, le chemin imprimé suffit
            subprocess.run(["open", "-a", "Preview", str(p)])
    elif a and a[0] == "fixe":
        fixe(a[1].upper(), force)
    elif a and a[0] == "cube":
        exiger(a[1].upper())
        ecrire_cube(a[2], f"essai {a[1].upper()}", a[1].upper(), force)
        print(a[2])
    else:
        sys.exit(__doc__)
