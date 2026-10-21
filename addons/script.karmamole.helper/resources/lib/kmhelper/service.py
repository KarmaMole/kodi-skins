# KarmaMole Skin Helper (script.karmamole.helper)
# Copyright (C) 2026 Omar Kamel
# SPDX-License-Identifier: GPL-2.0-or-later
"""KarmaMole Skin Helper service: browse-time colours + soft art, playing-album colours, album spines.

Cost model (NVIDIA Shield):
- Runs only the features the running skin asked for (features.py: the per-skin table, or
  Window(Home).Property(KarmaMole.Helper.Features)). No features: one skin id + one property check per second, no
  worker threads, no file access.
- Browsing: reads 2-3 infolabels every 0.15 s and compares strings. Work happens only when the focused item's art has
  been the same for REST seconds (fast scrolling costs nothing), and a repeat visit is a memory hit.
- Fullscreen video, slideshow and screensaver: browse polling drops to once a second and does no work.
- Playing album: checked once a second while audio plays; one render per album change.
- Spines: a background thread, only after library changes, paused while video plays or a scan runs.
- Grey prints (1.1.0): a background thread after start / library changes, incremental, paused while video plays or a
  scan runs, a yield after every item.
- Easel lists (1.1.0): a short background job after library / playback changes (debounced), never while video plays.
"""
import time

import xbmc

from . import artload, easel, features as feats, greyprints
from .common import ADDON_ID, cond, info, log, prop, set_prop, skin_is_groove
from .glow import Publisher, Renderer
from .spines import SpineBuilder

TICK = 0.15        # browse poll while active
IDLE_TICK = 1.0    # poll when disabled / fullscreen video / screensaver
REST = 0.4         # the focused art must rest this long before we render (spec: 400 ms)
PLAYER_EVERY = 1.0
SKIN_EVERY = 1.0
PAUSE_COND = ('Window.IsActive(fullscreenvideo) | Window.IsActive(slideshow) | System.ScreenSaverActive | '
              'Window.IsActive(startup)')
VIDEO_TYPES = ('movie', 'tvshow', 'season', 'episode', 'set', 'musicvideo', 'video')
VIDEO_ART = ('fanart', 'landscape', 'thumb', 'poster')
MUSIC_ART = ('thumb', 'album.thumb', 'fanart')
PLAYER_ART = ('Player.Art(thumb)', 'Player.Art(album.thumb)', 'MusicPlayer.Cover')
START_DELAY = 20.0  # first spine check after login: let Home settle first
RUNNING = 'KarmaMole.Helper.Running'   # 'true' while the service runs (skins gate on it)
ACTIVE = 'KarmaMole.Helper.Active'     # the features running for the current skin, comma list (empty = idle)
# Kodi announcements that change what the easel / New lists and the grey-print scope contain
LIBRARY_EVENTS = ('VideoLibrary.OnUpdate', 'VideoLibrary.OnRemove', 'Player.OnStop')


class Player(xbmc.Player):
    def __init__(self, svc):
        super(Player, self).__init__()
        self.svc = svc

    def onAVStarted(self):
        self.svc.player_dirty = True

    def onPlayBackStarted(self):
        self.svc.player_dirty = True

    def onPlayBackStopped(self):
        self.svc.player_dirty = True

    def onPlayBackEnded(self):
        self.svc.player_dirty = True

    def onPlayBackError(self):
        self.svc.player_dirty = True


class Service(xbmc.Monitor):
    def __init__(self):
        super(Service, self).__init__()
        # colour parts are made when a skin first asks for 'colours' (their fade threads and the soft-art prune
        # cost nothing until then); the spine worker starts on its first request
        self.renderer = self.browse = self.playing = None
        self.player = Player(self)
        self.spines = SpineBuilder(self)
        self.grey = greyprints.GreyBuilder(self)   # 1.1.0; no thread until 'greyprints' is first requested
        self.easel = easel.EaselBuilder(self)      # 1.1.0; no thread until 'easel' is first requested
        self.features = frozenset()
        self.enabled = False   # any feature on
        self.colours = False
        self.skin = None
        # browse state
        self.seen, self.seen_at, self.done = None, 0.0, None
        # player state
        self.player_dirty = True
        self.music = False
        self.player_key, self.player_pending = None, None
        self.next_player = 0.0
        self.next_skin = 0.0

    # ------------------------------------------------------------------------------------------- Kodi callbacks
    def onScanFinished(self, library):
        if library == 'music' and 'spines' in self.features:
            self.spines.request(delay=5.0)
        self.library_done(library)

    def onCleanFinished(self, library):
        if library == 'music' and 'spines' in self.features:
            self.spines.request(delay=5.0)
        self.library_done(library)

    def library_done(self, library):
        """A scan or clean ended (1.1.0 features only)."""
        if 'greyprints' in self.features and library in ('video', 'music'):
            self.grey.request(delay=greyprints.AFTER_SCAN)
        if 'easel' in self.features and library == 'video':
            self.easel.request(delay=easel.DEBOUNCE)

    def onNotification(self, sender, method, data):
        """NotifyAll(script.karmamole.helper,<message>) from a skin or from default.py; Kodi's library and player
        announcements for the 1.1.0 features."""
        if sender == 'xbmc':
            if method in LIBRARY_EVENTS:
                if 'easel' in self.features:
                    self.easel.request(delay=easel.DEBOUNCE)
                if 'greyprints' in self.features:
                    self.grey.touch(data)  # an item named here gets its art-less prints retried at once
                    self.grey.request(delay=greyprints.AFTER_UPDATE)
            return
        if sender != ADDON_ID:
            return
        msg = method.split('.', 1)[-1]
        log('notification %s' % msg)
        if msg == 'spines_rebuild':
            if 'spines' in self.features:
                self.spines.request(force=True)
        elif msg == 'greyprints_rebuild':
            if 'greyprints' in self.features:
                self.grey.request()
        elif msg == 'easel_refresh':
            if 'easel' in self.features:
                self.easel.request()
        elif msg == 'refresh':  # republish everything (e.g. after the skin reloaded)
            if self.colours:
                self.browse.source = self.playing.source = None
                self.done = self.player_key = None
            if 'spines' in self.features:
                self.spines.request()
            if 'greyprints' in self.features:
                self.grey.publish_existing()
            if 'easel' in self.features:
                self.easel.publish_existing()

    # ------------------------------------------------------------------------------------------- main loop
    def run(self):
        log('started')
        set_prop(RUNNING, 'true')
        try:
            self.loop()
        finally:
            self.shutdown()
        if 'greyprints' in self.features:
            greyprints.clear()
        if 'easel' in self.features:
            easel.clear()
        set_prop(RUNNING, None)
        set_prop(ACTIVE, None)
        log('stopped')

    def shutdown(self):
        """Kodi kills a service that hasn't ended within 5 s of the stop request, and it waits for EVERY Python thread
        (daemon or not). Stop the spine worker and both fade workers; all joins share one short budget."""
        end = time.time() + 2.0
        for worker in (self.spines, self.grey, self.easel, self.browse, self.playing):
            if worker is None:
                continue
            try:
                worker.stop(end - time.time())
            except Exception as e:  # noqa: BLE001
                log('stop failed: %s' % e, xbmc.LOGWARNING)

    def loop(self):
        while not self.abortRequested():
            now = time.time()
            if now >= self.next_skin:
                self.next_skin = now + SKIN_EVERY
                self.check_enabled()
            tick = IDLE_TICK
            if self.colours:
                if self.player_dirty or now >= self.next_player:
                    self.next_player = now + PLAYER_EVERY
                    self.player_tick()
                if prop('Groove.Helper.Browse').lower() != 'off' and not cond(PAUSE_COND):
                    self.browse_tick(now)
                    tick = TICK
            if self.waitForAbort(tick):
                break

    def check_enabled(self):
        skin = xbmc.getSkinDir()
        want = feats.resolve(skin, prop(feats.OPT_IN))
        if want != self.features:
            log('features for %s: %s' % (skin, ','.join(sorted(want)) or 'none (idle)'), xbmc.LOGINFO)
            set_prop(ACTIVE, ','.join(sorted(want)))
        colours = 'colours' in want
        if colours and not self.colours:
            if self.renderer is None:
                self.renderer = Renderer(soft='softart' in want)
                self.browse = Publisher('Groove')
                self.playing = Publisher('Groove.Player')
            self.player_dirty = True
        elif self.colours and not colours:
            self.browse.clear()
            self.playing.clear()
            self.seen = self.done = self.player_key = self.player_pending = None
            self.music = False
        if colours and self.renderer.soft != ('softart' in want):
            self.renderer.set_soft('softart' in want)
            self.browse.source = self.playing.source = None  # republish without / with the soft-art files
            self.done = self.player_key = None
        spines = 'spines' in want
        if spines and 'spines' not in self.features:
            self.spines.request(delay=START_DELAY if self.skin is None else 2.0)
        elif spines and skin != self.skin and skin_is_groove():
            self.spines.republish()
        self.check_new_features(want)
        self.features, self.colours, self.enabled, self.skin = want, colours, bool(want), skin

    def check_new_features(self, want):
        """greyprints / easel (1.1.0) on and off. On: show the last complete build / list at once, then re-check
        in the background. Off: clear what was published (files stay and are reused)."""
        first = self.skin is None
        if 'greyprints' in want and 'greyprints' not in self.features:
            self.grey.publish_existing()
            self.grey.request(delay=greyprints.START_DELAY if first else 2.0)
        elif 'greyprints' not in want and 'greyprints' in self.features:
            greyprints.clear()
        if 'easel' in want and 'easel' not in self.features:
            self.easel.publish_existing()
            self.easel.request(delay=easel.START_DELAY if first else 1.0)
        elif 'easel' not in want and 'easel' in self.features:
            easel.clear()

    # ------------------------------------------------------------------------------------------- browsing
    def focused_art(self):
        cid = prop('Groove.Helper.Container')
        base = 'Container(%s).ListItem' % cid if cid.isdigit() else 'ListItem'
        keys = VIDEO_ART if info(base + '.DBType') in VIDEO_TYPES else MUSIC_ART
        for k in keys:
            v = info('%s.Art(%s)' % (base, k))
            if artload.usable(v):
                return v
        return ''

    def browse_tick(self, now):
        url = self.focused_art()
        if url != self.seen:
            self.seen, self.seen_at = url, now
            return
        if url == self.done or now - self.seen_at < REST:
            return
        self.done = url
        self.browse.publish(url, self.renderer.render(url) if url else None)

    # ------------------------------------------------------------------------------------------- playing album
    def player_tick(self):
        if self.player_dirty:
            self.player_dirty = False
            playing = self.player.isPlayingAudio()
            if not playing and self.music:
                self.music = False
                self.player_key = self.player_pending = None
                self.playing.clear()
            self.music = playing
        if not self.music:
            return
        art = ''
        for label in PLAYER_ART:
            v = info(label)
            if artload.usable(v):
                art = v
                break
        key = (info('MusicPlayer.Album'), art)  # not the artist: compilations change it every track
        if key == self.player_key:
            self.player_pending = None
        elif key == self.player_pending:  # the same new key on two polls: settled (art can lag the track)
            self.player_pending = None
            self.player_key = key
            self.playing.publish(art, self.renderer.render(art) if art else None)
        else:
            self.player_pending = key


def main():
    Service().run()
