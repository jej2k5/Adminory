'use client'

import ProtectedRoute from '@/components/auth/ProtectedRoute'
import { useAuth } from '@/hooks/useAuth'

export default function ExternalDashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  )
}

function DashboardContent() {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">
                Adminory - Customer Portal
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm">
                <p className="text-gray-700 font-medium">{user?.name}</p>
                <p className="text-gray-500 text-xs">{user?.email}</p>
              </div>
              <button
                onClick={() => logout()}
                className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Welcome to Your Dashboard
            </h2>
            <p className="text-gray-600 mb-6">
              Manage your workspace, team members, and integrations.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-2">
                  Workspace Settings
                </h3>
                <p className="text-sm text-gray-600">
                  Configure your workspace and preferences
                </p>
              </div>

              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-2">
                  Team Members
                </h3>
                <p className="text-sm text-gray-600">
                  Invite and manage team members
                </p>
              </div>

              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-2">
                  Usage & Billing
                </h3>
                <p className="text-sm text-gray-600">
                  View usage statistics and billing information
                </p>
              </div>
            </div>

            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <h3 className="font-semibold text-green-900 mb-2">
                Account Status
              </h3>
              <p className="text-sm text-green-700">
                Your account is active and in good standing.
              </p>
              {!user?.email_verified_at && (
                <p className="text-sm text-yellow-700 mt-2">
                  ⚠️ Please verify your email address to access all features.
                </p>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
