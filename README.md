# netrunner_results
A collection of tools/scripts for agregating results from tournaments.nullsignal.games and aesopstables.net

## Requirements
* Python 3.10+

```
  pip install -r requirements.txt
```

## How To

```
  python3 ./src/netrunner_results.py
```
inputs tournaments from `tournaments.yml` and player details from `players.yml`

outputs standings in CSV format to `OUTPUT/standings/DATE.NAME.standings.csv`

outputs results in CSV format to `OUTPUT/results/DATE.NAME.results.csv`

outputs player data in JSON format to `OUTPUT/players/NRDB_ID.json`

## tournaments.yml

|parameter|required|type|description|default|
|---|---|---|---|---|
|url|**required**|string|tournament url||
|name|*optional*|string|tournament name|taken from tournament page|
|date|*optional*|date (ISO 8601)|tournament date|taken from tournament page|
|region|*optional*|string|EMEA/America/APAC||
|online|*optional*|boolean|online or offline tournament?|False|
|players|*optional*|dict|a dictionary of player to nrdb_id mappings for the tournament||


```yaml
---
meta:
  24.03:
    - url: https://www.aesopstables.net/440
      online: True
  24.05:
    - name: "EMEA"
      url: "https://tournaments.nullsignal.games/tournaments/3466"
      region: EMEA
    - name: "ACC"
      url: "https://www.aesopstables.net/475"
      online: True
      date: 2024-06-01
      region: America
```

## players.yml
```yaml
11479:
  aliases:
  - Kikai
  nrdb_name: Kikai
  teams:
  - EA Sports
39463:
  aliases:
  - not_yeti
  - Not Yeti
  nrdb_name: not_yeti
  teams:
  - EA Sports
```

### harvester.py
you can generate a new `players.yml` by using `src/harvestery.py` (this will overwrite any manual changes that have been made)

```
  python3 ./src/harvester.py
```
`harvester.py` uses nrdb to generate `OUTPUT/nrdb_ids.csv`, and also takes in team and alias data from `OUTPUT/sync_bre.csv`-- which is a export of the **DATA SHEET** page of the **SYNC BRE** google sheet