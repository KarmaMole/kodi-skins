# KarmaMole Skin Helper (script.karmamole.helper)
# Copyright (C) 2026 Omar Kamel
# SPDX-License-Identifier: GPL-2.0-or-later
"""A background job thread with Kodi-safe stop paths (used by the 1.1.0 features; spines.py keeps its own 1.0.0 loop).

- The thread is created by the first request, so a skin that never asks for the feature never gets it.
- Requests are debounced: request(delay) moves the start to max(pending start, now + delay).
- Every wait is sliced into 0.1 s steps that check Kodi's abort and our own stop flag, so stop() returns in about
  0.1 s plus whatever single step (one image render, one JSON-RPC call) is running.
- Kodi waits for every Python thread when it stops a service and kills it after 5 s (LESSONS Helper add-ons).
"""
import threading
import time

import xbmc

from .common import cond, log

BUSY_VIDEO = 'Player.HasVideo | Library.IsScanningVideo | Library.IsScanningMusic'


class Worker(object):
    name = 'job'
    feature = ''
    every = 0.0        # > 0: re-run this many seconds after the last run while the feature stays on
    idle_step = 5.0    # how often a job waiting for video / a scan to end looks again

    def __init__(self, monitor):
        self.monitor = monitor
        self.event = threading.Event()
        self.stopping = threading.Event()
        self.force = False
        self.not_before = 0.0
        self.last_run = 0.0
        self.thread = None

    # ------------------------------------------------------------------------------------------- control
    def _start(self):
        if self.thread is None and not self.stopping.is_set():
            self.thread = threading.Thread(target=self._run, name='kmhelper.' + self.name)
            self.thread.daemon = True  # Kodi still waits for daemon threads: stop() ends it
            self.thread.start()

    def request(self, delay=0.0, force=False):
        self.not_before = max(self.not_before, time.time() + delay)
        self.force = self.force or force
        self._start()
        self.event.set()

    def stop(self, timeout=1.0):
        self.stopping.set()
        self.event.set()
        if self.thread is not None and self.thread is not threading.current_thread():
            self.thread.join(max(0.0, timeout))

    def wanted(self):
        """The running skin still has this feature (it can switch away while a job waits or runs)."""
        return self.feature in getattr(self.monitor, 'features', ())

    def aborted(self):
        return self.stopping.is_set() or self.monitor.abortRequested() or not self.wanted()

    def wait(self, seconds):
        """Sleep in short slices; True as soon as we must stop (Kodi exit, stop(), or the feature turned off)."""
        end = time.time() + seconds
        while True:
            if self.aborted():
                return True
            left = end - time.time()
            if left <= 0:
                return False
            if self.monitor.waitForAbort(min(0.1, left)):
                return True

    def wait_idle(self, busy=BUSY_VIDEO):
        """Wait until no video plays and no scan runs. True when we must stop instead."""
        while cond(busy):
            if self.wait(self.idle_step):
                return True
        return self.aborted()

    # ------------------------------------------------------------------------------------------- loop
    def _run(self):
        while not (self.stopping.is_set() or self.monitor.abortRequested()):
            if not self.event.wait(0.25):
                if self.every and self.last_run and self.wanted() and time.time() - self.last_run >= self.every:
                    self.request()
                continue
            if self.stopping.is_set() or self.monitor.abortRequested():
                return
            while time.time() < self.not_before:  # a request during the wait may push not_before later
                left = self.not_before - time.time()
                if self.monitor.waitForAbort(min(0.1, max(0.0, left))) or self.stopping.is_set():
                    return
            self.event.clear()
            force, self.force = self.force, False
            if not self.wanted():
                continue  # the skin switched away (or opted out) while the request waited
            self.last_run = time.time()
            try:
                self.work(force)
            except Exception as e:  # noqa: BLE001
                log('%s failed: %s' % (self.name, e), xbmc.LOGERROR)
            self.last_run = time.time()

    def work(self, force):
        raise NotImplementedError
