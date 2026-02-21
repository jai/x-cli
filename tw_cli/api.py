"""X API v2 client — thin wrapper around requests-oauthlib."""

from __future__ import annotations

import os
import sys
from typing import Any

from requests_oauthlib import OAuth1Session

BASE = "https://api.x.com/2"

# Tweet fields to request by default
TWEET_FIELDS = "id,text,created_at,author_id,conversation_id,public_metrics,referenced_tweets"
USER_FIELDS = "id,name,username,description,public_metrics,profile_image_url,created_at,verified"


def _get_env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        print(f"error: missing env var {name}", file=sys.stderr)
        sys.exit(1)
    return val


def client() -> OAuth1Session:
    """Build an OAuth1Session from env vars."""
    return OAuth1Session(
        client_key=_get_env("TW_CONSUMER_KEY"),
        client_secret=_get_env("TW_CONSUMER_SECRET"),
        resource_owner_key=_get_env("TW_ACCESS_TOKEN"),
        resource_owner_secret=_get_env("TW_ACCESS_TOKEN_SECRET"),
    )


def _get(path: str, params: dict[str, Any] | None = None) -> dict:
    """GET request to X API v2. Returns parsed JSON or exits on error."""
    sess = client()
    url = f"{BASE}/{path.lstrip('/')}"
    resp = sess.get(url, params=params or {})
    if resp.status_code != 200:
        err = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"status": resp.status_code, "text": resp.text[:500]}
        print(f"error: X API returned {resp.status_code}", file=sys.stderr)
        import json
        print(json.dumps(err, indent=2), file=sys.stderr)
        sys.exit(1)
    return resp.json()


# ── Public helpers ──────────────────────────────────────────────


def get_me() -> dict:
    return _get("users/me", {"user.fields": USER_FIELDS})


def resolve_user(handle: str) -> dict:
    """Resolve @handle (with or without @) to user data."""
    handle = handle.lstrip("@")
    return _get(f"users/by/username/{handle}", {"user.fields": USER_FIELDS})


def get_user_id(handle: str) -> str:
    data = resolve_user(handle)
    return data["data"]["id"]


def get_my_id() -> str:
    return get_me()["data"]["id"]


def get_home_timeline(count: int = 20) -> dict:
    uid = get_my_id()
    return _get(
        f"users/{uid}/timelines/reverse_chronological",
        {"max_results": max(1, min(count, 100)), "tweet.fields": TWEET_FIELDS},
    )


def get_user_timeline(handle: str, count: int = 20) -> dict:
    uid = get_user_id(handle)
    return _get(
        f"users/{uid}/tweets",
        {"max_results": max(5, min(count, 100)), "tweet.fields": TWEET_FIELDS},
    )


def get_likes(count: int = 20) -> dict:
    uid = get_my_id()
    return _get(
        f"users/{uid}/liked_tweets",
        {"max_results": max(5, min(count, 100)), "tweet.fields": TWEET_FIELDS},
    )


def search_recent(query: str, count: int = 20, sort: str = "recency") -> dict:
    return _get(
        "tweets/search/recent",
        {
            "query": query,
            "max_results": max(10, min(count, 100)),
            "sort_order": sort,
            "tweet.fields": TWEET_FIELDS,
        },
    )


def get_tweet(tweet_id: str) -> dict:
    return _get(
        f"tweets/{tweet_id}",
        {"tweet.fields": TWEET_FIELDS, "expansions": "author_id", "user.fields": USER_FIELDS},
    )


def get_followers(handle: str, count: int = 100) -> dict:
    uid = get_user_id(handle)
    return _get(
        f"users/{uid}/followers",
        {"max_results": min(count, 100), "user.fields": USER_FIELDS},
    )


def get_following(handle: str, count: int = 100) -> dict:
    uid = get_user_id(handle)
    return _get(
        f"users/{uid}/following",
        {"max_results": min(count, 100), "user.fields": USER_FIELDS},
    )


def get_mentions(count: int = 20) -> dict:
    uid = get_my_id()
    return _get(
        f"users/{uid}/mentions",
        {"max_results": max(5, min(count, 100)), "tweet.fields": TWEET_FIELDS},
    )
