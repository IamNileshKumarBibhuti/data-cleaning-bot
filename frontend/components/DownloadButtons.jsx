'use client'

import React from 'react'

/**
 * DownloadButtons component - Provides download links for cleaned CSV and Python script.
 */
export default function DownloadButtons({ cleaningResult }) {
  /**
   * Download file from base64 encoded data.
   * @param {string} base64Data - Base64 encoded file content
   * @param {string} filename - Name of file to download
   */
  const downloadFile = (base64Data, filename) => {
    // Decode base64 to binary
    const binaryString = atob(base64Data)
    const bytes = new Uint8Array(binaryString.length)
    
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i)
    }
    
    // Create blob and download
    const blob = new Blob([bytes], { type: 'text/plain' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    window.URL.revokeObjectURL(url)
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Download Cleaned CSV */}
      <button
        onClick={() =>
          downloadFile(
            cleaningResult.cleaned_csv_base64,
            'cleaned_data.csv'
          )
        }
        className="
          bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-6
          rounded-lg transition-colors duration-200 flex items-center justify-center
          shadow-md hover:shadow-lg
        "
      >
        <span className="mr-2">📥</span>
        Download Cleaned CSV
      </button>

      {/* Download Python Script */}
      <button
        onClick={() =>
          downloadFile(
            cleaningResult.cleaning_script_base64,
            'clean_data.py'
          )
        }
        className="
          bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-6
          rounded-lg transition-colors duration-200 flex items-center justify-center
          shadow-md hover:shadow-lg
        "
      >
        <span className="mr-2">🐍</span>
        Download Python Script
      </button>
    </div>
  )
}
