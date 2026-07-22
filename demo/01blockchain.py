from random import Random, random


blockchain = []


def get_last_blockchain_value():
    """Returns the last value of the currrent blockhain."""
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def add_transaction(transaction_amount):
    """Takes a new value, creates a new node and appends the new node to the blockchain.

    Arguments:
        :transaction_amount: - the amount that should be added to form a node.
    """
    prevTx = get_last_blockchain_value()
    if prevTx == None:
        prevTx = [0]
    blockchain.append([prevTx, transaction_amount])


def get_transaction_amount():
    """Returns the input of a user (a new transaction amount) as a float."""
    return float(input("Transaction amount: "))


def pring_blockchain_elements():
    for block in blockchain:
        print(f"Outputting block: {block}")


def verify_chain():
    is_valid = True
    for index in range(len(blockchain)):
        if index == 0:
            continue
        elif blockchain[index][0] != blockchain[index - 1]:
            is_valid = False
            break
    else:
        print('Iterating over the blockchain nodes completed')
    # for block in blockchain:
    #     if index == 0:
    #         index += 1
    #         continue
    #     elif block[0] != blockchain[index - 1]:
    #         is_valid = False
    #         break
    #     index += 1
    # else:
    #     print('Iterating over the blockchain nodes completed')
    return is_valid

input_is_active = True

while input_is_active:
    print('Please choose an action:')
    print('1: Add a new transacton value.')
    print('2: Output the blockchain blocks.')
    print('m: Manipulate blockchain')
    print('q: Quit')
    user_choice = input('Yur choice: ')
    if user_choice == '1':
        txAmount = get_transaction_amount()
        add_transaction(txAmount)
        print(f"Block created: {get_last_blockchain_value()}")
    elif user_choice == '2':
        pring_blockchain_elements()
    elif user_choice == 'm':
        print(f'Blockchain before manipulation: {blockchain}')
        if len(blockchain) >= 1:
            r = Random().randint(0, len(blockchain) - 1)
            blockchain[r] = [-1]
        print(f'Blockchain after manipulation: {blockchain}')
    elif (user_choice == 'q' or user_choice == 'Q'):
        input_is_active = False
    else:
        print(f"Wrong input: '{user_choice}'")
    if not verify_chain():
        print('Blockchain is invalid!')
        input_is_active = False
else:
    print('Quitting...')
