# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LoC Downloader is a Python library and CLI tool for downloading metadata and files from the Library of Congress (loc.gov) API. It handles rate limiting, parallel downloads, and large collection processing with date faceting.

## Common Commands

### Installation
```bash
pip install -e .
```

### CLI Usage
```bash
# Download metadata
loc-downloader metadata https://www.loc.gov/item/2021667925/
loc-downloader metadata https://www.loc.gov/collections/civil-war-maps/

# Download files
loc-downloader files https://www.loc.gov/item/2021667925/
loc-downloader files https://www.loc.gov/collections/civil-war-maps/ --mimetype image/jpeg
```

## Architecture

### Core Components

1. **LocAPI** (`loc_downloader/api.py`): Main API client
   - Handles rate limiting using pyrate-limiter with separate limits for different endpoints
   - Uses tenacity for retry logic with exponential backoff
   - Supports concurrent downloads via ThreadPoolExecutor
   - Automatically handles large collections (>100k items) using date faceting

2. **Models** (`loc_downloader/models.py`): Pydantic models for API responses
   - ItemResponse: Individual item metadata and resources
   - SearchResponse: Collection search results with pagination
   - Resource: File information including URLs and metadata

3. **CLI** (`loc_downloader/cli.py`): Click-based command interface
   - Two main commands: `metadata` and `files`
   - Supports filtering by MIME type and limiting results

### Key Design Patterns

- **Rate Limiting**: Different rate limits for different endpoint types (newspapers, items, resources, collections)
- **Retry Logic**: Uses tenacity decorators for automatic retries on network errors and rate limits
- **Error Handling**: Custom exceptions (LocAPIError, RateLimitError) for API-specific errors
- **URL Parsing**: Regex-based parsing to extract item/collection IDs from loc.gov URLs
- **Concurrent Downloads**: ThreadPoolExecutor for parallel file downloads with configurable workers

### Important Implementation Details

- Rate limits are defined in `RATE_LIMITS` dict with burst and crawl rates
- Large collections use date faceting to split requests into manageable chunks
- Files are downloaded with streaming to handle large files efficiently
- Automatic filename extraction from Content-Disposition headers or URL paths