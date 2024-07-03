# netrunner_results
A collection of tools/scripts for agregating results from tournaments.nullsignal.games and aesopstables.net

<<<<<<< Updated upstream
=======
## Requirements
* Python 3.10+

```
  pip install -r requirements.txt
```

## Winrate

## Matches

```
  python3 ./matches/generate_match_report.py
```

reads config from **config.yml**

outputs all match results in CSV format to results.csv

>>>>>>> Stashed changes
## Standings

*Cobra only--Aesops is not currently implemented*

```
  python3 ./standings/generate_standings.py
```

reads config from **config.yml**

```
---
tournaments:
  - name: emea
    url: "https://tournaments.nullsignal.games/tournaments/3466"
```

outputs standings in CSV format to **TOURNAMENT-NAME.standings.csv**
