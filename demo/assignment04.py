# 1) Write a normal function that accepts another function as an argument.
# Output the result of that other function in your “normal” function.
def apply_action(a, b, action):
    return action(a, b)

def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

a = 3
b = 5
print(apply_action(a, b, add))
print(apply_action(a, b, multiply))

# 2) Call your “normal” function by passing a lambda function –
#  which performs any operation of your choice – as an argument.
print(apply_action(2,3, lambda a, b: a + b))

# 3) Tweak your normal function by allowing an infinite amount of arguments 
# on which your lambda function will be executed.
def apply_action_to_many(*arguments, action):
    for arg in arguments:
        print(action(arg))

apply_action_to_many(2, 4, 6, action=lambda arg: pow(arg, 2))
# 4) Format the output of your “normal” function such that numbers look nice  and are centered in a 20 character column.
print(f'{apply_action(2, 5, multiply):^20}')