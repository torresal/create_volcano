## Create Volcano PGE
Ingests products representing individual Volcanoes.
----
There are two associated jobs:
 - Volcano - Publish All GVN Volcano Products
 - Volcano - Publish Single Volcano Product

### Volcano - Publish All GVN Volcano Products
----
Job is of type individual. There are no inputs. The job queries the Smithsonian Volcano Archive API endpoint and retrieves a json of all Holocene Volcanoes. It parses the json, publishing a Volcano product for each return. It also attempts to localize browse files where possible. The Volcano Product spec is the following:

    VOLC-GVN_<GVN_Volcano_Number>-<Volcano_Name>-<Product_Version>

### Volcano - Publish Single Volcano Product
----
Job is of type individual. The job generates a Volcano Product based on user input. Inputs are:
 - volcano_name: String name. Eg "Kilauea". Non alphanumeric characters are stripped.
 - GVP_number: Digit String. This represents the GVN number. Please use a unique number, or publish will fail.
 - latitude: latitude of volcano summit
 - longitude: longitude of volcano summit

----

Volcano product publishing triggers AOI creation, which then initiates product localization, higher level product generation, etc.
