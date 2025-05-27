Understanding API Responses
===========================

The format of the response from the JSON/YAML API for loc.gov

A response is the data returned from a request to the loc.gov API in the specified representation (JSON/YAML). Because the API also provides data for the loc.gov website, some of its data elements (e.g. breadcrumbs, views) are specifically for that purpose. This page focuses on the sections of JSON responses that are most useful for working with digital collections information, those from search result endpoints, item endpoints, and resource endpoints.

```

/search/?q={query terms}
/{format}/
/collections/
/collections/{collection name}/
/item/{item_id}/
/resource/{resource_id}/

```

Copy

Please note, however, that Library of Congress data is incredibly heterogenous and that there is no such thing as a standard API response. Variations in data structure can stem from differences in underlying digitization, descriptive, cataloging, and technical practices. Furthermore, historic materials themselves do not neatly fall into distinct categories, especially after digitization. Below, we outline some general strategies for orienting yourself to the materials and encourage you to reach out to curatorial staff via the Library's [Ask a Librarian service](https://ask.loc.gov/) or technical staff via the LC Labs team at <LC-Labs@loc.gov> if you have additional questions.

JSON Response Objects
---------------------

Each of the endpoint types has a distinct response format, but they can be broadly grouped into two categories:

-   responses to queries for a list of items, or [Search Results Responses](https://www.loc.gov/apis/json-and-yaml/responses/search-results/) and
-   responses to queries for a single item, or [Item and Resource Responses](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/)