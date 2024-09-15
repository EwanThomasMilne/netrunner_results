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
