from functools import reduce
from hash_util import hash_block
import json
from block import Block
from transaction import Transaction
from verification import Verification

MINING_REWARD = 10


class Blockchain:

    def __init__(self, hosting_node_uuid):
        self.chain = [Block(0, "", [], 10, 0)]
        self.__open_transactions = []
        self.load_data()
        self.hosting_node_uuid = hosting_node_uuid


    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val


    def get_open_transacitions(self):
        return self.__open_transactions[:]

    # def _load_data_with_pickle(self):
    #     with open("blockchain.p", mode="rb") as f:
    #         file_content = pickle.loads(f.read())
    #         global blockchain
    #         global open_transactions
    #         blockchain = file_content["chain"]
    #         open_transactions = file_content["open_trxs"]

    # def _save_data_with_pickle(self):
    #     with open("blockchain.p", mode="wb") as f:
    #         data = {"chain": blockchain, "open_trxs": open_transactions}
    #         f.write(pickle.dumps(data))

    def load_data(self):
        try:
            with open("blockchain.txt", mode="r") as f:
                file_content = f.readlines()

                blockchain_restored = []
                for block in json.loads(file_content[0][:-1]):
                    restored_txs = [
                        Transaction(trx["sender"], trx["recipient"], trx["amount"])
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

                open_transactions_restored = []
                for trx_read in json.loads(file_content[1]):
                    trx_restored = Transaction(
                        trx_read["sender"], trx_read["recipient"], trx_read["amount"]
                    )
                    open_transactions_restored.append(trx_restored)

                self.chain = blockchain_restored
                self.__open_transactions = open_transactions_restored
        except (IOError, IndexError):
            pass
        finally:
            print("Loaded!")

    # load_data()
    # load_data_with_pickle()

    def save_data(self):
        try:
            with open("blockchain.txt", mode="w") as f:
                saveable_chain = [
                    block.__dict__
                    for block in [
                        Block(
                            block_elem.index,
                            block_elem.previous_hash,
                            [tx.__dict__ for tx in block_elem.transactions],
                            block_elem.proof,
                            block_elem.timestamp,
                        )
                        for block_elem in self.__chain
                    ]
                ]
                f.write(json.dumps(saveable_chain))
                f.write("\n")
                saveable_txs = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_txs))
        except IOError:
            print("Saving failed!")

    def proof_of_work(self):
        last_block = self.__chain[-1]
        hash_last_block = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(
            self.__open_transactions, hash_last_block, proof
        ):
            proof += 1
        return proof

    def get_balance(self):
        participant = self.hosting_node_uuid
        sent_amounts = [
            [tx.amount for tx in block.transactions if tx.sender == participant]
            for block in self.__chain
        ]
        sent_amounts_open = [
            tx.amount for tx in self.__open_transactions if tx.sender == participant
        ]
        sent_amounts.append(sent_amounts_open)
        total_sent = reduce(
            lambda sent_sum, sent_amount: (
                sent_sum + sum(sent_amount) if len(sent_amount) > 0 else sent_sum + 0
            ),
            sent_amounts,
            0,
        )

        received_amounts = [
            [tx.amount for tx in block.transactions if tx.recipient == participant]
            for block in self.__chain
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
        return total_received - total_sent

    def get_last_blockchain_value(self):
        """Returns the last value of the currrent blockhain."""
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def add_transaction(self, sender, recipient, amount=1.0):
        """Transfers coins from a sender to a recipient.
        Arguments:
            :sender:    The sender of the coins
            :recipient: The recioient of the coins
            :amount:    The amount of coint sent with the transaction (default = 1.0)
        """
        transaction = Transaction(sender, recipient, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        """Creates a new block storing a hash of the formed block.
        Returns True if the operations succeds otherwise False"""
        last_block = self.__chain[-1]
        previous_hash = hash_block(last_block)
        proof = self.proof_of_work()
        reward_transaction = Transaction("MINING", self.hosting_node_uuid, MINING_REWARD)
        copied_transactions = self.__open_transactions[:]
        copied_transactions.append(reward_transaction)
        new_block = Block(len(self.__chain), previous_hash, copied_transactions, proof)
        self.__chain.append(new_block)
        self.__open_transactions = []
        self.save_data()
        print(f"The new block formed: {new_block}")
        return True
