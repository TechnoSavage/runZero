# Shodan vulnerabilites custom integration for runZero

***THIS IS CURRENTLY A WORK IN PROGRESS***

This integration is designed to populate vulnerabilities found from an existing Shodan integration by using the NVD to enrich vulnerability information from CVEs reported by Shodan in the @shodan.dev.host.vulns attribute

## Background

Requirements (Global)

- Python 3.8+
- pipenv - https://pypi.org/project/pipenv/

## runZero Custom Integration Docs

- Inbound Integrations - https://www.runzero.com/docs/integrations-inbound/#custom-integrations
- SDK Docs- https://runzeroinc.github.io/runzero-sdk-py/index.html

## NVD API Docs

- NVD API: https://nvd.nist.gov/developers/vulnerabilities

## Configuration Explained

- There is a sample environment variables file called .env_sample under the root folder of this project
- You will clone this file and create one called .env where you actually input all of your secrets (API Keys + Access Key Pairs)
- Parameters - explanations of what you see in .env_sample

`RUNZERO_BASE_URL` - The domain or IP of the runZero console, minus any resource path e.g. "https://console.runzero.com"

`RUNZERO_ACCOUNT_TOKEN` - The account API token for the console instance. Found in the console under Account -> Account Settings -> Account API keys

`RUNZERO_CLIENT_ID` - runZero API client ID. Created in the console under Account -> API clients

`RUNZERO_CLIENT_SECRET` - Associated API client secret to the above ID. Displayed when creating an new API client

`RUNZERO_ORG_ID` - UUID of the Organization to which integration will send data. Found in the console URL after navigating to Organizations and clicking organization name

`RUNZERO_SITE_NAME` - Name of the site to which the integration will send data

`RUNZERO_SITE_ID` - UUID of the Site to which integration will send data. Found in the console URL after navigating to Sites and clicking site name

`RUNZERO_CUSTOM_SOURCE_ID` - UUID of the Custom Integration Source. Found in the console URL after navigating to Accounts -> Custom Integrations and clicking the integration name

`RUNZERO_IMPORT_TASK_NAME` - Name of the Custom Integration Source. Created in the console under Accounts -> Custom Integrations

## Getting Started

- Clone this repository

```
git clone https://github.com/TechnoSavage/runZero.git
```

- Clone runZero/custom_integrations/shodanVulns/.env_sample to .env under the same directory

```
cd runZero/custom_integrations/ShodanVulns
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