# Copyright Amethyst Reese
# Licensed under the MIT license

import logging
from dataclasses import field
from datetime import datetime, UTC
from pathlib import Path

import click
import platformdirs
from atproto import Client
from rich import print
from serde import serde
from serde.json import from_json, to_json
from typing_extensions import Self

LOG = logging.getLogger(__name__)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def cache_path() -> Path:
    return platformdirs.user_data_path("bluepost", "amethyst.cat") / "bluepost.db"


@serde
class Cache:
    dids: dict[str, str] = field(default_factory=dict)
    markers: dict[str, datetime] = field(default_factory=dict)

    @classmethod
    def load(cls) -> Self:
        path = cache_path()
        if path.is_file():
            LOG.debug("Loading cache")
            return from_json(Cache, path.read_bytes())
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


def run(username: str, password: str, target: str) -> None:
    cache = Cache.load()

    try:
        LOG.info("Initializing client")
        client = Client()
        profile = client.login(username, password)
        cache.dids[username] = profile.did
        cache.save()

        if not (did := cache.dids.get(target)):
            LOG.debug("Resolving handle %s", target)
            response = client.resolve_handle(target)
            did = response.did
            cache.dids[target] = did
            cache.save()
        LOG.info(f"Target handle %r -> %r", target, did)

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

                cache.marker = timestamp
                cache.save()

    finally:
        LOG.debug("Final cache object:\n%r", cache)
        cache.save()
