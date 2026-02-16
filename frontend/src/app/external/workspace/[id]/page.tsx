'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useWorkspaceStore, Workspace, WorkspaceMember } from '@/stores/workspaceStore'
import { ArrowLeft, Users, Settings, Trash2 } from 'lucide-react'
import Link from 'next/link'

export default function WorkspacePage() {
  const params = useParams()
  const router = useRouter()
  const workspaceId = params.id as string
  const { getWorkspace, getMembers, updateWorkspace, deleteWorkspace, isLoading } =
    useWorkspaceStore()

  const [workspace, setWorkspace] = useState<Workspace | null>(null)
  const [members, setMembers] = useState<WorkspaceMember[]>([])
  const [activeTab, setActiveTab] = useState<'general' | 'members' | 'danger'>('general')
  const [isEditing, setIsEditing] = useState(false)
  const [editForm, setEditForm] = useState({
    name: '',
    settings: {},
  })

  useEffect(() => {
    loadWorkspace()
    loadMembers()
  }, [workspaceId])

  const loadWorkspace = async () => {
    try {
      const data = await getWorkspace(workspaceId)
      setWorkspace(data)
      setEditForm({
        name: data.name,
        settings: data.settings || {},
      })
    } catch (error) {
      // Error handled by store
    }
  }

  const loadMembers = async () => {
    try {
      const data = await getMembers(workspaceId)
      setMembers(data)
    } catch (error) {
      // Error handled by store
    }
  }

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const updated = await updateWorkspace(workspaceId, {
        name: editForm.name,
        settings: editForm.settings,
      })
      setWorkspace(updated)
      setIsEditing(false)
    } catch (error) {
      // Error handled by store
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this workspace? This action cannot be undone.')) {
      return
    }

    try {
      await deleteWorkspace(workspaceId)
      router.push('/external/dashboard')
    } catch (error) {
      // Error handled by store
    }
  }

  const isOwner = workspace?.user_role === 'owner'
  const isAdmin = workspace?.user_role === 'admin' || isOwner

  if (!workspace) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading workspace...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <Link
            href="/external/dashboard"
            className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{workspace.name}</h1>
              <p className="text-gray-600 mt-1">
                {workspace.slug} • {workspace.plan} plan
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-3 py-1 text-sm font-medium text-blue-700 bg-blue-100 rounded-full capitalize">
                {workspace.user_role}
              </span>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('general')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'general'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <Settings className="w-4 h-4 inline mr-2" />
              General
            </button>
            <button
              onClick={() => setActiveTab('members')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'members'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <Users className="w-4 h-4 inline mr-2" />
              Members ({members.length})
            </button>
            {isOwner && (
              <button
                onClick={() => setActiveTab('danger')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'danger'
                    ? 'border-red-600 text-red-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                <Trash2 className="w-4 h-4 inline mr-2" />
                Danger Zone
              </button>
            )}
          </div>

          <div className="p-6">
            {activeTab === 'general' && (
              <div>
                {isEditing ? (
                  <form onSubmit={handleUpdate} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Workspace Name
                      </label>
                      <input
                        type="text"
                        value={editForm.name}
                        onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>
                    <div className="flex gap-4">
                      <button
                        type="submit"
                        disabled={isLoading}
                        className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50"
                      >
                        {isLoading ? 'Saving...' : 'Save Changes'}
                      </button>
                      <button
                        type="button"
                        onClick={() => setIsEditing(false)}
                        className="px-6 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                ) : (
                  <div>
                    <div className="space-y-4">
                      <div>
                        <div className="text-sm font-medium text-gray-700">Workspace Name</div>
                        <div className="mt-1 text-gray-900">{workspace.name}</div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-700">Workspace Slug</div>
                        <div className="mt-1 text-gray-900">{workspace.slug}</div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-700">Plan</div>
                        <div className="mt-1 text-gray-900 capitalize">{workspace.plan}</div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-700">SSO</div>
                        <div className="mt-1 text-gray-900">
                          {workspace.sso_enabled ? 'Enabled' : 'Disabled'}
                        </div>
                      </div>
                    </div>
                    {isAdmin && (
                      <button
                        onClick={() => setIsEditing(true)}
                        className="mt-6 px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700"
                      >
                        Edit Settings
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'members' && (
              <div>
                <div className="space-y-3">
                  {members.map((member) => (
                    <div
                      key={member.id}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                    >
                      <div>
                        <div className="font-medium text-gray-900">User {member.user_id.slice(0, 8)}...</div>
                        <div className="text-sm text-gray-500 capitalize">{member.role}</div>
                      </div>
                    </div>
                  ))}
                </div>
                {members.length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    No members found
                  </div>
                )}
              </div>
            )}

            {activeTab === 'danger' && isOwner && (
              <div>
                <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                  <h3 className="text-lg font-medium text-red-900 mb-2">
                    Delete Workspace
                  </h3>
                  <p className="text-sm text-red-700 mb-4">
                    Once you delete a workspace, there is no going back. All data associated with
                    this workspace will be permanently deleted.
                  </p>
                  <button
                    onClick={handleDelete}
                    disabled={isLoading}
                    className="px-6 py-2 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 disabled:opacity-50"
                  >
                    {isLoading ? 'Deleting...' : 'Delete Workspace'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
