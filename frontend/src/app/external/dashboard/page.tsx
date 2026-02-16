'use client'

import ProtectedRoute from '@/components/auth/ProtectedRoute'
import WorkspaceSelector from '@/components/workspace/WorkspaceSelector'
import { useAuth } from '@/hooks/useAuth'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import Link from 'next/link'
import { Settings, Users } from 'lucide-react'

export default function ExternalDashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  )
}

function DashboardContent() {
  const { user, logout } = useAuth()
  const { currentWorkspace } = useWorkspaceStore()

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-4">
              <h1 className="text-xl font-bold text-gray-900">
                Adminory
              </h1>
              <WorkspaceSelector />
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
          {currentWorkspace ? (
            <>
              <div className="bg-white rounded-lg shadow p-6 mb-6">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">
                      {currentWorkspace.name}
                    </h2>
                    <p className="text-gray-600">
                      {currentWorkspace.slug} • {currentWorkspace.plan} plan • {currentWorkspace.members?.length || 0} members
                    </p>
                  </div>
                  {(currentWorkspace.user_role === 'owner' || currentWorkspace.user_role === 'admin') && (
                    <Link
                      href={`/external/workspace/${currentWorkspace.id}`}
                      className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 flex items-center gap-2"
                    >
                      <Settings className="w-4 h-4" />
                      Manage Workspace
                    </Link>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Link
                  href={`/external/workspace/${currentWorkspace.id}?tab=general`}
                  className="bg-white border border-gray-200 rounded-lg p-6 hover:border-blue-500 hover:shadow-md transition-all"
                >
                  <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-4">
                    <Settings className="w-6 h-6 text-blue-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Workspace Settings
                  </h3>
                  <p className="text-sm text-gray-600">
                    Configure your workspace name, slug, and preferences
                  </p>
                </Link>

                <Link
                  href={`/external/workspace/${currentWorkspace.id}?tab=members`}
                  className="bg-white border border-gray-200 rounded-lg p-6 hover:border-blue-500 hover:shadow-md transition-all"
                >
                  <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mb-4">
                    <Users className="w-6 h-6 text-green-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Team Members
                  </h3>
                  <p className="text-sm text-gray-600">
                    Invite and manage team members ({currentWorkspace.members?.length || 0} members)
                  </p>
                </Link>

                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg mb-4">
                    <svg className="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Usage & Analytics
                  </h3>
                  <p className="text-sm text-gray-600">
                    View usage statistics and analytics (Coming soon)
                  </p>
                </div>
              </div>

              {!user?.email_verified_at && (
                <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <h3 className="font-semibold text-yellow-900 mb-2">
                    ⚠️ Email Verification Required
                  </h3>
                  <p className="text-sm text-yellow-700">
                    Please verify your email address to access all workspace features.
                  </p>
                </div>
              )}
            </>
          ) : (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Welcome to Adminory
              </h2>
              <p className="text-gray-600 mb-6">
                Get started by creating or selecting a workspace.
              </p>
              <Link
                href="/external/workspace/new"
                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700"
              >
                Create Your First Workspace
              </Link>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
