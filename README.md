# KarmaMole's Kodi Skins

Thirteen skins for **Kodi 21 Omega**, designed for the TV and tested on an NVIDIA Shield. Each one is a different idea
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
| **Groove** | For record collectors: art as light, a spinning record, crates, shelves, a time machine and a genre wheel. |
| **Vernissage** | A private gallery that changes with the light: grey prints on the walls, only the work in front of you in colour. |

## Install

1. In Kodi, go to **Settings → System → Add-ons** and turn on **Unknown sources**.
2. Go to **Settings → File manager → Add source**, enter `https://karmamole.github.io/kodi-skins/` and name it `karmamole`.
3. Go to **Add-ons → Install from zip file → karmamole** and pick `repository.karmamole.zip`.
4. Go to **Add-ons → Install from repository → KarmaMole's Kodi Skins → Look and feel → Skin** and choose a skin.
   Updates arrive automatically.

Every skin requires [Skin Variables](https://github.com/jurialmunkey/script.skinvariables) 2.1.21 or later (Search
uses it). Kodi installs it from its official repository along with the skin.

### Optional add-ons

The skins work without these; with them, some features get richer. Each skin's section on the
[showcase page](https://karmamole.github.io/kodi-skins/) lists the ones it uses.
- [TMDb Helper](https://github.com/jurialmunkey/plugin.video.themoviedb.helper) (Kodi's official repository): artwork
  colours and blurred backgrounds, in every skin except Void.
- Embuary Helper (Kodi's official repository): a real Next up row for TV.
- **KarmaMole Skin Helper** (`script.karmamole.helper`, this repository): one optional helper for these skins; each
  skin turns on only the features it uses. Groove: album colours while browsing, colour-matched spines, Up next
  reordering, true shuffle, and style and mood rings on the wheel (Groove's Settings has an Install button).
  Vernissage: the black-and-white prints on its walls, the Still on the easel and New in the collection walls, the
  spotlight's colour and album shuffle.
- **Album colours for visualisers** (`service.vizpalette`, this repository): the playing album's colours for Groove's
  room and the Shadertoy visualiser. Also installs from Groove's Settings.
- Shadertoy and YouTube (Kodi's official repository): Groove's visualiser and its Watch the video button.

## Repository layout

| Path | What |
|---|---|
| `skins/skin.<id>/` | each skin, the add-on itself; `_src/` holds the generators for its fonts, textures and generated XML |
| `addons/<id>/` | helper add-ons some skins use: `script.karmamole.helper` (the shared skin helper) and `service.vizpalette` (Groove's companion) |
| `repository.karmamole/` | the Kodi repository add-on |
| `site/` | the showcase page served as the front page of https://karmamole.github.io/kodi-skins/ (the plain install page moves to `install.html`; delete `site/` to go back) |
| `tools/build_repo.py` | builds the Kodi repository (zips, `addons.xml`, landing page) |
| `.github/workflows/publish.yml` | rebuilds and publishes the repository to GitHub Pages on every push to `main` |

To build locally, run `python tools/build_repo.py`; the output goes to `_site/`.

## Licence

The skins are released under the **GNU General Public License v2.0 or later** (see `LICENSE` and each skin's
`LICENSE.txt`). Their bundled fonts are under the **SIL Open Font License 1.1** (`fonts/OFL-*.txt` in each skin).
Fonts with skin-specific names are modified versions of those families and remain under the OFL.

Copyright © 2026 Omar Kamel.
