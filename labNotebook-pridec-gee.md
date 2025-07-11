# Notes for PRIDE-C GEE package

## Common commands

`pipreqs`: save requirements.txt file with list of dependencies
`source .venv/bin/active`: activate venv

## 2025-07-11

All scripts and full workflow now in Python. Copying over to this directory and starting git repo. Had to do some extra set up of the `venv` and package management.

Was ahving an issue with `post_dataValues.py` because the json was getting weirdly formatted in python. I have fixed it by having the functions return `dictionary` rather than json_dump.

**TO DO:**
- fix fetch_sen1_flood.py, which is still giving an odd return format from GEE (not sure what is happening there)

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