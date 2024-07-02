# netrunner_results
A collection of tools/scripts for agregating results from tournaments.nullsignal.games and aesopstables.net

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
