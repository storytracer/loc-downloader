Making API Requests
===================

How to craft a request to the JSON/YAML API for loc.gov

Content Covered by the loc.gov API
----------------------------------

Most of the collections content on the loc.gov website is presented on parts of the website, called **endpoints**, that are implemented via the loc.gov API. There are a number of subsites on loc.gov that were not implemented with the loc.gov API and so do not provide API responses. A few examples of sites that do not provide loc.gov API response are:

-   The National Library Service for the Blind and Print Disabled site at <https://www.loc.gov/nls/>
-   The Publishers site at <https://www.loc.gov/publish/>
-   The Cataloging and Acquisitions site at <https://www.loc.gov/aba/>
-   Research room sites at <https://www.loc.gov/rr/>
-   The American Folklife Center site at [/research-centers/american-folklife-center/](https://www.loc.gov/research-centers/american-folklife-center/)
-   The Prints and Photographs Online Catalog site at <https://www.loc.gov/pictures/>

There are other parts of the website that are implemented using the API, such as the Library's [events](https://www.loc.gov/events) site and the Library's [visitors](https://www.loc.gov/visit) site, but which do not provide simple search or item responses and are not discussed in the following documentation.

Base URL
--------

The API response underlying any page displayed may be exposed by adding an API response format parameter, `?fo=json`, to the end of any loc.gov page that is implemented using the API. Requests to the JSON/YAML API use the base url `https://www.loc.gov/{endpoint}/?fo=json`. To return data in YAML format, simply change `fo=json`to `fo=yaml`.

The base url can be adjusted by changing the [endpoint](https://www.loc.gov/apis/json-and-yaml/requests/endpoints/) and/or adding [parameters](https://www.loc.gov/apis/json-and-yaml/requests/parameters/) to the **query string**, i.e. the portion of the url following a `?` A query string uses **query parameters** to narrow search results. Multiple parameters, also known as **key value pairs**, can be used in the same query string and are conjoined by an `&`, e.g. <https://www.loc.gov/photos/?fa=location:washington+d.c.&q=bridges&fo=json>.

An explanation of the search endpoints (/search, /{format}, /collections, and /collections/{collection}) and the item / resource endpoints (/item, /resource) follows in the [API Endpoints](https://www.loc.gov/apis/json-and-yaml/requests/endpoints/) documentation. An explanation of some of the query parameters available with the API follows in the [API Parameters](https://www.loc.gov/apis/json-and-yaml/requests/parameters/) documentation.