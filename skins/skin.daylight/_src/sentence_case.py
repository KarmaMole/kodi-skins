"""One-off pass (kept for the record): Majan's tracked mono captions were written in CAPS; Daylight sets
everything in sentence case with Figtree. Converts all-caps literal words in labels / variable values /
label-like include params to sentence case (acronyms kept), and swaps triangle glyphs Figtree lacks
for arrows. Safe to re-run (idempotent)."""
from pathlib import Path
import re

X = Path(__file__).resolve().parents[1] / "1080i"
KEEP = {"HDR", "HDR10", "HDR10+", "HLG", "DTS", "DTS:X", "DTS-HD", "MA", "HRA", "AAC", "PCM", "HEVC", "AV1", "MPEG", "MPEG-2",
        "MPEG-4", "VC-1", "TV", "SDR", "DD", "DD+", "IMDB", "TMDB", "OSD", "EPG", "PVR", "DVD", "URL", "IP", "CPU", "GPU",
        "RAM", "FPS", "HW", "SW", "GUI", "RDS", "SMS", "UV", "ID", "ISO", "HD", "SD", "4K", "8K", "DVB", "CEC", "AC3", "MP3",
        "FLAC", "OK", "PG", "PG-13", "NC-17", "NR", "R", "G", "TV-MA", "TV-14", "TV-PG", "H.264", "AV", "A/V", "CC", "UPnP",
        "SMB", "NFS", "FTP", "HTTP", "API", "VPN", "HDMI", "USB", "LAN", "WAN", "DNS", "DHCP", "MAC", "IPTV", "4:3", "16:9", "x",
        "P", "TRUEHD"}
SPECIAL = {"TRUEHD": "TrueHD", "ATMOS": "Atmos", "DOLBY": "Dolby", "VISION": "Vision", "KODI": "Kodi"}
GLYPHS = {"◀": "←", "▶": "→", "▲": "↑", "▼": "↓", "✓": "", "■": ""}
SKIP = re.compile(r"(\$[A-Z]+\[(?:[^\[\]]|\[[^\[\]]*\])*\]|\[/?[A-Z]+(?: [^\]]*)?\])")
WORD = re.compile(r"\b[A-Z][A-Z0-9.+:/-]*[A-Z0-9+]\b|\b[A-Z]\b")


def fix_literal(seg: str) -> str:
    def w(m):
        t = m.group(0)
        if t in SPECIAL:
            return SPECIAL[t]
        if t in KEEP or len(t) == 1:
            return t
        return t.lower()
    return WORD.sub(w, seg)


def fix_text(text: str) -> str:
    if not re.search(r"[A-Z]{3,}", re.sub(SKIP, "", text)):
        for g, r in GLYPHS.items():
            text = text.replace(g, r)
        return text
    parts = SKIP.split(text)
    out = []
    for i, p in enumerate(parts):
        out.append(p if SKIP.fullmatch(p or "x") and p.startswith(("$", "[")) else fix_literal(p))
    s = "".join(out)
    # capitalise the first literal letter of the string
    m = re.search(r"[A-Za-z]", re.sub(SKIP, lambda k: " " * len(k.group(0)), s))
    if m and s[m.start()].islower():
        s = s[:m.start()] + s[m.start()].upper() + s[m.start() + 1:]
    for g, r in GLYPHS.items():
        s = s.replace(g, r)
    return s


def main():
    n = 0
    for f in sorted(X.glob("*.xml")):
        if f.name in ("Includes_Daylight.xml", "Font.xml"):
            continue
        s = f.read_text(encoding="utf-8")
        o = s
        s = re.sub(r"(<label>)([^<]*)(</label>)", lambda m: m.group(1) + fix_text(m.group(2)) + m.group(3), s)
        s = re.sub(r"(<label2>)([^<]*)(</label2>)", lambda m: m.group(1) + fix_text(m.group(2)) + m.group(3), s)
        s = re.sub(r"(<value(?: condition=\"[^\"]*\")?>)([^<]*)(</value>)", lambda m: m.group(1) + fix_text(m.group(2)) + m.group(3), s)
        s = re.sub(r'(<param name="(?:label|caption|title|kicker|hint|sub|empty|value)" value=")([^"]*)(")',
                   lambda m: m.group(1) + fix_text(m.group(2)) + m.group(3), s)
        if s != o:
            n += 1
            f.write_text(s, encoding="utf-8", newline="\n")
    print(f"updated {n} files")


if __name__ == "__main__":
    main()
