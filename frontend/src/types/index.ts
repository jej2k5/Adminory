// User types
export interface User {
  id: string
  email: string
  name: string
  avatar_url?: string
  role: 'super_admin' | 'admin' | 'user'
  is_active: boolean
  email_verified_at?: string
  sso_provider?: string
  created_at: string
  updated_at: string
}

// Workspace types
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
}

export interface WorkspaceMember {
  id: string
  workspace_id: string
  user_id: string
  user: User
  role: 'owner' | 'admin' | 'member' | 'viewer'
  permissions: Record<string, any>
  created_at: string
}

// Auth types
export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  name: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  user: User
}

// SSO types
export interface SSOConfiguration {
  id: string
  workspace_id: string
  provider_type: 'saml' | 'oauth'
  enabled: boolean
  configuration: Record<string, any>
  metadata: Record<string, any>
  created_at: string
  updated_at: string
}

// Control Plane type
export type ControlPlane = 'internal' | 'external'

// API Key types
export interface ApiKey {
  id: string
  workspace_id: string
  name: string
  key_prefix: string
  scopes: string[]
  last_used_at?: string
  expires_at?: string
  created_at: string
}

// Audit Log types
export interface AuditLog {
  id: string
  workspace_id?: string
  user_id?: string
  user?: User
  action: string
  resource_type?: string
  resource_id?: string
  metadata: Record<string, any>
  ip_address?: string
  user_agent?: string
  created_at: string
}

// Feature Flag types
export interface FeatureFlag {
  id: string
  key: string
  name: string
  description?: string
  enabled: boolean
  rules: Record<string, any>
  created_at: string
  updated_at: string
}

// Plugin types
export interface Plugin {
  id: string
  name: string
  version: string
  description?: string
  manifest: Record<string, any>
  enabled: boolean
  installed_at: string
  updated_at: string
}

// Support Ticket types
export interface SupportTicket {
  id: string
  workspace_id: string
  user_id: string
  user?: User
  subject: string
  description: string
  status: 'open' | 'in_progress' | 'resolved' | 'closed'
  priority: 'low' | 'normal' | 'high' | 'urgent'
  assigned_to?: string
  created_at: string
  updated_at: string
}

// Analytics types
export interface UsageMetrics {
  active_users: number
  api_calls: number
  storage_used: number
  period: 'day' | 'week' | 'month'
}

export interface SystemMetrics {
  cpu_usage: number
  memory_usage: number
  database_connections: number
  api_latency: number
  timestamp: string
}
