name = ""
age = 0


def greeting():
    global name, age
    name = input("Enter your name: ")
    age = int(input("Enter your age: "))


def pring_as_one_string(first, second):
    print(f"{first}, {second}")


def num_of_decades(age):
    return int(age) // 10


greeting()

pring_as_one_string(
    f"Hey {name}", f"you've already lived {num_of_decades(age)} decades"
)

pring_as_one_string(False, 'Random')
