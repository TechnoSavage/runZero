# Custom Integration: Ivanti Neurons - device inventory

## Getting Started

- Clone this repository

```
git clone https://github.com/TechnoSavage/runZero.git
``` 

## runZero requirements

- Superuser access to the [Custom Integrations configuration](https://console.runzero.com/custom-integrations) in runZero

##  Ivanti Neurons requirements

**Instance URL** - The Neurons Auth URL provided upon creating an app registration in the Neurons console e.g. "https://<url of Neurons server>" (defined within the starlark script as `NEURONS_AUTH_URL`)

`client_id` - Client ID provided upon creating an app registration in the Neurons console. Used for authentication to retrieve JWT token (configure this value in the Credentials section of the runZero console)

`client_secret` - Client Secret provided upon creating an app registration in the Neurons console. Used for authentication to retrieve JWT token(configure this value in Credentials section of the runZero console)

`Tenant ID` - The tenant ID of the Neurons instance provided with the Auth URL upon a new app registration. Used in request headers when authenticating to the "People and Devices" API endpoint. (defined within the starlark script as `NEURONS_TENANT_ID`)

## Ivanti Neurons API Docs

- [Ivanti Neurons API](https://help.ivanti.com/ht/help/en_US/CLOUD/api/Shared-Content/welcome.htm)
- [Ivanti Product API Hub](https://www.ivanti.com/support/api)

## Steps

### Ivanti Neurons configuration

1. Determine the proper Endpoint Manager URL:
    - Assign the URL to `NEURONS_BASE_URL` within the starlark script
2. Using an Ivanti Neurons API requires authentication configuration to your Ivanti Neurons tenant. When you first use the API, you need to create an App Registration in the Ivanti Neurons console.
2. Create login credentials with necessary, read-only access to retrieve JWT token for API access: 
    - Copy the username to the value for `access_key` when creating the Custom Integration credentials in the runZero console (see below)
    - Copy the password to the the value for `access_secret` when creating the Custom Integration credentials in the runZero console (see below)

New registration
In Ivanti Neurons, navigate to Admin > App Registrations.
Select New registration to open the New app registration panel.
From the drop-down, select Custom App.
Click Continue.
In the Custom App panel, optionally enter a Description for the registration.
Click Register to generate the authentication settings.
In the Complete this registration panel, the authentication settings, required to complete the registration, are provided:
Neurons Auth URL
Client ID
Client secret
Copy or record all of the registration settings. You need to enter these settings in the Get Neurons Token API to validate the authentication.
Warning: For security reasons, the Client Secret will not be visible again once you close this panel, so make sure you copy it before clicking Finish and close.
Once you have made a copy of the settings click Finish and close.
After completing the App Registration process, you will get the tenant hostname and tenant ID from the Auth URL.

[How to authenticate to Neurons API](https://help.ivanti.com/ht/help/en_US/CLOUD/api/Shared-Content/authenticate_api.htm)

### runZero configuration

1. (OPTIONAL) - make any neccessary changes to the script to align with your environment. 
    - Modify API calls as needed to filter assets
    - Modify datapoints uploaded to runZero as needed 
2. [Create the Credential for the Custom Integration](https://console.runzero.com/credentials)
    - Select the type `Custom Integration Script Secrets`
    - Both `access_key` and `access_secret` are required
    - `access_key` corresponds to the Client ID provided when creating the Endpoint Manager Application Registration
    -  `access_secret` corresponds to the Client secret provided when creating the Endpoint Manager Application Registration

Paste the parameters to pass on the field below as described in documentation.

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