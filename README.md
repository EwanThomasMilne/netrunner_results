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

outputs standings in CSV format to **OUTPUT/standings/DATE.NAME.standings.csv**

outputs results in CSV format to **OUTPUT/results/DATE.NAME.results.csv**

outputs player data in JSON format to **OUTPUT/players/NRDB_ID.json**

reads config from **config.yml**

## config.yml

```yaml
---
meta:
  24.03
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
