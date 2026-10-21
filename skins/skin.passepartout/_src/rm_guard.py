"""Reduce-motion guard for generated skin XML (Orbit 0.9.8, Passe-partout 0.9.10; LESSONS "Reduce motion").

guard_text(text, rm) rewrites every slide/zoom/rotate animation (time > 1) whose condition does not
already test reduce motion into a pair:
  original  condition = [C] + !RM
  twin      condition = [C] + RM, motion effects at time 0 / delay 0, fades unchanged
(no twin for loops, nor for leaving animations without a fade, nor EVER for Hidden: one Hidden per control). End states (layout slides, lifts)
are kept, movement is not.
"""
import re

RM = ""
exp_guard = set()


ANIM = re.compile(r"<animation\b([^>]*?)(?:/>|>(.*?)</animation>)", re.S)
MOTION = ("slide", "zoom", "rotate", "rotatex", "rotatey")


def guarded(cond):
    if "reducemotion" in cond:
        return True
    return any(e in exp_guard for e in re.findall(r"\$EXP\[([^\]]+)\]", cond))


def get(attr_text, name):
    m = re.search(r'\b%s="([^"]*)"' % name, attr_text)
    return m.group(1) if m else None


def setattr_(attr_text, name, value):
    if get(attr_text, name) is None:
        return attr_text + ' %s="%s"' % (name, value)
    return re.sub(r'\b%s="[^"]*"' % name, '%s="%s"' % (name, value), attr_text, count=1)


def is_moving(attr_text):
    kind = get(attr_text, "effect") or get(attr_text, "type")
    if kind not in MOTION:
        return False
    tm = get(attr_text, "time") or "0"
    try:
        return float(tm) > 1
    except ValueError:
        return True  # $PARAM


def still(attr_text):
    a = setattr_(attr_text, "time", "0")
    if get(a, "delay") is not None:
        a = setattr_(a, "delay", "0")
    return a


LIST_OPEN = re.compile(r'<control\s+type="(?:list|panel|fixedlist|wraplist)"[^>]*?\bid="(\d+)"')


def focus_test(text, at, cond):
    """' + Control.HasFocus(<list>)' when the animation sits in a container's focusedlayout; '' when its own condition
    already carries the focus test (a focusedlayout include param such as Search_Item's focused)."""
    fo = text.rfind("<focusedlayout", 0, at)
    if fo > text.rfind("</focusedlayout>", 0, at):
        ids = LIST_OPEN.findall(text, 0, fo)
        if ids:
            return " + Control.HasFocus(%s)" % ids[-1]
    if cond.strip():
        return ""
    raise ValueError("rm_guard: Focus animation with no focus context near offset %d; give it a focus condition" % at)


def combine(cond, extra):
    if not cond:
        return extra
    return "[%s] + %s" % (cond, extra)


def process(text):
    out = []
    pos = 0
    n = 0
    for m in ANIM.finditer(text):
        whole = m.group(0)
        head = m.group(1)
        body = m.group(2)
        if body is None:
            continue
        nested = list(re.finditer(r"<effect\b([^>]*?)\s*/>", body))
        if get(head, "effect"):
            moving = is_moving(head)
            fades_left = False
        else:
            moving = any(is_moving(e.group(1)) for e in nested)
            fades_left = any((get(e.group(1), "type") not in MOTION) for e in nested)
        if not moving:
            continue
        cond = get(head, "condition") or ""
        if guarded(cond):
            continue
        anim_type = get(head, "type") or (body.strip() if get(head, "effect") else "")
        loop = get(head, "loop") == "true" or any(get(e.group(1), "loop") == "true" for e in nested)
        # indentation of this animation
        ls = text.rfind("\n", 0, m.start()) + 1
        indent = text[ls:m.start()]
        if indent.strip():
            indent = ""
        orig_head = setattr_(head, "condition", combine(cond, "!" + RM))
        orig = "<animation" + orig_head + ">" + body + "</animation>"
        twin = None
        # Never a second Hidden animation (LESSONS, Groove device pass 2): Kodi resets only the FIRST Hidden animation
        # when a control shows again, so a reduce-motion Hidden twin that has run stays at fade 0 and the control never
        # comes back. A moving Hidden keeps the normal animation only: reduce motion hides at once.
        # Focus works like Hidden (LESSONS 2026-10-21, Void/Orbit/Daylight): on unfocus Kodi resets only the FIRST Focus
        # animation, so a reduce-motion Focus twin that ends off identity (zoom 112) stays applied. The reduce-motion
        # end state becomes a time-0 Conditional on the same focus instead (in a focusedlayout: Control.HasFocus(list)),
        # which Kodi reverses by itself. Unfocus then needs no twin unless a fade must still run.
        need_twin = not loop and anim_type != "Hidden" and (anim_type in ("Conditional", "Focus") or fades_left)
        if need_twin:
            th = setattr_(head, "condition", combine(cond, RM))
            if anim_type == "Focus":
                th = setattr_(head, "condition", combine(cond, RM + focus_test(text, m.start(), cond)))
                th = re.sub(r'\s+reversible="[^"]*"', "", th)
                if get(th, "type"):
                    th = setattr_(th, "type", "Conditional")
                else:
                    body = body.replace("Focus", "Conditional")
            if get(head, "effect"):
                th = still(th) if is_moving(th) else th
                tbody = body
            else:
                leaving = anim_type in ("Hidden", "WindowClose")

                def fix(e):
                    a = e.group(1)
                    if is_moving(a):
                        return "" if leaving else "<effect" + still(a) + "/>"
                    return "<effect" + a + "/>"
                tbody = re.sub(r"<effect\b([^>]*?)\s*/>", fix, body)
                tbody = re.sub(r"\r?\n[ \t]*(?=\r?\n)", "", tbody)
            twin = "<animation" + th + ">" + tbody + "</animation>"
        out.append(text[pos:m.start()])
        out.append(orig)
        if twin:
            out.append(("\r\n" if "\r\n" in text else "\n") + indent + twin)
        pos = m.end()
        n += 1
    out.append(text[pos:])
    return "".join(out), n




def guard_text(text, rm, guarded_exps=()):
    global RM, exp_guard
    RM = rm
    exp_guard = set(guarded_exps)
    return process(text)
