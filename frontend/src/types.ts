export type ApiOutput<T> = {
  status_code?: number
  message?: string
  data?: T
}

export type Organization = {
  id: string
  name: string
}

export type UserSession = {
  id: string
  email: string
  organization_id: string
  role: string
}

export type LoginData = {
  access_token: string
  refresh_token: string
  user: UserSession
}

export type User = {
  id: string
  email: string
  organization_id: string
  role: string
  is_active: boolean
}

export type Task = {
  id: string
  organization_id: string
  title: string
  description: string
  priority: string
  status: string
  assignee_id: string | null
  due_date: string | null
  created_at: string
  updated_at: string
  assigned_to: User | null
}

export type TaskPagination = {
  page: number
  limit: number
  total_count: number
  total_pages: number
}

export type TaskListResponse = {
  tasks: Task[]
  pagination: TaskPagination
}

