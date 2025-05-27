Item and Resource Responses
===========================

API responses to item and resource queries

JSON Response Objects
---------------------

### Item and Resource Responses

The API will respond to a query to the item or resource endpoint with a JSON response object containing the following attributes:

```

{
    "views": Object,
    "timestamp": Number,
    "locations": Array,
    "fulltext_service": String,
    "next_issue": String,
    "newspaper_holdings_url": String,
    "title_url": String,
    "page": Array,
    "pagination": Object,
    "resource": Object,
    "cite_this": Object,
    "calendar_url": String,
    "previous_issue": String,
    "segments": List,
    "related_items": List,
    "word_coordinates_query": Object,
    "more_like_this": List,
    "articles_and_essays": List,
    "traditional_knowledge_labels": List,
    "item": Object,
    "word_coordinates_pages": Object,
    "type": String,
    "options": Object,
    "resources": List
}

```

Copy

Of these many attributes in the response object returned by the item endpoint, we will focus on two: the item attribute of the response, and the resources attribute of the response.

#### Description of the Item Attribute Object

Of these elements the one of most interest is `item`. The `item` object has the following structure:

```

{
    "place_of_publication": String,
    "source_collection": Array,
    "display_offsite": Boolean,
    "contributors": Array,
    "location_county": Array,
    "access_restricted": Boolean,
    "site": Array,
    "original_format": Array,
    "partof_title": Array,
    "date": String,
    "item_type": String,
    "url": String,
    "subject_headings": Array,
    "newspaper_title": Array,
    "created_published": Array,
    "extract_urls": Array,
    "partof_division": Array,
    "contents": Array,
    "subject": Array,
    "index": Number,
    "digital_id": Array,
    "call_number": Array,
    "group": Array,
    "score": Number,
    "location_country": Array,
    "title": String,
    "numeric_shelf_id": Number,
    "description": Array,
    "related_items": Array,
    "id": String,
    "online_format": Array,
    "subjects": Array,
    "location": Array,
    "_version_": Number,
    "mime_type": Array,
    "type": Array,
    "other_formats": Array,
    "library_of_congress_control_number": String,
    "rights_advisory": Array,
    "medium": String,
    "reproduction_number": Array,
    "repository": Array,
    "format": Array,
    "partof": Array,
    "timestamp": String,
    "date_issued": String,
    "reel_numbers": Array,
    "campaigns": Array,
    "raw_lccn": String,
    "number_edition": Array,
    "extract_timestamp": String,
    "genre": Array,
    "number": Array,
    "dates_of_publication": String,
    "partof_collection": Array,
    "other_title": Array,
    "hassegments": Boolean,
    "dates": Array,
    "composite_location": Array,
    "number_lccn": Array,
    "language": Array,
    "rights": Array,
    "locations": Array,
    "notes": Array,
    "shelf_id": String,
    "batch": Array,
    "summary": Array,
    "digitized": Boolean,
    "publication_frequency": Array,
    "resources": Array,
    "aka": Array,
    "contributor_names": Array,
    "image_url": Array,
    "access_advisory": Array
}

```

Copy

This table provides a description of the important fields in the item attribute object accessed using `at=item` from an item endpoint. Fields that are included in the item summary in the search `results` attribute are indicated. Fields that are only used for the web site are not described.

| **Field** | **Description** | **Type** | **Example** |
| --- | --- | --- | --- |
| access_restricted | Full access to the item is limited to onsite users. Access restricted items maybe provide a lower resolution thumbnail to offsite users, or only the bibliographical description.

*Facetable* | boolean | false |
| aka | Alternative identifiers for documents (e.g., shortcut urls) | array | [ "https://www.loc.gov/item/sn85033000/1911-08-10/ed-1/", "https://www.loc.gov/resource/sn85033000/1911-08-10/ed-1/" ] |
| contributors | List of persons or institutions or organizations who contributed to the creation of the item. Each item consists of a dictionary with the key being the name of the contributor and the value being a faceting URL for items associated with that contributor.

*Facetable* | array | [ { "national archives and records administration": "https://dev.loc.gov/search/?fa=contributor:national+archives+and+records+administration&fo=json" } ] |
| coordinates | A text representation of geographical coordinates; typically drawn from a MARC field. This attribute is not universally implemented. | string | "2002-08-08" "1910" |
| date | Date of item creation. Could be a year or YYYY-MM-DD. Items are sortable by this date.

*Sortable* | string | "2002-08-08" "1910" |
| dates | List of dates related to the item. In ISO 8601 format, UTC. Items are facetable by these dates.

*Facetable* | array | ["2001-01-01T00:00:00Z", "2001-10-30T00:00:00Z", "2001-12-15T00:00:00Z", "2002-01-01T00:00:00Z"] |
| description | Often includes a short, summary description of the original physical item written to accompany the item in a list of search results. | array | [ "Correspondence. Typed letter regarding Scandinavian production rights to \"Kiss Me. Kate\" Courtesy of Cole Porter Trust (Copyright Notice)." ] [ "1 photographic print. | Two Pueblo Indian women posed standing, full-length, New Mexico." ] |
| digitized | Whether this item has been digitized.

*Facetable* | boolean | true |
| extract_timestamp | Timestamp of most recent ETL (extract-transform-load) process that produced this item. In ISO 8601 format, UTC. This is primarly for use by Library of Congress technical staff. | string | "2020-04-23T19:42:01.854Z" |
| group | The ETL processes that produced this item. For many items, different attributes are contributed by different ETL processes. This is primarly for use by Library of Congress technical staff. | array | ["ndnp/scu", "university-of-south-carolina-columbia-sc-awardee"] |
| hassegments | Whether this item has segmented data (pages, bounding boxes of images, audio segmentation, etc.) in the index. | boolean | true |
| id | HTTP version of the URL for the item, including its identifier. Always appears.\
Note: for historical reasons, the ID follows the pattern of an HTTP URL, not an HTTPS URL, event though loc.gov now supports only HTTPS. | string | "https://www.loc.gov/item/2017645977/" |
| image_url | URLs for images in various sizes, if available. If the item is not something that has an image (e.g. it's a book that's not digitized or an exhibit), the URL for the image might be for an icon image file. | array | ["//cdn.loc.gov/service/pnp/bbc/\
0000/0000/0004f_150px.jpg",] |
| item | The item attribute of the item response object provides subfields with information for display of the item on the loc.gov website. These subfields will vary from item type to item type, and are neither facetable nor sortable. A more thorough discussion is provided below under [Item Field Object](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#item_field_object). | Object | `"call_number": [ "" ], "contributor_names": [ "University of South Carolina" ], "created_published": [ "Lancaster, S.C., July 11, 1900" ], "date_issued": "1900-07-11", "digitized_label": "Present", "genre": [ "Newspapers" ],` |
| language | Languages associated with the item.

*Facetable* | array | ["english", "spanish"] |
| location | Place(s) related to the item. These are extracted from subject headings and other metadata, so there may be duplicates. In some collections, there may be hierarchical location attributes as well, such as *location_city*, *location_country*, but these are not universally implemented.

*Facetable* | array | ["earth (planet)", "planet", "earth"] |
| mime_type | Formats available for download | array | ["image/gif", "video/mov", "video/mpeg", "application/x-video", "image/jpeg"] |
| number | Numbers associated with the item, such as OCLC number, shelf number, ISSN, deprecated idenfitier, etc. | array | ["2018688580"] |
| online_format | Format available via the website.

*Facetable* | array | ["web page"], ["image","pdf"] |
| original_format | The kind of object being described (not the digitized version). If the record is for an entire collection, that is included here.

*Facetable* | array | [ "map" ], [ "photo, print, drawing", "collection"] |
| other_title | Alternative language titles and other alternative titles | array | ["Egypt Eyes"] |
| partof | Collections, divisions, units in the Library of Congress, or any of a number of less formal groupings and subgroupings used for organizing content.

*Facetable* | array | ["prints and photographs division", "lot 10526", "catalog"] |
| shelf_id | The primary sorting field of the item record. This field really only has meaning within loc.gov, and is not a canonical identifier.

*Sortable* | string | "MSS 44693: Reel 060" |
| subjects |

List of subjects. These are separated elements of the Library of Congress Subject Headings (LCSH). Geography is not shown here, but rather under the location element.

All elements separated by a double dash in an LCSH are tokenized. For example, an item with the subject heading "Women -- Afghanistan -- Social conditions" will have ["social conditions", "women's rights"] in the subject element and "afghanistan" in the location element.

For the full subject headings, request the JSON for the /item view

facetable

 | array | ["public interest/advocacy", "history", "september 11 terrorist attacks" ] |
| title | Title of the item.

*Sortable* | string | "Women Taxpayers; Women Voters" |
| url | URL on the loc.gov website. If the items is something in the library catalog, the URL will start with lccn.loc.gov. | string | https://www.loc.gov/item/2017711647/\
//lccn.loc.gov/08030295 |

#### Item Field Object

One of the attributes of the Item Response Object is an "item" field object, which provides a variety of fields that can be used to describe the item. The fields in this object will differ from collection to collection, depending upon the practices of the collecting division.

These fields are used by the loc.gov website to provide additional bibliographical data for the item, or to simplify display or other aspects of presentation. In some cases, the fields replicate or summarize the fields in the item response object, while in other cases they provide information specific to the collection or format of the item. Because this field varies in contents and structure, it is best not to depend upon the existence, datatype, or values of the fields in this object. If you have questions about the meaning of a particular subfield in the item field object, please contact [Ask a Librarian](https://ask.loc.gov/#s-la-box-83050-container-tab1), who will be able to route your question to the appropriate people.

-   access_advisory
-   call_number
-   contributors
-   control_number
-   created
-   created_published
-   created_published_date
-   creator
-   creators
-   contributor_names
-   date
-   digital_id
-   display_offsite
-   format
-   formats
-   genre
-   id
-   language
-   link
-   location
-   marc
-   medium
-   medium_brief
-   mediums
-   modified
-   number_former_id
-   notes
-   other_control_numbers
-   other_title
-   place
-   raw_collections
-   repository
-   reproduction_number
-   resource_links
-   restriction
-   rights_advisory
-   rights_information
-   service_low
-   service_medium
-   stmt_of_responsibility
-   sort_date
-   source_created
-   source_collection
-   source_modified
-   subject_headings
-   subjects
-   summary
-   thumb_gallery
-   title

#### Description of the Resource Attribute Object

    `"files": [
        [
            {
                "captions": Array, [image]
                "duration" Integer, [audio or video]
                "format": Object, [iiif or audio or video]
                "height": Integer, [image or video]
                "info": Url, [iiif]
                "levels": Integer, [maps, manuscripts]
                "mimetype": String,
                "other_name": String, [book?]
                "profile": Array, [iiif]
                "protocol": Uri, [iiif ?]
                "size": Integer, [image, manuscript, video]
                "streams": Array, [audio or video]
                "tiles": Array, [audio at least]
                "type": String,
                "url": Url, [usually the URL of the file, but for web archives, the url captured]
                "use": String, [newspaper?]
                "width": Integer [image or video]
              },
        ]
    ],
    "audio": Url, [audio]
    "background": Url, [video?]
    "begin": String [Time], [audio or video]
    "caption": String, [image, audio, or video]
    "capture_range": Array {of dates}, [web archives]
    "djvu_text_file": Url, [book]
    "download_restricted": Boolean, [audio or video]
    "duration": Integer, [audio or video]
    "end": String [Time], [audio or video]
    "fulltext_derivative": Url, [book]
    "fulltext_file": Url, [book]
    "height": Integer, [image or video]
    "id": String,
    "info": Url, [iiif]
    "image": Url,
    "paprika_resource_path": String, [book]
    "pdf": Url, [book]
    "representative_index": Integer, [book]
    "type": String,
    "url": Url,
    "uuid": String, [audio or video]
    "version": Integer, [book]
    "video_stream": Url, [video]
    "video": Url, [video]
    "width": Integer, [image or video]
    "word_coordinates": Url, [OCRed book or newspaper]`

Copy

| **Field** | **Description** | **Type** | **Example** | **Context** |
| --- | --- | --- | --- | --- |
| files | A list of files for digital representations of the resource. | Array | `files": [ [ { "aspectRation": "4:3", "autoPlay": false, "canDownload": true, "derivatives": [ { "derivativeUrl": "https://tile.loc.gov/storage-services/[...]_02.mp3" } ], "detailUrl": "https://www.loc.gov/item/jukebox-253530", "download": "https://tile.loc.gov/streaming-services/iiif/[...]/default.mp3", "duration": 229, "filename": "https://tile.loc.gov/storage-services/service/[...]_02.mp3", "mediaType": "A", "metadata": [ "Marriage of Figaro : Overture", "Band" ], "mimetype": "audio/mpeg", "poster": null, "rights_restricted": true, "shortName": "Marriage of Figaro : Overture", "thumbnail_url": "https://tile.loc.gov/image-services/iiif/[...]/default.jpg" } ] ],`\
## (URLs have been shortened.) | Images, Manuscripts, Maps, Audio, Videos, etc. |