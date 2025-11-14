'use client'

import React, { useRef } from 'react'

/**
 * FileUploader component - Handles CSV file selection and upload.
 * Provides drag-and-drop and click-to-select interfaces.
 */
export default function FileUploader({ onFileSelect, disabled }) {
  const fileInputRef = useRef(null)
  const [dragActive, setDragActive] = React.useState(false)
  const [selectedFile, setSelectedFile] = React.useState(null)

  /**
   * Validate file is a CSV.
   * @param {File} file - File to validate
   * @returns {boolean} - True if valid CSV
   */
  const isValidFile = (file) => {
    return file.name.endsWith('.csv') && file.type === 'text/csv'
  }

  /**
   * Handle file selection from input or drag-drop.
   */
  const handleFile = (file) => {
    if (!file) return

    if (!isValidFile(file)) {
      alert('Please select a valid CSV file')
      return
    }

    setSelectedFile(file)
    onFileSelect(file)
  }

  /**
   * Handle drag events for drop zone.
   */
  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()

    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  /**
   * Handle file drop.
   */
  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      handleFile(files[0])
    }
  }

  /**
   * Handle click to select file.
   */
  const handleClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  /**
   * Handle file input change.
   */
  const handleInputChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0])
    }
  }

  return (
    <div
      className={`
        border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
        transition-colors duration-200
        ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-blue-400'}
      `}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv"
        onChange={handleInputChange}
        disabled={disabled}
        className="hidden"
        aria-label="CSV file input"
      />

      <div className="space-y-3">
        <div className="text-5xl">📤</div>
        <h3 className="text-lg font-semibold text-gray-900">
          Drag and drop your CSV here
        </h3>
        <p className="text-gray-600">or click to browse your computer</p>
        <p className="text-sm text-gray-500">
          Maximum file size: 50MB
        </p>
      </div>

      {selectedFile && (
        <div className="mt-4 p-3 bg-green-50 rounded text-left">
          <p className="text-green-800 font-semibold">✓ File selected:</p>
          <p className="text-green-700">{selectedFile.name}</p>
          <p className="text-sm text-green-600">
            {(selectedFile.size / 1024).toFixed(2)} KB
          </p>
        </div>
      )}
    </div>
  )
}
