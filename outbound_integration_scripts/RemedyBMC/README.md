# runZero asset export to Remedy BMC
Outbound integration designed to pull asset information from the runZero export API, map asset data fields to Remedy BMC, and upload asset data to Rememdy BMC.

## Background

Requirements (Global)

- Python 3.8+
- pipenv - https://pypi.org/project/pipenv/

## Remedy BMC API Docs

## Configuration Explained

- There is a sample environment variables file called .env_sample under the root folder of this project
- Clone this file and create one called .env to input the below variables such as secrets (API Keys + Access Key Pairs)
- Parameters - explanations of what you see in .env_sample

`RUNZERO_BASE_URL` - The domain or IP of the runZero console, minus any resource path e.g. https://console.runzero.com

`RUNZERO_EXPORT_TOKEN` - Export API token for the runZero Organization to retrieve asset data from

`REMEDY_BASE_URL` - The domain or IP of the Remedy BMC console e.g. https://<your-instance>.bmc.com/api

`REMEDY_USERNAME` - The Remedy BMC username to use for authentication and retrieval of the JWT 

`REMEDY_PASSWORD` - The Remedy BMC password to use for authentication and retrieval of the JWT

`CSV_FILE_PATH` - Path to save location of generated CSV file

## Getting Started

- Clone this repository

```
git clone https://github.com/TechnoSavage/runZero.git
```

- Clone runZero/outbound_integration_scripts/RemedyBMC/.env_sample to .env under the same directory

```
cd runZero/outbound_integration_scripts/RemedyBMC
cp .env_sample .env
```

- Update all of the secrets in the `.env` file (NOTE: you need to rerun pipenv shell anytime you update these  values to reload them)

- Install dependancies

```
pipenv install -r requirements.txt
```

- Enter pipenv

```
pipenv shell
```

- run the script to sync assets to Remedy BMC. Sync can be scheduled with a job scheduler such as cron.
