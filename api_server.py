#!/usr/bin/env python3
"""
Minimal Flask API server for testing
"""

import os
import json
import uuid
import hashlib
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS

# Create a minimal Flask app
app = Flask(__name__)
CORS(app)

# In-memory storage for demo
transaction_store = {}
pgn_metadata_store = {}

def generate_transaction_id():
    """Generate a unique transaction ID"""
    return str(uuid.uuid4())

def validate_wallet_signature(wallet_address, signature, message):
    """Validate wallet signature (placeholder - implement actual validation)"""
    # In production, implement proper signature validation
    return len(wallet_address) > 20 and len(signature) > 50

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "features": {
            "chess_steganography": True,
            "blockchain_integration": True,
            "x402_payments": True,
            "coinbase_wallet": True
        }
    })

@app.route("/api/wallet/connect", methods=["POST"])
def connect_wallet():
    """Handle Coinbase Wallet connection"""
    try:
        data = request.get_json()
        wallet_address = data.get('wallet_address')
        signature = data.get('signature')
        message = data.get('message')
        
        if not all([wallet_address, signature, message]):
            return jsonify({"error": "Missing wallet credentials"}), 400
        
        # Validate signature (implement proper validation in production)
        if not validate_wallet_signature(wallet_address, signature, message):
            return jsonify({"error": "Invalid wallet signature"}), 401
        
        # Generate session token
        session_token = generate_transaction_id()
        
        return jsonify({
            "success": True,
            "session_token": session_token,
            "wallet_address": wallet_address,
            "message": "Wallet connected successfully"
        })
        
    except Exception as e:
        app.logger.error(f"Wallet connection error: {str(e)}")
        return jsonify({"error": "Wallet connection failed"}), 500

@app.route("/api/payment/initiate", methods=["POST"])
def initiate_payment():
    """Initiate X402 micropayment for encoding/decoding"""
    try:
        data = request.get_json()
        wallet_address = data.get('wallet_address')
        operation = data.get('operation')  # 'encode' or 'decode'
        file_hash = data.get('file_hash')
        
        # Validate required parameters
        if not wallet_address:
            return jsonify({
                "error": "Wallet address required",
                "code": "WALLET_REQUIRED",
                "message": "Please connect your Coinbase Wallet first"
            }), 400
            
        if not operation:
            return jsonify({
                "error": "Operation required",
                "code": "OPERATION_REQUIRED", 
                "message": "Please specify 'encode' or 'decode' operation"
            }), 400
            
        if not file_hash:
            return jsonify({
                "error": "File hash required",
                "code": "FILE_HASH_REQUIRED",
                "message": "File hash is required for payment verification"
            }), 400
        
        if operation not in ['encode', 'decode']:
            return jsonify({
                "error": "Invalid operation",
                "code": "INVALID_OPERATION",
                "message": "Operation must be either 'encode' or 'decode'"
            }), 400
        
        # Generate transaction ID
        transaction_id = generate_transaction_id()
        
        # X402 micropayment amounts (in wei)
        payment_amounts = {
            "encode": "2000000000000000",  # 0.002 ETH for encoding
            "decode": "1000000000000000"   # 0.001 ETH for decoding
        }
        
        payment_amount = payment_amounts[operation]
        
        # Store transaction details
        transaction_store[transaction_id] = {
            "wallet_address": wallet_address,
            "operation": operation,
            "file_hash": file_hash,
            "amount": payment_amount,
            "amount_eth": float(int(payment_amount) / 1e18),  # Convert to ETH for display
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=15)).isoformat(),
            "x402_protocol": "v1.0",
            "network": "ethereum"
        }
        
        app.logger.info(f"X402 payment initiated: {transaction_id} for {operation} by {wallet_address}")
        
        return jsonify({
            "success": True,
            "transaction_id": transaction_id,
            "payment_amount": payment_amount,
            "payment_amount_eth": float(int(payment_amount) / 1e18),
            "operation": operation,
            "payment_address": "0x742d35Cc6634C0532925a3b8D4C9db96590c6C87",  # X402 payment address
            "expires_in": 900,  # 15 minutes
            "x402_protocol": "v1.0",
            "message": f"X402 micropayment required for {operation} operation"
        })
        
    except Exception as e:
        app.logger.error(f"X402 payment initiation error: {str(e)}")
        return jsonify({
            "error": "X402 payment initiation failed",
            "code": "PAYMENT_INIT_FAILED",
            "message": str(e)
        }), 500

@app.route("/api/payment/verify", methods=["POST"])
def verify_payment():
    """Verify X402 micropayment completion"""
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        tx_hash = data.get('tx_hash')
        
        if not all([transaction_id, tx_hash]):
            return jsonify({"error": "Missing verification parameters"}), 400
        
        if transaction_id not in transaction_store:
            return jsonify({"error": "Invalid transaction ID"}), 404
        
        # In production, verify the actual blockchain transaction
        # For demo, we'll simulate verification
        transaction = transaction_store[transaction_id]
        
        # Check if transaction hasn't expired
        expires_at = datetime.fromisoformat(transaction["expires_at"])
        if datetime.now() > expires_at:
            return jsonify({"error": "Transaction expired"}), 400
        
        # Update transaction status
        transaction_store[transaction_id]["status"] = "confirmed"
        transaction_store[transaction_id]["tx_hash"] = tx_hash
        transaction_store[transaction_id]["confirmed_at"] = datetime.now().isoformat()
        
        return jsonify({
            "success": True,
            "status": "confirmed",
            "message": "Payment verified successfully"
        })
        
    except Exception as e:
        app.logger.error(f"Payment verification error: {str(e)}")
        return jsonify({"error": "Payment verification failed"}), 500

@app.route("/api/encode", methods=["POST"])
def encode_file():
    """Encode file into chess PGN with steganography"""
    try:
        app.logger.info("🔄 Encode endpoint called")
        
        # Check if this is multipart/form-data by checking if files are present
        if 'file' not in request.files:
            app.logger.error("❌ No file in request")
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            app.logger.error("❌ Empty filename")
            return jsonify({"error": "No file selected"}), 400
        
        # Get form data
        wallet_address = request.form.get('wallet_address')
        transaction_id = request.form.get('transaction_id')
        file_type = request.form.get('file_type', 'text')
        
        app.logger.info(f"📝 Processing encode request:")
        app.logger.info(f"   - Wallet: {wallet_address}")
        app.logger.info(f"   - Transaction: {transaction_id}")
        app.logger.info(f"   - File: {file.filename}")
        app.logger.info(f"   - Type: {file_type}")
        
        # Verify transaction exists and is confirmed
        if transaction_id not in transaction_store:
            app.logger.error(f"❌ Transaction not found: {transaction_id}")
            return jsonify({"error": "Invalid transaction ID"}), 400
        
        transaction = transaction_store[transaction_id]
        if transaction["status"] != "confirmed":
            app.logger.error(f"❌ Transaction not confirmed: {transaction['status']}")
            return jsonify({"error": "Payment not confirmed"}), 400
        
        # Read file content
        file_content = file.read()
        app.logger.info(f"📄 File size: {len(file_content)} bytes")
        
        # Generate PGN ID and hash
        pgn_id = generate_transaction_id()
        content_hash = hashlib.sha256(file_content).hexdigest()
        
        # Create a simple chess PGN with encoded data
        # In production, implement actual steganographic encoding
        pgn_content = f"""[Event "ChessCrypt Encoded Message"]
[Site "ChessCrypt DApp"]
[Date "{datetime.now().strftime('%Y.%m.%d')}"]
[Round "1"]
[White "Encoder"]
[Black "Decoder"]
[Result "1-0"]
[PGNId "{pgn_id}"]
[FileHash "{content_hash}"]
[WalletAddress "{wallet_address}"]
[FileType "{file_type}"]
[EncodedSize "{len(file_content)}"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 
9. h3 Nb8 10. d4 Nbd7 11. c4 c6 12. cxb5 axb5 13. Nc3 Bb7 14. Bg5 b4 15. Nb1 h6 
16. Bh4 c5 17. dxe5 Nxe4 18. Bxe7 Qxe7 19. exd6 Qf6 20. Nbd2 Nxd6 21. Nc4 Nxc4 
22. Bxc4 Nb6 23. Ne5 Rae8 24. Bxf7+ Rxf7 25. Nxf7 Rxe1+ 26. Qxe1 Kxf7 27. Qe3 Qg5 
28. Qxg5 hxg5 29. b3 Ke6 30. a3 Kd6 31. axb4 cxb4 32. Ra5 Nd5 33. f3 Bc8 34. Kf2 Bf5 
35. Ra7 g6 36. Ra6+ Kc5 37. Ke1 Nf4 38. g3 Nxh3 39. Kd2 Kb5 40. Rd6 Kc5 41. Ra6 Nf2 
42. g4 Bd3 43. Re6 1-0

; Encoded data: {file_content.hex()}
"""
        
        # Store PGN metadata
        pgn_metadata_store[pgn_id] = {
            "pgn_id": pgn_id,
            "file_hash": content_hash,
            "wallet_address": wallet_address,
            "transaction_id": transaction_id,
            "file_type": file_type,
            "file_size": len(file_content),
            "created_at": datetime.now().isoformat(),
            "pgn_content": pgn_content
        }
        
        app.logger.info(f"✅ Encoding completed successfully: {pgn_id}")
        
        return jsonify({
            "success": True,
            "pgn_id": pgn_id,
            "pgn_hash": content_hash,
            "file_size": len(file_content),
            "download_url": f"/api/download/{pgn_id}",
            "message": "File encoded successfully into chess PGN"
        })
        
    except Exception as e:
        app.logger.error(f"🚨 Encoding error: {str(e)}")
        return jsonify({
            "error": "Encoding failed",
            "message": str(e)
        }), 500

@app.route("/api/pgn/validate", methods=["POST"])
def validate_pgn():
    """Validate PGN file and check for hidden data"""
    try:
        app.logger.info("🔍 PGN validation endpoint called")
        
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Read PGN content
        pgn_content = file.read().decode('utf-8')
        file_hash = hashlib.sha256(pgn_content.encode()).hexdigest()
        
        app.logger.info(f"📄 Validating PGN file: {file.filename}")
        app.logger.info(f"🔐 File hash: {file_hash}")
        
        # Basic PGN validation
        is_valid_pgn = '[Event ' in pgn_content and '1.' in pgn_content
        
        # Check for ChessCrypt encoded data
        has_hidden_data = (
            '[PGNId ' in pgn_content and 
            '[FileHash ' in pgn_content and
            '; Encoded data:' in pgn_content
        )
        
        # Check if this PGN exists in our store
        pgn_exists_in_store = any(
            data['file_hash'] == file_hash 
            for data in pgn_metadata_store.values()
        )
        
        app.logger.info(f"✅ Validation results: valid={is_valid_pgn}, hidden={has_hidden_data}, in_store={pgn_exists_in_store}")
        
        return jsonify({
            "success": True,
            "is_valid_pgn": is_valid_pgn,
            "has_hidden_data": has_hidden_data,
            "file_hash": file_hash,
            "pgn_exists_in_store": pgn_exists_in_store,
            "message": "PGN validation completed"
        })
        
    except Exception as e:
        app.logger.error(f"🚨 PGN validation error: {str(e)}")
        return jsonify({
            "error": "PGN validation failed",
            "message": str(e)
        }), 500

@app.route("/api/decode", methods=["POST"])
def decode_file():
    """Decode hidden message from chess PGN"""
    try:
        app.logger.info("🔓 Decode endpoint called")
        
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Get form data
        wallet_address = request.form.get('wallet_address')
        transaction_id = request.form.get('transaction_id')
        file_type = request.form.get('file_type', 'text')
        
        app.logger.info(f"📝 Processing decode request:")
        app.logger.info(f"   - Wallet: {wallet_address}")
        app.logger.info(f"   - Transaction: {transaction_id}")
        app.logger.info(f"   - File: {file.filename}")
        app.logger.info(f"   - Expected type: {file_type}")
        
        # Verify transaction exists and is confirmed
        if transaction_id not in transaction_store:
            app.logger.error(f"❌ Transaction not found: {transaction_id}")
            return jsonify({"error": "Invalid transaction ID"}), 400
        
        transaction = transaction_store[transaction_id]
        if transaction["status"] != "confirmed":
            app.logger.error(f"❌ Transaction not confirmed: {transaction['status']}")
            return jsonify({"error": "Payment not confirmed"}), 400
        
        # Read PGN content
        pgn_content = file.read().decode('utf-8')
        app.logger.info(f"📄 PGN content length: {len(pgn_content)} characters")
        
        # Extract encoded data from PGN
        encoded_data_marker = '; Encoded data: '
        if encoded_data_marker not in pgn_content:
            app.logger.error("❌ No encoded data found in PGN")
            return jsonify({"error": "No hidden data found in PGN file"}), 400
        
        # Extract hex-encoded data
        encoded_section = pgn_content.split(encoded_data_marker)[1].strip()
        app.logger.info(f"🔐 Found encoded data section: {len(encoded_section)} characters")
        
        try:
            # Convert hex back to bytes
            decoded_bytes = bytes.fromhex(encoded_section)
            app.logger.info(f"✅ Successfully decoded {len(decoded_bytes)} bytes")
            
            # Return the decoded file as a download
            from flask import Response
            
            # Determine content type and filename
            if file_type == 'image':
                content_type = 'image/png'
                filename = 'decoded_message.png'
            else:
                content_type = 'text/plain'
                filename = 'decoded_message.txt'
            
            return Response(
                decoded_bytes,
                mimetype=content_type,
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}"',
                    'Content-Type': content_type
                }
            )
            
        except ValueError as e:
            app.logger.error(f"❌ Failed to decode hex data: {str(e)}")
            return jsonify({"error": "Invalid encoded data format"}), 400
        
    except Exception as e:
        app.logger.error(f"🚨 Decoding error: {str(e)}")
        return jsonify({
            "error": "Decoding failed",
            "message": str(e)
        }), 500

@app.route("/api/download/<pgn_id>", methods=["GET"])
def download_pgn(pgn_id):
    """Download encoded PGN file"""
    try:
        if pgn_id not in pgn_metadata_store:
            return jsonify({"error": "PGN not found"}), 404
        
        pgn_data = pgn_metadata_store[pgn_id]
        pgn_content = pgn_data["pgn_content"]
        
        from flask import Response
        return Response(
            pgn_content,
            mimetype='application/x-chess-pgn',
            headers={
                'Content-Disposition': f'attachment; filename="{pgn_id}.pgn"',
                'Content-Type': 'application/x-chess-pgn'
            }
        )
        
    except Exception as e:
        app.logger.error(f"Download error: {str(e)}")
        return jsonify({"error": "Download failed"}), 500

@app.route("/api/status", methods=["GET"])
def status():
    """Get status of transactions and stored data"""
    return jsonify({
        "transactions": len(transaction_store),
        "pgn_files": len(pgn_metadata_store),
        "server_time": datetime.now().isoformat()
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8001))
    print(f"Starting API server on port {port}")
    app.run(debug=False, port=port, host='0.0.0.0')
