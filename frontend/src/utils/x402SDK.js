/**
 * X402 Payment SDK
 * Simulated implementation for chess steganography micropayments
 */

class X402SDK {
  constructor(options = {}) {
    this.apiUrl = options.apiUrl || 'http://localhost:8001';
    this.walletProvider = options.walletProvider;
    this.networkConfig = {
      chainId: options.chainId || 1,
      name: options.network || 'ethereum',
      currency: 'ETH',
    };
    this.paymentProtocol = 'x402-v1.0';
  }

  /**
   * Initialize a payment session
   * @param {Object} paymentRequest - Payment request details
   * @returns {Promise<Object>} Payment session data
   */
  async initiatePayment(paymentRequest) {
    try {
      const { walletAddress, operation, fileHash, amount } = paymentRequest;

      if (!walletAddress) {
        throw new Error('Wallet address is required for X402 payments');
      }

      if (!operation || !['encode', 'decode'].includes(operation)) {
        throw new Error('Valid operation (encode/decode) is required');
      }

      if (!fileHash) {
        throw new Error('File hash is required for payment verification');
      }

      // Call the backend API to initiate payment
      const response = await fetch(`${this.apiUrl}/api/payment/initiate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Protocol': this.paymentProtocol,
        },
        body: JSON.stringify({
          wallet_address: walletAddress,
          operation,
          file_hash: fileHash,
          protocol: this.paymentProtocol,
          network: this.networkConfig.name,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Payment initiation failed');
      }

      const paymentData = await response.json();

      return {
        success: true,
        transactionId: paymentData.transaction_id,
        amount: paymentData.payment_amount,
        amountEth: paymentData.payment_amount_eth,
        paymentAddress: paymentData.payment_address,
        expiresIn: paymentData.expires_in,
        protocol: paymentData.x402_protocol,
        message: paymentData.message,
      };
    } catch (error) {
      console.error('X402 Payment Initiation Error:', error);
      throw error;
    }
  }

  /**
   * Process the payment through the wallet
   * @param {Object} paymentSession - Payment session from initiatePayment
   * @returns {Promise<Object>} Transaction result
   */
  async processPayment(paymentSession) {
    try {
      if (!this.walletProvider) {
        throw new Error('Wallet provider not configured');
      }

      const { transactionId, amount, paymentAddress } = paymentSession;

      // Simulate wallet transaction (in production, this would be real)
      const transactionParams = {
        to: paymentAddress,
        value: `0x${parseInt(amount).toString(16)}`, // Convert wei to hex
        gas: '0x5208', // Standard gas limit for ETH transfer
        gasPrice: '0x9184e72a000', // 10 Gwei
      };

      // Simulate the transaction
      console.log('Processing X402 payment with params:', transactionParams);
      
      // In a real implementation, this would call:
      // const txHash = await this.walletProvider.request({
      //   method: 'eth_sendTransaction',
      //   params: [transactionParams],
      // });

      // For demo purposes, generate a simulated transaction hash
      const simulatedTxHash = this.generateSimulatedTxHash();

      return {
        success: true,
        transactionId,
        txHash: simulatedTxHash,
        message: 'Payment processed successfully',
      };
    } catch (error) {
      console.error('X402 Payment Processing Error:', error);
      throw error;
    }
  }

  /**
   * Verify payment completion
   * @param {Object} paymentResult - Result from processPayment
   * @returns {Promise<Object>} Verification result
   */
  async verifyPayment(paymentResult) {
    try {
      const { transactionId, txHash } = paymentResult;

      const response = await fetch(`${this.apiUrl}/api/payment/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Protocol': this.paymentProtocol,
        },
        body: JSON.stringify({
          transaction_id: transactionId,
          tx_hash: txHash,
          protocol: this.paymentProtocol,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Payment verification failed');
      }

      const verificationData = await response.json();

      return {
        success: verificationData.success,
        status: verificationData.status,
        message: verificationData.message,
        transactionId,
        txHash,
      };
    } catch (error) {
      console.error('X402 Payment Verification Error:', error);
      throw error;
    }
  }

  /**
   * Complete payment flow (initiate + process + verify)
   * @param {Object} paymentRequest - Payment request details
   * @returns {Promise<Object>} Complete payment result
   */
  async completePayment(paymentRequest) {
    try {
      // Step 1: Initiate payment
      const paymentSession = await this.initiatePayment(paymentRequest);

      // Step 2: Process payment through wallet
      const paymentResult = await this.processPayment(paymentSession);

      // Step 3: Verify payment
      const verificationResult = await this.verifyPayment(paymentResult);

      return {
        success: verificationResult.success,
        transactionId: paymentResult.transactionId,
        txHash: paymentResult.txHash,
        amount: paymentSession.amountEth,
        status: verificationResult.status,
        message: verificationResult.message,
      };
    } catch (error) {
      console.error('X402 Complete Payment Error:', error);
      throw error;
    }
  }

  /**
   * Get payment status
   * @param {string} transactionId - Transaction ID to check
   * @returns {Promise<Object>} Payment status
   */
  async getPaymentStatus(transactionId) {
    try {
      const response = await fetch(`${this.apiUrl}/api/payment/status/${transactionId}`, {
        headers: {
          'X-Protocol': this.paymentProtocol,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch payment status');
      }

      return await response.json();
    } catch (error) {
      console.error('X402 Payment Status Error:', error);
      throw error;
    }
  }

  /**
   * Calculate file hash for payment verification
   * @param {File} file - File to calculate hash for
   * @returns {Promise<string>} SHA-256 hash of file
   */
  async calculateFileHash(file) {
    try {
      const arrayBuffer = await file.arrayBuffer();
      const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    } catch (error) {
      console.error('File hash calculation error:', error);
      throw error;
    }
  }

  /**
   * Generate simulated transaction hash for demo purposes
   * @returns {string} Simulated transaction hash
   */
  generateSimulatedTxHash() {
    const chars = '0123456789abcdef';
    let result = '0x';
    for (let i = 0; i < 64; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }

  /**
   * Get payment configuration
   * @returns {Object} Payment configuration
   */
  getConfig() {
    return {
      protocol: this.paymentProtocol,
      network: this.networkConfig,
      apiUrl: this.apiUrl,
      supportedOperations: ['encode', 'decode'],
      paymentAmounts: {
        encode: '0.002', // ETH
        decode: '0.001', // ETH
      },
    };
  }

  /**
   * Validate payment request
   * @param {Object} paymentRequest - Payment request to validate
   * @returns {Object} Validation result
   */
  validatePaymentRequest(paymentRequest) {
    const errors = [];

    if (!paymentRequest.walletAddress) {
      errors.push('Wallet address is required');
    }

    if (!paymentRequest.operation || !['encode', 'decode'].includes(paymentRequest.operation)) {
      errors.push('Valid operation (encode/decode) is required');
    }

    if (!paymentRequest.fileHash) {
      errors.push('File hash is required');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}

// Export singleton instance
const x402SDK = new X402SDK();

export default x402SDK;
export { X402SDK };
