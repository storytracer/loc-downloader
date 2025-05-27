Search Results Responses
========================

API responses to search queries

### Search Results Response Object

The API will respond to a query to a search results endpoint (/search, /collections, or /format) with a JSON response object containing the following attributes:

```

{
  [...],
  "facets": Array,
  "pagination": Object,
  "results": Array,
  [...]
}

```

Copy

#### Facets Attribute

The index behind loc.gov stores a number of fields as **facets**, which allow users to narrow their result set by filtering on certain recurring values, such as subject, location, language, and date. Results can be filtered on facets by using the [`fa` parameter](https://www.loc.gov/apis/json-and-yaml/requests/parameters/#facet-parameter).

One facet of particular use is the `partof` facet, which is used for collection names, custodial divisions, and other subsets of collection data.

The facets attribute provides information about the top five facet values by frequency for each facet field. The following fields, which are also fields in the item object, are described above.

-   [access-restricted](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#access_restricted_field)
-   [contributor](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#contributor_field)
-   [dates](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#dates_field)
-   [digitized](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#digitized_field)
-   [language](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#language_field)
-   [location](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#location_field)
-   [online-format](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#online_format_field)
-   [original-format](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#original_format_field)
-   [partof](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#partof_field)
-   [subject](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#subjects_field)

```

"facets": [
    {
        "filters": [
            {
                "count": 322,
                "not": null,
                "off": null,
                "on": "https://www.loc.gov/collections/vietnam-era-pow-mia-database/?dates=2020/2029&fo=json",
                "term": "2020-01-01T00:00:00Z",
                "title": "2020 to 2029"
            },
           [...]
       ]
    },
    [...]
]

```

Copy

#### Pagination Attribute

When accessing the API at the **/search/ **or **/collections/ **endpoints it is possible to traverse through the pages of the result programmatically using the **pagination **section of the response, which has the following structure:

```

{
    "from": Number,
    "results": String,
    "last": String,
    "total": Number,
    "previous": String,
    "perpage": Number,
    "perpage_options": List,
    "of": Number,
    "next": String,
    "current": Number,
    "to": Number,
    "page_list": List,
    "first": String
}

```

Copy

##### Description of pagination data

| **Field** | **Description** | **Example** |
| --- | --- | --- |
| from | Index number of the first result item in this page of results. | 26 |
| to | Index number of the last result in this page of results. | 50 |
| results | Index numbers of the result items in this page. | "26 - 50" |
| last | URL of the last page of results in the whole set of results pages. | "https://www.loc.gov/search/?q=giraffe&sp=5&fo=json" |
| of | Total number of items in the results. | 318 |
| previous | URL of the preceding page of results. Will be null when this is the first page. | "https://www.loc.gov/search/?q=giraffe&sp=1&fo=json", |
| next | URL of the next page of results. Will be null when there are not more pages. | "https://www.loc.gov/search/?q=giraffe&sp=3&fo=json" |
| perpage | Number of result items on each page. | 25 |
| total | Total number of pages available. | 5 |
| current | Page number you are currently on. | 2 |

##### An Example Pagination Object

```

{
    "from": 1,
    "results": "1 - 1",
    "last": "https://www.loc.gov/resource/20001931/1918-04-05/ed-1/?at=pagination&fo=json&sp=4",
    "total": 8,
    "previous": null,
    "perpage": 1,
    "perpage_options": [
      25,
      50,
      100,
      150
    ],
    "of": 8,
    "next": "https://www.loc.gov/resource/20001931/1918-04-05/ed-1/?at=pagination&fo=json&sp=2",
    "current": 1,
    "to": 1,
    "page_list": [
      {
        "url": null,
        "number": 1
      },
      {
        "url": "https://www.loc.gov/resource/20001931/1918-04-05/ed-1/?at=pagination&fo=json&sp=2",
        "number": 2
      },
      {
        "url": "https://www.loc.gov/resource/20001931/1918-04-05/ed-1/?at=pagination&fo=json&sp=3",
        "number": 3
      },
      {
        "url": "https://www.loc.gov/resource/20001931/1918-04-05/ed-1/?at=pagination&fo=json&sp=4",
        "number": "..."
      }
    ],
    "first": null
}

```

Copy

#### Results Attribute

The results attribute is an array listing summary bibliographic details for some sequence of the items that respond to a query, with the count based on the per-page count and the sort order based on the sort-order parameter. The fields for each result item are a subset of the fields in the item object. In some cases, a result item field is a summary of the values in the item response object field (e.g., contributor, subject).

The following fields are described in the section on [Item and Resource Responses](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#item_and_resource_response):

-   [access-restricted](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#access_restricted_field)
-   [aka](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#aka_field)
-   campaigns
-   [contributor](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#contributor_field)
-   [date](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#date_field)
-   [dates](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#dates_field)
-   [digitized](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#digitized_field)
-   [extract_timestamp](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#extract_timestamp_field)
-   [group](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#group_field%22)
-   [hassegments](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#hassegments_field)
-   [id](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#id_field)
-   [image_url](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#image_url_field)
-   [index](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#index_field)
-   [item](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#item_field)
-   [language](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#language_field)
-   [location](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#location_field)
-   [language](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#language_field)
-   [mime_type](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#mime_type_field)
-   [number_field](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#number_field)
-   [online-format](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#online_format_field)
-   [original-format](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#original_format_field)
-   [other_title](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#other_title_field)
-   [partof](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#partof_field)
-   [publication_frequency](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#publication_frequency_field)
-   [shelf_id](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#shelfid_field)
-   [site](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#site_field)
-   [subject](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#subject_field)

The following fields are not taken directly from the item response object, and are either specific to search result responses or summaries of their analogous item response field:

| **Field** | **Description** | **Type** | **Example** |
| --- | --- | --- | --- |
| contributor | List of persons or institutions or organizations who contributed to the creation of the item. Each item consists of a string. This is a summary of the [contributors](https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/#contributors_field) field.\
facetable | array | [{ "national archives and records administration": "https://dev.loc.gov/search/?fa=contributor:" "national+archives+and+records+administration" "&fo=json" }] |
| subject |

List of subjects. These are separated elements of the Library of Congress Subject Headings (LCSH). Geography is not shown here, but rather under the location element.\
facetable

All elements separated by a double dash in an LCSH are tokenized. For example, an item with the subject heading "Women -- Afghanistan -- Social conditions" will have ["social conditions", "women's rights"] in the subject element and "afghanistan" in the location element.

For the full subject headings, request the JSON for the /item view

 | array | ["public interest/advocacy", "history", "september 11 terrorist attacks"] |
| index | The index number of the results among all results. This starts with 1 and continues through all of the results in the whole set (not just this page). | integer | 1 |