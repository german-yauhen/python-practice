from uuid import uuid4

from blockchain import Blockchain
from verification import Verification

 
class Node:

    def __init__(self):
        # self.uuid = str(uuid4())
        self.uuid = "Eugene"
        self.blockchain = Blockchain(self.uuid)

    def listen_for_input(self):
        input_is_active = True
        while input_is_active:
            print("Please choose an action:")
            print("1: Add a new transacton value.")
            print("2: Mine a new block")
            print("3: Output the blockchain blocks.")
            print("4: Verify transactions.")
            print("q: Quit")
            user_choice = input("Your choice: ")
            if user_choice == "1":
                try:
                    tx_data = self.get_transaction_value()
                    recipient, amount = tx_data
                    if self.blockchain.add_transaction(self.uuid, recipient, amount):
                        print("Added transaction")
                    else:
                        print("Transaction failed")
                    print(self.blockchain.get_open_transacitions())
                except (IOError, ValueError):
                    print(f"Wrong input: '{user_choice}'")
                    input_is_active = False
            elif user_choice == "2":
                self.blockchain.mine_block()
            elif user_choice == "3":
                self.print_blockchain_elements()
            elif user_choice == "4":
                if Verification.verify_transactions(
                    self.blockchain.get_open_transacitions(), self.blockchain.get_balance
                ):
                    print("All open transactions are valid")
                else:
                    print("At least one open transaction is invalid")
            elif user_choice == "q" or user_choice == "Q":
                input_is_active = False
                self.blockchain.save_data()
            else:
                print(f"Wrong input: '{user_choice}'")
            if not Verification.verify_chain(self.blockchain.chain):
                print("Blockchain is invalid!")
                input_is_active = False
            print(
                "Balance of {}: {:6.2f}".format(self.uuid, self.blockchain.get_balance())
            )
        else:
            print("Quitting...")

    def get_transaction_value(self):
        """Returns the input of a user (a new transaction amount) as a float."""
        tx_recipient = input("Enter the recipient of the transaction: ")
        tx_amount = float(input("Your transaction amount please: "))
        return (tx_recipient, tx_amount)

    def print_blockchain_elements(self):
        for block in self.blockchain.chain:
            print(f"Outputting block: {block}")
        else:
            print("-" * 20)


node = Node()
node.listen_for_input()
