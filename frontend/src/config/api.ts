export const logger = {
    info: (message: string, data?: unknown) => {
      if (process.env.NODE_ENV === 'development') {
        console.log(`ℹ️ ${message}`, data ? data : '');
      }
    },
    success: (message: string, data?: unknown) => {
      if (process.env.NODE_ENV === 'development') {
        console.log(`✅ ${message}`, data ? data : '');
      }
    },
    warn: (message: string, data?: unknown) => {
      if (process.env.NODE_ENV === 'development') {
        console.warn(`⚠️ ${message}`, data ? data : '');
      }
    },
  };

// Get API base URL based on environment
const getApiBaseUrl = () => {
    if (process.env.NODE_ENV === 'development') {
      return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    }
    // In production, use the same Vercel domain for API
    // Check if window exists (client-side only)
    return process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' ? window.location.origin : '');
  };

export const API_BASE_URL = getApiBaseUrl();

export const API_ENDPOINTS = {
    HEALTH: `${API_BASE_URL}/health`,
    UPLOAD_PDF: `${API_BASE_URL}/api/upload_pdf`,
    ANALYZE_DEVICE: `${API_BASE_URL}/api/analyze_device`,
    FETCH_BULK_IFU: `${API_BASE_URL}/api/fetch-bulk-ifu`,
    CHECK_PREDICATE_EQUIVALENCE: `${API_BASE_URL}/api/check-predicate-equivalence`,
    SEARCH_DEVICES: `${API_BASE_URL}/api/search-devices`,
    DISCOVER_PREDICATES: `${API_BASE_URL}/api/discover-predicates`,
} as const; 
