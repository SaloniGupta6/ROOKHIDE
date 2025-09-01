import os
import random
import logging
import time
from time import time as current_time, strftime
from math import log2, floor
from chess import pgn, Board
from typing import List, Optional, Dict

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
def read_input_file(file_path: str) -> List[int]:
    if not os.path.exists(file_path):
        logger.error(f"Input file does not exist: {file_path}")
        raise ValueError("Input file does not exist")
    with open(file_path, "rb") as input_file:
        file_bytes = list(input_file.read())
    if not file_bytes:
        logger.error("Input file is empty")
        raise ValueError("Input file is empty")
    return file_bytes
def extract_bits(file_bytes: List[int], bit_index: int, bits_to_extract: int) -> str:
    """Extract bits from file bytes starting at bit_index"""
    total_bits = len(file_bytes) * 8
    if bit_index >= total_bits:
        return '0' * bits_to_extract
    
    # Limit bits_to_extract to available bits
    available_bits = total_bits - bit_index
    bits_to_extract = min(bits_to_extract, available_bits)
    
    result_bits = ""
    current_bit_index = bit_index
    
    for _ in range(bits_to_extract):
        byte_index = current_bit_index // 8
        bit_offset = current_bit_index % 8
        
        if byte_index < len(file_bytes):
            # Extract bit from MSB to LSB (left to right)
            bit_value = (file_bytes[byte_index] >> (7 - bit_offset)) & 1
            result_bits += str(bit_value)
        else:
            result_bits += '0'
        
        current_bit_index += 1
    
    return result_bits
def create_game_record(board: Board, seed: int, expiry_time: Optional[int] = None,
                       custom_headers: Optional[Dict[str, str]] = None, data_bit_length: Optional[int] = None) -> str:
    game = pgn.Game()
    game.headers["Seed"] = str(seed)
    default_headers = {
        "Event": "Encoded Game",
        "Date": strftime("%Y.%m.%d"),
        "White": "Player1",
        "Black": "Player2",
        "Result": "*"  
    }
    if custom_headers:
        for key, value in custom_headers.items():
            if value:  
                default_headers[key] = value
    for key, value in default_headers.items():
        game.headers[key] = value
    if expiry_time is not None:
        logger.debug(f"Setting ExpiryTime header to {expiry_time}")
        game.headers["ExpiryTime"] = str(expiry_time)
        readable_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expiry_time))
        game.headers["ExpiryTimeReadable"] = readable_time
    else:
        logger.debug("No expiry time provided, not setting ExpiryTime header")
    if data_bit_length is not None:
        game.headers["DataBitLength"] = str(data_bit_length)
        logger.debug(f"Setting DataBitLength header to {data_bit_length}")
    game.add_line(board.move_stack)
    return str(game)
def should_end_game(board: Board) -> bool:
    return (board.is_game_over() or
            board.is_insufficient_material() or
            board.can_claim_draw() or
            len(board.move_stack) >= 50)
def encode(file_path: str, output_pgn_path: str, self_destruct_timer: Optional[int] = None,
           custom_headers: Optional[Dict[str, str]] = None) -> None:
    try:
        start_time = current_time()
        logger.debug(f"Starting encoding of file: {file_path}")
        file_bytes = read_input_file(file_path)
        file_bits_count = len(file_bytes) * 8
        logger.debug(f"File size: {len(file_bytes)} bytes ({file_bits_count} bits)")
        expiry_time = None
        if self_destruct_timer is not None and self_destruct_timer > 0:
            expiry_time = int(current_time()) + self_destruct_timer
            logger.debug(f"Setting expiry time to: {expiry_time} (current time + {self_destruct_timer} seconds)")
            human_readable = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expiry_time))
            logger.debug(f"File will expire at: {human_readable}")
        else:
            logger.debug("No self-destruct timer provided, file will not expire")

        output_pgns = []
        file_bit_index = 0
        chess_board = Board()
        base_seed = random.randint(1, 1_000_000)
        move_random = random.Random(base_seed)
        logger.debug(f"Generated seed: {base_seed}")
        game_number = 1

        while file_bit_index < file_bits_count:
            legal_moves = list(chess_board.legal_moves)
            logger.debug(f"Position has {len(legal_moves)} legal moves")
            if len(legal_moves) <= 1:
                if legal_moves:
                    chess_board.push(legal_moves[0])
                    logger.debug("Pushed forced move")
                if len(legal_moves) == 0 or chess_board.is_game_over():
                    logger.debug("Creating new game")
                    if custom_headers:
                        game_headers = custom_headers.copy()
                        if game_number > 1 and "Round" not in game_headers:
                            game_headers["Round"] = str(game_number)
                    else:
                        game_headers = {"Round": str(game_number)} if game_number > 1 else None
                    if game_number == 1:
                        output_pgns.append(create_game_record(
                            chess_board, base_seed, expiry_time, game_headers, file_bits_count))
                    else:
                        output_pgns.append(create_game_record(
                            chess_board, base_seed, expiry_time, game_headers))
                    chess_board.reset()
                    base_seed = random.randint(1, 1_000_000)
                    move_random = random.Random(base_seed)
                    logger.debug(f"New game created with seed: {base_seed}")
                    game_number += 1
                continue
            max_bits = floor(log2(len(legal_moves)))
            remaining_bits = file_bits_count - file_bit_index
            bits_to_encode = min(max_bits, remaining_bits)
            logger.debug(f"Encoding {bits_to_encode} bits in this move")
            bits = extract_bits(file_bytes, file_bit_index, bits_to_encode)
            move_index = int(bits, 2)
            if move_index >= len(legal_moves):
                logger.error(f"Move index {move_index} out of range for {len(legal_moves)} moves")
                raise ValueError("Invalid move index calculated")
            move_random.shuffle(legal_moves)
            chosen_move = legal_moves[move_index]
            chess_board.push(chosen_move)
            logger.debug(f"Pushed move: {chosen_move.uci()}")
            file_bit_index += bits_to_encode
            if should_end_game(chess_board):
                logger.debug("Ending current game")
                if custom_headers:
                    game_headers = custom_headers.copy()
                    if game_number > 1 and "Round" not in game_headers:
                        game_headers["Round"] = str(game_number)
                else:
                    game_headers = {"Round": str(game_number)} if game_number > 1 else None
                if game_number == 1:
                    output_pgns.append(create_game_record(
                        chess_board, base_seed, expiry_time, game_headers, file_bits_count))
                else:
                    output_pgns.append(create_game_record(
                        chess_board, base_seed, expiry_time, game_headers))
                if file_bit_index < file_bits_count:
                    chess_board.reset()
                    base_seed = random.randint(1, 1_000_000)
                    move_random = random.Random(base_seed)
                    logger.debug("Started new game")
                    game_number += 1
        if chess_board.move_stack:
            logger.debug("Saving final game")
            if custom_headers:
                game_headers = custom_headers.copy()
                if game_number > 1 and "Round" not in game_headers:
                    game_headers["Round"] = str(game_number)
            else:
                game_headers = {"Round": str(game_number)} if game_number > 1 else None
            if game_number == 1:
                output_pgns.append(create_game_record(
                    chess_board, base_seed, expiry_time, game_headers, file_bits_count))
            else:
                output_pgns.append(create_game_record(
                    chess_board, base_seed, expiry_time, game_headers))
        logger.debug(f"Writing output to: {output_pgn_path}")
        with open(output_pgn_path, "w", encoding='utf-8') as f:
            f.write("\n\n".join(output_pgns))
        logger.debug("Verifying PGN headers in output file...")
        with open(output_pgn_path, "r", encoding='utf-8') as f:
            pgn_content = f.read()
            if expiry_time is not None and str(expiry_time) not in pgn_content:
                logger.error("ExpiryTime header not found in output PGN!")
            else:
                logger.debug("ExpiryTime header verified in output PGN")
            if custom_headers:
                for key, value in custom_headers.items():
                    if value and value not in pgn_content:
                        logger.warning(f"Custom header {key}: {value} not found in output PGN!")
                    else:
                        logger.debug(f"Custom header {key} verified in output PGN")
        elapsed_time = current_time() - start_time
        logger.debug(f"Encoding completed successfully in {elapsed_time:.2f} seconds")
    except Exception as e:
        logger.error(f"Encoding error: {str(e)}", exc_info=True)
        raise