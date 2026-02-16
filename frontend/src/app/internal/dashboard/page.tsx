'use client'

import ProtectedRoute from '@/components/auth/ProtectedRoute'
import { useAuth } from '@/hooks/useAuth'

export default function InternalDashboardPage() {
  return (
    <ProtectedRoute requireAdmin={true}>
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
                Adminory - Internal Control Plane
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
              Welcome to the Internal Dashboard
            </h2>
            <p className="text-gray-600 mb-6">
              This is the internal control plane for operations teams and
              administrators.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-2">
                  System Health
                </h3>
                <p className="text-sm text-gray-600">
                  Monitor system performance and health metrics
                </p>
              </div>

              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-2">
                  User Management
                </h3>
                <p className="text-sm text-gray-600">
                  Manage users, workspaces, and permissions
                </p>
              </div>

              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-2">
                  Audit Logs
                </h3>
                <p className="text-sm text-gray-600">
                  View system audit logs and activity
                </p>
              </div>
            </div>

            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">
                User Information
              </h3>
              <dl className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <dt className="text-blue-700">ID:</dt>
                  <dd className="text-blue-900 font-mono">{user?.id}</dd>
                </div>
                <div>
                  <dt className="text-blue-700">Role:</dt>
                  <dd className="text-blue-900 font-semibold uppercase">
                    {user?.role}
                  </dd>
                </div>
                <div>
                  <dt className="text-blue-700">Email Verified:</dt>
                  <dd className="text-blue-900">
                    {user?.email_verified_at ? 'Yes' : 'No'}
                  </dd>
                </div>
                <div>
                  <dt className="text-blue-700">Created:</dt>
                  <dd className="text-blue-900">
                    {user?.created_at
                      ? new Date(user.created_at).toLocaleDateString()
                      : 'N/A'}
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
