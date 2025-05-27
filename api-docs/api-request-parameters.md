API Request Parameters
======================

Using loc.gov API parameters to define your query

Query Parameters
----------------

All endpoints in the loc.gov API provide parameters that can be used to alter the response.

### Control Parameters

Parameters for controlling the response output.

* * * * *

#### `fo`

Specify the format of the returned results.\
Options: JSON and YAML.

#### Examples:

```

fo=json
fo=yaml

```

Copy

* * * * *

#### `at`

Select one or more attributes to return in the results\
This is helpful for removing extraneous information from the results, such as `more_like_this` and `related_items`. You can specify elements to exclude using `at!=`.

A selection of more than one top-level attributes may be specified as a comma-separated list. Sub-attributes may be specified by dot notation. Individual values in a list attribute (like `results` or `resources`) can be selected using zero-indexed numbers in dot notation.

#### Examples:

    `at=item
    at=item,resources,reproductions
    at=item.data
    at=resources.0
    at=resources.0.files
    at!=more_like_this`

Copy

### Other Parameters

* * * * *

#### `q`

query parameter\
Conducts a keyword search in the metadata and any available full text including video transcripts

#### Supported Endpoints

-   /search/
-   /{format}/
-   /collections/{name of collection}/
-   /item/{id}/ and /resource/{id}/

#### Examples:

```

q=kittens

```

Copy

* * * * *

#### `fa`

filter or facet\
takes the format filter-name:value\
multiple filters can be used by separating them with a pipe character: |

Available filters/facets include:

-   access-restricted
-   digitized
-   contributor
-   language
-   location
-   subject
-   online-format
-   original-format

Please note, however, that facet values are not controlled vocabularies. Instead, they derive from fields in catalog records, which are often but not always the same across Library of Congress divisions.

#### Supported Endpoints

-   /search/
-   /{format}/
-   /collections/{name of collection}/

#### Examples:

```

fa=location:ohio
fa=location:yellowstone national park
fa=subject:meterology
fa=original-format:periodical|subject:wildlife
fa=partof:performing arts encyclopedia
fa=contributor:lange, dorothea

```

Copy

Many formats are also available as endpoints (e.g. /maps/). Those that are ONLY available using the filters/facets parameter include:

```

original-format:sound recording
original-format:legislation
original-format:periodical
original-format:personal narrative
original-format:software,e-resource
original-format:3d object
partof

```

Copy

Collections, divisions, and units in the Library of Congress. Most are also available using the collections endpoint. See [Part ofs](https://www.loc.gov/search/index/partof/) for a list.

* * * * *

#### `c`

results per page. The default is 25

#### Supported Endpoints

-   /search/
-   /{format}/
-   /collections/{name of collection}/

#### Examples:

```

c=50

```

Copy

* * * * *

#### `sp`

page in results (results are returned in pages of 25 items unless specified using the c parameter) The first page is sp=1.

#### Supported Endpoints

-   /search/
-   /{format}/
-   /collections/{name of collection}/

#### Examples:

```

sp=2

```

Copy

* * * * *

#### `sb`

sort field

#### Supported Endpoints

-   /search/
-   /{format}/
-   /collections/{name of collection}/

#### Examples:

```

sb=date

```

Copy

Available sort options include:

```

date (earliest to latest)
date_desc (latest to earliest)
title_s (by title)
title_s_desc (reverse by title)
shelf_id (call number/physical location)
shelf_id_desc (reverse by call number/physical location)

```

`\
`