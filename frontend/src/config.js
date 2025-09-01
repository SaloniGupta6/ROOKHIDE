// API Configuration
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

// API endpoints
export const API_ENDPOINTS = {
  HEALTH: '/api/health',
  WALLET_CONNECT: '/api/wallet/connect',
  PAYMENT_INITIATE: '/api/payment/initiate',
  PAYMENT_VERIFY: '/api/payment/verify',
  ENCODE: '/api/encode',
  DECODE: '/api/decode',
  PGN_VALIDATE: '/api/pgn/validate',
  PGN_LIST: '/api/pgn/list',
  DOWNLOAD: '/api/download'
};

// Helper function to build full API URLs
export const getApiUrl = (endpoint) => `${API_BASE_URL}${endpoint}`;