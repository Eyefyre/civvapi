# Civ V API

This repo contains data about various aspects of Sid Meier's Civilization V in JSON format
This repo also contains the SQL databases used and the script I created to generate the data.

If you have any suggestions or notice any issues with the data, please do let me know or open an issue on the repo.

How to use:

The base URL for the repo is https://eyefyre.github.io/civvapi/v1
There are 16 endpoints for this API:
* beliefs
* buildings
* citystates
* civilizations
* features
* improvements
* policies
* promotions
* religions
* resolutions
* resources
* specialists
* tech
* terrains
* units
* wonders

The data in this API is also offered in 10 languages
* English - en
* German - de
* Spanish - es
* French - fr
* Italian - it
* Japanese - jp
* Korean - kr
* Polish - pl
* Russina - ru
* Chinese - zh

Here is an example of an endpoint call in multiple languages:

https://eyefyre.github.io/civvapi/v1/en/buildings/courthouse.json
https://eyefyre.github.io/civvapi/v1/de/buildings/courthouse.json
https://eyefyre.github.io/civvapi/v1/jp/buildings/courthouse.json
https://eyefyre.github.io/civvapi/v1/ru/buildings/courthouse.json

https://eyefyre.github.io/civvapi/v1/it/tech/agriculture.json
https://eyefyre.github.io/civvapi/v1/zh/tech/agriculture.json
https://eyefyre.github.io/civvapi/v1/kr/tech/agriculture.json
https://eyefyre.github.io/civvapi/v1/fr/tech/agriculture.json


---

https://eyefyre.github.io/civvapi/v1/en/civilizations/america.json
The above URL will provide the data for just the American civilization

https://eyefyre.github.io/civvapi/v1/en/civilizations/civilizations.json
This URL will provide a list of data with every civilization in it instead
This can be applied to every other endpoint

https://eyefyre.github.io/civvapi/v1/en/beliefs/beliefs.json
https://eyefyre.github.io/civvapi/v1/en/features/features.json
https://eyefyre.github.io/civvapi/v1/en/citystates/citystates.json
etc..
