import hashlib
import json
from time import time
from uuid import uuid4


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new block and add it to the chain.

        Arguments:
            proof {int} -- The proof given by the Proof of Work algorithm.

        Keyword Arguments:
            previous_hash {str} -- Hash of the previous block (default: {None}).

        Returns:
            dict -- New block.
        """

        block = {
            'index': len(self.chain) + 1,
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.last_block)
        }

        # Reset the current transactions and add the current block to the chain
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined block.

        Arguments:
            sender {str} -- Address of the sender.
            recipient {str} -- Address of the recipient.
            amount {int} -- Amount being transferred.

        Returns:
            int -- The index of the block that will hold this transaction.
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        """
        Simple proof of work algorithm:
        - p is the prior proof; p' is the new proof.
        - Find a number (p') such that hash(pp') contains 4 leading zeroes.
        
        Arguments:
            last_proof {int} -- prior nonce.
        
        Returns:
            int -- new nonce.
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        
        return proof

    @staticmethod
    def valid_proof(last_proof, current_proof):
        """
        Validates the current_proof: does hash(last_proof, current_proof) contain 4 leading zeroes?
        
        Arguments:
            last_proof {int} -- Previous proof
            current_proof {int} -- Current proof.
        
        Returns:
            bool -- True if correct, else False.
        """

        guess = f'{last_proof}{current_proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'

    @staticmethod
    def hash(block):
        """
        Create a SHA-256 hash of a given block.

        Arguments:
            block {dict} -- The Block to hash.

        Returns:
            str -- SHA-256 hash.
        """

        # The dict is ordered to ensure hashes are consistent
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # Retrieve the last block in the chain
        return self.chain[-1]
