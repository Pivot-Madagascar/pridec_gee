# Notes for PRIDE-C GEE package

## Common commands

`pipreqs`: save requirements.txt file with list of dependencies
`source .venv/bin/activate`: activate venv


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