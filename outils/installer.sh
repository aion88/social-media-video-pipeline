#!/bin/bash
# installer.sh : dit ce qui manque pour faire tourner le dépôt.
#
# Usage : outils/installer.sh             vérifie, installe les modules python légers (via uv)
#         outils/installer.sh --verifier  vérifie seulement, ne touche à rien
#         outils/installer.sh --lier      en plus, lie les skills dans ~/.claude/skills et `derush`
#                                         dans ~/.local/bin, pour les lancer depuis n'importe quel dossier
#
# Idempotent. Il ne remplace JAMAIS un lien ou un dossier existant qui vise ailleurs : il le
# signale (CONFLIT) et passe. Sans --lier, aucun lien n'est posé : ouvert dans Claude Code, le
# dépôt charge déjà ses skills depuis .claude/skills/.
set -uo pipefail

_self="${BASH_SOURCE[0]}"
while [[ -L "$_self" ]]; do
  _t="$(readlink "$_self")"; [[ "$_t" = /* ]] && _self="$_t" || _self="$(dirname "$_self")/$_t"
done
ROOT="$(cd "$(dirname "$_self")/.." && pwd)"
VERIFIER=0; LIER=0
for a in "$@"; do
  case "$a" in
    --verifier) VERIFIER=1;;
    --lier) LIER=1;;
    *) echo "option inconnue : $a (voir l'en-tête)" >&2; exit 2;;
  esac
done
SKILLS="sm-video sm-recherche sm-montage sm-motion derush"
MANQUE=0

ok()     { printf '  OK      %s\n' "$1"; }
manque() { printf '  MANQUE  %s\n          -> %s\n' "$1" "$2"; MANQUE=$((MANQUE + 1)); }
fait()   { printf '  POSE    %s\n' "$1"; }

# lien <cible dans le dépôt> <lien à poser>
lien() {
  local cible="$1" l="$2"
  if [[ -L "$l" ]]; then
    if [[ "$(realpath "$l" 2>/dev/null)" == "$(realpath "$cible")" ]]; then ok "$l"
    else manque "$l vise $(readlink "$l"), pas ce dépôt (CONFLIT, non touché)" "rm '$l' puis relancer, si c'est voulu"; fi
  elif [[ -e "$l" ]]; then
    manque "$l existe et n'est pas un lien (CONFLIT, non touché)" "le comparer à '$cible', le ranger, puis relancer"
  elif (( VERIFIER )); then
    manque "$l absent" "outils/installer.sh --lier"
  else
    mkdir -p "$(dirname "$l")" && ln -s "$cible" "$l" && fait "$l -> $cible"
  fi
}

binaire() {  # binaire <nom> <commande d'install>
  if command -v "$1" >/dev/null 2>&1; then ok "$1 ($(command -v "$1"))"; else manque "$1" "$2"; fi
}

echo "Dépôt : $ROOT"

echo "Skills et agent du dépôt"
for s in $SKILLS; do
  if [[ -f "$ROOT/.claude/skills/$s/SKILL.md" ]]; then ok ".claude/skills/$s"
  else manque "$ROOT/.claude/skills/$s/SKILL.md" "le dépôt est incomplet : git status"; fi
done
if [[ -f "$ROOT/.claude/agents/motion-reviewer.md" ]]; then ok ".claude/agents/motion-reviewer.md"
else manque ".claude/agents/motion-reviewer.md" "le dépôt est incomplet : git status"; fi

if (( LIER )); then
  echo "Liens (--lier)"
  for s in $SKILLS; do lien "$ROOT/.claude/skills/$s" "$HOME/.claude/skills/$s"; done
  lien "$ROOT/.claude/skills/derush/scripts/derush.sh" "$HOME/.local/bin/derush"
  [[ ":$PATH:" == *":$HOME/.local/bin:"* ]] || manque "~/.local/bin dans le PATH" "echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc"
fi

echo "Binaires"
binaire ffmpeg "brew install ffmpeg   (ou apt install ffmpeg)"
binaire ffprobe "brew install ffmpeg"
binaire python3 "brew install python@3.12"
binaire uv "curl -LsSf https://astral.sh/uv/install.sh | sh"
binaire node "brew install node   (Node 22 ou plus pour HyperFrames)"
binaire npx "brew install node"
binaire claude "https://claude.com/claude-code"
if command -v whisper >/dev/null 2>&1 || { [[ -n "${WHISPER:-}" && -x "${WHISPER:-}" ]]; }; then ok "whisper"
else manque "whisper" "uv tool install openai-whisper   (ou export WHISPER=/chemin/whisper)"; fi

echo "Modules python ($(command -v python3 || echo 'python3 absent'))"
LEGERS=""
for paire in numpy:numpy cv2:opencv-python PIL:pillow soundfile:soundfile fontTools:fonttools; do
  mod="${paire%%:*}"; pkg="${paire#*:}"
  if python3 -c "import $mod" >/dev/null 2>&1; then ok "$mod"; else LEGERS="$LEGERS $pkg"; fi
done
if [[ -n "$LEGERS" ]]; then
  if (( VERIFIER )) || ! command -v uv >/dev/null 2>&1; then
    manque "modules :$LEGERS" "uv pip install --system --python \"\$(command -v python3)\"$LEGERS"
  elif uv pip install --system --python "$(command -v python3)" $LEGERS; then fait "modules :$LEGERS"
  else manque "modules :$LEGERS (uv a échoué)" "uv pip install --system --python \"\$(command -v python3)\"$LEGERS"; fi
fi
for mod in torch torchaudio; do  # lourds : jamais installés d'office
  python3 -c "import $mod" >/dev/null 2>&1 && ok "$mod" \
    || manque "$mod (alignement CTC de derush)" "uv pip install --system --python \"\$(command -v python3)\" torch torchaudio"
done

echo "Facultatif"
if [[ -n "${SFX_DIR:-}" && -d "${SFX_DIR:-}" ]]; then ok "SFX_DIR=$SFX_DIR"
else echo "  --      SFX_DIR non défini : le motion sort sans bruitages (voir README, section Sounds)"; fi
LOOKS="${RESOLVE_FILM_LOOKS:-/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/Film Looks}"
if [[ -d "$LOOKS" ]]; then ok "LUT Film Looks de DaVinci Resolve"
else echo "  --      LUT Film Looks de DaVinci Resolve absents : outils/look.py en a besoin (RESOLVE_FILM_LOOKS), ou \"look\": null"; fi

echo
if (( MANQUE )); then echo "$MANQUE manque(s). Le reste est en place."; exit 1; fi
echo "Tout est en place."
