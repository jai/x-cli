"""tw — X/Twitter CLI. JSON output, unix-style."""

from __future__ import annotations

import json
import sys

import click

from . import api


def _out(data: dict | list) -> None:
    """Print JSON to stdout."""
    # If the response has a 'data' key, unwrap it for cleaner output
    if isinstance(data, dict) and "data" in data:
        payload = data["data"]
    else:
        payload = data
    click.echo(json.dumps(payload, indent=2, ensure_ascii=False))


@click.group()
@click.version_option(package_name="tw-cli")
def main():
    """tw — X/Twitter API v2 CLI."""
    pass


@main.command()
def me():
    """Show authenticated user info."""
    _out(api.get_me())


@main.command()
@click.option("--count", "-n", default=20, help="Number of tweets (max 100)")
def timeline(count):
    """Home timeline (reverse-chronological)."""
    _out(api.get_home_timeline(count))


@main.command("user-timeline")
@click.argument("handle")
@click.option("--count", "-n", default=20, help="Number of tweets (max 100)")
def user_timeline(handle, count):
    """A user's tweets. HANDLE is @username."""
    _out(api.get_user_timeline(handle, count))


@main.command()
@click.option("--count", "-n", default=20, help="Number of tweets (max 100)")
def likes(count):
    """Your liked tweets."""
    _out(api.get_likes(count))


@main.command()
@click.argument("query")
@click.option("--count", "-n", default=20, help="Number of results (10-100)")
@click.option("--sort", "-s", type=click.Choice(["recency", "relevancy"]), default="recency", help="Sort order")
def search(query, count, sort):
    """Search recent tweets. QUERY supports operators like from:user, #hashtag."""
    _out(api.search_recent(query, count, sort))


@main.command()
@click.argument("handle")
def user(handle):
    """Look up a user profile. HANDLE is @username."""
    _out(api.resolve_user(handle))


@main.command()
@click.argument("tweet_id")
def tweet(tweet_id):
    """Get a single tweet by ID."""
    result = api.get_tweet(tweet_id)
    _out(result)


@main.command()
@click.argument("handle")
@click.option("--count", "-n", default=100, help="Number of followers (max 100)")
def followers(handle, count):
    """List a user's followers."""
    _out(api.get_followers(handle, count))


@main.command()
@click.argument("handle")
@click.option("--count", "-n", default=100, help="Number of following (max 100)")
def following(handle, count):
    """List who a user follows."""
    _out(api.get_following(handle, count))


@main.command()
@click.option("--count", "-n", default=20, help="Number of mentions (max 100)")
def mentions(count):
    """Your recent mentions."""
    _out(api.get_mentions(count))


if __name__ == "__main__":
    main()
