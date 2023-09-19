# Greenbone GVM community edition custom integration for runZero
Custom integration designed to pull asset information from Greenbone Vulnerability Management (formerly OpenVAS) and create or merge GVM asset data to runZero asset data. GVM is an open-source vulnerability management platform.

## Background

Requirements (Global)

- Python 3.8+
- pipenv - https://pypi.org/project/pipenv/
- python-gvm - https://python-gvm.readthedocs.io/en/latest/index.html

## runZero Custom Integration Docs

- Inbound Integrations - https://www.runzero.com/docs/integrations-inbound/#custom-integrations
- SDK Docs- https://runzeroinc.github.io/runzero-sdk-py/index.html

## GVM API Docs

- GVM API Docs - https://greenbone.github.io/docs/latest/api.html

## Configuration Explained

- There is a sample environment variables file called .env_sample under the root folder of this project
- You will clone this file and create one called .env where you actually input all of your secrets (API Keys + Access Key Pairs)
- Parameters - explanations of what you see in .env_sample

```
RUNZERO_BASE_URL - The domain or IP of the runZero console, minus any resource path e.g. "https://console.runzero.com"
RUNZERO_ACCOUNT_TOKEN - The account API token for the console instance. Found in the console under Account -> Account Settings -> Account API keys
RUNZERO_CLIENT_ID - runZero API client ID. Created in the console under Account -> API clients
RUNZERO_CLIENT_SECRET - Associated API client secret to the above ID. Displayed when creating an new API client
RUNZERO_ORG_ID - UUID of the Organization to which integration will send data. Found in the console URL after navigating to Organizations and clicking organization name
RUNZERO_SITE_NAME - Name of the site to which the integration will send data.  
RUNZERO_SITE_ID - UUID of the Site to which integration will send data. Found in the console URL after navigating to Sites and clicking site name.
RUNZERO_CUSTOM_SOURCE_ID - UUID of the Custom Integration Source. Found in the console URL after navigating to Accounts -> Custom Integrations and clicking the integration name.
RUNZERO_IMPORT_TASK_NAME - Name of the Custom Integration Source. Created in the console under Accounts -> Custom Integrations.

GVM_BASE_URL - The domain or IP of the GVM instance, minus any resource path e.g. "http://my.gvm.instance"
GVM_PORT - The port the GVM web interface is running on
GVM_USERNAME - Username for an account with sufficient privileges to call Gmp.get_hosts()
GVM_PASSWORD - Password for the account
```

## GVM Configuration

There are multiple methods for connecting to the GVM API: Unix socket connection, SSH, and TLS. Additional configurations must be made if using the GVM community edition container as well. Each of these methods and configurations are discussed below.

### Method 1: Unix Socket

Using the Unix socket is the simplest method to connect to the GVM API with the caveat that the connections must be made on localhost, therefore this integrations script must run on the same host as GVM.

Per python-gvm docs:

"If gvmd is provided by a package of the distribution, it should be /run/gvmd/gvmd.sock. If gvmd was built from source and did not set a prefix, the default path can be used by setting path = None"



### Method 2: SSH

### Method 3: TLS

## Getting Started

- Clone this repository

```
git clone https://github.com/TechnoSavage/runZero.git
```

- Clone .env_sample to .env under the same directory

```
cd runZero/custom_integrations/GVM
cp .env_sample .env
```

- Update all of the secrets in the `.env` needed based on the script you'd like to run (NOTE: you need to rerun pipenv shell anytime you update these  values to reload them)

- Install dependancies

```
pipenv install -r requirements.txt
```

- Enter pipenv
w
```
pipenv shell
```
- In your runZero console, navigate to Account -> Custom Integrations -> Add custom integration. Name the integration consistent to the parameter RUNZERO_IMPORT_TASK_NAME in the .env file. Optionally upload an image for the source. 
(This step is optional; the script will create the source if it doesn't already exist.)

- run the script to sync assets. Sync can be scheduled with a job scheduler such as cron