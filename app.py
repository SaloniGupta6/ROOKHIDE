import os
import json
import uuid
import hashlib
from datetime import datetime, timedelta
from base64 import b64encode, b64decode
from flask import Flask, request, render_template, send_file, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from encode import encode
from decode import decode
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)  # Enable CORS for React frontend

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
STORAGE_FOLDER = "blockchain_storage"
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpeg', 'pgn'}

# Create necessary directories
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, STORAGE_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['STORAGE_FOLDER'] = STORAGE_FOLDER

# In-memory storage for demo (replace with proper database in production)
transaction_store = {}
pgn_metadata_store = {}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_safe_filename(filename):
    filename = os.path.basename(filename)
    return secure_filename(filename)

def generate_transaction_id():
    """Generate a unique transaction ID"""
    return str(uuid.uuid4())

def calculate_file_hash(file_data):
    """Calculate SHA-256 hash of file data"""
    return hashlib.sha256(file_data).hexdigest()

def validate_wallet_signature(wallet_address, signature, message):
    """Validate wallet signature (placeholder - implement actual validation)"""
    # In production, implement proper signature validation
    return len(wallet_address) > 20 and len(signature) > 50

# Blockchain Integration Endpoints

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

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/file_upload")
def file_upload():
    return render_template("file.html")

@app.route("/about")
def about():
    return render_template("About.html")

@app.route("/get_in_touch")
def get_in_touch():
    return render_template("touch.html")

@app.route("/visualizer")
def visualizer():
    return render_template("visualizer.html")

@app.route('/preview', methods=["GET", "POST"])
def preview():
    if request.method == "GET":
        # Render the preview template when accessed via GET
        return render_template("preview.html")
    else:
        # Handle POST request for file preview
        try:
            if 'file' not in request.files:
                return jsonify({"error": "No file part"}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400
            
            file_type = request.form.get("file_type")
            if not file_type or file_type not in ['text', 'image']:
                return jsonify({"error": "Invalid file type"}), 400
            
            # Read file data
            file_data = file.read()
            if len(file_data) == 0:
                return jsonify({"error": "File is empty"}), 400
                
            # For preview, we'll return some basic info and a sample of the binary data
            file_info = {
                "filename": file.filename,
                "size": len(file_data),
                "file_type": file_type,
                "bit_count": len(file_data) * 8,
                # Send back a base64 sample for the UI to show
                "data_sample": b64encode(file_data[:1024] if len(file_data) > 1024 else file_data).decode('utf-8')
            }
            
            return jsonify({"success": True, "file_info": file_info})
            
        except Exception as e:
            app.logger.error(f"Preview encoding error: {str(e)}", exc_info=True)
            return jsonify({"error": f"Error processing file: {str(e)}"}), 500

@app.route("/api/encode", methods=["POST"])
def handle_encode():
    try:
        app.logger.debug("Starting encode request")
        
        # MANDATORY: Check wallet connection
        wallet_address = request.form.get("wallet_address")
        if not wallet_address:
            return jsonify({
                "error": "Wallet connection required", 
                "code": "WALLET_NOT_CONNECTED",
                "message": "Please connect your Coinbase Wallet before encoding"
            }), 401
        
        # MANDATORY: Check for X402 payment verification
        transaction_id = request.form.get("transaction_id")
        if not transaction_id:
            return jsonify({
                "error": "X402 payment required", 
                "code": "PAYMENT_REQUIRED",
                "message": "Please complete X402 micropayment before encoding"
            }), 402
            
        if transaction_id not in transaction_store:
            return jsonify({
                "error": "Invalid transaction ID", 
                "code": "INVALID_TRANSACTION",
                "message": "Transaction ID not found or expired"
            }), 400
        
        transaction = transaction_store[transaction_id]
        if transaction["status"] != "confirmed":
            return jsonify({
                "error": "Payment not confirmed", 
                "code": "PAYMENT_PENDING",
                "message": "X402 payment is still pending confirmation"
            }), 402
        
        if transaction["operation"] != "encode":
            return jsonify({
                "error": "Invalid operation", 
                "code": "WRONG_OPERATION",
                "message": "This transaction is not for encoding operation"
            }), 400
            
        # Verify wallet address matches transaction
        if transaction["wallet_address"] != wallet_address:
            return jsonify({
                "error": "Wallet mismatch", 
                "code": "WALLET_MISMATCH",
                "message": "Wallet address doesn't match the payment transaction"
            }), 403
        
        if 'file' not in request.files:
            app.logger.error("No file part in request")
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        app.logger.debug(f"Received file: {file.filename}")
        
        if file.filename == '':
            app.logger.error("No selected file")
            return jsonify({"error": "No selected file"}), 400
        
        file_type = request.form.get("file_type")
        wallet_address = request.form.get("wallet_address")
        app.logger.debug(f"File type: {file_type}, Wallet: {wallet_address}")
        
        # Get self-destruct timer from form (in seconds)
        self_destruct_timer = request.form.get("self_destruct_timer")
        if self_destruct_timer:
            try:
                self_destruct_timer = int(self_destruct_timer)
                app.logger.debug(f"Self-destruct timer set to: {self_destruct_timer} seconds")
            except ValueError:
                app.logger.error(f"Invalid self-destruct timer value: {self_destruct_timer}")
                return jsonify({"error": "Invalid self-destruct timer value"}), 400
        else:
            self_destruct_timer = None
            app.logger.debug("No self-destruct timer provided")
        
        # Get custom PGN headers from form
        custom_headers = {}
        pgn_header_fields = [
            "Event", "Site", "Date", "Round", "White", "Black", 
            "WhiteElo", "BlackElo", "Result", "ECO"
        ]
        
        for field in pgn_header_fields:
            value = request.form.get(f"pgn_{field.lower()}")
            if value:
                custom_headers[field] = value
                app.logger.debug(f"Custom header {field}: {value}")
        
        if not file_type or file_type not in ['text', 'image']:
            app.logger.error(f"Invalid file type: {file_type}")
            return jsonify({"error": "Invalid file type"}), 400
        
        if file and allowed_file(file.filename):
            filename = get_safe_filename(file.filename)
            app.logger.debug(f"Safe filename: {filename}")

            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            app.logger.debug(f"Saving to: {input_path}")
            file.save(input_path)

            output_path = os.path.join(app.config['OUTPUT_FOLDER'], "encoded_output.pgn")
            app.logger.debug(f"Output path: {output_path}")

            try:
                # Pass the self-destruct timer and custom headers to the encode function
                encode(input_path, output_path, self_destruct_timer, custom_headers if custom_headers else None)
                app.logger.debug("Encoding completed")
                
                # Store PGN metadata for blockchain tracking
                with open(output_path, 'rb') as f:
                    pgn_data = f.read()
                    pgn_hash = calculate_file_hash(pgn_data)
                
                # Generate unique PGN ID
                pgn_id = generate_transaction_id()
                
                # Store metadata
                pgn_metadata_store[pgn_id] = {
                    "pgn_hash": pgn_hash,
                    "original_filename": filename,
                    "wallet_address": wallet_address,
                    "transaction_id": transaction_id,
                    "created_at": datetime.now().isoformat(),
                    "file_type": file_type,
                    "self_destruct_timer": self_destruct_timer,
                    "custom_headers": custom_headers
                }
                
                # Store PGN file in blockchain storage
                blockchain_path = os.path.join(app.config['STORAGE_FOLDER'], f"{pgn_id}.pgn")
                with open(blockchain_path, 'wb') as f:
                    f.write(pgn_data)
                
            except Exception as e:
                app.logger.error(f"Encoding failed: {str(e)}", exc_info=True)
                return jsonify({"error": f"Encoding failed: {str(e)}"}), 500

            if not os.path.exists(output_path):
                app.logger.error("Output file was not created")
                return jsonify({"error": "Output file was not created"}), 500

            app.logger.debug("Sending encoded file")
            
            # Return both file and metadata
            response_data = {
                "success": True,
                "pgn_id": pgn_id,
                "pgn_hash": pgn_hash,
                "message": "File encoded successfully"
            }
            
            # For API calls (from React frontend), return JSON with download link
            if request.path.startswith('/api/'):
                response_data["download_url"] = f"/api/download/{pgn_id}"
                return jsonify(response_data)
            else:
                # For direct form uploads, return file directly
                return send_file(output_path, as_attachment=True, download_name="encoded_output.pgn")
        
        app.logger.error("File type not allowed")
        return jsonify({"error": "File type not allowed"}), 400

    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route("/api/decode", methods=["POST"])
def handle_decode():
    try:
        app.logger.debug("Starting decode request")
        
        # MANDATORY: Check wallet connection
        wallet_address = request.form.get("wallet_address")
        if not wallet_address:
            return jsonify({
                "error": "Wallet connection required", 
                "code": "WALLET_NOT_CONNECTED",
                "message": "Please connect your Coinbase Wallet before decoding"
            }), 401
        
        # MANDATORY: Check for X402 payment verification
        transaction_id = request.form.get("transaction_id")
        if not transaction_id:
            return jsonify({
                "error": "X402 payment required", 
                "code": "PAYMENT_REQUIRED",
                "message": "Please complete X402 micropayment before decoding"
            }), 402
            
        if transaction_id not in transaction_store:
            return jsonify({
                "error": "Invalid transaction ID", 
                "code": "INVALID_TRANSACTION",
                "message": "Transaction ID not found or expired"
            }), 400
        
        transaction = transaction_store[transaction_id]
        if transaction["status"] != "confirmed":
            return jsonify({
                "error": "Payment not confirmed", 
                "code": "PAYMENT_PENDING",
                "message": "X402 payment is still pending confirmation"
            }), 402
        
        if transaction["operation"] != "decode":
            return jsonify({
                "error": "Invalid operation", 
                "code": "WRONG_OPERATION",
                "message": "This transaction is not for decoding operation"
            }), 400
            
        # Verify wallet address matches transaction
        if transaction["wallet_address"] != wallet_address:
            return jsonify({
                "error": "Wallet mismatch", 
                "code": "WALLET_MISMATCH",
                "message": "Wallet address doesn't match the payment transaction"
            }), 403
        
        if 'file' not in request.files:
            app.logger.error("No file part in request")
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        app.logger.debug(f"Received file: {file.filename}")

        if file.filename == '':
            app.logger.error("No selected file")
            return jsonify({"error": "No selected file"}), 400

        file_type = request.form.get("file_type")
        wallet_address = request.form.get("wallet_address")
        app.logger.debug(f"File type: {file_type}, Wallet: {wallet_address}")
        
        if not file_type or file_type not in ['text', 'image']:
            app.logger.error(f"Invalid file type: {file_type}")
            return jsonify({"error": "Invalid file type"}), 400

        if file and allowed_file(file.filename):
            filename = get_safe_filename(file.filename)
            app.logger.debug(f"Safe filename: {filename}")
            
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            app.logger.debug(f"Saving to: {input_path}")
            file.save(input_path)

            output_extension = "txt" if file_type == "text" else "png"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"decoded_output.{output_extension}")
            app.logger.debug(f"Output path: {output_path}")
            
            try:
                decode(input_path, output_path)
                app.logger.debug("Decoding completed")
            except Exception as e:
                app.logger.error(f"Decoding failed: {str(e)}", exc_info=True)
                return jsonify({"error": f"Decoding failed: {str(e)}"}), 500
            
            if not os.path.exists(output_path):
                app.logger.error("Output file was not created")
                return jsonify({"error": "Output file was not created"}), 500
                
            app.logger.debug("Sending decoded file")
            return send_file(output_path, as_attachment=True, 
                             download_name=f"decoded_output.{output_extension}")
        
        app.logger.error("File type not allowed")
        return jsonify({"error": "File type not allowed"}), 400

    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
        
# Additional API endpoints for decentralized features

@app.route("/api/download/<pgn_id>", methods=["GET"])
def download_pgn(pgn_id):
    """Download PGN file by ID"""
    try:
        if pgn_id not in pgn_metadata_store:
            return jsonify({"error": "PGN not found"}), 404
        
        blockchain_path = os.path.join(app.config['STORAGE_FOLDER'], f"{pgn_id}.pgn")
        if not os.path.exists(blockchain_path):
            return jsonify({"error": "PGN file not found"}), 404
        
        metadata = pgn_metadata_store[pgn_id]
        return send_file(blockchain_path, as_attachment=True, 
                        download_name=f"encoded_{metadata['original_filename']}.pgn")
        
    except Exception as e:
        app.logger.error(f"Download error: {str(e)}")
        return jsonify({"error": "Download failed"}), 500

@app.route("/api/pgn/metadata/<pgn_id>", methods=["GET"])
def get_pgn_metadata(pgn_id):
    """Get PGN metadata by ID"""
    try:
        if pgn_id not in pgn_metadata_store:
            return jsonify({"error": "PGN not found"}), 404
        
        metadata = pgn_metadata_store[pgn_id]
        # Remove sensitive information
        public_metadata = {
            "pgn_id": pgn_id,
            "pgn_hash": metadata["pgn_hash"],
            "created_at": metadata["created_at"],
            "file_type": metadata["file_type"]
        }
        
        return jsonify({"success": True, "metadata": public_metadata})
        
    except Exception as e:
        app.logger.error(f"Metadata retrieval error: {str(e)}")
        return jsonify({"error": "Metadata retrieval failed"}), 500

@app.route("/api/pgn/list", methods=["GET"])
def list_user_pgns():
    """List PGNs for a specific wallet address"""
    try:
        wallet_address = request.args.get('wallet_address')
        if not wallet_address:
            return jsonify({"error": "Wallet address required"}), 400
        
        user_pgns = []
        for pgn_id, metadata in pgn_metadata_store.items():
            if metadata.get("wallet_address") == wallet_address:
                user_pgns.append({
                    "pgn_id": pgn_id,
                    "pgn_hash": metadata["pgn_hash"],
                    "original_filename": metadata["original_filename"],
                    "created_at": metadata["created_at"],
                    "file_type": metadata["file_type"]
                })
        
        return jsonify({"success": True, "pgns": user_pgns})
        
    except Exception as e:
        app.logger.error(f"PGN listing error: {str(e)}")
        return jsonify({"error": "PGN listing failed"}), 500

@app.route("/api/pgn/validate", methods=["POST"])
def validate_pgn():
    """Validate a PGN file and check if it contains hidden data"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Read and validate PGN
        pgn_content = file.read().decode('utf-8')
        file_hash = calculate_file_hash(pgn_content.encode('utf-8'))
        
        # Basic PGN validation (you can enhance this)
        is_valid_pgn = '[Event ' in pgn_content and '[Result ' in pgn_content
        has_hidden_data = 'DataBitLength' in pgn_content
        
        # Check if this PGN exists in our store
        pgn_exists = any(metadata["pgn_hash"] == file_hash for metadata in pgn_metadata_store.values())
        
        return jsonify({
            "success": True,
            "is_valid_pgn": is_valid_pgn,
            "has_hidden_data": has_hidden_data,
            "file_hash": file_hash,
            "pgn_exists_in_store": pgn_exists
        })
        
    except Exception as e:
        app.logger.error(f"PGN validation error: {str(e)}")
        return jsonify({"error": "PGN validation failed"}), 500

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

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File is too large. Maximum file size is 16 MB"}), 413

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=False, port=port, host='0.0.0.0')