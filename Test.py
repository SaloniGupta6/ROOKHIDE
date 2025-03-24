from blockchain import ChessBlockchain, blockchain_encode, blockchain_decode
import os
import time

# Create test file
test_data = "This is test data for blockchain verification"
with open("test_file.txt", "w") as f:
    f.write(test_data)

# Initialize blockchain
blockchain = ChessBlockchain(difficulty=2)

# 1. Encode file to PGN and store in blockchain
block_index = blockchain_encode("test_file.txt", "test_encoded.pgn",
                              self_destruct_timer=300, blockchain=blockchain)
print(f"Encoded data stored in block {block_index}")

# 2. Verify chain integrity
is_valid = blockchain.verify_chain()
print(f"Blockchain integrity: {is_valid}")

# 3. Decode PGN file back to original
blockchain_decode("test_encoded.pgn", "test_decoded.txt", blockchain=blockchain)

# 4. Verify the decoded content matches the original
with open("test_decoded.txt", "r") as f:
    decoded_data = f.read()
print(f"Original data: {test_data}")
print(f"Decoded data: {decoded_data}")
print(f"Data match: {test_data == decoded_data}")

# 5. Show blockchain structure
print("\nBlockchain structure:")
for i, block in enumerate(blockchain.chain):
    print(f"Block {i}: Hash={block.hash[:10]}..., PGN length={len(block.pgn_data)}")