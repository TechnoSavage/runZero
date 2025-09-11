## Configuration

`ATLAS_BASE_URL` - The domain or IP of the Snow Atlas web server e.g. http://<'ip address'>:<'port'>

`client_secret` - The bearer token

## Getting Started

- Clone this repository

```
git clone https://github.com/TechnoSavage/runZero.git
``` 

# Custom Integration: Flexera Snow Atlas

## runZero requirements

- Superuser access to the [Custom Integrations configuration](https://console.runzero.com/custom-integrations) in runZero

##  Snow Atlas requirements

- <INSERT_REQUIREMENT_1> - example API Client Credentials
- <INSERT_REQUIREMENT_2> - example API URL

## Snow Atlas API Docs

- [Snow Atlas API Reference](https://docs-snow.flexera.com/snow-atlas-api/resources/)

- [Snow Atlas Docs](https://docs-snow.flexera.com/snow-atlas/user-documentation/)

## Steps

### Snow Atlas configuration

1. <INSERT_STEP_1> - example get API URL
2. <INSERT_STEP_2> - create API credentials
3. <INSERT_STEP_3> - example update `API_URL` in the code

### runZero configuration

1. (OPTIONAL) - make any neccessary changes to the script to align with your environment. 
    - Modify API calls as needed to filter assets
    - Modify datapoints uploaded to runZero as needed 
2. [Create the Credential for the Custom Integration](https://console.runzero.com/credentials)
    - Select the type `Custom Integration Script Secrets`
    - Both `access_key` and `access_secret` are required, but not all scripts will use both
    - Input a placeholde value like `foo` if the value is unused 
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