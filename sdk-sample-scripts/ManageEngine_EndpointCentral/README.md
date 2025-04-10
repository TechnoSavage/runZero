# ManageEngine Endpoint Central custom integration for runZero

Unified Endpoint Management (UEM) & Endpoint protection suite

## Background

Requirements (Global)

- Python 3.8+

- pipenv - https://pypi.org/project/pipenv/

## runZero Custom Integration Docs

- Inbound Integrations - https://www.runzero.com/docs/integrations-inbound/#custom-integrations

- SDK Docs- https://runzeroinc.github.io/runzero-sdk-py/index.html

## ManageEngine API Docs

- ManageEngine Endpoint Central API Reference: https://www.manageengine.com/products/desktop-central/api/api-inventory-scancomputers.html

- ManageEngine Endpoint Central Docs: https://www.manageengine.com/products/desktop-central/resources/?ec_resources_drop&page=doc&ec-home-new

## Configuration Explained

- There is a sample environment variables file called .env_sample under the root folder of this project

- You will clone this file and create one called .env where you actually input all of your secrets (API Keys + Access Key Pairs)

- Parameters - explanations of what you see in .env_sample

`RUNZERO_BASE_URL` - The domain or IP of the runZero console, minus any resource path e.g. https://console.runzero.com

`RUNZERO_ACCOUNT_TOKEN` - The account API token for the console instance. Found in the console under Account -> Account Settings -> Account API keys

`RUNZERO_CLIENT_ID` - runZero API client ID. Created in the console under Account -> API clients

`RUNZERO_CLIENT_SECRET` - Associated API client secret to the above ID. Displayed when creating a new API client

`RUNZERO_ORG_ID` - UUID of the Organization to which the integration will report data. Found in the console URL after navigating to "Organizations" and clicking on an organization name

`RUNZERO_SITE_NAME` - Name of the site to which the integration will create new assets

`RUNZERO_SITE_ID` - UUID of the Site to which the integration will create new assts. Found in the console URL after navigating to "Sites" and clicking on a site name

`MEEC_CUSTOM_SOURCE_ID` - UUID of the Custom Integration Source. Found in the console URL after navigating to "Accounts" -> "Custom Integrations" and clicking on an  integration name

`MEEC_IMPORT_TASK_NAME` - Name of the Custom Integration Source. Created in the console under "Accounts" -> "Custom Integrations"

`MEEC_URL` - URL of ManageEngine Endpoint Central webserver

`MEEC_KEY` - ManageEngine Endpoint Central API Key

## Getting Started

- Clone this repository

```
git clone https://github.com/TechnoSavage/runZero.git
```

- Clone runZero/sdk-sample-scripts/ManageEngine_EndpointCentral/.env_sample to .env under the same directory

```
cd runZero/sdk-sample-scripts/ManageEngine_EndpointCentral
cp .env_sample .env
```

- Update all of the necessary secrets in the `.env` file (NOTE: you need to rerun pipenv shell anytime you update these values to reload them)

- Install dependencies

```
pipenv install -r requirements.txt
```

- Enter pipenv

```
pipenv shell
```
- In your runZero console, navigate to Account -> Custom Integrations -> Add custom integration. Name the integration consistent to the parameter RUNZERO_IMPORT_TASK_NAME in the .env file. Optionally upload an image for the source. 

- run the script to sync assets. Sync can be scheduled with a job scheduler such as cron