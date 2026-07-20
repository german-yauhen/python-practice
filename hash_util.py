import hashlib
import json

def hash_string_256(string):
    return hashlib.sha256(string).hexdigest()

def hash_block(block):
    """
    Hashes block and returns a string representation of it.

    Arguments:
        :block: the block that should be addded

    """
    hashable_block = block.__dict__.copy()
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())
