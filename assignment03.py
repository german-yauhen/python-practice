# 1) Create a list of “person” dictionaries with a name, age and list of hobbies for each person.
# Fill in any data you want.
persons = [
    {'name': 'A', 'age': 20, 'hobbies': ['films', 'tv series']},
    {'name': 'B', 'age': 25, 'hobbies': ['music', 'theater']},
    {'name': 'C', 'age': 30, 'hobbies': ['gardening', 'swimming']}
]

# 2) Use a list comprehension to convert this list of persons into a list of names (of the persons).
names = [person['name'] for person in persons]

# 3) Use a list comprehension to check whether all persons are older than 20.
all_older_than_twenty = all([person['age'] > 20 for person in persons])

# 4) Copy the person list such that you can safely edit the name of the first person (without changing the original list).

copied_persons = [{'name': person['name'], 'age': person['age'], 'hobbies': person['hobbies']} for person in persons]
copied_persons = [person.copy() for person in persons]

print(f'Copied persons before changing the name of the first person: {copied_persons}')
copied_persons[0]['name'] = '123'
print(f'Persons {persons}')
print(f'Copied persons after changing the name of the first person: {copied_persons}')

# 5) Unpack the persons of the original list into different variables and output these variables.
p_one, p_two, p_three = persons