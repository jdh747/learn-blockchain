class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

    def new_block(self):
        # Create a new block and add it to the chain
        pass

    def new_transaction(self):
        # Add a new transaction to current current_transactions
        pass

    @staticmethod
    def hash(block):
        # Hash a given block
        pass

    @property
    def last_block(self):
        # Retrieve the last block in the chain
        pass