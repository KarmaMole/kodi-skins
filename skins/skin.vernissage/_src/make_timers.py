"""Generate 1080i/Timers.xml (Kodi 21 skin timers).   python skins/skin.vernissage/_src/make_timers.py

Timers don't expand $EXP (LESSONS Six Degrees): every condition is written out here. Every timer that reads control
visibility or focus is guarded with !System.HasActiveModalDialog and the in-window library panel / picker / clean
card (LESSONS Fold 0.9.7: timers evaluate against the focused window). Every stop is always reachable (LESSONS Final
device check pass 2: timers run every 500 ms and can miss a short-lived stop).
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_home as HM  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "1080i" / "Timers.xml"
PANELS = "!ControlGroup(9800).HasFocus() + !ControlGroup(9850).HasFocus() + !ControlGroup(9890).HasFocus()"

# Kodi stores views per skin and path; a fresh skin has none, and Kodi opens an unsaved node in the panel view
# (Salon) where Salon is allowed, else the first visible <views> entry (Catalogue). These correct a first visit per
# content once (SPEC 8) and then never again (the flag), so a later choice is kept.
# content, window, default view
FIRST = [
    ("movies", "videos", 500), ("sets", "videos", 500), ("tvshows", "videos", 500), ("seasons", "videos", 500),
    ("episodes", "videos", 50), ("albums", "music", 500), ("artists", "music", 500), ("songs", "music", 50),
]


def expand(text: str) -> str:
    """Write $EXP[...] out in full (timers don't expand it): Home's expressions from make_home, the helper guards
    from Includes_Vernissage.xml."""
    exprs = dict(HM.EXPR)
    vn = (Path(__file__).resolve().parents[1] / "1080i" / "Includes_Vernissage.xml").read_text(encoding="utf-8")
    exprs.update(dict(re.findall(r'<expression name="(\w+)">(.*?)</expression>', vn)))
    for _ in range(10):
        new = re.sub(r"\$EXP\[(\w+)\]", lambda m: "[" + exprs[m.group(1)] + "]", text)
        if new == text:
            return text
        text = new
    raise ValueError("expression loop")


def timer(name, start, onstart, stop=None, note=None):
    o = []
    if note:
        o.append(f"\t<!-- {note} -->")
    o += ["\t<timer>", f"\t\t<name>{name}</name>", f"\t\t<start>{start}</start>"]
    if stop:
        o.append(f"\t\t<stop>{stop}</stop>")
    o += [f"\t\t<onstart>{a}</onstart>" for a in onstart]
    o.append("\t</timer>")
    return "\n".join(o)


def main():
    t = []
    # Home: the walls fill after onload, so defaultcontrol finds nothing on the first open (and after a skin
    # reload): hand focus to the room on show when its works arrive (LESSONS Keepsake / Six Degrees 0.9.2).
    home = "Window.IsActive(home) + String.IsEmpty(System.CurrentControlId) + !System.HasActiveModalDialog"
    stop = "!String.IsEmpty(System.CurrentControlId) | !Window.IsActive(home)"
    targets = [("tonight", "$EXP[Home_ShowTonight]", HM.TONIGHT)]
    targets += [(f"easel_{cid}", f"$EXP[Home_ShowEasel] + {c}", cid) for c, cid in HM.EASEL_TARGETS]
    targets += [(f"new_{cid}", f"$EXP[Home_ShowNew] + {c}", cid) for c, cid in HM.NEW_TARGETS]
    for i, (name, cond, cid) in enumerate(targets):
        t.append(timer(f"vn_home_{name}", expand(f"{home} + {cond}"), [f"SetFocus({cid})"], stop,
                       "Home opens on the room on show (SPEC 6.1): one timer per wall list (onstart takes no conditions)" if i == 0 else None))
    # After Kodi starts it can land on the rail while the walls are still empty: on the FIRST Home visit of the
    # session (Startup.xml sets vn.home.first), move to Tonight when it fills. What ends the
    # hand-over: Tonight taking focus, or Home unloading (Home.xml onunload), so it never pulls focus later.
    first = "String.IsEqual(Window(Home).Property(vn.home.first),yes)"
    t.append(timer("vn_home_first", expand(f"Window.IsActive(home) + {first} + Control.HasFocus(9000) + !System.HasActiveModalDialog + $EXP[Home_HasTonight]"),
                   ["SetFocus(9101)", "ClearProperty(vn.home.first,home)"], f"!{first} | !Window.IsActive(home)",
                   "First Home visit of a session: Tonight, even when Kodi focused the rail before the wall filled"))
    t.append(timer("vn_home_first_end", f"Window.IsActive(home) + {first} + Control.HasFocus(9101)",
                   ["ClearProperty(vn.home.first,home)"], f"!{first} | !Window.IsActive(home)"))
    t.append(timer(
        "vn_home_focus",
        expand(f"{home} + !$EXP[Home_HasTonight] + !$EXP[Home_HasEasel] + !$EXP[Home_HasNew] + System.IdleTime(2)"),
        ["SetFocus(9000)"],
        "!String.IsEmpty(System.CurrentControlId) | !Window.IsActive(home) | !System.IdleTime(2)",
        "No works anywhere (or nothing focused after Dialog.Close(all) + ActivateWindow): the rail, after 2 s."))
    for content, win, view in FIRST:
        flag = f"vernissage.vfirst.{content}"
        base = (f"Window.IsActive({win}) + Container.Content({content}) + !Skin.HasSetting({flag}) + "
                f"!Container.IsUpdating + !System.HasActiveModalDialog + {PANELS}")
        t.append(timer(f"vn_vfirst_{content}", f"{base} + !Control.IsVisible({view})",
                       [f"Skin.SetBool({flag})", f"Container.SetViewMode({view})", "SetFocus(50)"],
                       note=f"first visit: {content} -> view {view}" if content == "movies" else None))
        t.append(timer(f"vn_vfirst_{content}_ok", f"{base} + Control.IsVisible({view})", [f"Skin.SetBool({flag})"]))
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           "<!-- GENERATED by _src/make_timers.py - edit the generator, then re-run. Conditions written out in full",
           "     (timers don't expand $EXP); every timer reading focus / visibility is guarded against modal dialogs",
           "     and the in-window library panel, picker and clean card. -->",
           "<timers>", "\n\n".join(t), "</timers>", ""]
    OUT.write_text("\n".join(xml), encoding="utf-8", newline="\n")
    print(f"wrote {OUT.name}: {len(t)} timers")


if __name__ == "__main__":
    main()
