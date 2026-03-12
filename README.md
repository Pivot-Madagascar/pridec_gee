# pridec-gee 

A python library to extract environmental and climate variables from DHIS2 polygons and optionally import the data into a DHIS2 instance

## Pre-requisites

### DHIS2 Instance

Any DHIS2 instance can be used for the extraction of climate variables if it has associated polygons for the orgUnits of interest.

If you would like to import the climate variables into the DHIS2 instance, the PRIDE-C metadata must already be in place. Please see [`docs/pridec-climate-metadata.json`](docs/pridec-climate-metadata.json) for a list of dataElements to create. More info can be found at this [configuration repo](https://gitlab.com/pivot-dev/PRIDE-C/create-dev-dhis2).

For testing, it is recommended that you use a local instance via the [DHIS2 CLI](https://developers.dhis2.org/docs/cli/).

You will need to either create a personal access token to access this account or have access to a username/password that can acces the geojson data and POST dataElements. 

### Google Earth Engine Service Account

This workflow requires an activated GEE service account, project, and service token. The information for this is stored in `.gee-private-key.json`. You can create your account following instructions [here](https://developers.google.com/earth-engine/guides/service_account#use-a-service-account-with-a-private-key).

The GEE account can then either be authenticated via script or interactively:

```
#via script
credentials = ee.ServiceAccountCredentials(GEE_SERVICE_ACCOUNT, ".gee-private-key.json")
ee.Initialize(credentials)

#interactively
ee.Authenticate() 
ee.Initialize(project=os.environ.get("GEE_PROJECT"))
```

### Python 

This requires Python>=3.12.

## Installation

**via github**

```
pip install git+https://github.com/Pivot-Madagascar/pridec-gee.git
```
**via pyPI**

```
pip install pridec_gee
```

## Usage

### Create  `.env` file

The library uses several sensitive variables that can be provided via script or `.env` file. An example `.env` file is below:

```
DHIS_URL='http://your-dhis-url.com' 
DHIS_TOKEN='YOUR_DHIS_TOKEN' #or userame and password
DHIS_USER='your-dhis-username'
DHIS_PWD='your-dhis-password'

PARENT_OU='parent-orgunit-uid' #usually an 11 character string from DHIS2, corresponding to parent unit containing orgUnits of interest
OU_LEVEL='5' # corresponds to orgUnit hierarchy level for which you want to extract variables
GEE_PROJECT='YOUR_GEE_PROJECT_NAME'
GEE_SERVICE_ACCOUNT='YOUR_SERVICE_ACCOUNT@YOUR_CLOUD_PROJECT.iam.gserviceaccount.com'
```

### (Opt) Back up sql database on server

If you are not using a test server, it is recommended to back up the SQL database before importing climate variables.

```
sudo -u postgres pg_dump dhis2 | gzip > NAME_OF_FILE.sql.gz
```

### Extract climate vairables

Individual climate variables can be extracted using the `fetch_*` functions by providing a `FeatureCollection` of the orgUnits and a dateRange to extract.  An example python script using the DHIS2 play instance is in [`docs/example.py`](docs/example.py).

The `import_pridec_climate` function runs the full PRIDE-C climate variable extraction and importation process if your DHIS2 instance contains the appropriate metadata structure.