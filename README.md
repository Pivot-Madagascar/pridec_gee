# pridec-gee package

These python scripts are used to inject PRIDE-C climate variables into a dhis2 instance.

## Pre-requisites

### DHIS2 Instance

Your DHIS2 instance must already have the PRIDE-C metadata structure in place. This includes the creation of the `dataElements` necessary for PRIDE-C to run. More info can be found at this configuration repo: https://gitlab.com/pivot-dev/PRIDE-C/create-dev-dhis2

For testing, it is recommended that you use a local instance via `d2` or the PRIDE-C Test instance (does not exist yet as of July 2025). Otherwise it will replace the climate data that we need for production.

You will need to either create a personal access token to access this account or have access to a username/password that can POST PRIDE-C `dataElements`. 

### Google Earth Engine Account

This workflow requires an activated GEE account and project that will be verified through the following call:

```
ee.Authenticate() #eventaully use token from environment
ee.Initialize(project=os.environ.get("GEE_PROJECT"))
```

We will eventually update this so that it can use a Token for Authentication, rather than manually athenticating via a browser. Code for this is in the ETL app developed by Mariot: https://gitlab.com/pivot-dev/PRIDE-C/pride-c-api

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
DHIS_URL_PRIDEC="http://44.218.51.103:8080/" #PRIDE-C URL, can replace with local one
TOKEN_DHIS_PRIDEC= YOUR_DHIS_TOKEN
PARENT_OU_ID="VtP4BdCeXIo" #corresponds to Ifanadiana in PRIDE-C PRIDE-C and PIVOT instances
GEE_PROJECT= YOUR_GEE_PROJECT_NAME
```

4. Run `fetch_all_climate_pridec.py` file

This python file goes through the climate variables one by one to download them from GEE and then POST to a DHIS2 instance. It is curently set up to use a local test instance launched with `d2 to avoid interfering with the production server. Please update as needed for your own configuration (i.e. base_url, token, etc.).

*Note: Each function/step of this file will likely correspond to a controller in the ultimate ETL app*