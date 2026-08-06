from functools import reduce

import requests
from utility.hash_util import hash_block
import json
from block import Block
from transaction import Transaction
from utility.verification import Verification
from wallet import Wallet

MINING_REWARD = 10


class Blockchain:

    def __init__(self, public_key, node_id):
        gen_block = Block(0, "", [], 10, 0)
        self.chain = [gen_block]
        self.__open_transactions = []
        self.public_key = public_key
        self.__peer_nodes = set()
        self.node_id = node_id
        self.resolve_conflicts = False
        self.load_data()

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
            with open(f"blockchain-{self.node_id}.txt", mode="r") as f:
                file_content = f.readlines()

                blockchain_restored = []
                for block in json.loads(file_content[0][:-1]):
                    restored_txs = [
                        Transaction(
                            trx["sender"],
                            trx["recipient"],
                            trx["signature"],
                            trx["amount"],
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
                self.chain = blockchain_restored

                open_transactions_restored = []
                for trx_read in json.loads(file_content[1][:-1]):
                    trx_restored = Transaction(
                        trx_read["sender"],
                        trx_read["recipient"],
                        trx_read["signature"],
                        trx_read["amount"],
                    )
                    open_transactions_restored.append(trx_restored)
                self.__open_transactions = open_transactions_restored

                peer_nodes = json.loads(file_content[2])
                self.__peer_nodes = set(peer_nodes)
        except (IOError, IndexError):
            pass
        finally:
            print("Previous state loaded!")

    # load_data()
    # load_data_with_pickle()

    def save_data(self):
        try:
            with open(f"blockchain-{self.node_id}.txt", mode="w") as f:
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
                f.write("\n")
                f.write(json.dumps(list(self.__peer_nodes)))
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

    def get_balance(self, sender=None):
        """Calculate and retunr the balance for a participant"""

        if sender == None:   
            if self.public_key == None:
                return None
            participant = self.public_key
        else:
            participant = sender

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
        print(f"Total sent: {total_sent}")

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
        print(f"Total received: {total_received}")
        return total_received - total_sent

    def get_last_blockchain_value(self):
        """Returns the last value of the currrent blockhain."""
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def add_transaction(self, sender, recipient, signature, amount=1.0, is_receiving=False):
        """Transfers coins from a sender to a recipient.
        Arguments:
            :sender:    The sender of the coins
            :recipient: The recioient of the coins
            :signature: The signature of the transaction
            :amount:    The amount of coint sent with the transaction (default = 1.0)
        """

        transaction = Transaction(sender, recipient, signature, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            if not is_receiving:
                for peer_node_id in self.__peer_nodes:
                    url = f"http://{peer_node_id}/acceptance/transaction"
                    try:
                        response = requests.post(
                            url,
                            json={
                                "sender": sender,
                                "recipient": recipient,
                                "amount": amount,
                                "signature": signature,
                            },
                        )
                        if response.status_code == 400 or response.status_code == 500:
                            print("Transaction declined, needs resolving!")
                            return False
                    except requests.exceptions.ConnectionError:
                        print(f"There is no connection to a peer node with id {peer_node_id}")
                        continue
            return True
        return False

    def mine_block(self):
        """Creates a new block storing a hash of the formed block.
        Returns True if the operations succeds otherwise False"""
        if self.public_key == None:
            return None
        last_block = self.__chain[-1]
        previous_hash = hash_block(last_block)
        proof = self.proof_of_work()
        reward_transaction = Transaction("MINING", self.public_key, "", MINING_REWARD)
        copied_transactions = self.__open_transactions[:]
        for trx in copied_transactions:
            if not Wallet.verify_transaction(trx):
                return None
        copied_transactions.append(reward_transaction)
        new_block = Block(len(self.__chain), previous_hash, copied_transactions, proof)
        self.__chain.append(new_block)
        self.__open_transactions = []
        self.save_data()
        for peer_node_id in self.__peer_nodes:
            url = f"http://{peer_node_id}/acceptance/block"
            converted_block = new_block.__dict__.copy()
            converted_block["transactions"] = [trx.__dict__ for trx in converted_block["transactions"]]
            try:
                response = requests.post(url, json={"block": converted_block})
                if response.status_code == 400 or response.status_code == 500:
                    print("Block declined, needs resolving!")
                if response.status_code == 409:
                    self.resolve_conflicts = True
            except requests.exceptions.ConnectionError:
                continue
        print(f"The new block formed: {new_block}")
        return new_block

    def add_block(self, block):
        transactions = [
            Transaction(
                trx["sender"], trx["recipient"], trx["signature"], trx["amount"]
            )
            for trx in block["transactions"]
        ]
        proof_is_valid = Verification.valid_proof(transactions[:-1], block["previous_hash"], block["proof"])
        hashes_match = hash_block(self.chain[-1]) == block["previous_hash"]
        if not proof_is_valid or not hashes_match:
            return False
        converted_block = Block(block["index"], block["previous_hash"], transactions, block["proof"], block["timestamp"])
        self.__chain.append(converted_block)
        open_trxs_copy = self.__open_transactions[:]
        for in_trx in block["transactions"]:
            for open_trx in open_trxs_copy:
                if (
                    open_trx.sender == in_trx["sender"]
                    and open_trx.recipient == in_trx["recipient"]
                    and open_trx.amount == in_trx["amount"]
                    and open_trx.signature == in_trx["signature"]
                ):
                    try:
                        self.__open_transactions.remove(open_trx)
                    except ValueError:
                        print("Item has been already removed")
        self.save_data()
        return True

    def resolve(self):
        winner_chain = self.chain
        replaced = False
        for peer_node_id in self.__peer_nodes:
            url = f"http://{peer_node_id}/chain"
            try:
                rs = requests.get(url)
                node_chain = rs.json()
                node_chain = [
                    Block(
                        block["index"],
                        block["previous_hash"],
                        [
                            Transaction(
                                trx["sender"],
                                trx["recipient"],
                                trx["signature"],
                                trx["amount"],
                            )
                            for trx in block["transactions"]
                        ],
                        block["proof"],
                        block["timestamp"],
                    )
                    for block in node_chain
                ]
                node_chain_length = len(node_chain)
                local_chain_length = len(winner_chain)
                if node_chain_length > local_chain_length and Verification.verify_chain(node_chain):
                    winner_chain = node_chain
                    replaced = True
            except requests.exceptions.ConnectionError:
                print(f"Connection error with {peer_node_id}")
                continue
        self.resolve_conflicts = False
        self.chain = winner_chain
        if replaced:
            self.__open_transactions = []
        self.save_data()
        return replaced


    def add_peer_node(self, node):
        """Adds a new node to the peer node set

        Args:
            node: The node URL which should be added
        """
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        """Removes (silently) a registered node from the peer node set

        Args:
            node: The node URl which should be removed
        """
        self.__peer_nodes.discard(node)
        self.save_data()

    def get_peer_nodes(self):
        """Returns a list of all connected peer nodes"""
        return list(self.__peer_nodes)[:]
