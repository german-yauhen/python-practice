from time import time


class Block:

    def __init__(self, index, previous_hash, transactions, proof, timestamp=None):
        self.index = index
        self.previous_block_hash = previous_hash
        self.transactions = transactions
        self.proof_of_work = proof
        self.timestamp = time() if timestamp is None else timestamp
