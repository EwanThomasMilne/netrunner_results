# netrunner_results
A collection of tools/scripts for agregating results from tournaments.nullsignal.games and aesopstables.net

## Winrate

## Matches

```
    python3 ./matches/generate_match_report.py
```

reads config from **config.yml**

outputs all match results in CSV format to results.csv

## Standings

*Cobra only--Aesops is not currently implemented*

```
    python3 ./standings/generate_standings.py
```

outputs standings in CSV format to **TOURNAMENT-NAME.standings.csv**

reads config from **config.yml**

## config.yml

```
---
tournaments:
  - name: "EMEA"
    url: "https://tournaments.nullsignal.games/tournaments/3466"
  - name: "ACC"
    url: "https://www.aesopstables.net/475"
```
