# LoC Downloader

A Python library and CLI tool for downloading metadata and files from the Library of Congress (loc.gov) API.

## Features

- Download metadata for items and collections
- Download associated digital files (with optional MIME type filtering)
- Automatic rate limiting to comply with API restrictions
- Support for large collections using date faceting
- Parallel file downloads for improved performance
- Simple CLI interface

## Installation

```bash
pip install -e .
```

## Usage

### CLI

Download metadata:
```bash
loc-downloader metadata https://www.loc.gov/item/2021667925/
loc-downloader metadata https://www.loc.gov/collections/civil-war-maps/
```

Download files:
```bash
loc-downloader files https://www.loc.gov/item/2021667925/
loc-downloader files https://www.loc.gov/collections/civil-war-maps/ --mimetype image/jpeg
```

### Python Library

```python
from loc_downloader import LocAPI

api = LocAPI()

# Download item metadata
item = api.get_item("2021667925")

# Download collection metadata
collection_items = api.get_collection_items("civil-war-maps")

# Download files
api.download_item_files("2021667925", output_dir="downloads/")
```

## License

MIT