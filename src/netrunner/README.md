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