# pridec-gee package

These python scripts are used to inject PRIDE-C climate variables into a dhis2 instance.

## Pre-requisites

### DHIS2 Instance

Your DHIS2 instance must already have the PRIDE-C metadata structure in place. This includes the creation of the `dataElements` necessary for PRIDE-C to run. More info can be found at this configuration repo: https://gitlab.com/pivot-dev/PRIDE-C/create-dev-dhis2

For testing, it is recommended that you use a local instance via `d2` or the PRIDE-C Test instance (does not exist yet as of July 2025). Otherwise it will replace the climate data that we need for production.

You will need to either create a personal access token to access this account or have access to a username/password that can POST PRIDE-C `dataElements`. 

### Google Earth Engine Service Account

This workflow requires an activated GEE servce account, project, and service token. The information for this is stored in `.gee-private-key.json`. Ask Michelle for a copy of this information, or create your own following instructions [here](https://developers.google.com/earth-engine/guides/service_account#use-a-service-account-with-a-private-key).

It can also be authenticated if being run interactively by uncommenting the below lines in `fetch_all_cimate_pridec.py`.

```
ee.Authenticate() #eventaully use token from environment
ee.Initialize(project=os.environ.get("GEE_PROJECT"))
```

### Python 

This requires Python 3.

## Usage

1. Clone the repo

```
git clone https://github.com/Pivot-Madagascar/pridec-gee.git
```

2. Initiate a `venv` in the root folder and install dependencies

```
python3 -m venv .venv --prompt="pridec-gee"
source .venv/bin/activate
pip install -r requirements.txt
```

3. Create  `.env` file

The `.env` file contains the configurations and tokens needed to run the script. It should have the following format:

```
DHIS2_PRIDEC_URL ="http://44.218.51.103:8080/" #PRIDE-C URL, can replace with local one
DHIS2_TOKEN= YOUR_DHIS_TOKEN
PARENT_OU="VtP4BdCeXIo" #corresponds to Ifanadiana in PRIDE-C PRIDE-C and PIVOT instances
GEE_PROJECT= YOUR_GEE_PROJECT_NAME
GEE_SERVICE_ACCOUNT='YOUR_SERVICE_ACCOUNT@YOUR_CLOUD_PROJECT.iam.gserviceaccount.com'
```

4. Run `fetch_all_climate_pridec.py` file

This python file goes through the climate variables one by one to download them from GEE and then POST to a DHIS2 instance. By default, it uses `dryRun` = `True` and will not actually change data on the instance. This can be changed by passing an environment variable directly to the `python`:

```
export DRYRUN="False" && python fetch_all_climate_pridec.py
```

It can also be added to your `.env` file, but we recommend explicitly specifying it to protect production instances.