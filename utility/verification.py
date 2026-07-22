from utility.hash_util import hash_block, hash_string_256


class Verification:

    @staticmethod
    def valid_proof(transactions, previous_hash, proof):
        guess = (
            str([tx.to_ordered_dict() for tx in transactions])
            + str(previous_hash)
            + str(proof)
        ).encode()
        guess_hash = hash_string_256(guess)
        print(guess_hash)
        return guess_hash[0:2] == "00"

    @classmethod
    def verify_chain(cls, chain):
        """Verify the current blockchain and return True if it's validm False otherwise"""
        for index, block in enumerate(chain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(chain[index - 1]):
                return False
            if not cls.valid_proof(
                block.transactions[:-1], block.previous_hash, block.proof
            ):
                print("Proof of work is invalid")
                return False
        return True

    @classmethod
    def verify_transactions(cls, transactions, get_balance):
        return all([cls.verify_transaction(tx, get_balance) for tx in transactions])

    @staticmethod
    def verify_transaction(transaction, get_balance):
        sender_balance = get_balance()
        return sender_balance >= transaction.amount
