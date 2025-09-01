from time import time
from math import log2, floor
from chess import pgn, Board
import io
import os
import random
import struct
def decode(pgn_file_path: str, output_file_path: str) -> None:
    try:
        if not os.path.exists(pgn_file_path):
            raise ValueError("Input PGN file does not exist")
        with open(pgn_file_path, encoding='utf-8') as pgn_file:
            pgn_content = pgn_file.read()
        if not pgn_content.strip():
            raise ValueError("Input PGN file is empty")
        games = []
        pgn_io = io.StringIO(pgn_content)
        while True:
            game = pgn.read_game(pgn_io)
            if game is None:
                break
            games.append(game)
        if not games:
            raise ValueError("No valid chess games found in PGN file")
        current_time = int(time())
        if "ExpiryTime" in games[0].headers:
            expiry_time = int(games[0].headers.get("ExpiryTime"))
            print(f"DEBUG: Current time: {current_time}, Expiry time: {expiry_time}")  
            if current_time > expiry_time:
                time_diff = current_time - expiry_time
                if time_diff < 60:
                    time_msg = f"{time_diff} seconds"
                elif time_diff < 3600:
                    time_msg = f"{time_diff // 60} minutes"
                else:
                    time_msg = f"{time_diff // 3600} hours"
                print(f"DEBUG: File expired {time_msg} ago")  
                if os.path.exists(output_file_path):
                    os.remove(output_file_path)
                raise ValueError(f"This file has expired {time_msg} ago and can no longer be decrypted")
            else:
                print(f"DEBUG: File valid for {expiry_time - current_time} more seconds")
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        output_bytes = bytearray()
        total_bits = ""
        expected_bits = None
        if "DataBitLength" in games[0].headers:
            expected_bits = int(games[0].headers.get("DataBitLength"))
            print(f"DEBUG: Expected data length: {expected_bits} bits")
        extracted_bits = 0  
        for game_index, game in enumerate(games):
            try:
                base_seed = int(game.headers.get("Seed", "1"))
            except ValueError:
                raise ValueError(f"Invalid seed in game {game_index + 1}")
            move_random = random.Random(base_seed)
            board = Board()
            for move in game.mainline_moves():
                # Stop if we've extracted enough bits
                if expected_bits is not None and extracted_bits >= expected_bits:
                    print(f"DEBUG: Stopping extraction - have {extracted_bits} bits, need {expected_bits}")
                    break
                    
                legal_moves = list(board.legal_moves)
                if len(legal_moves) <= 1:
                    board.push(move)
                    continue
                move_random.shuffle(legal_moves)
                try:
                    move_index = [m.uci() for m in legal_moves].index(move.uci())
                except ValueError:
                    raise ValueError(f"Invalid move found in game {game_index + 1}")
                max_bits = floor(log2(len(legal_moves)))
                
                # Limit bits to extract based on what we still need
                if expected_bits is not None:
                    remaining_needed = expected_bits - extracted_bits
                    bits_to_extract = min(max_bits, remaining_needed)
                else:
                    bits_to_extract = max_bits
                
                if bits_to_extract > 0:
                    move_bits = format(move_index, f'0{bits_to_extract}b')
                    total_bits += move_bits
                    extracted_bits += bits_to_extract
                    
                    while len(total_bits) >= 8:
                        byte_val = int(total_bits[:8], 2)
                        output_bytes.append(byte_val)
                        total_bits = total_bits[8:]
                
                board.push(move)
            
            # Stop processing games if we have enough bits
            if expected_bits is not None and extracted_bits >= expected_bits:
                break
        # Calculate how many bits we actually need
        if expected_bits is not None:
            # We know exactly how many bits the original file had
            total_available_bits = len(output_bytes) * 8 + len(total_bits)
            print(f"DEBUG: Available bits: {total_available_bits}, Expected: {expected_bits}")
            
            # Calculate how many complete bytes we need
            complete_bytes_needed = expected_bits // 8
            remaining_bits_needed = expected_bits % 8
            
            print(f"DEBUG: Need {complete_bytes_needed} complete bytes + {remaining_bits_needed} bits")
            
            # If we have excess bits, we need to trim carefully
            if total_available_bits > expected_bits:
                excess_bits = total_available_bits - expected_bits
                print(f"DEBUG: Have {excess_bits} excess bits to trim")
                
                # Strategy: we need to be more careful about which bits to trim
                # The excess bits are likely at the end, so we should trim from the end
                
                if excess_bits <= len(total_bits):
                    # The excess bits are all in total_bits, just trim them
                    total_bits = total_bits[:-excess_bits] if excess_bits > 0 else total_bits
                    print(f"DEBUG: Trimmed {excess_bits} bits from total_bits")
                else:
                    # Some excess bits are in complete bytes, some in total_bits
                    # This is more complex - let's reconstruct carefully
                    all_bits = ""
                    for byte in output_bytes:
                        all_bits += format(byte, '08b')
                    all_bits += total_bits
                    
                    # Take only the bits we need from the beginning
                    needed_bits = all_bits[:expected_bits]
                    print(f"DEBUG: Extracted exactly {len(needed_bits)} bits from {len(all_bits)} available")
                    
                    # Reconstruct bytes from the needed bits
                    output_bytes = bytearray()
                    for i in range(0, len(needed_bits), 8):
                        byte_bits = needed_bits[i:i+8]
                        if len(byte_bits) == 8:
                            output_bytes.append(int(byte_bits, 2))
                        elif len(byte_bits) > 0:
                            # Pad the last partial byte with zeros
                            padded_bits = byte_bits.ljust(8, '0')
                            output_bytes.append(int(padded_bits, 2))
                            print(f"DEBUG: Added final byte with {len(byte_bits)} significant bits")
                    
                    # Clear total_bits since we've reconstructed everything
                    total_bits = ""
                
            else:
                # We have exactly the right amount or need more bits
                if len(output_bytes) > complete_bytes_needed:
                    output_bytes = output_bytes[:complete_bytes_needed]
                    print(f"DEBUG: Trimmed output_bytes to {len(output_bytes)} bytes")
                
                # Handle the last partial byte if needed
                if remaining_bits_needed > 0:
                    if len(total_bits) >= remaining_bits_needed:
                        # Use only the bits we need from total_bits
                        final_bits = total_bits[:remaining_bits_needed]
                        # Pad to complete byte for storage
                        padded_bits = final_bits.ljust(8, '0')
                        last_byte = int(padded_bits, 2)
                        output_bytes.append(last_byte)
                        print(f"DEBUG: Added final byte with {remaining_bits_needed} significant bits")
                    elif len(output_bytes) < complete_bytes_needed:
                        # We don't have enough bits - this shouldn't happen
                        print(f"DEBUG: Missing bits - padding with zeros")
                        missing_bits = expected_bits - (len(output_bytes) * 8 + len(total_bits))
                        total_bits += '0' * missing_bits
                        if len(total_bits) >= 8:
                            while len(total_bits) >= 8 and len(output_bytes) < complete_bytes_needed:
                                byte_val = int(total_bits[:8], 2)
                                output_bytes.append(byte_val)
                                total_bits = total_bits[8:]
                        if remaining_bits_needed > 0 and total_bits:
                            final_bits = total_bits[:remaining_bits_needed]
                            padded_bits = final_bits.ljust(8, '0')
                            last_byte = int(padded_bits, 2)
                            output_bytes.append(last_byte)

        # Write the final result
        with open(output_file_path, 'wb') as f:
            f.write(output_bytes)
            
        # Handle case where no expected length is available
        if expected_bits is None and total_bits:
            padded_bits = total_bits.ljust(8, '0')
            last_byte = int(padded_bits, 2)
            with open(output_file_path, 'ab') as f:
                f.write(bytes([last_byte]))
            print(f"DEBUG: Wrote final byte (no length info available)")
        if not os.path.exists(output_file_path):
            raise ValueError("Failed to create output file")
        if os.path.getsize(output_file_path) == 0:
            raise ValueError("Decoded output file is empty")
    except Exception as e:
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        raise ValueError(f"Decoding failed: {str(e)}")