import axios from 'axios'

/**
 * API client for communicating with the Data Cleaning Bot backend.
 * Handles file uploads and data retrieval.
 */

// Get backend URL from environment or use default
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Upload a CSV file for cleaning.
 * 
 * @param {File} file - The CSV file to upload
 * @returns {Promise} - Response with cleaned data, script, and AI report
 */
export async function uploadAndCleanData(file) {
  try {
    // Create FormData for file upload
    const formData = new FormData()
    formData.append('file', file)

    // Send request to backend
    const response = await axios.post(`${API_BASE_URL}/clean`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 second timeout
    })

    return response.data
  } catch (error) {
    // Handle different error types
    if (error.response) {
      // Server responded with error
      throw new Error(
        error.response.data?.detail || 'Server error: ' + error.response.status
      )
    } else if (error.request) {
      // Request made but no response
      throw new Error('No response from server. Is the backend running?')
    } else {
      // Error in setup
      throw new Error('Error: ' + error.message)
    }
  }
}

/**
 * Check backend health status.
 * 
 * @returns {Promise<boolean>} - True if backend is healthy
 */
export async function checkHealth() {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`, {
      timeout: 5000,
    })
    return response.data.status === 'ok'
  } catch {
    return false
  }
}

/**
 * Decode base64 string to text.
 * Used for downloaded CSV and Python scripts.
 * 
 * @param {string} base64 - Base64 encoded string
 * @returns {string} - Decoded text
 */
export function decodeBase64(base64) {
  return Buffer.from(base64, 'base64').toString('utf-8')
}
