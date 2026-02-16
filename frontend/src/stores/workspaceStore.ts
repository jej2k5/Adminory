import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { apiClient } from '@/lib/api'
import { toast } from '@/stores/toastStore'

export interface Workspace {
  id: string
  name: string
  slug: string
  owner_id: string
  plan: 'free' | 'pro' | 'enterprise'
  sso_enabled: boolean
  sso_enforced: boolean
  settings: Record<string, any>
  metadata: Record<string, any>
  created_at: string
  updated_at: string
  members: WorkspaceMember[]
  user_role?: 'owner' | 'admin' | 'member' | 'viewer'
}

export interface WorkspaceMember {
  id: string
  workspace_id: string
  user_id: string
  role: 'owner' | 'admin' | 'member' | 'viewer'
  permissions: Record<string, any>
  created_at: string
}

interface WorkspaceState {
  workspaces: Workspace[]
  currentWorkspace: Workspace | null
  isLoading: boolean
  error: string | null
}

interface WorkspaceActions {
  fetchWorkspaces: () => Promise<void>
  createWorkspace: (name: string, slug?: string) => Promise<Workspace>
  getWorkspace: (workspaceId: string) => Promise<Workspace>
  updateWorkspace: (workspaceId: string, data: Partial<Workspace>) => Promise<Workspace>
  deleteWorkspace: (workspaceId: string) => Promise<void>
  setCurrentWorkspace: (workspace: Workspace | null) => void
  addMember: (workspaceId: string, userId: string, role: string) => Promise<WorkspaceMember>
  removeMember: (workspaceId: string, memberId: string) => Promise<void>
  getMembers: (workspaceId: string) => Promise<WorkspaceMember[]>
  clearError: () => void
}

type WorkspaceStore = WorkspaceState & WorkspaceActions

export const useWorkspaceStore = create<WorkspaceStore>()(
  persist(
    (set, get) => ({
      // Initial state
      workspaces: [],
      currentWorkspace: null,
      isLoading: false,
      error: null,

      // Actions
      fetchWorkspaces: async () => {
        set({ isLoading: true, error: null })
        try {
          const response = await apiClient.get<Workspace[]>('/api/external/workspaces')
          set({ workspaces: response, isLoading: false })
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Failed to fetch workspaces'
          set({ error: errorMessage, isLoading: false })
          toast.error('Error', errorMessage)
          throw error
        }
      },

      createWorkspace: async (name: string, slug?: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await apiClient.post<Workspace>('/api/external/workspaces', {
            name,
            slug,
          })

          // Add to workspaces list
          set((state) => ({
            workspaces: [...state.workspaces, response],
            isLoading: false,
          }))

          toast.success('Workspace created', `Successfully created ${response.name}`)
          return response
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Failed to create workspace'
          set({ error: errorMessage, isLoading: false })
          toast.error('Error', errorMessage)
          throw error
        }
      },

      getWorkspace: async (workspaceId: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await apiClient.get<Workspace>(
            `/api/external/workspaces/${workspaceId}`
          )
          set({ isLoading: false })
          return response
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Failed to fetch workspace'
          set({ error: errorMessage, isLoading: false })
          toast.error('Error', errorMessage)
          throw error
        }
      },

      updateWorkspace: async (workspaceId: string, data: Partial<Workspace>) => {
        set({ isLoading: true, error: null })
        try {
          const response = await apiClient.patch<Workspace>(
            `/api/external/workspaces/${workspaceId}`,
            data
          )

          // Update in workspaces list
          set((state) => ({
            workspaces: state.workspaces.map((w) =>
              w.id === workspaceId ? response : w
            ),
            currentWorkspace:
              state.currentWorkspace?.id === workspaceId
                ? response
                : state.currentWorkspace,
            isLoading: false,
          }))

          toast.success('Workspace updated', 'Settings saved successfully')
          return response
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Failed to update workspace'
          set({ error: errorMessage, isLoading: false })
          toast.error('Error', errorMessage)
          throw error
        }
      },

      deleteWorkspace: async (workspaceId: string) => {
        set({ isLoading: true, error: null })
        try {
          await apiClient.delete(`/api/external/workspaces/${workspaceId}`)

          // Remove from workspaces list
          set((state) => ({
            workspaces: state.workspaces.filter((w) => w.id !== workspaceId),
            currentWorkspace:
              state.currentWorkspace?.id === workspaceId
                ? null
                : state.currentWorkspace,
            isLoading: false,
          }))

          toast.success('Workspace deleted', 'Workspace has been removed')
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Failed to delete workspace'
          set({ error: errorMessage, isLoading: false })
          toast.error('Error', errorMessage)
          throw error
        }
      },

      setCurrentWorkspace: (workspace: Workspace | null) => {
        set({ currentWorkspace: workspace })
      },

      addMember: async (workspaceId: string, userId: string, role: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await apiClient.post<WorkspaceMember>(
            `/api/external/workspaces/${workspaceId}/members`,
            { user_id: userId, role }
          )
          set({ isLoading: false })
          toast.success('Member added', 'User has been added to the workspace')
          return response
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Failed to add member'
          set({ error: errorMessage, isLoading: false })
          toast.error('Error', errorMessage)
          throw error
        }
      },

      removeMember: async (workspaceId: string, memberId: string) => {
        set({ isLoading: true, error: null })
        try {
          await apiClient.delete(
            `/api/external/workspaces/${workspaceId}/members/${memberId}`
          )
          set({ isLoading: false })
          toast.success('Member removed', 'User has been removed from the workspace')
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Failed to remove member'
          set({ error: errorMessage, isLoading: false })
          toast.error('Error', errorMessage)
          throw error
        }
      },

      getMembers: async (workspaceId: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await apiClient.get<WorkspaceMember[]>(
            `/api/external/workspaces/${workspaceId}/members`
          )
          set({ isLoading: false })
          return response
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Failed to fetch members'
          set({ error: errorMessage, isLoading: false })
          toast.error('Error', errorMessage)
          throw error
        }
      },

      clearError: () => {
        set({ error: null })
      },
    }),
    {
      name: 'workspace-storage',
      partialize: (state) => ({
        currentWorkspace: state.currentWorkspace,
        workspaces: state.workspaces,
      }),
    }
  )
)
