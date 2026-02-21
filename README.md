# tw — X/Twitter CLI

A minimal, unix-style CLI for the X (Twitter) API v2. OAuth 1.0a user context, JSON output, designed for scripting and AI agents.

## Install

```bash
pip install -e .
# or
pip install .
```

## Credentials

Credentials are read from environment variables. You can source them from 1Password:

```bash
# Manual
export TW_CONSUMER_KEY="..."
export TW_CONSUMER_SECRET="..."
export TW_ACCESS_TOKEN="..."
export TW_ACCESS_TOKEN_SECRET="..."

# Or via 1Password CLI (recommended)
eval $(tw auth op --item "X.com API (govindani)" --vault "Local AI Agent")
```

## Usage

```bash
tw me                              # Authenticated user info
tw timeline [--count 20]           # Home timeline (reverse-chronological)
tw user-timeline @handle [--count 20]  # User's tweets
tw likes [--count 20]              # Your liked tweets
tw search "query" [--count 20]     # Search recent tweets
tw user @handle                    # User profile lookup
tw tweet <id>                      # Single tweet details
tw followers @handle [--count 100] # User's followers
tw following @handle [--count 100] # Who a user follows
```

All commands output JSON to stdout. Pipe to `jq` for formatting:

```bash
tw timeline --count 5 | jq '.[].text'
tw search "OpenAI" | jq '.[] | {text, author_id, created_at}'
```

## API Tier & Limits

This tool uses **X API v2** with **OAuth 1.0a User Context**. What works depends on your API tier:

| Endpoint | Free | Basic ($200/mo) | Pro ($5k/mo) |
|----------|------|-----------------|--------------|
| User lookup | ✅ | ✅ | ✅ |
| User timeline | ❌ | ✅ | ✅ |
| Home timeline | ❌ | ✅ | ✅ |
| Search (recent) | ❌ | ✅ | ✅ |
| Likes | ❌ | ✅ | ✅ |
| Bookmarks | ❌* | ❌* | ❌* |
| Post tweet | ✅ (limited) | ✅ | ✅ |

*\*Bookmarks require OAuth 2.0 User Context with PKCE — not supported by OAuth 1.0a. See [Bookmarks](#bookmarks) below.*

## Bookmarks

The bookmarks endpoint (`GET /2/users/:id/bookmarks`) **requires OAuth 2.0 Authorization Code Flow with PKCE**. OAuth 1.0a is explicitly rejected.

To add bookmark support:
1. Enable OAuth 2.0 in the X Developer Portal for your app
2. Get a Client ID + Client Secret
3. Run `tw auth oauth2` to complete the PKCE flow (opens browser)
4. Token auto-refreshes (stored in `~/.config/tw/oauth2_token.json`)

This is tracked in [#1](../../issues/1).

## Why This Exists — Existing Tool Survey

Before building `tw`, we evaluated every existing X/Twitter CLI tool we could find. None were viable:

| Tool | Language | Status | Why Not |
|------|----------|--------|---------|
| **twurl** (Twitter official) | Ruby | Dead (last updated 2020) | v1.1 API only, Twitter themselves abandoned it |
| **sferik/t** | Ruby | Dead | v1.1 only, hasn't tracked v2 API migration |
| **twikit** | Python | Active but fragile | Cookie-based scraper, not API — breaks on auth changes, no official API support |
| **tweepy** | Python | Active (library) | Library, not CLI — you'd still need to build the CLI layer on top |
| **python-twitter-v2** | Python | Stale | Library only, minimal maintenance |
| **twitter-api-v2 (npm)** | Node.js | Active (library) | Library, not CLI |
| Various MCP servers | Mixed | Exist | We use CLIs, not MCP servers. Also most wrap v1.1 or are cookie scrapers |

**tl;dr**: Every existing CLI is dead or targets the deprecated v1.1 API. The v2 API has good Python libraries but no proper CLI. So we built one.

## Architecture

- **Language**: Python 3.10+
- **Auth**: `requests-oauthlib` for OAuth 1.0a
- **CLI**: `click` for subcommands
- **Output**: JSON to stdout, errors to stderr
- **Config**: Environment variables (12-factor)

## License

MIT
