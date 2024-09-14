# netrunner_results
A collection of tools/scripts for agregating results from tournaments.nullsignal.games and aesopstables.net

## Requirements
* Python 3.10+

```
  pip install -r requirements.txt
```

## Winrate

```
  python3 ./src/winrate/generate_report.py
```

reads config from **config.txt**

outputs win rate report to results.csv

## Matches

```
  python3 ./src/matches/generate_match_report.py
```

reads config from **config.yml**

outputs all match results in CSV format to results.csv

## Standings

*Cobra only--Aesops is not currently implemented*

```
  python3 ./src/generate_standings.py
```

outputs standings in CSV format to **TOURNAMENT-NAME.standings.csv**

reads config from **config.yml**

## config.yml

```yaml
---
tournaments:
  - name: "EMEA"
    url: "https://tournaments.nullsignal.games/tournaments/3466"
  - name: "ACC"
    url: "https://www.aesopstables.net/475"
```

## netrunner/identities.yml
There is an `Identity` class that you can use for easily handling identities. You can give it the full name, short name, or alt name (as definied in `netrunner/identities.yml`), of an Identity and it will get the id_data for that identity (again, from `netrunner/identities.yml`).  For example:

```python
  from netrunner.identity import Identity
  id = Identity('PD')
  print('full name: ' + id.name)
  print('faction: ' + id.faction)
  print('short name: ' + id.short_name)
```
would give the output
```
  full name: Haas-Bioroid: Precision Design
  faction: HB
  short name: PD
```
