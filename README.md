# KarmaMole's Kodi Skins

Eleven skins for **Kodi 21 Omega**, designed for the TV and tested on an NVIDIA Shield. Each one is a different idea
about how a media library should feel.

| Skin | Idea |
|---|---|
| **Majan** | An editorial index for your library: Swiss hairlines, big type, numbered sections. |
| **Void** | One thing at a time. More information arrives the longer you rest. |
| **Orbit** | Browse on a dial; rings carry the data. |
| **Daylight** | A skin that knows the time, the weather and your bedtime. |
| **Duotone** | Every picture printed in its section's colour. |
| **Sentence** | Ask for what you want in a sentence, built with the remote. |
| **Passe-partout** | Every film framed like a gallery print, on paper that takes the artwork's colour. |
| **Nocturne** | Your library after hours, explored by torchlight. |
| **Six Degrees** | Every direction on the remote is a connection: director, lead actor, second star, year. |
| **Fold** | Everything unfolds: cards, spreads and concertinas on real 3D hinges. |
| **Keepsake** | The skin that remembers: a black photo album of what you've watched, date-stamped. |

## Install

1. In Kodi, go to **Settings → System → Add-ons** and turn on **Unknown sources**.
2. Go to **Settings → File manager → Add source**, enter `https://karmamole.github.io/kodi-skins/` and name it `karmamole`.
3. Go to **Add-ons → Install from zip file → karmamole** and pick `repository.omarkamel.zip`.
4. Go to **Add-ons → Install from repository → KarmaMole's Kodi Skins → Look and feel → Skin** and choose a skin.
   Updates arrive automatically.

Every skin works on its own. A few features get richer when these optional add-ons are installed:
- [TMDb Helper](https://github.com/jurialmunkey/plugin.video.themoviedb.helper) adds artwork colours, blur and cast.
- [Skin Variables](https://github.com/jurialmunkey/script.skinvariables) is used by Six Degrees and Keepsake.
- Embuary Helper adds next-up episodes.

## Repository layout

| Path | What |
|---|---|
| `skins/skin.<id>/` | each skin, the add-on itself; `_src/` holds the generators for its fonts, textures and generated XML |
| `repository.omarkamel/` | the Kodi repository add-on |
| `tools/build_repo.py` | builds the Kodi repository (zips, `addons.xml`, landing page) |
| `.github/workflows/publish.yml` | rebuilds and publishes the repository to GitHub Pages on every push to `main` |

To build locally, run `python tools/build_repo.py`; the output goes to `_site/`.

## Licence

The skins are released under the **GNU General Public License v2.0 or later** (see `LICENSE` and each skin's
`LICENSE.txt`). Their bundled fonts are under the **SIL Open Font License 1.1** (`fonts/OFL-*.txt` in each skin).
Fonts with skin-specific names are modified versions of those families and remain under the OFL.

Copyright © 2026 Omar Kamel.
