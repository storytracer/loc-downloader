JSON/YAML for LoC.gov
=====================

Provides structured data about Library of Congress collections.

Introduction
------------

The loc.gov application programming interface (API) provides structured data about Library of Congress collections in JSON and YAML formats. Software programs routinely access the JSON/YAML API to keep the loc.gov website updated as new digital content is added to the Library's collections. For example, JSON data is used to build loc.gov pages for items (loc.gov/item), collections (loc.gov/collections/), searches (loc.gov/search/), and more.

However, in addition to being a resource for the computer applications powering the loc.gov website, the API can be used by developers, digital librarians, and researchers to directly retrieve digital collections information formatted as JSON or YAML data.

### Retrievable Information

The loc.gov JSON/YAML API provides information about the following content on the Library of Congress website:

-   **items** (books, archived websites, photos, videos, maps, manuscripts, etc.)
    1.  *Note:* not all the items you find on the website necessarily belong to a historic library collection. For example, many recordings of Library of Congress events are shared on the website. So you may find videos like [this virtual event recording](https://www.loc.gov/item/webcast-9253/) of the 2020 Newspaper Navigator Data Jam hosted by LC Labs alongside digitized historical materials.
-   **collections** (groups of items selected by subject matter experts according to a theme or other principle)
-   **images** (thumbnails and higher resolution formats)
-   **metadata** (descriptive and/or bibliographic information retrieved from library systems)
    1.  *Note:* the API does not include records from the library catalog (although items that have been digitized are retrievable). See the [MARC Open Access dataset](https://www.loc.gov/cds/products/marcDist.php) for bulk access to the catalog records up through 2014.

Access and Limitations
----------------------

The API is accessible to the public with no API key or authentication required. However, [rate limiting](https://www.loc.gov/apis/json-and-yaml/working-within-limits/#rate-limits) is enforced. Requests that exceed the rate which loc.gov can successfully accommodate will be blocked to prevent a denial of service.

There is also a [limit on how deeply a user can paginate](https://www.loc.gov/apis/json-and-yaml/working-within-limits/#deep-paging) into results ("deep paging"). Paging past the 100,000th item in a search result is not supported at this time. In some searches, responses may fail before 100,000 items. To avoid this limit, we suggest filtering results using [facets](https://www.loc.gov/apis/json-and-yaml/working-within-limits/#using-faceting).

***For more information, please read our page about [working within limits](https://www.loc.gov/apis/json-and-yaml/working-within-limits).***

Get Help
--------

Additional examples and Jupyter notebooks implementing the API are available in the Library of Congress' [data-exploration](https://github.com/LibraryOfCongress/data-exploration) GitHub repository.

If you have questions about using the API, the API's data coverage, data structure, or technical access pathways that are not answered by the documentation, please contact the Library's Digital Innovation Lab (LC Labs) team at <LC-Labs@loc.gov>.

If you have questions about a specific digital collection, please contact the Library's reference staff via the [Ask a Librarian service](https://ask.loc.gov/).