from hashlib import sha256
import json
import time
from typing import List, Dict, Any, Optional
import random


class Block:
    def __init__(self, index: int, timestamp: float, pgn_data: str,
                 previous_hash: str, nonce: int = 0):
        self.index = index
        self.timestamp = timestamp
        self.pgn_data = pgn_data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "pgn_data": self.pgn_data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return sha256(block_string).hexdigest()

    def mine_block(self, difficulty: int) -> None:
        """Mine block with proof of work"""
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()


class ChessBlockchain:
    def __init__(self, difficulty: int = 2):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.pending_transactions: List[Dict[str, Any]] = []

        # Create genesis block
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        """Create the first block in the chain"""
        genesis_block = Block(0, time.time(), "Genesis Block", "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)

    def get_latest_block(self) -> Block:
        """Return the most recent block in the chain"""
        return self.chain[-1]

    def add_pgn(self, pgn_data: str, expiry_time: Optional[int] = None) -> int:
        """Add PGN data to the blockchain"""
        # Create block with chess PGN data
        latest_block = self.get_latest_block()
        new_block = Block(
            latest_block.index + 1,
            time.time(),
            pgn_data,
            latest_block.hash
        )

        # Mine block (proof of work)
        new_block.mine_block(self.difficulty)

        # Add the new block to the chain
        self.chain.append(new_block)

        # Record expiry transaction if needed
        if expiry_time is not None:
            self.pending_transactions.append({
                "block_index": new_block.index,
                "expiry_time": expiry_time,
                "action": "expire"
            })

        return new_block.index

    def verify_chain(self) -> bool:
        """Verify the integrity of the blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Verify current block's hash
            if current_block.hash != current_block.calculate_hash():
                return False

            # Verify chain connection
            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def retrieve_pgn(self, block_index: int) -> Optional[str]:
        """Retrieve PGN data if not expired"""
        # Check if block exists
        if block_index >= len(self.chain) or block_index <= 0:
            return None

        block = self.chain[block_index]

        # Check if data is expired
        for transaction in self.pending_transactions:
            if (transaction["block_index"] == block_index and
                    transaction["action"] == "expire" and
                    transaction["expiry_time"] < time.time()):
                return None  # Data has expired

        return block.pgn_data

    def process_pending_transactions(self) -> None:
        """Process all pending transactions (like expiry checks)"""
        current_time = time.time()
        active_transactions = []

        for transaction in self.pending_transactions:
            if (transaction["action"] == "expire" and
                    transaction["expiry_time"] < current_time):
                # Mark the data as expired (we keep the block but mark it)
                block_index = transaction["block_index"]
                if block_index < len(self.chain):
                    # We could encrypt the data here, but for simplicity
                    # we'll just append an expiry flag
                    self.chain[block_index].pgn_data += "[EXPIRED]"
            else:
                # Keep transactions that haven't triggered yet
                active_transactions.append(transaction)

        self.pending_transactions = active_transactions


# Integration with existing encode.py
def blockchain_encode(file_path: str, output_pgn_path: str,
                      self_destruct_timer: Optional[int] = None,
                      custom_headers: Optional[Dict[str, str]] = None,
                      blockchain: ChessBlockchain = None) -> None:
    """
    Encodes a file into PGN and stores it in the blockchain
    """
    # Create blockchain if not provided
    if blockchain is None:
        blockchain = ChessBlockchain()

    # Call the original encode function to get PGN data
    from encode import encode as original_encode

    # First generate the PGN output
    original_encode(file_path, output_pgn_path, self_destruct_timer, custom_headers)

    # Read the generated PGN file
    with open(output_pgn_path, "r", encoding='utf-8') as f:
        pgn_data = f.read()

    # Calculate expiry time if needed
    expiry_time = None
    if self_destruct_timer is not None:
        expiry_time = int(time.time()) + self_destruct_timer

    # Add to blockchain
    block_index = blockchain.add_pgn(pgn_data, expiry_time)

    # Add blockchain reference to the PGN file
    with open(output_pgn_path, "a", encoding='utf-8') as f:
        f.write(f"\n\n[BlockchainRef \"{block_index}\"]")

    return block_index


# Integration with existing decode.py
def blockchain_decode(pgn_file_path: str, output_file_path: str,
                      blockchain: ChessBlockchain = None) -> None:
    """
    Decodes PGN data, verifying blockchain integrity first
    """
    # Create blockchain if not provided
    if blockchain is None:
        blockchain = ChessBlockchain()

    # Process any pending transactions (like expiry)
    blockchain.process_pending_transactions()

    # Extract blockchain reference if present
    block_index = None
    with open(pgn_file_path, "r", encoding='utf-8') as f:
        pgn_content = f.read()
        import re
        match = re.search(r'\[BlockchainRef "(\d+)"\]', pgn_content)
        if match:
            block_index = int(match.group(1))

    # Verify blockchain integrity
    if not blockchain.verify_chain():
        raise ValueError("Blockchain integrity check failed")

    # If we have a blockchain reference, verify data hasn't been tampered with
    if block_index is not None:
        blockchain_pgn = blockchain.retrieve_pgn(block_index)
        if blockchain_pgn is None:
            raise ValueError("PGN data has expired or doesn't exist in blockchain")

        # Check if the data matches (ignoring the blockchain reference tag)
        clean_pgn_content = re.sub(r'\[BlockchainRef "(\d+)"\]', '', pgn_content).strip()
        clean_blockchain_pgn = re.sub(r'\[BlockchainRef "(\d+)"\]', '', blockchain_pgn).strip()

        if clean_pgn_content != clean_blockchain_pgn:
            raise ValueError("PGN data has been tampered with")

    # Call the original decode function
    from decode import decode as original_decode
    original_decode(pgn_file_path, output_file_path)