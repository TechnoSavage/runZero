# Custom Integration: Flexera Snow Atlas

## Getting Started

- Clone this repository

```
git clone https://github.com/TechnoSavage/runZero.git
``` 

# Custom Integration: Flexera Snow Atlas

## runZero requirements

- Superuser access to the [Custom Integrations configuration](https://console.runzero.com/custom-integrations) in runZero

##  Snow Atlas requirements

**ATLAS Instance URL** - The domain or IP of the Snow Atlas web server e.g. "https://<region>.snowsoftware.io" (defined within the starlark script as `ATLAS_BASE_URL`)

`client_id` - Oauth Client ID for authentication (configured in Credentials section of runZero)

`client_secret` - Oauth Client secret for authentication (configured in Credentials section of runZero)

## Snow Atlas API Docs

- [Snow Atlas API Reference](https://docs-snow.flexera.com/snow-atlas-api/resources/)

- [Snow Atlas Docs](https://docs-snow.flexera.com/snow-atlas/user-documentation/)

## Steps

### Snow Atlas configuration

1. Determine the proper Snow Atlas URL:
    - Identify the region for your instance
    - Assign the URL to `ATLAS_BASE_URL` within the starlark script 
2. Create an Application Registration in Snow Atlas: 
    - [Application Registration documentation](https://docs-snow.flexera.com/snow-atlas/user-documentation/snow-atlas-settings/application-registrations/manage-application-registrations)
    - Copy the Client ID; this will be used as the value for `access_key` when creating the Custom Integration credentials in the runZero console (see below)
    - Copy the Client secret; this will be used as the value for `access_secret` when creating the Custom Integration credentials in the runZero console (see below)

### runZero configuration

1. (OPTIONAL) - make any neccessary changes to the script to align with your environment. 
    - Modify API calls as needed to filter assets
    - Modify datapoints uploaded to runZero as needed 
2. [Create the Credential for the Custom Integration](https://console.runzero.com/credentials)
    - Select the type `Custom Integration Script Secrets`
    - Both `access_key` and `access_secret` are required
    - `access_key` corresponds to the Client ID provided when creating the Snow Atlas Application Registration
    -  `access_secret` corresponds to the Client secret provided when creating the Snow Atlas Application Registration
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