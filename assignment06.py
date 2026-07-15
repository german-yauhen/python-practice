file_path: str = './assignment06.txt'
# 1) Write a short Python script which queries the user for input 
# (infinite loop with exit possibility) and writes the input to a file.
def solution1():
    print('Type anything you want')
    input_is_active = True
    while input_is_active:
        user_input = input('Waiting your input: ')
        user_input_lowercase = user_input.casefold()
        if user_input_lowercase == 'q' or user_input_lowercase == 'quit':
            print('Quitting...')
            input_is_active = False
        if user_input_lowercase == 'p' or user_input_lowercase == 'print':
            print_file_content()
        else:
            with open(file_path, mode='a') as f:
                f.write(f'{user_input}\n')
        
        

# 2) Add another option to your user interface: 
# The user should be able to output the data stored in the file in the terminal.
def print_file_content():
    print(f"File '{file_path}' contains the following content:")
    with open(file_path, mode='r') as f:
        [print(line[:-1]) for line in f.readlines()]

solution1()
print_file_content()
        