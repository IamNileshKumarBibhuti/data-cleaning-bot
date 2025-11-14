'use client'

import React, { useState } from 'react'
import FileUploader from '../components/FileUploader'
import DownloadButtons from '../components/DownloadButtons'
import CleaningSummary from '../components/CleaningSummary'
import AIReport from '../components/AIReport'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorBoundary from '../components/ErrorBoundary'
import { uploadAndCleanData } from '../utils/api'

/**
 * Main page component for the Data Cleaning Bot.
 * Handles file upload, displays results, and manages application state.
 */
export default function Home() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [cleaningResult, setCleaningResult] = useState(null)

  /**
   * Handle file upload and data cleaning.
   * Sends file to backend, receives cleaned data + script + report.
   */
  const handleFileUpload = async (file) => {
    setLoading(true)
    setError(null)
    setCleaningResult(null)

    try {
      const result = await uploadAndCleanData(file)

      if (!result.success) {
        throw new Error(result.message || 'Cleaning failed')
      }

      setCleaningResult(result)
    } catch (err) {
      setError(err.message || 'An error occurred during cleaning')
      console.error('Cleaning error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <ErrorBoundary>
      <main className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              🤖 Data Cleaning Bot
            </h1>
            <p className="text-xl text-gray-600">
              Automatically clean your CSV data with AI-powered insights
            </p>
          </div>

          {/* Main Container */}
          <div className="bg-white rounded-lg shadow-xl p-8 mb-8">
            {/* File Uploader Section */}
            <div className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                📁 Upload CSV File
              </h2>
              <FileUploader
                onFileSelect={handleFileUpload}
                disabled={loading}
              />
            </div>

            {/* Loading State */}
            {loading && (
              <div className="py-12">
                <LoadingSpinner />
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="bg-red-50 border-2 border-red-300 rounded-lg p-6 mb-8">
                <p className="text-red-800 font-semibold">❌ Error</p>
                <p className="text-red-600">{error}</p>
              </div>
            )}

            {/* Results Section */}
            {cleaningResult && !loading && (
              <div className="space-y-8">
                {/* Download Section */}
                <div>
                  <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                    📥 Download Results
                  </h2>
                  <DownloadButtons cleaningResult={cleaningResult} />
                </div>

                {/* Cleaning Summary */}
                {cleaningResult.summary && (
                  <div>
                    <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                      📊 Cleaning Summary
                    </h2>
                    <CleaningSummary summary={cleaningResult.summary} />
                  </div>
                )}

                {/* AI Report */}
                {cleaningResult.ai_report && (
                  <div>
                    <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                      🔍 AI Analysis Report
                    </h2>
                    <AIReport report={cleaningResult.ai_report} />
                  </div>
                )}
              </div>
            )}

            {/* Empty State */}
            {!cleaningResult && !loading && !error && (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📤</div>
                <p className="text-gray-500 text-lg">
                  Upload a CSV file to get started
                </p>
              </div>
            )}
          </div>

          {/* Footer Info */}
          <div className="bg-blue-50 rounded-lg p-6 text-center">
            <p className="text-sm text-gray-600">
              💡 Tip: The system will automatically trim spaces, normalize text,
              fix dates, handle missing values, remove duplicates, and detect outliers.
            </p>
          </div>
        </div>
      </main>
    </ErrorBoundary>
  )
}
