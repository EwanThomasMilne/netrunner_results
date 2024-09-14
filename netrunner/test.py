from identity import Identity

print('=== Test 1 - AgInfusion: New Miracles for a New World (proper name) ===')
id1 = Identity('AgInfusion: New Miracles for a New World')
print('full name: ' + id1.name)
print('faction: ' + id1.faction)
print('short name: ' + id1.short_name)

print('=== Test 2 - Esa Afontov: Eco-Insurrectionist (alt spelling) ===')
id2 = Identity('Esa Afontov: Eco-Insurrectionist')
print('full name: ' + id2.name)
print('faction: ' + id2.faction)
print('short name: ' + id2.short_name)

print('=== Test 3 - PD (short name) ===')
id3 = Identity('PD')
print('full name: ' + id3.name)
print('faction: ' + id3.faction)
print('short name: ' + id3.short_name)