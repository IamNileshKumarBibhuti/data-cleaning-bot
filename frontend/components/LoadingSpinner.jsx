'use client'

import React from 'react'

/**
 * LoadingSpinner component - Shows during data cleaning process.
 */
export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center space-y-4">
      <div className="relative w-16 h-16">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full animate-spin-slow opacity-75" />
        <div className="absolute inset-2 bg-white rounded-full" />
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl animate-pulse">🔄</span>
        </div>
      </div>
      <div className="text-center">
        <p className="text-lg font-semibold text-gray-800">Cleaning your data...</p>
        <p className="text-sm text-gray-600 mt-2">
          This may take a few moments. Please don't close this page.
        </p>
      </div>
    </div>
  )
}
