'use client'

import { useEffect, useState } from 'react'
import { useWorkspaceStore, Workspace } from '@/stores/workspaceStore'
import { ChevronDown, Plus, Check } from 'lucide-react'

export default function WorkspaceSelector() {
  const { workspaces, currentWorkspace, setCurrentWorkspace, fetchWorkspaces, isLoading } =
    useWorkspaceStore()
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    fetchWorkspaces()
  }, [])

  const handleSelectWorkspace = (workspace: Workspace) => {
    setCurrentWorkspace(workspace)
    setIsOpen(false)
  }

  const handleCreateWorkspace = () => {
    // Navigate to create workspace page
    window.location.href = '/external/workspace/new'
  }

  if (isLoading && workspaces.length === 0) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 text-sm text-gray-500">
        Loading workspaces...
      </div>
    )
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 min-w-[200px]"
      >
        <div className="flex-1 text-left truncate">
          {currentWorkspace ? (
            <div>
              <div className="font-medium truncate">{currentWorkspace.name}</div>
              <div className="text-xs text-gray-500 capitalize">{currentWorkspace.plan} Plan</div>
            </div>
          ) : (
            <span className="text-gray-500">Select workspace</span>
          )}
        </div>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown */}
          <div className="absolute left-0 z-20 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg min-w-[280px]">
            <div className="p-2 border-b border-gray-200">
              <div className="text-xs font-medium text-gray-500 uppercase px-2 py-1">
                Your Workspaces
              </div>
            </div>

            <div className="py-2 max-h-[300px] overflow-y-auto">
              {workspaces.length === 0 ? (
                <div className="px-4 py-6 text-sm text-center text-gray-500">
                  No workspaces found. Create one to get started.
                </div>
              ) : (
                workspaces.map((workspace) => (
                  <button
                    key={workspace.id}
                    onClick={() => handleSelectWorkspace(workspace)}
                    className="w-full px-3 py-2 text-left hover:bg-gray-50 flex items-center gap-3 group"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm text-gray-900 truncate">
                          {workspace.name}
                        </span>
                        {workspace.user_role === 'owner' && (
                          <span className="px-1.5 py-0.5 text-xs font-medium text-blue-700 bg-blue-100 rounded">
                            Owner
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-gray-500 capitalize mt-0.5">
                        {workspace.plan} • {workspace.members?.length || 0} members
                      </div>
                    </div>
                    {currentWorkspace?.id === workspace.id && (
                      <Check className="w-4 h-4 text-blue-600 flex-shrink-0" />
                    )}
                  </button>
                ))
              )}
            </div>

            <div className="p-2 border-t border-gray-200">
              <button
                onClick={handleCreateWorkspace}
                className="w-full px-3 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg flex items-center gap-2 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Create New Workspace
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
