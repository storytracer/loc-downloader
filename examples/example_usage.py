#!/usr/bin/env python3

from loc_downloader import LocAPI

def main():
    api = LocAPI()
    
    # Example 1: Get item metadata
    print("Example 1: Fetching item metadata")
    item = api.get_item("2021667925")
    print(f"Item title: {item.item.title}")
    print(f"Number of resources: {len(item.resources)}")
    print()
    
    # Example 2: Get collection items (limited to 10)
    print("Example 2: Fetching collection items")
    items = api.get_collection_items("civil-war-maps", limit=10)
    print(f"Fetched {len(items)} items from collection")
    for i, item in enumerate(items[:3]):
        print(f"  {i+1}. {item.title}")
    print()
    
    # Example 3: Download item files
    print("Example 3: Downloading files from an item")
    downloaded = api.download_item_files("2021667925", "downloads/item_example")
    print(f"Downloaded {len(downloaded)} files")
    print()
    
    # Example 4: Save metadata
    print("Example 4: Saving metadata to JSON")
    api.save_metadata(item, "metadata/item_metadata.json")
    api.save_metadata(items, "metadata/collection_metadata.json")
    print("Metadata saved successfully")


if __name__ == "__main__":
    main()