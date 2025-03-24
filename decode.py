# decode.py
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
        for game_index, game in enumerate(games):
            try:
                base_seed = int(game.headers.get("Seed", "1"))
            except ValueError:
                raise ValueError(f"Invalid seed in game {game_index + 1}")
            move_random = random.Random(base_seed)
            board = Board()
            for move in game.mainline_moves():
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
                move_bits = format(move_index, f'0{max_bits}b')
                total_bits += move_bits
                while len(total_bits) >= 8:
                    byte_val = int(total_bits[:8], 2)
                    output_bytes.append(byte_val)
                    total_bits = total_bits[8:]
                board.push(move)
        if expected_bits is not None:
            total_processed_bits = len(output_bytes) * 8
            print(f"DEBUG: Processed {total_processed_bits} complete bits so far")
            if total_processed_bits >= expected_bits:
                print(f"DEBUG: Already extracted all needed bits ({total_processed_bits} >= {expected_bits})")
                if total_processed_bits > expected_bits:
                    excess_bits = total_processed_bits - expected_bits
                    excess_bytes = (excess_bits + 7) // 8  
                    output_bytes = output_bytes[:-excess_bytes]
                    print(f"DEBUG: Trimmed {excess_bytes} excess bytes")
                total_bits = ""
        with open(output_file_path, 'wb') as f:
            f.write(output_bytes)
        if total_bits:
            if expected_bits is not None:
                total_processed_bits = len(output_bytes) * 8
                remaining_expected = expected_bits - total_processed_bits
                if remaining_expected > 0:
                    print(f"DEBUG: Need {remaining_expected} more bits to complete file")
                    if len(total_bits) > remaining_expected:
                        print(f"DEBUG: Trimming excess bits ({len(total_bits)} -> {remaining_expected})")
                        total_bits = total_bits[:remaining_expected]
                    if total_bits:
                        padded_bits = total_bits.ljust(8, '0')
                        last_byte = int(padded_bits, 2)
                        with open(output_file_path, 'ab') as f:
                            f.write(bytes([last_byte]))
                            print(f"DEBUG: Wrote final byte with {len(total_bits)} significant bits")
            else:
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