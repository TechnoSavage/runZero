# Snipe-IT custom integration for runZero
Custom integration designed to pull asset information from Snipe-IT ITAM and create or merge to runZero asset data. Snipe-IT is highly customizable in terms of the field an asset can contain; some relevant attributes are hardware serial number, maufacturer, and hardware EOL. This integration is useful for representing assets that are part of the network infrastructure that do not communicate at OSI Layer 2 and above (e.g. network TAPs).

## Background

Requirements (Global)

- Python 3.8+
- pipenv - https://pypi.org/project/pipenv/

## runZero Custom Integration Docs

- Inbound Integrations - https://www.runzero.com/docs/integrations-inbound/#custom-integrations
- SDK Docs- https://runzeroinc.github.io/runzero-sdk-py/index.html

## Snipe-IT API Docs

- Snipe-IT API Reference: https://snipe-it.readme.io/reference/api-overview
- Snipe-IT Docs: https://snipe-it.readme.io/docs

## Configuration Explained

- There is a sample environment variables file called .env_sample under the root folder of this project
- You will clone this file and create one called .env where you actually input all of your secrets (API Keys + Access Key Pairs)
- Parameters - explanations of what you see in .env_sample

`RUNZERO_BASE_URL` - The domain or IP of the runZero console, minus any resource path e.g. "https://console.runzero.com" \
`RUNZERO_ACCOUNT_TOKEN` - The account API token for the console instance. Found in the console under Account -> Account Settings -> Account API keys\
`RUNZERO_CLIENT_ID` - runZero API client ID. Created in the console under Account -> API clients\
`RUNZERO_CLIENT_SECRET` - Associated API client secret to the above ID. Displayed when creating an new API client\
`RUNZERO_ORG_ID` - UUID of the Organization to which integration will send data. Found in the console URL after navigating to Organizations and clicking organization name\
`RUNZERO_SITE_NAME` - Name of the site to which the integration will send data\
`RUNZERO_SITE_ID` - UUID of the Site to which integration will send data. Found in the console URL after navigating to Sites and clicking site name\
`RUNZERO_CUSTOM_SOURCE_ID` - UUID of the Custom Integration Source. Found in the console URL after navigating to Accounts -> Custom Integrations and clicking the integration name\
`RUNZERO_IMPORT_TASK_NAME` - Name of the Custom Integration Source. Created in the console under Accounts -> Custom Integrations\

`SNIPE_BASE_URL` - The domain or IP of the Snipe-IT instance, minus any resource path e.g. "http://mycompany.snipeit" \
`SNIPE_API_KEY` - The API token for the Snipe instance. Created in user account dropdown -> Manage API Keys\

## Getting Started

- Clone this repository

```
git clone https://github.com/TechnoSavage/runZero.git
```

- Clone runZero/custom_integrations/Snipe-IT/.env_sample to .env under the same directory

```
cd runZero/custom_integrations/Snipe-IT
cp .env_sample .env
```

- Update all of the secrets in the `.env` needed based on the script you'd like to run (NOTE: you need to rerun pipenv shell anytime you update these  values to reload them)

- Install dependancies

```
pipenv install -r requirements.txt
```

- Enter pipenv

```
pipenv shell
```
- In your runZero console, navigate to Account -> Custom Integrations -> Add custom integration. Name the integration consistent to the parameter RUNZERO_IMPORT_TASK_NAME in the .env file. Optionally upload an image for the source. 
(This step is optional; the script will create the source if it doesn't already exist.)

- run the script to sync assets. Sync can be scheduled with a job scheduler such as cron

# Important

For runZero to merge asset data from Snipe-IT to existing assets there must be a common matching asset attribute and field between what is reported by Snipe-IT and what can be found in runZero scans or passive discovery. A MAC address field in Snipe-IT is a recommended method. Snipe-IT has a default fieldset called 'Asset with MAC Address' that will serve this purpose. This script in its current form expects this field to be present for merge logic to work. The user is free to define and utilize other fields/attributes for this purpose as well (see SDK documentation).

New assets created by the integration that do not have MAC address (or other merge attributes) associated, such as the Network TAP example, will continue to be updated by subsequent sync tasks.