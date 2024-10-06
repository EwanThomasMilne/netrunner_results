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

### Arguments
#### --- cache-refresh
By default, `netrunner_results.py` will use cached JSON (if available)
This argument overrides that default, and forces a refresh of any cached JSON

#### --- tournaments-file
defaults to `tournaments.yml`, but you can specify a different file if you just want to collect results for a smaller set of tournaments

## tournaments.yml

|parameter|required|type|description|default|
|---|---|---|---|---|
|url|**required**|string|tournament url||
|name|*optional*|string|tournament name|taken from tournament page|
|date|*optional*|date (ISO 8601)|tournament date|taken from tournament page|
|region|*optional*|string|EMEA/America/APAC||
|online|*optional*|boolean|online or offline tournament?|False|
|players|*optional*|dict|a dictionary of player to nrdb_id mappings for the tournament||
|abr_id|*optional*|int|the abr_id of the tournament||
|level|*optional*|string|worlds championship, continental championship, etc||


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
