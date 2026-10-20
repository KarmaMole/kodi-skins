"""Reduce-motion guard for generated skin XML (Orbit 0.9.8, Passe-partout 0.9.10; LESSONS "Reduce motion").

guard_text(text, rm) rewrites every slide/zoom/rotate animation (time > 1) whose condition does not
already test reduce motion into a pair:
  original  condition = [C] + !RM
  twin      condition = [C] + RM, motion effects at time 0 / delay 0, fades unchanged
(no twin for loops, nor for leaving animations without a fade). End states (layout slides, lifts)
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
        need_twin = not loop and (anim_type in ("Conditional", "Focus", "Unfocus") or fades_left)
        if need_twin:
            th = setattr_(head, "condition", combine(cond, RM))
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
