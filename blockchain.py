class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

    def new_block(self):
        # Create a new block and add it to the chain
        pass

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined block.
        
        Arguments:
            sender {str} -- Address of the sender.
            recipient {str} -- Address of the recipient.
            amount {int} -- Amount being transferred.
            return {int} -- The index of the block that will hold this transaction.
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        # Hash a given block
        pass

    @property
    def last_block(self):
        # Retrieve the last block in the chain
        pass