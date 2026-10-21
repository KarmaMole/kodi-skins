# KarmaMole Skin Helper (script.karmamole.helper)
# Copyright (C) 2026 Omar Kamel
# SPDX-License-Identifier: GPL-2.0-or-later
"""Still on the easel / New in the collection (feature 'easel', Vernissage SPEC 12.2).

  easel   films in progress + one item per in-progress show: its episode with a resume point (the latest played),
          else the first unwatched episode after the highest watched one by (season, episode); specials skipped;
          a show with no next episode in the library drops out. Merged by last played, newest first.
  new     films and episodes added in the last `days` days, one item per show (its earliest new unwatched episode),
          merged by date added, newest first; when nothing is that new, the RECENT_LIMIT newest additions
          (window 'recent', else 'week').

The service computes both lists in its own thread after library changes (debounced, never while video plays) and
writes addon_data/script.karmamole.helper/easel.json; the plugin (plugin.py) only reads that file. When the lists
change, Window(Home).Property(KarmaMole.Easel.Rev) changes, so a skin path carrying &rev=$INFO[...] reloads.
The selection logic is pure (next_episode, easel_list, new_list) and unit-tested.
Episode items also carry the show's plot (showplot -> ListItem.Property(KarmaMole.ShowPlot)): a spoiler-safe premise
where the episode plot would give the story away. Kodi 21 has no tagline for TV shows (JSON-RPC Video.Fields.TVShow,
xbmc/interfaces/json-rpc/schema/types.json on the Omega branch), so there is no show tagline to pass on.
"""
import math
import os
import time

import xbmc

from .common import PROFILE, log, prop, read_json, rpc, set_prop, write_json
from .worker import Worker

VERSION = 1
CACHE = os.path.join(PROFILE, 'easel.json')
REV = 'KarmaMole.Easel.Rev'
EASEL_COUNT = 'KarmaMole.Easel.Count'   # works on the easel (all of them, not capped by MAX_LIMIT / &limit=)
NEW_COUNT = 'KarmaMole.New.Count'       # works in New in the collection (in the window, or the recent fallback)
MAX_LIMIT = 50        # stored list length; the plugin's &limit= slices it
DEFAULT_DAYS = 7
RECENT_LIMIT = 12
RECENT_SCAN = 300     # episodes looked at for New (newest first)
MOVIE_SCAN = 100      # films looked at for New
START_DELAY = 5.0
DEBOUNCE = 2.0
ART_KEYS = ('poster', 'fanart', 'thumb', 'landscape', 'clearlogo', 'banner', 'tvshow.poster', 'tvshow.fanart',
            'tvshow.landscape', 'tvshow.clearlogo', 'tvshow.banner', 'season.poster')
MOVIE_PROPS = ['title', 'year', 'art', 'resume', 'lastplayed', 'file', 'runtime', 'playcount', 'dateadded', 'genre',
               'director', 'rating', 'studio', 'plot', 'tagline', 'premiered', 'set', 'setid']
EP_LIGHT = ['season', 'episode', 'playcount', 'resume', 'lastplayed', 'dateadded', 'tvshowid', 'showtitle']
EP_FULL = ['title', 'season', 'episode', 'playcount', 'resume', 'lastplayed', 'dateadded', 'tvshowid', 'showtitle',
           'file', 'art', 'runtime', 'firstaired', 'rating', 'plot', 'studio', 'genre', 'director']
SHOW_PROPS = ['title', 'art', 'lastplayed', 'studio', 'year', 'plot']


# ----------------------------------------------------------------------------------------------- pure selection
def _se(e):
    return (int(e.get('season') or 0), int(e.get('episode') or 0))


def _pos(e):
    return float((e.get('resume') or {}).get('position') or 0)


def _watched(e):
    return int(e.get('playcount') or 0) > 0


def next_episode(episodes):
    """The episode a show continues with, or None. Specials (season 0) never count."""
    eps = [e for e in episodes if _se(e)[0] > 0]
    resumed = [e for e in eps if _pos(e) > 0]
    if resumed:
        return max(resumed, key=lambda e: (e.get('lastplayed') or '', _se(e)))
    watched = [_se(e) for e in eps if _watched(e)]
    top = max(watched) if watched else (0, 0)
    after = sorted((e for e in eps if not _watched(e) and _se(e) > top), key=_se)
    return after[0] if after else None


def episodes_left(episodes):
    return sum(1 for e in episodes if _se(e)[0] > 0 and not _watched(e))


def minutes_left(item):
    """Minutes left of a started item, rounded up; None when it hasn't been started."""
    pos = _pos(item)
    if pos <= 0:
        return None
    total = float((item.get('resume') or {}).get('total') or 0) or float(item.get('runtime') or 0)
    if total <= pos:
        return None
    return int(math.ceil((total - pos) / 60.0))


def easel_list(movies, shows, limit=MAX_LIMIT):
    """movies: in-progress film dicts (resume, lastplayed). shows: [(show, [light episode dicts])].
    Returns [(kind, dict, extra)] newest played first; extra = {'tvshow', 'next', 'episodesleft', 'lastplayed'}."""
    out = []
    for m in movies:
        if _pos(m) > 0:
            out.append(('movie', m, {'lastplayed': m.get('lastplayed') or ''}))
    for show, eps in shows:
        nxt = next_episode(eps)
        if nxt is None:
            continue
        last = max([e.get('lastplayed') or '' for e in eps] + [show.get('lastplayed') or ''])
        out.append(('episode', nxt, {'tvshow': show, 'next': _pos(nxt) <= 0, 'episodesleft': episodes_left(eps),
                                     'lastplayed': last}))
    out.sort(key=lambda t: t[2]['lastplayed'], reverse=True)
    return out[:limit]


def new_list(movies, episodes, since, limit=MAX_LIMIT, recent_limit=RECENT_LIMIT):
    """movies / episodes: newest-added first (dateadded 'YYYY-MM-DD HH:MM:SS'); since = the same format.
    Returns (window, [(kind, dict, extra)]); extra = {'newcount', 'dateadded'}; window 'week' or 'recent'."""
    def build(ms, es):
        units = [('movie', m, {'dateadded': m.get('dateadded') or ''}) for m in ms]
        groups = {}
        for e in es:
            if _se(e)[0] <= 0 or e.get('tvshowid') is None:
                continue
            groups.setdefault(e['tvshowid'], []).append(e)
        for eps in groups.values():
            unwatched = [e for e in eps if not _watched(e)]
            pick = min(unwatched or eps, key=_se)
            units.append(('episode', pick, {'newcount': len(eps),
                                            'dateadded': max(e.get('dateadded') or '' for e in eps)}))
        units.sort(key=lambda t: t[2]['dateadded'], reverse=True)
        return units

    week = build([m for m in movies if (m.get('dateadded') or '') >= since],
                 [e for e in episodes if (e.get('dateadded') or '') >= since])
    if week:
        return 'week', week[:limit]
    return 'recent', build(movies, episodes)[:min(limit, recent_limit)]


# ----------------------------------------------------------------------------------------------- stored items
def _art(src, show=None):
    """The art keys skins read; an episode gets its show's art as tvshow.* and falls back to it for fanart,
    landscape, clearlogo and poster (as Kodi's own library items do)."""
    art = {k: v for k, v in (src.get('art') or {}).items() if k in ART_KEYS and v}
    for k, v in ((show or {}).get('art') or {}).items():
        if k in ('poster', 'fanart', 'landscape', 'clearlogo', 'banner') and v:
            art.setdefault('tvshow.' + k, v)
    for k in ('fanart', 'landscape', 'clearlogo', 'poster'):
        if k not in art and art.get('tvshow.' + k):
            art[k] = art['tvshow.' + k]
    return art


def item(kind, d, extra):
    """The JSON-able record the plugin turns into a ListItem."""
    show = extra.get('tvshow')
    rec = {
        'kind': kind,
        'dbid': d.get('movieid') if kind == 'movie' else d.get('episodeid'),
        'title': d.get('title') or d.get('label') or '',
        'file': d.get('file') or '',
        'art': _art(d, show),
        'resume': {'position': _pos(d), 'total': float((d.get('resume') or {}).get('total') or 0)},
        'runtime': int(d.get('runtime') or 0),
        'playcount': int(d.get('playcount') or 0),
        'lastplayed': d.get('lastplayed') or '',
        'dateadded': d.get('dateadded') or '',
        'rating': float(d.get('rating') or 0),
        'plot': d.get('plot') or '',
        'genre': list(d.get('genre') or []),
        'director': list(d.get('director') or []),
        'studio': list(d.get('studio') or (show or {}).get('studio') or []),
    }
    m = minutes_left(d)
    rec['minleft'] = m if m is not None else ''
    if kind == 'movie':
        rec.update({'year': int(d.get('year') or 0), 'tagline': d.get('tagline') or '',
                    'premiered': d.get('premiered') or '', 'set': d.get('set') or '', 'setid': d.get('setid') or 0})
    else:
        rec.update({'tvshowid': d.get('tvshowid'), 'showtitle': d.get('showtitle') or (show or {}).get('title') or '',
                    'showplot': extra.get('showplot') or (show or {}).get('plot') or '',
                    'season': int(d.get('season') or 0), 'episode': int(d.get('episode') or 0),
                    'firstaired': d.get('firstaired') or '', 'next': bool(extra.get('next')),
                    'episodesleft': extra.get('episodesleft', '')})
    if 'newcount' in extra:
        rec['newcount'] = extra['newcount']
    return rec


# ----------------------------------------------------------------------------------------------- library
def _details(kind, d, props):
    if kind == 'movie':
        return d
    r = rpc('VideoLibrary.GetEpisodeDetails', {'episodeid': d['episodeid'], 'properties': props}) or {}
    full = r.get('episodedetails')
    return full or d


def show_plots(tvshowids, stop=lambda: False):
    """{tvshowid: plot} for the shows of the New episode cards (one GetTVShowDetails per show, at most MAX_LIMIT),
    or None when stopped."""
    out = {}
    for tid in tvshowids:
        if tid in out or tid is None:
            continue
        if stop():
            return None
        r = rpc('VideoLibrary.GetTVShowDetails', {'tvshowid': tid, 'properties': ['plot']})
        det = r.get('tvshowdetails') if isinstance(r, dict) else None
        out[tid] = (det or {}).get('plot') or ''
    return out


def collect_easel(stop=lambda: False):
    """([(kind, details, extra)] up to MAX_LIMIT, total count) for Still on the easel, or None when stopped."""
    movies = (rpc('VideoLibrary.GetMovies', {
        'properties': MOVIE_PROPS, 'filter': {'field': 'inprogress', 'operator': 'true', 'value': ''},
        'sort': {'method': 'lastplayed', 'order': 'descending'}}) or {}).get('movies', [])
    shows = (rpc('VideoLibrary.GetInProgressTVShows', {'properties': SHOW_PROPS}) or {}).get('tvshows', [])
    pairs = []
    for s in shows:
        if stop():
            return None
        eps = (rpc('VideoLibrary.GetEpisodes', {'tvshowid': s['tvshowid'], 'properties': EP_LIGHT}) or {}).get(
            'episodes', [])
        pairs.append((s, eps))
    full = easel_list(movies, pairs, 10 ** 6)
    out = []
    for kind, d, extra in full[:MAX_LIMIT]:
        if stop():
            return None
        out.append((kind, _details(kind, d, EP_FULL), extra))
    return out, len(full)


def collect_new(days=DEFAULT_DAYS, stop=lambda: False, now=None):
    """(window, [(kind, details, extra)] up to MAX_LIMIT, total count) for New in the collection, or None."""
    since = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime((now or time.time()) - days * 86400))
    movies = (rpc('VideoLibrary.GetMovies', {
        'properties': MOVIE_PROPS, 'sort': {'method': 'dateadded', 'order': 'descending'},
        'limits': {'start': 0, 'end': MOVIE_SCAN}}) or {}).get('movies', [])
    eps = (rpc('VideoLibrary.GetEpisodes', {
        'properties': EP_LIGHT, 'sort': {'method': 'dateadded', 'order': 'descending'},
        'limits': {'start': 0, 'end': RECENT_SCAN}}) or {}).get('episodes', [])
    window, units = new_list(movies, eps, since, 10 ** 6)
    plots = show_plots([d.get('tvshowid') for kind, d, extra in units[:MAX_LIMIT] if kind == 'episode'], stop)
    if plots is None:
        return None
    out = []
    for kind, d, extra in units[:MAX_LIMIT]:
        if stop():
            return None
        if kind == 'episode':
            extra = dict(extra, showplot=plots.get(d.get('tvshowid'), ''))
        out.append((kind, _details(kind, d, EP_FULL), extra))
    return window, out, len(units)


def compute(stop=lambda: False, days=DEFAULT_DAYS):
    """{'easel': [records], 'easel_count': n, 'new': {'days', 'window', 'items', 'count'}} or None when stopped."""
    ea = collect_easel(stop)
    if ea is None:
        return None
    nw = collect_new(days, stop)
    if nw is None:
        return None
    return {'easel': [item(*t) for t in ea[0]], 'easel_count': ea[1],
            'new': {'days': days, 'window': nw[0], 'items': [item(*t) for t in nw[1]], 'count': nw[2]}}


def read_cache():
    c = read_json(CACHE, {}) or {}
    return c if c.get('v') == VERSION else {}


def publish(c):
    """Rev + the two counts from a stored / computed cache dict (counts are published as numbers, 0 included)."""
    set_prop(REV, c.get('rev'))
    set_prop(EASEL_COUNT, c.get('easel_count', len(c.get('easel') or [])) if 'easel' in c else None)
    new = c.get('new') or {}
    set_prop(NEW_COUNT, new.get('count', len(new.get('items') or [])) if new else None)


def clear():
    for name in (REV, EASEL_COUNT, NEW_COUNT):
        set_prop(name, None)


# ----------------------------------------------------------------------------------------------- service worker
class EaselBuilder(Worker):
    name = 'easel'
    feature = 'easel'
    every = 3600.0   # the 7-day window moves; also catches anything a notification missed

    def publish_existing(self):
        c = read_cache()
        if c.get('rev'):
            publish(c)

    def work(self, force):
        if self.wait_idle():
            return
        lists = compute(self.aborted)
        if lists is None:
            return
        old = read_cache()
        same = (old.get('easel') == lists['easel'] and old.get('new') == lists['new']
                and old.get('easel_count') == lists['easel_count'])
        rev = old.get('rev') if (same and old.get('rev') and not force) else str(int(time.time() * 1000))
        stored = {'v': VERSION, 'rev': rev, 'at': int(time.time()), 'easel': lists['easel'],
                  'easel_count': lists['easel_count'], 'new': lists['new']}
        if not same or force or not old:
            write_json(CACHE, stored)
        if prop(REV) != rev or prop(EASEL_COUNT) != str(lists['easel_count']):
            publish(stored)
        log('easel: %d on the easel, %d new (%s)%s' % (lists['easel_count'], lists['new']['count'],
                                                       lists['new']['window'], '' if same else ', rev ' + rev),
            xbmc.LOGINFO if not same else xbmc.LOGDEBUG)
