# KarmaMole Skin Helper (script.karmamole.helper)
# Copyright (C) 2026 Omar Kamel
# SPDX-License-Identifier: GPL-2.0-or-later
"""Read art bytes for an infolabel art URL, the way TMDb Helper does (resources/tmdbhelper/lib/monitor/images.py):
1) Kodi's texture cache (Thumbnails/<h>/<crc>.jpg|png; hash of the unwrapped and of the wrapped URL) - the usual hit,
   because the art is on screen when we ask; 2) the URL through the VFS; 3) a VFS copy into our profile folder."""
import os
from urllib.parse import unquote

import xbmc
import xbmcvfs

from .common import PROFILE, log


def usable(url):
    """Skin fallbacks (DefaultAlbumCover.png ...) and empty labels are not art."""
    return bool(url) and not url.startswith('Default') and not url.startswith('special://skin/')


def _read(path, quiet=False):
    try:
        f = xbmcvfs.File(path, 'rb')
        try:
            return bytes(f.readBytes())
        finally:
            f.close()
    except Exception as e:  # noqa: BLE001
        if not quiet:
            log('read failed %s: %s' % (path, e))
        return b''


def _inner(url):
    inner = unquote(url[len('image://'):]) if url.startswith('image://') else url
    return inner[:-1] if inner.endswith('/') else inner


def cached(url):
    """(special:// path, size, mtime) of the art in Kodi's texture cache, or None. A stat only, nothing is read."""
    inner = _inner(url)
    for key in (inner, url):
        name = xbmc.getCacheThumbName(key)  # 'xxxxxxxx.tbn'
        for ext in ('jpg', 'png'):
            path = 'special://profile/Thumbnails/%s/%s.%s' % (name[0], name[:-4], ext)
            try:
                st = os.stat(xbmcvfs.translatePath(path))
            except OSError:
                continue
            return path, st.st_size, int(st.st_mtime)
    return None


def is_local(url):
    """A plain local file (no network scheme): safe to read from a worker that must stop within a second."""
    inner = _inner(url)
    return '://' not in inner or inner.startswith('special://')


def load_bounded(url):
    """(bytes, mtime) from the texture cache, else from a local file; (b'', 0) for art that would need the network
    (it is picked up on a later build, once Kodi has cached it). Used by grey prints (bounded stop time). Quiet: the
    caller logs one count for all the items without art, not a line per item."""
    hit = cached(url)
    if hit:
        data = _read(hit[0], quiet=True)
        if data:
            return data, hit[2]
    if is_local(url):
        for path in (_inner(url), url):
            data = _read(path, quiet=True)
            if data:
                return data, 0
    return b'', 0


def load(url):
    """(bytes, stamp). stamp identifies this version of the image (cached file + size + mtime when the texture cache
    served it), so a replaced cover with the same URL gets a new soft-art file name. (b'', '') when unreadable."""
    inner = unquote(url[len('image://'):]) if url.startswith('image://') else url
    if inner.endswith('/'):
        inner = inner[:-1]
    for key in (inner, url):
        name = xbmc.getCacheThumbName(key)  # 'xxxxxxxx.tbn'
        for ext in ('jpg', 'png'):
            cached = 'special://profile/Thumbnails/%s/%s.%s' % (name[0], name[:-4], ext)
            real = xbmcvfs.translatePath(cached)
            try:
                st = os.stat(real)
            except OSError:
                continue
            data = _read(cached)
            if data:
                return data, '%s|%d|%d' % (cached, st.st_size, int(st.st_mtime))
    for path in (url, inner) if inner != url else (url,):
        data = _read(path)
        if data:
            return data, '%s|%d' % (url, len(data))
    tmp = os.path.join(PROFILE, 'art.tmp')
    try:
        if not os.path.isdir(PROFILE):
            os.makedirs(PROFILE, exist_ok=True)
        if xbmcvfs.copy(url, tmp):
            with open(tmp, 'rb') as f:
                data = f.read()
            return data, '%s|%d' % (url, len(data))
    except Exception as e:  # noqa: BLE001
        log('copy failed %s: %s' % (url, e))
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    return b'', ''
