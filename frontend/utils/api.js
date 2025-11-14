import axios from 'axios'

/**
 * API client for communicating with the Data Cleaning Bot backend.
 * Handles file uploads and data retrieval.
 */

// Backend URL from environment (Vercel) OR fallback to localhost
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  'https://data-cleaning-bot-btya.onrender.com'; // fallback for safety

console.log("🔗 Using Backend URL:", API_BASE_URL);

/**
 * Upload a CSV file for cleaning.
 */
export async function uploadAndCleanData(file) {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_BASE_URL}/clean`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000,
    });

    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(
        error.response.data?.detail || 'Server error: ' + error.response.status,
      );
    } else if (error.request) {
      throw new Error('No response from server.');
    } else {
      throw new Error('Error: ' + error.message);
    }
  }
}

/**
 * Health check
 */
export async function checkHealth() {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`, {
      timeout: 5000,
    });
    return response.data.status === 'ok';
  } catch {
    return false;
  }
}

/**
 * Decode base64 to UTF-8
 */
export function decodeBase64(base64) {
  return Buffer.from(base64, 'base64').toString('utf-8');
}
