'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'

export default function NewWorkspacePage() {
  const router = useRouter()
  const { createWorkspace, isLoading } = useWorkspaceStore()
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      await createWorkspace(formData.name, formData.slug || undefined)
      router.push('/external/dashboard')
    } catch (error) {
      // Error is already handled by the store
    }
  }

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name = e.target.value
    setFormData((prev) => ({
      ...prev,
      name,
      // Auto-generate slug from name if slug is empty
      slug: prev.slug === '' ? name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') : prev.slug,
    }))
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <Link
            href="/external/dashboard"
            className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Create a new workspace</h1>
          <p className="mt-2 text-gray-600">
            Workspaces help you organize your team and projects.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Workspace Name *
              </label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={handleNameChange}
                required
                placeholder="My Awesome Company"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="mt-1 text-sm text-gray-500">
                This is the display name for your workspace.
              </p>
            </div>

            <div>
              <label htmlFor="slug" className="block text-sm font-medium text-gray-700 mb-2">
                Workspace Slug
              </label>
              <div className="flex items-center gap-2">
                <span className="text-gray-500 text-sm">adminory.com/</span>
                <input
                  type="text"
                  id="slug"
                  value={formData.slug}
                  onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
                  placeholder="my-company"
                  pattern="[a-z0-9-]+"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <p className="mt-1 text-sm text-gray-500">
                URL-friendly identifier (lowercase letters, numbers, and hyphens only). Leave empty to auto-generate.
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="text-sm font-medium text-blue-900 mb-2">Free Plan Features</h3>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• Up to 5 team members</li>
                <li>• Basic role-based access control</li>
                <li>• Standard support</li>
              </ul>
              <p className="text-xs text-blue-600 mt-3">
                You can upgrade to Pro or Enterprise plans anytime from workspace settings.
              </p>
            </div>

            <div className="flex gap-4">
              <button
                type="submit"
                disabled={isLoading || !formData.name}
                className="flex-1 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Creating...' : 'Create Workspace'}
              </button>
              <Link
                href="/external/dashboard"
                className="px-6 py-3 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
              >
                Cancel
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
