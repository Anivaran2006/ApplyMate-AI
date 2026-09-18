/**
 * ApplyMate AI – Frontend Configuration
 *
 * Backend API:  https://applymate-ai.onrender.com/api/v1
 * Frontend:     https://applymate-ai-gz7k.onrender.com
 *
 * Automatically uses localhost when running locally.
 */

const _isProd = window.location.hostname !== 'localhost'
             && window.location.hostname !== '127.0.0.1';

window.API_BASE_URL = _isProd
  ? 'https://applymate-ai.onrender.com/api/v1'
  : 'http://localhost:8000/api/v1';
