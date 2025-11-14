import React from 'react'
import '../styles/globals.css'

export const metadata = {
  title: 'Data Cleaning Bot',
  description: 'Automatic CSV data cleaning with AI reports',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
        {children}
      </body>
    </html>
  )
}
