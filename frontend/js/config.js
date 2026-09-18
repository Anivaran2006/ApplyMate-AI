/**
 * ApplyMate AI – Frontend Configuration
 * Automatically points to the current origin's /api/v1
 */
window.API_BASE_URL = window.location.origin
  ? `${window.location.origin}/api/v1`
  : '/api/v1';
