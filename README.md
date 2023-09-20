# runZero
Scripts and projects using runZero

## Background

Requirements (Global)

- Python 3.8+
- pipenv - https://pypi.org/project/pipenv/

## runZero API Docs

- Using the API - https://www.runZero.com/docs/organization-api/
- Swagger Docs- https://app.swaggerhub.com/apis/runZero/runZero/3.6.0

## Configuration Explained

- There is a sample environment variables file called .env_sample under the root folder of this project
- You will clone this file and create one called .env where you actually input all of your secrets (API Keys + Access Key Pairs)
- Parameters - explanations of what you see in .env_sample

```
RUNZERO_BASE_URL - The domain or IP of the runZero console, minus any resource path e.g. "https://console.runzero.com"
RUNZERO_ORG_ID - UUID of the Organization to which integration will send data. Found in the console URL after navigating to Organizations and clicking organization name
RUNZERO_SITE_NAME - Name of the site to which the integration will send data.  
RUNZERO_SITE_ID - UUID of the Site to which integration will send data. Found in the console URL after navigating to Sites and clicking site name.
RUNZERO_CLIENT_ID - runZero API client ID. Created in the console under Account -> API clients
RUNZERO_CLIENT_SECRET - Associated API client secret to the above ID. Displayed when creating an new API client
RUNZERO_EXPORT_TOKEN - used for data export
RUNZERO_ORG_TOKEN - used to for management
RUNZERO_ACCOUNT_TOKEN - The account API token for the console instance. Found in the console under Account -> Account Settings -> Account API keys
```

## Getting Started

- Clone this repository

```
git clone https://github.com/TechnoSavage/runZero.git
```

- Clone .env_sample to .env under the same directory

```
cp .env_sample .env
```

- Update all of the secrets in the `.env` needed based on the script you'd like to run (NOTE: you need to rerun pipenv shell anytime you update these values to reload them)

- Install dependancies

```
pipenv install -r requirements.txt
```

- Enter pipenv

```
pipenv shell
```
