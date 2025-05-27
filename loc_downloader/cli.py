import logging
import sys
from pathlib import Path
from typing import Optional

import click

from .api import LocAPI
from .exceptions import LocAPIError


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option()
def main():
    pass


@main.command()
@click.argument("url")
@click.option("--output", "-o", help="Output file path")
@click.option("--limit", "-l", type=int, help="Maximum number of items to fetch (collections only)")
def metadata(url: str, output: Optional[str], limit: Optional[int]):
    api = LocAPI()
    
    try:
        url_type, identifier = api.parse_url(url)
        
        if url_type == "item":
            click.echo(f"Fetching metadata for item: {identifier}")
            data = api.get_item(identifier)
            
            # Use LCCN for filename if available and no output specified
            if not output:
                if data.item.number_lccn:
                    output = f"{data.item.number_lccn[0]}.json"
                else:
                    output = f"{identifier}.json"
            
            api.save_metadata(data, output)
            click.echo(f"Metadata saved to: {output}")
            
        elif url_type == "collection":
            click.echo(f"Fetching metadata for collection: {identifier}")
            items = api.get_collection_items(identifier, limit=limit)
            
            # Use collection slug for filename if no output specified
            if not output:
                output = f"{identifier}.json"
            
            api.save_metadata(items, output)
            click.echo(f"Metadata for {len(items)} items saved to: {output}")
            
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except LocAPIError as e:
        click.echo(f"API Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error")
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("url")
@click.option("--output-dir", "-o", help="Output directory")
@click.option("--mimetype", "-m", help="Filter files by MIME type (e.g., image/jpeg, application/pdf)")
@click.option("--limit", "-l", type=int, help="Maximum number of items to process (collections only)")
@click.option("--workers", "-w", default=10, type=int, help="Number of parallel download workers")
def files(url: str, output_dir: Optional[str], mimetype: Optional[str], limit: Optional[int], workers: int):
    api = LocAPI(max_workers=workers)
    
    try:
        url_type, identifier = api.parse_url(url)
        
        if url_type == "item":
            click.echo(f"Downloading files for item: {identifier}")
            
            # Get item to check for LCCN
            if not output_dir:
                item_data = api.get_item(identifier)
                if item_data.item.number_lccn:
                    output_dir = item_data.item.number_lccn[0]
                else:
                    output_dir = identifier
            
            downloaded = api.download_item_files(identifier, output_dir, mimetype=mimetype)
            click.echo(f"Downloaded {len(downloaded)} files to: {output_dir}")
            
        elif url_type == "collection":
            click.echo(f"Downloading files for collection: {identifier}")
            if mimetype:
                click.echo(f"Filtering by MIME type: {mimetype}")
            
            # Use collection slug for output directory if not specified
            if not output_dir:
                output_dir = identifier
            
            downloaded = api.download_collection_files(identifier, output_dir, 
                                                     limit=limit, mimetype=mimetype)
            click.echo(f"Downloaded {len(downloaded)} files to: {output_dir}")
            
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except LocAPIError as e:
        click.echo(f"API Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error")
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()