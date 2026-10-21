"""Build the Kodi repository that GitHub Pages serves (https://karmamole.github.io/kodi-skins/).

  python tools/build_repo.py [--out _site]

Output layout (what Kodi's repository add-on expects):
  _site/addons.xml, _site/addons.xml.md5          every add-on's addon.xml, concatenated
  _site/<id>/<id>-<version>.zip                    installable zips (top folder = <id>/), skins/skin.* and addons/*
  _site/repository.karmamole-<version>.zip         the repository add-on, for the first manual install
  _site/index.html                                 a small landing page with the install steps

Zips leave out generator sources (_src/) and editor junk, like the release packager in the studio.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import re
import shutil
import zipfile
from fnmatch import fnmatch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {"_src", ".git", "__pycache__", "docs", ".vscode", ".idea", "previews"}
EXCLUDE_FILES = ["*.psd", "*.afdesign", "*.xcf", "*.kra", "*.ai", "*.sketch", "*.fig", "Thumbs.db",
                 ".DS_Store", "*.pyc", ".gitignore", ".gitattributes"]
REPO_ID = "repository.karmamole"


def addon_dirs() -> list[Path]:
    # skins, helper add-ons some skins use (addons/<id>/, e.g. script.karmamole.helper), the repository add-on
    return (sorted((ROOT / "skins").glob("skin.*")) + sorted(p for p in (ROOT / "addons").glob("*") if p.is_dir())
            + [ROOT / REPO_ID])


def meta(d: Path) -> tuple[str, str, str, str]:
    x = (d / "addon.xml").read_text(encoding="utf-8")
    head = re.search(r"<addon\s[^>]*>", x, re.S).group(0)
    get = lambda a: re.search(r'\s%s="([^"]*)"' % a, head).group(1)
    summary = re.search(r"<summary[^>]*>(.*?)</summary>", x, re.S)
    return get("id"), get("version"), get("name"), summary.group(1).strip() if summary else ""


def zip_addon(d: Path, dest: Path) -> None:
    addon_id = d.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(d.rglob("*")):
            rel = p.relative_to(d)
            if p.is_dir() or any(part in EXCLUDE_DIRS for part in rel.parts):
                continue
            if any(fnmatch(p.name, pat) for pat in EXCLUDE_FILES):
                continue
            z.write(p, f"{addon_id}/{rel.as_posix()}")


def page(rows: list[tuple[str, str, str, str]], repo_zip: str) -> str:
    items = "\n".join(
        f'<li><b>{html.escape(name)}</b> <span class="v">{html.escape(ver)}</span>'
        f'<br><span class="s">{html.escape(summary.split(" - ", 1)[-1])}</span></li>'
        for aid, ver, name, summary in rows if aid.startswith("skin."))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>KarmaMole's Kodi Skins</title>
<style>
:root{{--bg:#f4f3ef;--fg:#18181a;--dim:#66645e;--line:#d9d7d1;--accent:#c8442b}}
@media (prefers-color-scheme:dark){{:root{{--bg:#121213;--fg:#ecebe6;--dim:#97948d;--line:#2b2b2e;--accent:#f06a4c}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:17px/1.55 system-ui,sans-serif;padding:48px max(20px,env(safe-area-inset-left))}}
main{{max-width:760px;margin:0 auto}} h1{{font-size:44px;line-height:1;margin:0 0 12px;letter-spacing:-.02em}}
p{{color:var(--dim)}} a{{color:var(--accent)}} ol li{{margin:6px 0}} code{{font:15px ui-monospace,monospace}}
ul{{list-style:none;padding:0;border-top:1px solid var(--line)}} ul li{{padding:12px 0;border-bottom:1px solid var(--line)}}
.v{{font:13px ui-monospace,monospace;color:var(--dim)}} .s{{color:var(--dim)}}
</style></head><body><main>
<h1>KarmaMole's Kodi Skins</h1>
<p>Thirteen skins for Kodi 21 Omega, designed for the TV and tested on an NVIDIA Shield. Free under the GPL-2.0.</p>
<h2>Install</h2>
<ol>
<li>In Kodi: <b>Settings → System → Add-ons</b>, turn on <b>Unknown sources</b>.</li>
<li><b>Settings → File manager → Add source</b>, enter <code>https://karmamole.github.io/kodi-skins/</code> and name it <code>karmamole</code>.</li>
<li><b>Add-ons → Install from zip file → karmamole →</b> <code>{html.escape(repo_zip)}</code>.</li>
<li><b>Add-ons → Install from repository → KarmaMole's Kodi Skins → Look and feel → Skin</b>, pick one. Updates arrive automatically.</li>
</ol>
<p>Or download the repository zip directly: <a href="{html.escape(repo_zip)}">{html.escape(repo_zip)}</a>.</p>
<h2>The skins</h2>
<ul>
{items}
</ul>
<p>Source: <a href="https://github.com/KarmaMole/kodi-skins">github.com/KarmaMole/kodi-skins</a></p>
</main></body></html>
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="_site")
    out = ROOT / ap.parse_args().out
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    rows, xmls = [], []
    for d in addon_dirs():
        aid, ver, name, summary = meta(d)
        assert aid == d.name, f"{d}: folder name must equal addon id {aid}"
        zip_addon(d, out / aid / f"{aid}-{ver}.zip")
        for art in ("icon.png", "fanart.jpg"):  # Kodi shows these from the datadir before install
            if (d / art).exists():
                shutil.copy2(d / art, out / aid / art)
        xmls.append(re.sub(r"<\?xml[^>]*\?>\s*", "", (d / "addon.xml").read_text(encoding="utf-8")).strip())
        rows.append((aid, ver, name, summary))
        print(f"{aid} {ver}")
    addons = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n' + "\n".join(xmls) + "\n</addons>\n"
    (out / "addons.xml").write_text(addons, encoding="utf-8")
    (out / "addons.xml.md5").write_text(hashlib.md5(addons.encode("utf-8")).hexdigest(), encoding="utf-8")
    repo_ver = next(v for a, v, _, _ in rows if a == REPO_ID)
    repo_zip = f"{REPO_ID}.zip"  # stable name for links and docs; Kodi reads the version from addon.xml
    shutil.copy2(out / REPO_ID / f"{REPO_ID}-{repo_ver}.zip", out / repo_zip)
    # the showcase (site/) is the front page when present; the plain install page stays at install.html.
    # To go back to the plain front page, delete site/ (or `git revert` the commit that added it).
    plain = page(rows, repo_zip)
    site = ROOT / "site"
    if site.is_dir():
        shutil.copytree(site, out, dirs_exist_ok=True)
        (out / "install.html").write_text(plain, encoding="utf-8")
    else:
        (out / "index.html").write_text(plain, encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    print(f"-> {out} ({len(rows)} add-ons)")


if __name__ == "__main__":
    main()
