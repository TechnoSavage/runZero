# Custom Integration: OpenWeatherMap

Provide current weather forecast attributes for all external assets based in GeoIP latitude and longitude lookups in runZero

## Getting Started

- Clone this repository

```
git clone https://github.com/TechnoSavage/runZero.git
``` 

## runZero requirements

- Superuser access to the [Custom Integrations configuration](https://console.runzero.com/custom-integrations) in runZero

##  OpenWeatherMap requirements

`client_id` - Export token of runZero organization (configured in Credentials section of runZero)

`client_secret` - API token for openweather API (configured in Credentials section of runZero)

## OpenWeatherMap API Docs

- [API Docs](https://openweathermap.org/api/one-call-3?collection=one_call_api_3.0)

## Steps

### OpenWeatherMap configuration

1. Get a free API key and configure as `client_secret` in the Custom Integration Credentials section of the runZero console.

### runZero configuration

1. (OPTIONAL) - make any neccessary changes to the script to align with your environment.  
2. [Create the Credential for the Custom Integration](https://console.runzero.com/credentials)
    - Select the type `Custom Integration Script Secrets`
    - Both `access_key` and `access_secret` are required
    - `access_key` corresponds to the runZero Export API token of the Organization you want to perform the integration in.
    -  `access_secret` corresponds to the OpenWeatherMap API key.
3. [Create the Custom Integration](https://console.runzero.com/custom-integrations/new)
    - Add a Name and Icon 
    - Toggle `Enable custom integration script` to input your finalized script
    - Click `Validate` to ensure it has valide syntax
    - Click `Save` to create the Custom Integration 
4. [Create the Custom Integration task](https://console.runzero.com/ingest/custom/)
    - Select the Credential and Custom Integration created in steps 2 and 3
    - Update the task schedule to recur at the desired timeframes
    - Select the Explorer you'd like the Custom Integration to run from
    - Click `Save` to kick off the first task 


### What's next?

- You will see the task kick off on the [tasks](https://console.runzero.com/tasks) page like any other integration 
- The task will update the existing assets with the data pulled from the Custom Integration source 
- The task will create new assets for when there are no existing assets that meet merge criteria (hostname, MAC, etc)
- You can search for assets enriched by this custom integration with the runZero search `custom_integration:<INSERT_NAME_HERE>`

P.S. Happy April, 1 2026