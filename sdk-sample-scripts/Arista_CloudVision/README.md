# Arista CloudVision custom integration for runZero

Custom integration designed to pull asset information from CloudVision and merge to runZero asset data.

## Background

Requirements (Global)

- Python 3.8+

- pipenv - https://pypi.org/project/pipenv/

## runZero Custom Integration Docs

- Inbound Integrations - https://www.runzero.com/docs/integrations-inbound/#custom-integrations

- SDK Docs- https://runzeroinc.github.io/runzero-sdk-py/index.html

## CloudVision API Docs

- CloudVision API Documentation: https://aristanetworks.github.io/cloudvision-apis/

- CloudVision Python Client:https://github.com/aristanetworks/cloudvision-python 
https://github.com/aristanetworks/cvprac

## Configuration Explained

- There is a sample environment variables file called .env_sample under the root folder of this project

- Clone this file and create one called .env then input all of your secrets (API Keys + Access Key Pairs)

- Parameters - explanations of what you see in .env_sample

`RUNZERO_BASE_URL` - The domain or IP of the runZero console, minus any resource path e.g. https://console.runzero.com

`RUNZERO_CLIENT_ID` - runZero API client ID. Created in the console under "Account" -> "API clients"

`RUNZERO_CLIENT_SECRET` - Associated API client secret to the above ID. Displayed when creating a new API client

`RUNZERO_ORG_ID` - UUID of the Organization to which the integration will report data. Found in the console URL after navigating to "Organizations" and clicking on an organization name

`RUNZERO_SITE_NAME` - Name of the site to which the integration will create new assets

`RUNZERO_SITE_ID` - UUID of the Site to which the integration will create new assts. Found in the console URL after navigating to "Sites" and clicking on a site name

`CV_CUSTOM_SOURCE_ID` - UUID of the Custom Integration Source. Found in the console URL after navigating to "Accounts" -> "Custom Integrations" and clicking on an integration name

`CV_IMPORT_TASK_NAME` - Name of the Custom Integration Source. Created in the console under "Accounts" -> "Custom Integrations"

### CloudVision On-Prem node connection variables

`CV_NODE_LIST` - The CloudVision Node(s) to connect to. Each node separated by a comma and space (', ')

`CV_USERNAME` - Username for connecting to the specified nodes

`CV_PASSWORD` - Password for connecting to the specified nodes

`CV_CONSOLE_URL` - The domain of the CloudVision instance, minus any resource path e.g. www.arista.io (The sample env file includes the domains for two US based instances. Uncomment the one you prefer)

`CV_API_KEY` - The API token for the CloudVision instance.

## Getting Started

- Clone this repository

```
git clone https://github.com/TechnoSavage/runZero.git
```

- Clone runZero/sdk-sample-scripts/Arista_CloudVision/.env_sample to .env under the same directory

```
cd runZero/sdk-sample-scripts/Arista_CloudVision
cp .env_sample .env
```

- Update all of the necessary secrets in the `.env` file (NOTE: you need to rerun pipenv shell anytime you update these  values to reload them)

- Install dependancies

```
pipenv install -r requirements.txt
```

- Enter pipenv

```
pipenv shell
```

- In your runZero console, navigate to Account -> Custom Integrations -> Add custom integration. Name the integration consistent to the parameter RUNZERO_IMPORT_TASK_NAME in the .env file. Optionally upload an image for the source. 

- run the script to sync assets. Sync can be scheduled with a job scheduler such as cron