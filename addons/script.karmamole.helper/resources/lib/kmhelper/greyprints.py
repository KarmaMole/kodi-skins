# KarmaMole Skin Helper (script.karmamole.helper)
# Copyright (C) 2026 Omar Kamel
# SPDX-License-Identifier: GPL-2.0-or-later
"""Grey prints (feature 'greyprints', Vernissage SPEC 12.1): two opaque grey JPEGs per library item, one per room.

  evening   Rec.709 luma on linearised sRGB (gamma 2.2), re-encoded, x 0x8C/255 (= colordiffuse FF8C8C8C, ~0.55)
  day       the same luma at 0xB3/255 (~70 %) over the Day wall #F4F2EE ("printed on the wall")
The constants are the approved mockups' (docs/skin.vernissage/mockups/_src/make_assets.py luma() / prints_for()).
Both rooms are one Color3DLUT pass each (C speed, within 1 level of the exact float maths); RECIPE names every
constant, and a change rebuilds everything.

Files:   special://temp/script.karmamole.helper/grey/<gen>/<room>/<kind>/<dbid>.jpg   (room = day | evening)
Index:   addon_data/script.karmamole.helper/greyprints.json
         {v, recipe, sig, gen, count, items: {"kind:dbid": {url, mtime}}, missing: {"kind:dbid": {url, mtime, at}}}
Pending: addon_data/script.karmamole.helper/greyprints.pending.json (a build that was stopped; the next one resumes it)
Published (Window(Home)): KarmaMole.Grey.Path (with a trailing slash), KarmaMole.Grey.Count, KarmaMole.Grey.Gen.

Generations: each build renders new / changed art into a new <gen> folder first (the published one is untouched while
that runs), then moves the unchanged files across (os.replace), publishes the new path and deletes the old folder.
A check that renders nothing (a restart, items still without art, prints that only leave the scope) keeps the
published generation in place: no new folder, no moves, dropped prints deleted where they are.
Items without readable art are remembered in the index ('missing') and retried only when it can help: the art URL
changed, Kodi has cached the art since (one stat), a library update named the item, or RETRY_AFTER has passed.
Never while video plays or a scan runs; a yield after every item (at least 30 ms, and half the item's own time, so
the thread is busy at most ~2/3 of one core); every step checks the stop flag (stop < 0.5 s).
Art is read only from Kodi's texture cache or a local file (artload.load_bounded): art that would need the network
is skipped and retried later (see 'missing' above), so a network read can never hold up Kodi's shutdown.
"""
import hashlib
import io
import json
import os
import time

import xbmc

from . import artload, library
from .common import PROFILE, TEMP, TEMP_SPECIAL, get_pil, log, read_json, rpc, set_prop, write_atomic, write_json
from .worker import Worker

VERSION = 1
KINDS = {                         # kind -> the box the print covers (the source aspect ratio is kept)
    'movie_poster': (240, 360),
    'movie_fanart': (480, 270),   # films in progress or added in the last FANART_DAYS days (easel / New walls)
    'set_poster': (240, 360),
    'tvshow_poster': (240, 360),
    'tvshow_fanart': (480, 270),  # all shows (easel cards; episode prints use the show's: ListItem.TvShowDBID)
    'album_thumb': (300, 300),
}
ROOMS = ('day', 'evening')
GAMMA = 2.2
REC709 = (0.2126, 0.7152, 0.0722)
EVENING_MUL = 0x8C / 255.0        # FF8C8C8C
DAY_ALPHA = 0xB3 / 255.0          # B3 over the wall
DAY_WALL = (0xF4, 0xF2, 0xEE)
QUALITY = 82
LUT_SIZE = 33
FANART_DAYS = 30
RECIPE = 'luma709-g%.1f-e%02X-d%02X-w%02X%02X%02X-q%d-lut%d-%s' % (
    GAMMA, 0x8C, 0xB3, DAY_WALL[0], DAY_WALL[1], DAY_WALL[2], QUALITY, LUT_SIZE,
    ','.join('%s=%dx%d' % (k, w, h) for k, (w, h) in sorted(KINDS.items())))

INDEX = os.path.join(PROFILE, 'greyprints.json')
PENDING = os.path.join(PROFILE, 'greyprints.pending.json')
ROOT = os.path.join(TEMP, 'grey')
PATH = 'KarmaMole.Grey.Path'
COUNT = 'KarmaMole.Grey.Count'
GEN = 'KarmaMole.Grey.Gen'
START_DELAY = 30.0     # after Kodi start: let Home settle
AFTER_SCAN = 10.0      # after a video / music scan or clean ends
AFTER_UPDATE = 30.0    # after a library update (a film newly in progress needs its fanart print)
YIELD = 0.03           # minimum pause after every rendered item
DUTY = 0.5             # ... and at least half the time the item took
SAVE_EVERY = 25        # renders between pending-index saves
RETRY_AFTER = 86400.0  # an item without readable art is tried again after a day (sooner on the triggers above)
# Kodi library announcement type -> the print kinds of that item (VideoLibrary.OnUpdate data {"item": {type, id}})
TOUCH_KINDS = {'movie': ('movie_poster', 'movie_fanart'), 'set': ('set_poster',),
               'tvshow': ('tvshow_poster', 'tvshow_fanart')}


# ----------------------------------------------------------------------------------------------- recipe (pure)
def luma(r, g, b):
    """Rec.709 luma of linearised sRGB (0..1 in, 0..1 out, gamma-encoded again)."""
    y = REC709[0] * r ** GAMMA + REC709[1] * g ** GAMMA + REC709[2] * b ** GAMMA
    return y ** (1.0 / GAMMA)


def evening_rgb(r, g, b):
    y = luma(r, g, b) * EVENING_MUL
    return y, y, y


def day_rgb(r, g, b):
    y = luma(r, g, b)
    return tuple(w / 255.0 * (1.0 - DAY_ALPHA) + y * DAY_ALPHA for w in DAY_WALL)


def make_luts(ImageFilter):
    """{'day': lut, 'evening': lut}, or None when this PIL has no Color3DLUT (Pillow < 5.2)."""
    lut = getattr(ImageFilter, 'Color3DLUT', None)
    if lut is None:
        return None
    return {'day': lut.generate(LUT_SIZE, day_rgb), 'evening': lut.generate(LUT_SIZE, evening_rgb)}


def cover_size(w, h, box):
    """The size that covers box with the source's aspect ratio, never upscaled: the skin's aspectratio then treats
    the grey print and the colour art identically."""
    bw, bh = box
    s = min(1.0, max(float(bw) / w, float(bh) / h))
    return max(1, int(round(w * s))), max(1, int(round(h * s)))


def _resample(Image):
    return getattr(Image, 'Resampling', Image).BICUBIC


def open_art(data, box, Image):
    """Decode art bytes for a print: JPEG draft (DCT-scaled) decode, alpha flattened on black, scaled to cover box."""
    im = Image.open(io.BytesIO(data))
    w, h = im.size
    size = cover_size(w, h, box)
    try:
        im.draft('RGB', size)  # JPEG only: decodes at 1/2, 1/4 or 1/8 scale, never below size
    except Exception:  # noqa: BLE001
        pass
    if im.mode in ('RGBA', 'LA', 'P', 'PA') or 'transparency' in im.info:
        rgba = im.convert('RGBA')
        bg = Image.new('RGBA', rgba.size, (0, 0, 0, 255))
        bg.alpha_composite(rgba)
        im = bg
    im = im.convert('RGB')
    if im.size != size:
        im = im.resize(size, _resample(Image))
    return im


def _grade_slow(im, room):
    """Pure-Python fallback for a PIL without Color3DLUT (slow: only used if the fast path is missing)."""
    fn = day_rgb if room == 'day' else evening_rgb
    cache = {}
    src = im.tobytes()
    out = bytearray(len(src))
    for i in range(0, len(src), 3):
        px = src[i:i + 3]
        v = cache.get(px)
        if v is None:
            v = bytes(int(c * 255.0 + 0.5) for c in fn(px[0] / 255.0, px[1] / 255.0, px[2] / 255.0))
            cache[px] = v
        out[i:i + 3] = v
    return _from(im, bytes(out))


def _from(im, data):
    res = im.copy()
    res.frombytes(data)
    return res


def render(data, kind, pil, luts):
    """{'day': jpeg bytes, 'evening': jpeg bytes} for one piece of art."""
    Image, _, ImageFilter = pil
    im = open_art(data, KINDS[kind], Image)
    out = {}
    for room in ROOMS:
        graded = im.filter(luts[room]) if luts else _grade_slow(im, room)
        buf = io.BytesIO()
        graded.save(buf, 'JPEG', quality=QUALITY)
        out[room] = buf.getvalue()
    return out


# ----------------------------------------------------------------------------------------------- scope (pure)
def stamp(when):
    """'YYYY-MM-DD HH:MM:SS' local time for an epoch (Kodi's dateadded / lastplayed format: compares as text)."""
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(when))


def _art(item, key):
    url = (item.get('art') or {}).get(key) or ''
    return url if artload.usable(url) else ''


def scope(movies, sets, shows, albums, now):
    """{'kind:dbid': url} of every print the skin hangs (SPEC 12.1 'Kinds and scope')."""
    out = {}
    since = stamp(now - FANART_DAYS * 86400)
    for m in movies:
        mid = m.get('movieid')
        if mid is None:
            continue
        url = _art(m, 'poster')
        if url:
            out['movie_poster:%d' % mid] = url
        resumed = ((m.get('resume') or {}).get('position') or 0) > 0
        if resumed or (m.get('dateadded') or '') >= since:
            url = _art(m, 'fanart')
            if url:
                out['movie_fanart:%d' % mid] = url
    for s in sets:
        url = _art(s, 'poster')
        if url and s.get('setid') is not None:
            out['set_poster:%d' % s['setid']] = url
    for t in shows:
        tid = t.get('tvshowid')
        if tid is None:
            continue
        for kind, key in (('tvshow_poster', 'poster'), ('tvshow_fanart', 'fanart')):
            url = _art(t, key)
            if url:
                out['%s:%d' % (kind, tid)] = url
    for a in albums:
        url = a.get('thumb') or ''
        if artload.usable(url) and a.get('id') is not None:
            out['album_thumb:%d' % a['id']] = url
    return out


def signature(sc):
    return hashlib.sha1(json.dumps(sc, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def same_art(entry, url, mtime):
    """An index entry still matches the art: same URL, and the cached file wasn't replaced (an unknown mtime on
    either side counts as unchanged, e.g. a print first rendered from a local file that Kodi has cached since)."""
    if not entry or entry.get('url') != url:
        return False
    old = entry.get('mtime') or 0
    return not old or not mtime or old == mtime


def plan(sc, mtimes, old_items, old_has, done_items, done_has):
    """Decide per print what a build does. Pure: the callers pass file checks as functions.

    sc          {key: url} wanted now;  mtimes {key: cached mtime or 0}
    old_items   the published generation's index entries;  old_has(key) -> both room files exist there
    done_items  entries already rendered into the generation being built (a resumed build);  done_has(key)
    Returns {'keep': [...] already in the new folder, 'move': [...] from the published folder,
             'render': [...] new keys first, then changed ones, 'drop': [...] in the index but no longer wanted}.
    """
    keep, move, new, changed = [], [], [], []
    for key in sorted(sc):
        url, mt = sc[key], mtimes.get(key, 0)
        if same_art(done_items.get(key), url, mt) and done_has(key):
            keep.append(key)
        elif same_art(old_items.get(key), url, mt) and old_has(key):
            move.append(key)
        elif key in old_items:
            changed.append(key)
        else:
            new.append(key)
    drop = sorted(k for k in old_items if k not in sc)
    return {'keep': keep, 'move': move, 'render': new + changed, 'drop': drop}


def retry_due(entry, url, mtime, now, touched=False):
    """An item that had no readable art last time: try it again now? Pure.

    entry  its 'missing' record {url, mtime, at} (None: never failed -> always due)
    mtime  the texture-cache file's mtime now (0 = not cached); touched = a library update named the item."""
    if not entry or entry.get('url') != url or touched:
        return True
    if mtime and mtime != (entry.get('mtime') or 0):
        return True  # Kodi has cached (or re-cached) the art since the last try
    at = entry.get('at') or 0
    return now - at >= RETRY_AFTER or now < at  # a day later (or the clock went back)


def touched_keys(data):
    """{'kind:dbid', ...} named by a VideoLibrary.OnUpdate / OnRemove data string; empty when it names nothing."""
    try:
        item = (json.loads(data) if isinstance(data, str) else data or {}).get('item') or {}
        kinds, dbid = TOUCH_KINDS.get(item.get('type'), ()), int(item.get('id'))
    except (ValueError, TypeError, AttributeError):
        return set()
    return {'%s:%d' % (k, dbid) for k in kinds}


def file_rel(key, room):
    kind, dbid = key.split(':', 1)
    return os.path.join(room, kind, dbid + '.jpg')


# ----------------------------------------------------------------------------------------------- library
def fetch():
    """The library lists the scope needs (JSON-RPC; art dicts only)."""
    movies = (rpc('VideoLibrary.GetMovies', {'properties': ['art', 'resume', 'dateadded']}) or {}).get('movies', [])
    sets = (rpc('VideoLibrary.GetMovieSets', {'properties': ['art']}) or {}).get('sets', [])
    shows = (rpc('VideoLibrary.GetTVShows', {'properties': ['art']}) or {}).get('tvshows', [])
    albums = library.albums()
    return movies, sets, shows, albums


def publish(gen, count):
    set_prop(PATH, '%sgrey/%s/' % (TEMP_SPECIAL, gen))
    set_prop(COUNT, count)
    set_prop(GEN, gen)


def clear():
    for name in (PATH, COUNT, GEN):
        set_prop(name, None)


def read_index():
    index = read_json(INDEX, {}) or {}
    if index.get('v') != VERSION or index.get('recipe') != RECIPE:
        return {}
    return index


# ----------------------------------------------------------------------------------------------- builder
class GreyBuilder(Worker):
    name = 'grey'
    feature = 'greyprints'
    every = 6 * 3600.0   # the 30-day fanart window moves: a cheap re-check (nothing renders when nothing changed)

    def __init__(self, monitor):
        super(GreyBuilder, self).__init__(monitor)
        self.gen = None
        self.luts = None
        self.pil = None
        self.stats = {}
        self.touched = set()   # 'kind:dbid' named by library announcements since the last check

    def publish_existing(self):
        """On activation: a complete earlier build is shown at once (the files survive restarts in temp)."""
        index = read_index()
        gen = index.get('gen')
        if gen and os.path.isdir(os.path.join(ROOT, str(gen))):
            self.gen = str(gen)
            publish(self.gen, index.get('count', 0))
            return True
        return False

    def _pil(self):
        if self.pil is None:
            self.pil = get_pil() or False
            if self.pil:
                self.luts = make_luts(self.pil[2])
                if self.luts is None:
                    log('grey prints: this PIL has no Color3DLUT, using the slow path', xbmc.LOGWARNING)
        return self.pil

    def _has(self, gen):
        base = os.path.join(ROOT, str(gen)) if gen else ''

        def has(key):
            return bool(base) and all(os.path.isfile(os.path.join(base, file_rel(key, r))) for r in ROOMS)
        return has

    def touch(self, data):
        """A library announcement named an item: its prints without art are retried on the next check."""
        self.touched |= touched_keys(data)

    @staticmethod
    def _mtime(url):
        hit = artload.cached(url)
        return hit[2] if hit else 0

    def work(self, force):
        t0 = time.time()
        if self.wait_idle():
            return
        now = time.time()
        touched, self.touched = self.touched, set()
        index = read_index()
        old_gen = str(index.get('gen') or '')
        old_dir = os.path.join(ROOT, old_gen) if old_gen else ''
        has_old = bool(old_dir) and os.path.isdir(old_dir)
        sc = scope(*fetch(), now=now)
        sig = signature(sc)
        # items without readable art last time (an index from before 'missing' existed has none: all are due once)
        missing = {} if force else {k: v for k, v in (index.get('missing') or {}).items() if sc.get(k) == v.get('url')}
        if not force and index.get('sig') == sig and has_old:
            due = [k for k in sorted(missing) if retry_due(missing[k], sc[k], self._mtime(sc[k]), now, k in touched)]
            if not due:
                self.gen = old_gen
                publish(old_gen, index.get('count', 0))
                log('grey prints: unchanged (%d, %d without art waiting), gen %s'
                    % (index.get('count', 0), len(missing), old_gen))
                if os.path.exists(PENDING):  # a forced rebuild that was stopped: nothing left to finish
                    try:
                        os.remove(PENDING)
                    except OSError:
                        pass
                    self._prune(old_gen)
                return
        if not self._pil():
            log('grey prints: no PIL (script.module.pil), nothing built', xbmc.LOGWARNING)
            return
        pending = read_json(PENDING, {}) or {}
        if (not force and pending.get('v') == VERSION and pending.get('recipe') == RECIPE and pending.get('gen')
                and pending.get('gen') != old_gen and os.path.isdir(os.path.join(ROOT, str(pending['gen'])))):
            gen, done = str(pending['gen']), dict(pending.get('items') or {})
        else:
            gen, done = str(int(time.time())), {}
            if gen == old_gen:
                gen += 'b'
        base = os.path.join(ROOT, gen)
        old_items = {} if force else dict(index.get('items') or {})
        mtimes = {}
        for n, (key, url) in enumerate(sc.items()):
            hit = artload.cached(url)
            mtimes[key] = hit[2] if hit else 0
            if n % 200 == 199 and self.aborted():
                return
        p = plan(sc, mtimes, old_items, self._has(old_gen), done, self._has(gen))
        waiting = [k for k in p['render'] if k in missing
                   and not retry_due(missing[k], sc[k], mtimes.get(k, 0), now, k in touched)]
        wait_set = set(waiting)
        todo = [k for k in p['render'] if k not in wait_set]
        items = {k: done[k] for k in p['keep']}
        log('grey prints: %d wanted, %d kept, %d unchanged, %d to render, %d without art waiting, %d dropped (gen %s)'
            % (len(sc), len(p['keep']), len(p['move']), len(todo), len(waiting), len(p['drop']), old_gen or '-'),
            xbmc.LOGINFO)
        state = {'gen': gen, 'items': items}
        failed = []
        rendered = self._render(todo, sc, mtimes, base, state, failed)
        if rendered is None:
            return
        still = {k: missing[k] for k in waiting}
        for key in failed:
            still[key] = {'url': sc[key], 'mtime': mtimes.get(key, 0), 'at': int(now)}
        if not rendered and not p['keep'] and has_old and not force:
            self._in_place(index, old_gen, old_dir, sig, p, old_items, still, len(failed), t0)
            return
        # unchanged files move across in one quick pass (the published folder is complete until now)
        late = []
        for n, key in enumerate(p['move']):
            if n % 100 == 99 and self.aborted():
                self._save_pending(state)
                return
            try:
                for room in ROOMS:
                    dst = os.path.join(base, file_rel(key, room))
                    if not os.path.isdir(os.path.dirname(dst)):
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                    os.replace(os.path.join(old_dir, file_rel(key, room)), dst)
                items[key] = old_items[key]
            except OSError:
                late.append(key)
        if late:
            more = self._render(late, sc, mtimes, base, state, failed)
            if more is None:
                return
            rendered += more
            for key in failed:
                still.setdefault(key, {'url': sc[key], 'mtime': mtimes.get(key, 0), 'at': int(now)})
        if not os.path.isdir(base):
            os.makedirs(base, exist_ok=True)  # an empty library still publishes a (complete, empty) generation
        write_json(INDEX, {'v': VERSION, 'recipe': RECIPE, 'sig': sig, 'gen': gen, 'count': len(items),
                           'items': items, 'missing': still})
        self.gen = gen
        publish(gen, len(items))
        try:
            os.remove(PENDING)
        except OSError:
            pass
        self._prune(gen)
        self.stats = {'wanted': len(sc), 'rendered': rendered, 'moved': len(p['move']) - len(late),
                      'kept': len(p['keep']), 'failed': len(failed), 'waiting': len(waiting), 'deleted': 0,
                      'in_place': False, 'seconds': round(time.time() - t0, 1)}
        log('grey prints built: %(wanted)d wanted, %(rendered)d rendered, %(moved)d moved, %(kept)d kept, '
            '%(failed)d tried without art, %(waiting)d waiting, %(seconds).1f s' % self.stats + ', gen %s' % gen,
            xbmc.LOGINFO)

    def _in_place(self, index, gen, gen_dir, sig, p, old_items, still, failed, t0):
        """Nothing rendered: keep the published generation where it is (no new folder, no moves). Prints that left the
        scope, and changed prints whose new art isn't readable yet (their old file shows the old art), are deleted."""
        gone = p['drop'] + [k for k in p['render'] if k in old_items]
        for key in gone:
            for room in ROOMS:
                try:
                    os.remove(os.path.join(gen_dir, file_rel(key, room)))
                except OSError:
                    pass
        items = {k: old_items[k] for k in p['move']}
        stored = {'v': VERSION, 'recipe': RECIPE, 'sig': sig, 'gen': gen, 'count': len(items), 'items': items,
                  'missing': still}
        if stored != index:
            write_json(INDEX, stored)
        self.gen = gen
        publish(gen, len(items))
        try:
            os.remove(PENDING)
        except OSError:
            pass
        self._prune(gen)  # the new folder (empty: nothing rendered) and any stale generation
        self.stats = {'wanted': len(items) + len(still), 'rendered': 0, 'moved': 0, 'kept': len(items),
                      'failed': failed, 'waiting': len(still) - failed, 'deleted': len(gone), 'in_place': True,
                      'seconds': round(time.time() - t0, 1)}
        log('grey prints: gen %s kept in place: %d prints, %d deleted, %d without art (%d tried now; retried when Kodi '
            'caches the art, after a library update of the item, or daily), %.1f s'
            % (gen, len(items), len(gone), len(still), failed, self.stats['seconds']), xbmc.LOGINFO)

    def _render(self, keys, sc, mtimes, base, state, failed):
        """Render keys into base; keys without readable art go to failed (one log line for all of them, by the caller).
        Returns the number rendered, or None when stopped (progress saved as pending)."""
        count = 0
        errors = 0
        for key in keys:
            if self.aborted() or self.wait_idle():
                self._save_pending(state)
                return None
            t = time.time()
            data, mt = artload.load_bounded(sc[key])
            if not data:
                failed.append(key)
                continue
            try:
                files = render(data, key.split(':', 1)[0], self.pil, self.luts)
            except Exception as e:  # noqa: BLE001
                if not errors:
                    log('grey print failed for %s: %s (further failures are only counted)' % (key, e))
                errors += 1
                failed.append(key)
                continue
            for room in ROOMS:
                write_atomic(os.path.join(base, file_rel(key, room)), files[room])
            state['items'][key] = {'url': sc[key], 'mtime': mt or mtimes.get(key, 0)}
            count += 1
            if count % SAVE_EVERY == 0:
                self._save_pending(state)
            if self.wait(max(YIELD, DUTY * (time.time() - t))):
                self._save_pending(state)
                return None
        return count

    def _save_pending(self, state):
        if state['items']:
            try:
                write_json(PENDING, {'v': VERSION, 'recipe': RECIPE, 'gen': state['gen'], 'items': state['items']})
            except OSError as e:
                log('grey prints: pending index not written: %s' % e)

    def _prune(self, keep):
        """Delete every other generation folder, file by file, so a stop request is honoured within ~100 files."""
        try:
            names = [d for d in os.listdir(ROOT) if d != keep]
        except OSError:
            return
        n = 0
        for d in names:
            top = os.path.join(ROOT, d)
            for dirpath, dirnames, filenames in os.walk(top, topdown=False):
                for f in filenames:
                    try:
                        os.remove(os.path.join(dirpath, f))
                    except OSError:
                        pass
                    n += 1
                    if n % 100 == 0 and self.aborted():
                        return  # the rest goes on the next build
                try:
                    os.rmdir(dirpath)
                except OSError:
                    pass
