# Notes for PRIDE-C GEE package [pridec_gee]

## Common commands

`pipreqs`: save requirements.txt file with list of dependencies
`pip install -r requirements`: install requirements
`source .venv/bin/activate`: activate venv
`pip install -e .`: install editable for during development
`pytest path/to/file -vv`: run all pytests in verbose mode
`uv run coverage run -m pytest -v`: pytest via uv
`uv run ruff check`: code formatting

## To Publish a release

```
#PR into main branch
# update version in toml
git add pyproject.toml
git commit -m "update version to X.X.X"
git push

git tag vX.X.X
git push origin vX.X.X
#manually add relase on github

# to publish on pyPI
uv publish
```

## 2026-04-24

Writing a fetch function for the climate variables that returns the data locally rather than pushing it to an instance. This allows it to be used in other instances. It probably makes sense to combine this with the import function and then just send one POST rather than multiple? REalistically the three month updates are relatively small and larger ones would be done manually. Thsi does invovle turning files from datafames to json and back again, but I don't think that will be much overhead really. Or I could just drop that from the individual fetch files since it is very easy to turn into a json format.

NEW WORKFLOW: fetch_* functions return a pandas dataFrame. This is then turned into a json file to POST to DHIS2. I could eventually split these up or apply a function to the lsit if I wanted, but it makes sense to have them return dataFrames rather than going back and forth and basically just only use JSON when posting.

I have created a function `fetch_climate_gee` that I now just need to link into the import function. Soemthign isn't working quite in the testing of it for the proportionFire but I'm not super sure why, it may just be due to dataquality, but I thought it all got filled in kind of automatically. The test works now, just needed to reload the package.

Updated import_pridec_climate to also use this workflow. Hopefully this helps reduce duplication a bit.

Updated example document to show how to fetch variables

**TO DO:**
- ~~test fetch_climate_gee~~
- ~~update import_pridec_climate to use fetch_climate_gee. Update tests too~~


## 2026-04-23

Turned off the GHA becuase it was using a lot of minutes and wasn't really necessary for publishing. Using versions and releases manually now.

Working on things corresponding to [issue #6](https://github.com/Pivot-Madagascar/pridec_gee/issues/6), specifically being able to select variables in the importation step and fetch steps.

**TO DO**:
- ~~add variables to individual fetch functions~~
- ~~add variables to import_ function~~
- write seperate fetch function to do multiple at once and combine into a Pandas DF

## 2026-04-20

Getting pytests working if I can. Added coverage checker and github actions. 

The github actions will run the tests on any PR to the main branch. I also created something for automatic publishing to PyPI and for github releases. I just need to do a quick test to be sure it works. Created a seperate branch to test the PR workflow.

Everythign works but I need to add a PAT that allows for posting releases for the github action to work I think: https://docs.github.com/en/rest/releases/releases?apiVersion=2026-03-10#create-a-release

**TO DO:**
- publish v1.0.0

## 2026-03-12

Package is nearly ready to publish the first version of. I have updated function documentation, updated package docmuentation, and am now just building out tests. To do is now tracked by the issue tracker on github.

**TO DO:**
- run pytests
- check uv
- publish on PyPI

## 2026-03-02

The wrapper function seems to work, but the error messages leave a lot to be desired. I will need to work on this and the testing in the future.

Doign some ad-hoc testing in `scratch/test_package.py`

Saved pivot-specific rice fields in a data place.

FEWSNET has a super slow latency. For example, today, it only has the data available for January (not Feb), and won't have February until the end of march. So I will just drop from analyses for now. Done, except actulaly it is doing it based on the label and not the end date. So I need to fix that. [done]

REalized I don't even use the start and end lable bits of the date range so this could just be two string dates without a name, which would be must easier. I just ened to update all the functions to deal with that. But that can be done later. [done]

Tested the climate_docker_service on a local isntance and it worked!

**TO DO:**
- configure full testing infrastructure with env variables and offline testing [still working on getting something to work with tokens]
- document and build with `uv`
- update docker with this package and scripts for certain calls `climate_docker_service.py` has this for now.


## 2026-02-27

Writing wrapper function so it should then be able to be integrated into the docker image. Nearly done


**TO DO**
- configure full testing infrastructure with env variables and offline testing [still working on getting something to work with tokens]
- document and build with `uv`
- wrap wrapper function to run multiple climate variables at once. Then each can be turned on/off in one call.


## 2026-02-25

Started restructuring using a `src` directory structure. Also rewrote the fetch functions to be more generalizable for other needs with DHIS2 data and GEE. And wrote tests for the functions.

All of the gee functions have been updated and tested.

I need to decide whether I want to leave the DHIS2 functions here or not? I think the ability to delete and manage the climate data could be useful. So like, POST, DELETE, GET names of dataElements with climate? Also getting the geojson. This way everything could just be done in this package if needed. I will get rid of the analytics launching though. And still make a seperate package for Pivot's own dhis2 tools. [done]

**TO DO**
- configure full testing infrastructure with env variables and offline testing [still working on getting something to work with tokens]
- rewrite/structure dhis2 module [done]
- document and build with `uv`
- wrap wrapper function to run multiple climate variables at once. Then each can be turned on/off in one call.

## 2026-02-23

I've renamed the github repo for this so that it follows Python naming conventions. 

**TO DO**:
- restructure code [remove delete,get,post, etc.]
- use actual gee_s1_processing package [ actually not using this because it is a bit too different]

## 2026-02-19

I may work on creating the package in a seperate branch so as not to mess with this one as much. In a package-dev branch now.

Also, rahter than directly copying the python files for the Sentinel-1 processing, it may be easier to just call the package, now that it seems to be supported in PyPI: https://github.com/LSCE-forest/gee_s1_processing/tree/main (https://libraries.io/pypi/gee_s1_processing).

i also renamed the repo to pridec_gee so that it works in PyPI. I think I will essentially just expose the main climate_data function, and then add argumnets so the user can choose what to import. I will have to think abotu how the flood data works since that is the one fully specific to Pivot (or at least this region of Mada). I could add something so the threshold can be user supplied for other regions? But for now I will leave. IT also depends on data specific to us, but that could be provided I guess.


## 2026-02-10

Given our current ETL structure, we have decided the easiest way to use these scripts (and make it shareable), is to structure it as a python package. This will involve restructuring and cleaning up the repo a bit, and then doing the changes we decided on after havin Toky test it.

## 2025-08-11

Spoke with Paul and we've decided we will leave this within docker and just add it as a seperate service like `import-gee`.  Beofre I move it to docker I need to do the following:

- investigate why sen2 indicators are different and fix: I think this was becuase I was using top of atmosphere reflectnce instead of SR. It is stil different values than from befoe when I was using javascript, but the seasonality of this seems more realistic, so I will just delete the past 10 years of data and replace it with this new data. This also involved adding a looping functionality to side step the 5000 limit. This could eventually be added to the other fetch functions as well.

- add delete functinality to remove data before adding new data (this may fix sen2 issue): created two seperate functions for this. `delete_dataValues` just deletes those in the json file that we are are to POST while `delete_historic_climate` gives more control over the time period and deletes a full range of data.

- add call for launching analytics to the workflow. [done]

Okay I will test this on a local instance, then run it on our production one so that the data is updated. Done.


**TO DO:**
- move this workflow over to Docker


## 2025-08-08

Finishing up the sen1 flooding workflow. I will just use this like normal to update PRIDE-C for now so it is done.

To add to a docker workflow, I will need to change it to use a GEE token instead of ee.Authorize(), I think? Done following instructions here: https://developers.google.com/earth-engine/guides/service_account#use-a-service-account-with-a-private-key. Updated README.md to take this into account.

this means it should mostly be ready for Docker, but I can work on that next week.

There also seems to be an issue with the sen2 indicators being super different than those gotten through javascript. I need to investigate that function

**TO DO:**
- add call to start analytics to the workflow
- troubleshoot sen2 indicators
- functionality for deleting old climate data when needed: I think this can just be my own util script in `pridec-utils`
- add tests
- combine into an actual package? or just leave as is within docker

## 2025-08-07

Working on integrating this into the Docker workflow. I may add as a service? But for now, it is just launched locally.

Updating the env variables to match that used by the Docker workflow so the same `.env` file can be used. also added some notification messages for the user.

Fixed the bugs in the sen1 flooding. some were coming from the ARD code and some were coming from mine. All that is left to do is change the `comm_fkt` to `orgUnit` and format for JSONs.

**TO DO:**
- ~~fix fetch_sen1_flood.py, which is still giving an odd return format from GEE (not sure what is happening there)~~
- ~~option to just POST more recent climate data (I am 99% sure we already do this)~~
- functionality for deleting old cliamte data when needed (sometimes partial months will mess things up)
- ~~function to check quality of climate data [remove outliers? ensure it is in a reasonable range for each variable]~~: This is done in each variables fetch now.
- write tests? or will this be in the ETL package?

## 2025-07-11

All scripts and full workflow now in Python. Copying over to this directory and starting git repo. Had to do some extra set up of the `venv` and package management.

Was ahving an issue with `post_dataValues.py` because the json was getting weirdly formatted in python. I have fixed it by having the functions return `dictionary` rather than json_dump.

**TO DO:**
- fix fetch_sen1_flood.py, which is still giving an odd return format from GEE (not sure what is happening there)
- option to just POST more recent climate data (I am 99% sure we already do this)
- functionality for deleting old cliamte data when needed (sometimes partial months will mess things up)
- function to check quality of climate data [remove outliers? ensure it is in a reasonable range for each variable]
- write tests? or will this be in the ETL package?

## 2025-04-11

All of the GEE scripts are now written in Javascript and work by providing the orgUnit that you want to extract for.

The Sen1 flooding just seems a little suspect becuase it seems to be highest at the driest part of the year. I am torn between just using this, since it is the published method, or dropping it for now. It may also be that it is catching the backscatter from dry, untilled land that is also reflective like water.

Here is code to inspect it:

```
sen1 <- read.csv("Downloads/sen1_Flooding.csv")


library(dplyr)
library(ggplot2)

range(na.omit(sen1$floodProp))
hist(sen1$floodProp)


sen1 |>
  filter(comm_fkt %in% sample(unique(comm_fkt),3)) |>
  mutate(date = as.Date(date)) |>
  # mutate(floodProp = ifelse(is.na(floodProp), 0, floodProp)) |>
  mutate(flood_mean = mean(floodProp, na.rm = TRUE),
            .by = c("comm_fkt", "date")) |>
  ggplot(aes(x = date, y = floodProp)) +
  geom_point(aes(group = rice_id)) +
  geom_line(aes(group = comm_fkt), color = "red") +
  facet_wrap(~comm_fkt)

sen1 |>
  filter(comm_fkt %in% sample(unique(comm_fkt),9)) |>
  mutate(date = as.Date(date)) |>
  # mutate(floodProp = ifelse(is.na(floodProp), 0, floodProp)) |>
  mutate(year_month = substr(date, 1,7)) |>
  summarise(flood_mean = mean(floodProp, na.rm = TRUE),
             .by = c("comm_fkt", "year_month")) |>
  mutate(date = as.Date(paste(year_month, "01", sep = "-"))) |>
  mutate(flood_sub  = 1 - flood_mean) |>
  ggplot(aes(x = date, y = flood_mean)) +
  geom_line() +
  facet_wrap(~comm_fkt)
```