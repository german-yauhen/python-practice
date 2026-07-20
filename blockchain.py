from functools import reduce
from hash_util import hash_block, hash_string_256
from collections import OrderedDict
import json
import pickle
from block import Block

MINING_REWARD = 10

blockchain = []
open_transactions = []
owner = "Eugene"

participants = {owner}


def load_data_with_pickle():
    with open("blockchain.p", mode="rb") as f:
        file_content = pickle.loads(f.read())
        global blockchain
        global open_transactions
        blockchain = file_content["chain"]
        open_transactions = file_content["open_trxs"]


def save_data_with_pickle():
    with open("blockchain.p", mode="wb") as f:
        data = {"chain": blockchain, "open_trxs": open_transactions}
        f.write(pickle.dumps(data))


def load_data():
    try:
        with open("blockchain.txt", mode="r") as f:
            file_content = f.readlines()
            global blockchain
            global open_transactions
            blockchain_read = json.loads(file_content[0][:-1])
            blockchain_restored = []
            for block in blockchain_read:
                restored_txs = [
                    OrderedDict(
                        [
                            ("sender", trx["sender"]),
                            ("recipient", trx["recipient"]),
                            ("amount", trx["amount"]),
                        ]
                    )
                    for trx in block["transactions"]
                ]
                restored_block = Block(
                    index=block["index"],
                    previous_hash=block["previous_hash"],
                    proof=block["proof"],
                    transactions=restored_txs,
                    timestamp=block["timestamp"],
                )
                blockchain_restored.append(restored_block)
            blockchain = blockchain_restored

            open_transactions_read = json.loads(file_content[1])
            open_transactions_restored = []
            for trx_read in open_transactions_read:
                trx_restored = OrderedDict(
                    [
                        ("sender", trx_read["sender"]),
                        ("recipient", trx_read["recipient"]),
                        ("amount", trx_read["amount"]),
                    ]
                )
                open_transactions_restored.append(trx_restored)
            open_transactions = open_transactions_restored
    except (IOError, IndexError):
        genesis_block = Block(0, "", [], 10, 0)
        blockchain.append(genesis_block)
        open_transactions = []
    finally:
        print("Loaded!")


load_data()
# load_data_with_pickle()


def save_data():
    try:
        with open("blockchain.txt", mode="w") as f:
            saveable_chain = [block.__dict__ for block in blockchain]
            f.write(json.dumps(saveable_chain))
            f.write("\n")
            f.write(json.dumps(open_transactions))
    except IOError:
        print("Saving failed!")


def get_last_blockchain_value():
    """Returns the last value of the currrent blockhain."""
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def verify_transaction(transaction):
    sender_balance = get_balance(transaction["sender"])
    return sender_balance >= transaction["amount"]


def add_transaction(sender, recipient, amount=1.0):
    """Transfers coins from a sender to a recipient.
    Arguments:
        :sender:    The sender of the coins
        :recipient: The recioient of the coins
        :amount:    The amount of coint sent with the transaction (default = 1.0)
    """
    transaction = OrderedDict(
        [("sender", sender), ("recipient", recipient), ("amount", amount)]
    )
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    return False


def valid_proof(transactions, previous_hash, proof):
    guess = (str(transactions) + str(previous_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    print(guess_hash)
    return guess_hash[0:2] == "00"


def proof_of_work():
    last_block = blockchain[-1]
    hash_last_block = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, hash_last_block, proof):
        proof += 1
    return proof


def get_balance(participant):
    sent_amounts = [
        [tx["amount"] for tx in block.transactions if tx["sender"] == participant]
        for block in blockchain
    ]
    sent_amounts_open = [
        tx["amount"] for tx in open_transactions if tx["sender"] == participant
    ]
    sent_amounts.append(sent_amounts_open)
    total_sent = reduce(
        lambda sent_sum, sent_amount: (
            sent_sum + sum(sent_amount) if len(sent_amount) > 0 else sent_sum + 0
        ),
        sent_amounts,
        0,
    )
    # for sent_amount in sent_amounts:
    #     if len(sent_amount) > 0:
    #         total_sent += sent_amount[0]

    received_amounts = [
        [tx["amount"] for tx in block.transactions if tx["recipient"] == participant]
        for block in blockchain
    ]
    total_received = reduce(
        lambda received_sum, received_amount: (
            received_sum + sum(received_amount)
            if len(received_amount) > 0
            else received_sum + 0
        ),
        received_amounts,
        0,
    )
    # for received_amount in received_amounts:
    #     if len(received_amount) > 0:
    #         total_received += received_amount[0]

    return total_received - total_sent


def mine_block():
    """Creates a new block storing a hash of the formed block.
    Returns True if the operations succeds otherwise False"""
    last_block = blockchain[-1]
    previous_hash = hash_block(last_block)
    proof = proof_of_work()
    reward_transaction = OrderedDict(
        [("sender", "MINING"), ("recipient", owner), ("amount", MINING_REWARD)]
    )
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    new_block = Block(len(blockchain), previous_hash, copied_transactions, proof)
    blockchain.append(new_block)
    print(f"The new block formed: {new_block}")
    return True


def get_transaction_value():
    """Returns the input of a user (a new transaction amount) as a float."""
    tx_recipient = input("Enter the recipient of the transaction: ")
    tx_amount = float(input("Your transaction amount please: "))
    return (tx_recipient, tx_amount)


def pring_blockchain_elements():
    for block in blockchain:
        print(f"Outputting block: {block}")
    else:
        print("-" * 20)


def verify_chain():
    """Verify the current blockchain and return True if it's validm False otherwise"""
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block.previous_hash != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
            print("Proof of work is invalid")
            return False
    return True


def verify_transactions():
    return all([verify_transaction(tx_open) for tx_open in open_transactions])


input_is_active = True

while input_is_active:
    print("Please choose an action:")
    print("1: Add a new transacton value.")
    print("2: Mine a new block")
    print("3: Output the blockchain blocks.")
    print("q: Quit")
    user_choice = input("Your choice: ")
    if user_choice == "1":
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        if add_transaction(owner, recipient, amount):
            print("Added transaction")
        else:
            print("Transaction failed")
        print(open_transactions)
    elif user_choice == "2":
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == "3":
        pring_blockchain_elements()
    elif user_choice == "4":
        print(participants)
    elif user_choice == "5":
        if verify_transactions():
            print("All open transactions are valid")
        else:
            print("At least one open transaction is invalid")
    elif user_choice == "q" or user_choice == "Q":
        input_is_active = False
        save_data()
    else:
        print(f"Wrong input: '{user_choice}'")
    if not verify_chain():
        print("Blockchain is invalid!")
        input_is_active = False
    print("Balance of {}: {:.4f}".format(owner, get_balance(owner)))
else:
    print("Quitting...")
