# KarmaMole Skin Helper (script.karmamole.helper)
# Copyright (C) 2026 Omar Kamel
# SPDX-License-Identifier: GPL-2.0-or-later
"""plugin://script.karmamole.helper/ routes.

  plugin://script.karmamole.helper/                              = ?info=rings
  plugin://script.karmamole.helper/?info=rings[&min=3]          the rings that have slices (Genre, Style, Mood)
  plugin://script.karmamole.helper/?info=wheel&ring=genre|style|mood[&min=3][&sort=name|count]
  plugin://script.karmamole.helper/?action=play_slice&ring=R&value=V   (RunPlugin) replace the queue, play shuffled
  plugin://script.karmamole.helper/?info=easel[&limit=24][&rev=R]       (1.1.0, feature 'easel') Still on the easel
  plugin://script.karmamole.helper/?info=new[&days=7][&limit=24][&rev=R] (1.1.0, feature 'easel') New in the collection
The wheel routes need the 'wheel' feature, the easel routes 'easel'. `rev` is ignored: it is only there so the skin's
path changes (and the list reloads) when Window(Home).Property(KarmaMole.Easel.Rev) changes.
"""
import sys
from urllib.parse import parse_qsl, urlencode

import xbmc
import xbmcgui
import xbmcplugin

from . import easel, library, wheel
from .common import ADDON_ID, localize
from .features import allowed

BASE = 'plugin://%s/' % ADDON_ID
RING_LABEL = {'genre': 515, 'style': 176, 'mood': 175}  # Kodi core strings: Genre, Styles, Moods


def url(**kw):
    return BASE + '?' + urlencode(kw)


def _int(v, default):
    try:
        return max(1, int(v))
    except (TypeError, ValueError):
        return default


def list_rings(handle, params):
    minimum = _int(params.get('min'), 3)
    albums = library.albums()
    items = []
    for ring in wheel.RINGS:
        sl = wheel.slices(ring, albums, minimum)
        if not sl:
            continue
        covered = len({i for s in sl for i in s['ids']})
        li = xbmcgui.ListItem(xbmc.getLocalizedString(RING_LABEL[ring]), str(len(sl)), offscreen=True)
        li.setProperty('Groove.Ring', ring)
        li.setProperty('Groove.Count', str(len(sl)))
        li.setProperty('Groove.Albums', str(covered))
        li.setArt({'icon': 'DefaultMusicGenres.png'})
        items.append((url(info='wheel', ring=ring, min=minimum), li, True))
    xbmcplugin.addDirectoryItems(handle, items, len(items))
    xbmcplugin.setContent(handle, 'genres')
    xbmcplugin.endOfDirectory(handle, cacheToDisc=False)


def list_wheel(handle, params):
    ring = params.get('ring', 'genre')
    if ring not in wheel.RINGS:
        ring = 'genre'
    minimum = _int(params.get('min'), 3)
    sl = wheel.slices(ring, library.albums(), minimum)
    if params.get('sort') == 'count':
        sl.sort(key=lambda s: (-s['count'], s['value'].lower()))
    else:
        sl.sort(key=lambda s: s['value'].lower())
    mix = localize(32001)  # English fallback: see common.STRINGS_EN (Kodi skips strings of copy-installed add-ons)
    items = []
    for s in sl:
        path = wheel.albums_path(ring, s['value'], s.get('genreid'))
        play = url(action='play_slice', ring=ring, value=s['value'])
        li = xbmcgui.ListItem(s['value'], str(s['count']), path=path, offscreen=True)
        cov = wheel.covers(s)
        if cov:
            li.setArt({'thumb': cov[0], 'icon': cov[0]})
        for n, c in enumerate(cov, 1):
            li.setProperty('Groove.Cover%d' % n, c)
        li.setProperty('Groove.Ring', ring)
        li.setProperty('Groove.Value', s['value'])
        li.setProperty('Groove.Count', str(s['count']))
        li.setProperty('Groove.AlbumsPath', path)
        li.setProperty('Groove.PlayPath', play)
        if s.get('genreid') is not None:
            li.setProperty('Groove.GenreID', str(s['genreid']))
        li.addContextMenuItems([(mix, 'RunPlugin(%s)' % play)])
        items.append((path, li, True))
    xbmcplugin.addDirectoryItems(handle, items, len(items))
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.setContent(handle, 'genres')
    xbmcplugin.endOfDirectory(handle, cacheToDisc=False)


def _limit(v, default, top=easel.MAX_LIMIT):
    return min(top, _int(v, default))


def _set(tag, name, *args):
    """InfoTagVideo setter, skipped quietly if this Kodi lacks it or the value is empty."""
    fn = getattr(tag, name, None)
    if fn is None or not args or args[0] in (None, '', [], 0, 0.0):
        return
    try:
        fn(*args)
    except Exception:  # noqa: BLE001
        pass


def video_item(rec, window=''):
    """A library-backed ListItem: dbid + media type (Info opens the library info page), resume point, art, the file
    in the path and in ListItem.Property(file), and the KarmaMole.* properties (API doc section 10)."""
    kind = rec.get('kind') or 'movie'
    li = xbmcgui.ListItem(rec.get('title', ''), rec.get('showtitle', ''), path=rec.get('file', ''), offscreen=True)
    tag = li.getVideoInfoTag()
    tag.setMediaType(kind)
    _set(tag, 'setDbId', int(rec.get('dbid') or 0))
    _set(tag, 'setTitle', rec.get('title', ''))
    _set(tag, 'setPlaycount', int(rec.get('playcount') or 0))
    _set(tag, 'setLastPlayed', rec.get('lastplayed', ''))
    _set(tag, 'setDateAdded', rec.get('dateadded', ''))
    _set(tag, 'setDuration', int(rec.get('runtime') or 0))
    _set(tag, 'setPlot', rec.get('plot', ''))
    _set(tag, 'setGenres', rec.get('genre') or [])
    _set(tag, 'setDirectors', rec.get('director') or [])
    _set(tag, 'setStudios', rec.get('studio') or [])
    _set(tag, 'setRating', float(rec.get('rating') or 0))
    _set(tag, 'setFilenameAndPath', rec.get('file', ''))
    resume = rec.get('resume') or {}
    if float(resume.get('position') or 0) > 0:
        _set(tag, 'setResumePoint', float(resume['position']), float(resume.get('total') or rec.get('runtime') or 0))
    if kind == 'movie':
        _set(tag, 'setYear', int(rec.get('year') or 0))
        _set(tag, 'setTagLine', rec.get('tagline', ''))
        _set(tag, 'setPremiered', rec.get('premiered', ''))
        _set(tag, 'setSet', rec.get('set', ''))
        _set(tag, 'setSetId', int(rec.get('setid') or 0))
    else:
        _set(tag, 'setTvShowTitle', rec.get('showtitle', ''))
        _set(tag, 'setSeason', int(rec.get('season') or 0))
        _set(tag, 'setEpisode', int(rec.get('episode') or 0))
        _set(tag, 'setFirstAired', rec.get('firstaired', ''))
    li.setArt(rec.get('art') or {})
    props = {
        'file': rec.get('file', ''),
        'KarmaMole.Kind': kind,
        'KarmaMole.MinLeft': rec.get('minleft', ''),
        'KarmaMole.Next': 'true' if rec.get('next') else '',
        'KarmaMole.TvShowDBID': rec.get('tvshowid') if kind == 'episode' else '',
        'KarmaMole.EpisodesLeft': rec.get('episodesleft', '') if kind == 'episode' else '',
        'KarmaMole.ShowPlot': rec.get('showplot', '') if kind == 'episode' else '',
        'KarmaMole.NewCount': rec.get('newcount', ''),
        'KarmaMole.Window': window,
    }
    for k, v in props.items():
        if v not in (None, ''):
            li.setProperty(k, str(v))
    return li


def list_easel(handle, params):
    """Still on the easel / New in the collection, read from the service's easel.json (computed live only when
    the file isn't there yet, or for a `days` value the service doesn't precompute)."""
    which = params.get('info')
    limit = _limit(params.get('limit'), 24)
    cache = easel.read_cache()
    window = ''
    if which == 'new':
        days = _int(params.get('days'), easel.DEFAULT_DAYS)
        new = cache.get('new') or {}
        if not new or int(new.get('days') or 0) != days:
            res = easel.collect_new(days)
            new = {'window': res[0], 'items': [easel.item(*t) for t in res[1]], 'count': res[2]} if res else {}
        window, recs = new.get('window', ''), new.get('items') or []
    else:
        recs = cache.get('easel')
        if recs is None:
            res = easel.collect_easel()
            recs = [easel.item(*t) for t in res[0]] if res else []
    items = [(r.get('file', ''), video_item(r, window), False) for r in recs[:limit]]
    xbmcplugin.addDirectoryItems(handle, items, len(items))
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.setContent(handle, 'videos')
    xbmcplugin.endOfDirectory(handle, cacheToDisc=False)


def main():
    handle = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].lstrip('-').isdigit() else -1
    params = dict(parse_qsl(sys.argv[2].lstrip('?'))) if len(sys.argv) > 2 else {}
    if params.get('info') in ('easel', 'new'):
        if allowed('easel'):
            list_easel(handle, params)
        elif handle >= 0:
            xbmcplugin.endOfDirectory(handle, succeeded=True, cacheToDisc=False)  # an empty listing, not an error
        return
    if not allowed('wheel'):  # the running skin didn't ask: an empty listing (not an error), no play
        if handle >= 0:
            xbmcplugin.endOfDirectory(handle, succeeded=params.get('action') != 'play_slice', cacheToDisc=False)
        return
    if params.get('action') == 'play_slice':
        wheel.play(params.get('ring', ''), params.get('value', ''))
        if handle >= 0:
            xbmcplugin.endOfDirectory(handle, succeeded=False)
        return
    if params.get('info') == 'wheel':
        list_wheel(handle, params)
    else:
        list_rings(handle, params)

