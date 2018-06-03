import argparse
import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.neigbouring_nodes = set()

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def register_node(self, address):
        """
        Add a new node to the network.

        Arguments:
            address {str} -- Address of the node to add. E.g. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        self.neigbouring_nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid.

        Arguments:
            chain {list} -- A list of blocks i.e. a blockchain.

        Returns:
            bool -- True if valid, else False.
        """

        last_block = chain[0]
        for current_block in chain[1:]:
            print(last_block)
            print(current_block)
            print('\n-----------\n')

            # Check that the hash is correct
            if current_block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the proof of work is correct
            if not self.valid_proof(last_block['proof'], current_block['proof']):
                return False

            last_block = current_block

        return True

    def resolve_conflicts(self):
        """
        The consensus algorithm. It resolves conflicts by replacing our chain with the longest one in the network.

        Returns:
            bool -- True if our chain was replaced, else False.
        """

        replaced = False
        for node in self.neigbouring_nodes:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Replace our own chain if we discover a neighbour with a valid longer one
                if length > len(self.chain) and self.valid_chain(chain):
                    self.chain = chain
                    replaced = True

        return replaced

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


# Initialise node in the Blockchain
app = Flask(__name__)

# Generate globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Initialise the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # Run the proof-of-work algo to get the next nonce
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    current_proof = blockchain.proof_of_work(last_proof)

    # Reward ourselves for finding the proof
    blockchain.new_transaction(
        sender='0',
        recipient=node_identifier,
        amount=1,
    )

    # Forge the new block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(current_proof, previous_hash)

    response = {
        'message': 'New block forged!!!',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Validate data to ensure required fields are present
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return f'Missing values.\nRequired:{required}, given:{values}', 400

    # Create a new transaction
    index = blockchain.new_transaction(
        values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }

    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return 'Error: Please supply a valid list of nodes', 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added!!!',
        'total_nodes': list(blockchain.neigbouring_nodes),
    }

    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    response = {
        'message': 'Our chain was replaced' if replaced else 'Our chain is authoritative',
        'new_chain': blockchain.chain,
    }

    return jsonify(response), 200


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--port', help='the port for this blockchain node to listen on')
    args = parser.parse_args()
    port = 5000 if not args.port else args.port

    app.run(host='0.0.0.0', port=port)
