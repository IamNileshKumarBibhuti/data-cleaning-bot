'use client'

import React from 'react'

/**
 * CleaningSummary component - Displays statistics about the cleaning operation.
 * Shows before/after metrics and what was changed.
 */
export default function CleaningSummary({ summary }) {
  /**
   * Calculate percentage change.
   */
  const getPercentage = (value, total) => {
    if (total === 0) return 0
    return ((value / total) * 100).toFixed(1)
  }

  const removalPercentage = getPercentage(
    summary.rows_removed,
    summary.original_rows
  )

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Data Volume Section */}
      <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-4">📊 Data Volume</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-blue-800">Original Rows:</span>
            <span className="text-2xl font-bold text-blue-900">
              {summary.original_rows}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-blue-800">Cleaned Rows:</span>
            <span className="text-2xl font-bold text-blue-900">
              {summary.cleaned_rows}
            </span>
          </div>
          <div className="flex justify-between items-center pt-2 border-t border-blue-200">
            <span className="text-blue-800">Rows Removed:</span>
            <span className="text-lg font-bold text-red-600">
              {summary.rows_removed} ({removalPercentage}%)
            </span>
          </div>
        </div>
      </div>

      {/* Cleaning Operations Section */}
      <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-purple-900 mb-4">
          ✨ Cleaning Operations
        </h3>
        <div className="space-y-3">
          {summary.duplicates_removed > 0 && (
            <div className="flex justify-between items-center">
              <span className="text-purple-800">Duplicates Removed:</span>
              <span className="font-bold text-purple-900">
                {summary.duplicates_removed}
              </span>
            </div>
          )}
          {summary.missing_values_handled > 0 && (
            <div className="flex justify-between items-center">
              <span className="text-purple-800">Missing Values Fixed:</span>
              <span className="font-bold text-purple-900">
                {summary.missing_values_handled}
              </span>
            </div>
          )}
          {summary.outliers_replaced > 0 && (
            <div className="flex justify-between items-center">
              <span className="text-purple-800">Outliers Replaced:</span>
              <span className="font-bold text-purple-900">
                {summary.outliers_replaced}
              </span>
            </div>
          )}
          {summary.date_columns_fixed > 0 && (
            <div className="flex justify-between items-center">
              <span className="text-purple-800">Date Columns Fixed:</span>
              <span className="font-bold text-purple-900">
                {summary.date_columns_fixed}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Data Quality Metrics */}
      <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-green-900 mb-4">📈 Data Quality</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-green-800">Total Columns:</span>
            <span className="text-2xl font-bold text-green-900">
              {summary.columns}
            </span>
          </div>
          <div className="w-full bg-green-200 rounded-full h-2">
            <div
              className="bg-green-600 h-2 rounded-full transition-all"
              style={{
                width: `${100 - (removalPercentage || 0)}%`,
              }}
            />
          </div>
          <p className="text-sm text-green-700">
            Data retained: {(100 - (removalPercentage || 0)).toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Quality Score */}
      <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-orange-900 mb-4">
          🎯 Quality Score
        </h3>
        <div className="text-center">
          <div className="text-5xl font-bold text-orange-900 mb-2">
            {Math.max(0, Math.min(100, 100 - (removalPercentage || 0))).toFixed(0)}%
          </div>
          <p className="text-sm text-orange-700">
            Data quality after cleaning
          </p>
        </div>
      </div>
    </div>
  )
}
