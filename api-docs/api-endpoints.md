API Endpoints
=============

Selecting an API endpoint to query

Endpoints
---------

The first step in building an API query is choosing an endpoint. There are several url endpoints for resources on loc.gov. Each of these is structured as a distinct response type with certain attributes, depending upon the endpoint's role in the site. Three endpoint types are particularly of interest to API users hoping to work with the digital collections: search result, item, and resource.

### "Search Result" Endpoints

Most data explorations with the loc.gov API will begin with a search endpoint. Endpoints of this type provide summarized data about multiple collection items in response to query terms. In addition to the basic `search` endpoint, which can be narrowed using query terms and facets, there are `collections` endpoints and `format` endpoints which provide the same results but focused on a specific collection or online item format. All of these endpoints can be broadly categorized as search result endpoints because they have the same response structure: a results element with a list of items.

#### Response Attributes

All search result endpoints share the same attributes. Some of the most useful attributes include:

```

 {
    [...],
    "facets": {},
    "pagination": {},
    "results": [{[item summary]},{[item summary]},],
    [...]
}

```

Copy

1.  **Facets** are terms used to filter results (fa=). Results can be filtered on facets by using the [`fa` parameter](https://www.loc.gov/apis/json-and-yaml/requests/parameters/#facet-parameter)
2.  The **pagination** attribute (sp=, c=) provides the number of items in the total result, the number of items per page, and the current page number, as described in the [Pagination Attribute](https://www.loc.gov/apis/json-and-yaml/responses/search-results/#pagination-attribute) documentation on the *Understanding API Responses* page. This information can be used with the [`c` parameter](https://www.loc.gov/apis/json-and-yaml/requests/parameters/#count-parameter) and the [`sp` parameter](https://www.loc.gov/apis/json-and-yaml/requests/parameters/#page-parameter).
3.  The **results** attribute (at=results) provides a list of the collection items that are responsive to the search query, with a summary of the bibliographic data on each item, as described in the [Results Attribute](https://www.loc.gov/apis/json-and-yaml/responses/search-results/#results-attribute) documentation on the *Understanding API Reponses* page. The `id` attribute of the results attribute can be used to retrieve more detailed bibliographic data using the [Item Endpoint](https://www.loc.gov/apis/json-and-yaml/requests/endpoints/#item-endpoint).

#### /search/

The `/search` endpoint searches everything on the www.loc.gov website. This includes items in the collection, legislation, web pages, blog posts, events, and press releases. To use this endpoint one must include the `q=search term` query parameter in the query string.

Example: <https://www.loc.gov/search/?q=baseball&fo=json>

Some subsites and other resources have not been migrated to the API, so the individual pages for some search results must be accessed using traditional text crawling techniques.

Accessing Attributes

-   */search/?q=baseball&fo=json&at=pagination*
-   */search/?q=baseball&fo=json&at=results*
-   */search/?q=baseball&fo=json&at=results.0*
-   */search/?q=baseball&fo=json&at=facets*

#### /collections/

The `/collections` endpoint returns a list of all the digital collections at the LOC. In the response, collections are listed under the `results `attribute. To simplify things, we can make use of another query parameter `at=attribute(s)`. So putting this together, to fetch a list of all digitized collections, request:

<https://www.loc.gov/collections/?fo=json&at=results>

Accessing Attributes

-   */collections/?fo=json&at=pagination*
-   */collections/?fo=json&at=results*
-   */collections/?fo=json&at=results.0*
-   */collections/?fo=json&at=facets*

#### /collections/{name of collection}/

The `/collections/{name of collection}` endpoint returns the web presentation of a specified digital collection in JSON format. The name of the collection needs to be in so-called "kebab" case - words separated by hyphens, e.g., `abraham-lincoln-papers` or `baseball-cards`. This is known as a **URL slug**: any part of the URL that comes after the domain, e.g `example.com/foo-bar/ `where `example.com `is the domain and `foo-bar `is the slug.

Example: <https://www.loc.gov/collections/civil-war-maps?fo=json>

Accessing Attributes

-   */collections/{name of collection}/?fo=json&at=pagination*
-   */collections/{name of collection}/?fo=json&at=results*
-   */collections/{name of collection}/?fo=json&at=results.0*
-   */collections/{name of collection}/?fo=json&at=facets*

#### /{format}/

The `/{format}/` endpoint returns items which have the specified original format. Below is a list of formats along with their URL slugs:

**Audio Recordings:**

`audio`

**Books/Printed Material [1]:**

`books`

**Film, Videos:**

`film-and-videos`

**Legislation [2]:**

`legislation`

**Manuscripts/Mixed Material:**

`manuscripts`

**Maps:**

`maps`

**Newspapers:**

`newspapers`

**Photo, Print, Drawing:**

`photos`

**Printed Music (such as sheet music):**

`notated-music`

**Web Archives:**

`web-archives`

-   [1] Does not provide all catalog information for books at the Library of Congress; best used for digitized books available from the Library website. More complete catalog coverage is available from the [Search/Retrieval via URL](https://www.loc.gov/apis/additional-apis/search-retrieval-via-url/) Z39.50 gateway.
-   [2] More complete results are available at [api.congress.gov](https://api.congress.gov/).

Example: [https://www.loc.gov/film-and-videos/?q=dog&fo=json](https://www.loc.gov/?film-and-videos/?q=dog&fo=json)

Accessing Attributes

-   */{format}/?fo=json&at=pagination*
-   */{format}/?fo=json&at=results*
-   */{format}/?fo=json&at=results.0*
-   */{format}/?fo=json&at=facets*

### "Item" Endpoint

To access detailed bibliographic data on a collections item, or to access the digital representation of the item (digitized photograph or map, web archive link, digitized audio or video), a query is sent to the item endpoint with the item identifier in the URL. The `id` attribute of each item is structured to mirror the actual url for the item in loc.gov, except that for historical reasons the `id` attribute shows a protocol scheme of `http://` instead of `https://`.

The structure of the item endpoint response is similar to that for the individual result items in the search endpoint response, but the item endpoint provides additional data and the links to digital resources.

#### Response Attributes

Some of the most helpful attributes for the item endpoint include:

```

{
    [...],
    "cite_this": {},
    "item": {},
    "resources": [{resource}],
    [...]
}

```

Copy

1.  The **cite_this** attribute is an experimental feature that attempts to assemble usable citations in the Chicago Manual of Style, Modern Language Association Manual of Style, and the American Psychological Association Manual of Style citation formats. It should be used as a starting point for citing materials, and not relied upon to be complete or correct.
2.  The **item** attribute includes bibliographic information for just the requested item. This information is sourced from various metadata formats provided by Library research centers. The structure of the item attribute is described in more detail in the [Item Attribute](https://www.loc.gov/apis/json-and-yaml/requests/responses/responses/#item-attribute) documentation on the *Understanding API Responses*.
3.  The **resource** attribute provides a link to a discrete element or representation of a collection item. The structure of the resource attribute is described in more detail in the [Resource Attribute](https://www.loc.gov/apis/json-and-yaml/requests/responses/responses/#resource-attribute) documentation on the *Understanding API Responses*.

#### /item/{item_id}/

Returns bibliographic information for a single item noted by its identifier. All item records in search results have an id field (the URL for that item's metadata). Many items are composed of one or more resources; the item endpoint provides summary information about all resources for the item. Some, but not all, collections have an item_id field, which contains just the unique identifier itself. Since not all collections have item_id, it's better to rely on the id field and the URL it contains.

**Examples:**

-   <https://www.loc.gov/item/2014717546/?fo=json>
-   <https://www.loc.gov/item/2016687038/?fo=json>

Accessing Attributes

-   */item/{item_id}/?fo=json&at=item*
-   */item/{item_id}/?fo=json&at=resources*
-   */item/{item_id}/?fo=json&at=cite_this*

The structure of the item description returned for a request to an item endpoint is described in more detail under [Response Objects](https://www.loc.gov/apis/json-and-yaml/responses/search-results/#response_objects).

### "Resource" Endpoint

Resource endpoints are points of access for discrete digitized files belonging to multi-part items. For example, the individual pages of a digitized newspapers are resources while the newspaper is an item.

#### Response Attributes

Some of the most helpful attributes for the resource endpoint include:

```

{
    [...],
    "cite_this": {},
    "item": {},
    "page": {},
    "resource": {},
    "resources": [{[resource},],
    "segments": [{segment}],
    [...]
}

```

Copy

1.  The **page** attribute provides information about the images for the current resource.
2.  The **resource** attribute describes the specific data for this resource.
3.  The **segments** attribute describes subdivisions of an item resource. The exact nature of the segments of a resource will depend upon the bibliographic practice of the research center that created the metadata; for instance, for newspapers, segments are usually pages of a particular issue, while for an atlas, segments would be individual maps.

#### /resource/{resource_id}/

Returns information about a single item resource (for instance, an edition of a newspaper), along with bibliographic context for the item to which the resource belongs. Resource records have an id field (the URL for that resource's metadata). The resource record also includes information about the segments of a resource (for instance, the pages of newspaper).

**Examples:**

-   <https://www.loc.gov/resource/20001931/1918-04-05/ed-1/?fo=json>

Accessing Attributes

-   */resource/{resource_id}/?fo=json&at=cite_this*
-   */resource/{resource_id}/?fo=json&at=item*
-   */resource/{resource_id}/?fo=json&at=page*
-   */resource/{resource_id}/?fo=json&at=resource*
-   */resource/{resource_id}/?fo=json&at=resources*
-   */resource/{resource_id}/?fo=json&at=resources.0*
-   */resource/{resource_id}/?fo=json&at=segments*
-   */resource/{resource_id}/?fo=json&at=segments.0*