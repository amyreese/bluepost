# Copyright Amethyst Reese
# Licensed under the MIT license

from __future__ import annotations

import logging
import signal
import threading
from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path
from time import monotonic
from types import FrameType

import platformdirs
from atproto import Client
from serde import serde
from serde.json import from_json, to_json

LOG = logging.getLogger(__name__)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def cache_path() -> Path:
    return platformdirs.user_data_path("bluepost", "amethyst.cat") / "bluepost.db"


@serde
class Cache:
    dids: dict[str, str] = field(default_factory=dict)
    markers: dict[str, datetime] = field(default_factory=dict)

    @classmethod
    def load(cls) -> Cache:
        path = cache_path()
        if path.is_file():
            LOG.debug("Loading cache")
            return from_json(Cache, path.read_text())
        else:
            LOG.debug("No cache found")
            return Cache()

    def save(self) -> Path:
        path = cache_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        LOG.debug("Saving cache")
        path.write_text(to_json(self))
        return path

    @classmethod
    def clear(cls) -> None:
        LOG.debug("Clearing cache")
        cache = Cache()
        cache.save()


@dataclass
class Options:
    dry_run: bool


@dataclass
class Bluepost:
    client: Client
    cache: Cache

    @classmethod
    def init(cls, username: str, password: str) -> Bluepost:
        cache = Cache.load()

        LOG.info("Initializing client")
        client = Client()
        profile = client.login(username, password)
        cache.dids[username] = profile.did
        cache.save()

        return Bluepost(client=client, cache=cache)

    def repost(self, target: str) -> None:
        client = self.client
        cache = self.cache

        if not (did := cache.dids.get(target)):
            LOG.debug("Resolving handle %s", target)
            response = client.resolve_handle(target)
            did = response.did
            assert did is not None, f"Unresolvable handle {target}"
            self.cache.dids[target] = did
            cache.save()
        LOG.info("Target handle %r -> %r", target, did)

        threshold = cache.markers.setdefault(target, datetime.now(UTC))
        data = client.get_author_feed(did, filter="posts_and_author_threads", limit=5)
        for item in reversed(data.feed):
            post = item.post

            text = post.record.text
            timestamp = datetime.fromisoformat(post.record.created_at)
            if timestamp > threshold and not text.startswith("@"):
                LOG.info(
                    "Reposting: %s @%s: %s ...",
                    timestamp,
                    post.author.handle,
                    post.record.text[:50],
                )
                client.repost(post.uri, post.cid)

                cache.markers[target] = timestamp
                cache.save()

    def run_once(self, target: str) -> None:
        try:
            self.repost(target)
        finally:
            LOG.debug("Final cache object: %r", self.cache)
            self.cache.save()

    def run_forever(self, target: str, *, interval: int) -> None:
        interval = interval * 60
        running = True
        event = threading.Event()

        def stop(sig: int, frame: FrameType | None) -> None:
            nonlocal running
            LOG.info("%s -- Stopping...", signal.strsignal(sig))
            running = False
            event.set()

        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)

        before = monotonic()
        error_count = 0
        while running:
            try:
                self.repost(target)

            except Exception:
                error_count += 1
                LOG.exception("Exception #%s", error_count)

                if error_count > 5:
                    LOG.error("Too many continuous errors, exiting")
                    raise

            else:
                error_count = 0

            finally:
                after = monotonic()
                before += interval
                wait = before - after
                LOG.debug("Waiting %.1f seconds...", wait)
                event.wait(timeout=wait)

        LOG.debug("Final cache object: %r", self.cache)
        self.cache.save()
