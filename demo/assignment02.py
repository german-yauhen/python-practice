# 1) Create a list of names and use a for loop to output the length of each name (len()).
names = ["Alexander", "Eugene", "Erik", "Gareth", "Ava"]
for name in names:
    print(f"{name} has {len(name)} characters")

# 2) Add an if check inside the loop to only output names longer than 5 characters.
for name in names:
    if len(name) > 5:
        print(name)

# 3) Add another if check to see whether a name includes a “n” or “N” character.
for name in names:
    if len(name) > 5:
        print(name)
    if 'n' in name or 'N' in name:
        print(f'{name} contains either n or N character')

# 4) Use a while loop to empty the list of names (via pop())
cleared = False

while not cleared:
    if len(names) > 0:
        print('Removing the name from the tail...')
        names.pop()
    else:
        cleared = True
else:
    print(f'Cleared? -> {len(names) == 0}')
    
    
