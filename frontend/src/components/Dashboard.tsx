import { useEffect, useState } from "react"
import type { ReactNode } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { API_BASE_URL, getErrorMessage, authenticatedFetch } from "../lib/api"
import type { UserSession, User, Task, TaskListResponse } from "../types"
import { 
  Users, 
  Briefcase, 
  CheckSquare, 
  Calendar, 
  User as UserIcon, 
  Loader2, 
  AlertTriangle,
  Eye,
  EyeOff,
  PlusCircle,
  X,
  Pencil
} from "lucide-react"

interface DashboardProps {
  user: UserSession
  onLogout: () => void
}

export function Dashboard({ user, onLogout }: DashboardProps) {
  const roleName = user.role.toUpperCase()
  const isAdmin = roleName === "ADMIN"
  const isManager = roleName === "MANAGER"
  const isMember = roleName === "MEMBER"
  const canCreateTask = isAdmin || isManager

  // Live real-time states
  const [users, setUsers] = useState<User[]>([])
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [showTaskList, setShowTaskList] = useState(false)

  // Create Task form/modal states
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [isSubmittingTask, setIsSubmittingTask] = useState(false)
  const [taskFormError, setTaskFormError] = useState("")
  const [taskTitle, setTaskTitle] = useState("")
  const [taskDescription, setTaskDescription] = useState("")
  const [taskPriority, setTaskPriority] = useState("MEDIUM")
  const [taskAssigneeId, setTaskAssigneeId] = useState("")
  const [taskDueDate, setTaskDueDate] = useState("")

  // Edit Task form/modal states
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [isUpdatingTask, setIsUpdatingTask] = useState(false)
  const [editFormError, setEditFormError] = useState("")
  const [editTitle, setEditTitle] = useState("")
  const [editDescription, setEditDescription] = useState("")
  const [editPriority, setEditPriority] = useState("MEDIUM")
  const [editAssigneeId, setEditAssigneeId] = useState("")
  const [editDueDate, setEditDueDate] = useState("")
  const [editStatus, setEditStatus] = useState("TODO")

  // Enforce future due date constraint (tomorrow or later)
  const tomorrowStr = new Date(Date.now() + 86400000).toISOString().split("T")[0]

  async function fetchDashboardData() {
    setIsLoading(true)
    setError("")

    try {
      // 1. Fetch users only for Admin and Manager roles
      let fetchedUsers: User[] = []
      if (isAdmin || isManager) {
        const usersResponse = await authenticatedFetch(`${API_BASE_URL}/api/user/list`, {}, onLogout)
        const usersPayload = await usersResponse.json()

        if (!usersResponse.ok) {
          throw new Error(getErrorMessage(usersPayload, "Failed to retrieve organization users."))
        }
        fetchedUsers = (usersPayload.data ?? []) as User[]
      }

      // 2. Fetch tasks for all roles
      const tasksResponse = await authenticatedFetch(`${API_BASE_URL}/api/task/list?limit=100`, {}, onLogout)
      const tasksPayload = await tasksResponse.json()

      if (!tasksResponse.ok) {
        throw new Error(getErrorMessage(tasksPayload, "Failed to retrieve tasks."))
      }

      const taskListData = (tasksPayload.data ?? { tasks: [] }) as TaskListResponse
      
      setUsers(fetchedUsers)
      setTasks(taskListData.tasks ?? [])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load dashboard metrics.")
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    void fetchDashboardData()
  }, [isAdmin, isManager])

  // Handles task creation submission
  const handleCreateTaskSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setTaskFormError("")

    if (!taskTitle.trim()) {
      setTaskFormError("Task title is required.")
      return
    }

    setIsSubmittingTask(true)

    try {
      const response = await authenticatedFetch(`${API_BASE_URL}/api/task`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: taskTitle.trim(),
          description: taskDescription.trim() || null,
          priority: taskPriority,
          assignee_id: taskAssigneeId || null,
          due_date: taskDueDate ? new Date(taskDueDate).toISOString() : null,
        }),
      }, onLogout)

      const payload = await response.json()

      if (!response.ok) {
        throw new Error(getErrorMessage(payload, "Failed to create task."))
      }

      // Reset form on success
      setTaskTitle("")
      setTaskDescription("")
      setTaskPriority("MEDIUM")
      setTaskAssigneeId("")
      setTaskDueDate("")
      setIsCreateModalOpen(false)
      
      // Auto-open backlog and reload data
      setShowTaskList(true)
      void fetchDashboardData()
    } catch (err) {
      setTaskFormError(err instanceof Error ? err.message : "Unable to submit task creation request.")
    } finally {
      setIsSubmittingTask(false)
    }
  }

  // Trigger editing a task
  const handleStartEdit = (task: Task) => {
    setEditingTask(task)
    setEditTitle(task.title)
    setEditDescription(task.description || "")
    setEditPriority(task.priority)
    setEditAssigneeId(task.assignee_id || "")
    setEditDueDate(task.due_date ? task.due_date.split("T")[0] : "")
    setEditStatus(task.status)
    setEditFormError("")
  }

  // Handles task editing submission
  const handleEditTaskSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setEditFormError("")

    if (!editingTask) return

    if (!editTitle.trim()) {
      setEditFormError("Task title is required.")
      return
    }

    setIsUpdatingTask(true)

    try {
      const response = await authenticatedFetch(`${API_BASE_URL}/api/task/${editingTask.id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: editTitle.trim(),
          description: editDescription.trim() || null,
          priority: editPriority,
          assignee_id: editAssigneeId || null,
          due_date: editDueDate ? new Date(editDueDate).toISOString() : null,
          status: editStatus,
        }),
      }, onLogout)

      const payload = await response.json()

      if (!response.ok) {
        throw new Error(getErrorMessage(payload, "Failed to update task."))
      }

      setEditingTask(null)
      void fetchDashboardData()
    } catch (err) {
      setEditFormError(err instanceof Error ? err.message : "Unable to submit task updates.")
    } finally {
      setIsUpdatingTask(false)
    }
  }

  // Fast inline status changes for all roles
  const handleStatusChange = async (taskId: string, newStatus: string) => {
    try {
      const response = await authenticatedFetch(`${API_BASE_URL}/api/task/${taskId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          status: newStatus,
        }),
      }, onLogout)

      const payload = await response.json()

      if (!response.ok) {
        throw new Error(getErrorMessage(payload, "Failed to update task status."))
      }

      void fetchDashboardData()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to change task status.")
    }
  }

  // Real data calculations
  const membersCount = users.filter((u) => u.role.toUpperCase() === "MEMBER").length
  const managersCount = users.filter((u) => u.role.toUpperCase() === "MANAGER").length
  const tasksCount = tasks.length

  // Custom dashboard branding and dynamic stats based on role
  const config = {
    ADMIN: {
      gradient: "from-indigo-600 to-violet-600 dark:from-indigo-950 dark:to-violet-950",
      accent: "text-violet-600 bg-violet-100 dark:bg-violet-950 dark:text-violet-400 border-violet-200 dark:border-violet-800",
      title: "ADMIN Dashboard",
      subtitle: "System Administration & Orchestration",
      description: "Manage global settings, database syncs, organization configurations, and user policies.",
      stats: [
        { 
          label: "Organization Members", 
          value: isLoading ? "..." : `${membersCount} Members`, 
          icon: <Users className="h-5 w-5 text-indigo-500" />,
          clickable: false 
        },
        { 
          label: "Organization Managers", 
          value: isLoading ? "..." : `${managersCount} Managers`, 
          icon: <Briefcase className="h-5 w-5 text-violet-500" />,
          clickable: false 
        },
        { 
          label: "Organization Tasks", 
          value: isLoading ? "..." : `${tasksCount} Tasks`, 
          icon: <CheckSquare className="h-5 w-5 text-purple-500" />,
          clickable: true,
          action: () => setShowTaskList((prev) => !prev),
          active: showTaskList,
          helperText: showTaskList ? "Click to hide backlog" : "Click to view backlog"
        }
      ]
    },
    MANAGER: {
      gradient: "from-teal-600 to-emerald-600 dark:from-teal-950 dark:to-emerald-950",
      accent: "text-emerald-600 bg-emerald-100 dark:bg-emerald-950 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800",
      title: "Manager Dashboard",
      subtitle: "Operations & Workspaces Manager",
      description: "Coordinate team assignments, monitor backlog progression, and approve system changes.",
      stats: [
        { 
          label: "Organization Members", 
          value: isLoading ? "..." : `${membersCount} Members`, 
          icon: <Users className="h-5 w-5 text-teal-500" />,
          clickable: false 
        },
        { 
          label: "Organization Managers", 
          value: isLoading ? "..." : `${managersCount} Managers`, 
          icon: <Briefcase className="h-5 w-5 text-emerald-500" />,
          clickable: false 
        },
        { 
          label: "Organization Tasks", 
          value: isLoading ? "..." : `${tasksCount} Tasks`, 
          icon: <CheckSquare className="h-5 w-5 text-cyan-500" />,
          clickable: true,
          action: () => setShowTaskList((prev) => !prev),
          active: showTaskList,
          helperText: showTaskList ? "Click to hide backlog" : "Click to view backlog"
        }
      ]
    },
    MEMBER: {
      gradient: "from-amber-500 to-orange-600 dark:from-amber-950 dark:to-orange-950",
      accent: "text-amber-600 bg-amber-100 dark:bg-amber-955 dark:text-amber-400 border-amber-200 dark:border-amber-800",
      title: "Member Dashboard",
      subtitle: "Personal Collaboration Space",
      description: "Access shared workspaces, edit profile cards, upload project media, and coordinate with managers.",
      stats: [
        { 
          label: "My Assigned Tasks", 
          value: isLoading ? "..." : `${tasksCount} Tasks`, 
          icon: <CheckSquare className="h-5 w-5 text-amber-500" />,
          clickable: true,
          action: () => setShowTaskList((prev) => !prev),
          active: showTaskList,
          helperText: showTaskList ? "Click to hide my tasks" : "Click to view my tasks"
        }
      ]
    }
  }[roleName as "ADMIN" | "MANAGER" | "MEMBER"] || {
    gradient: "from-slate-600 to-slate-800 dark:from-slate-900 dark:to-slate-950",
    accent: "text-slate-600 bg-slate-100 dark:bg-slate-950 dark:text-slate-400 border-slate-200 dark:border-slate-800",
    title: `${roleName} Dashboard`,
    subtitle: "Standard Workspace Dashboard",
    description: "Welcome to your organization's workspace platform dashboard.",
    stats: []
  }

  // Priority Badge colors
  const getPriorityBadge = (priority: string) => {
    switch (priority.toUpperCase()) {
      case "HIGH":
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 dark:bg-rose-950/50 dark:text-rose-400 border border-rose-200 dark:border-rose-900/50">
            <span className="h-1.5 w-1.5 rounded-full bg-rose-500 mr-1.5 animate-pulse"></span>
            High
          </span>
        )
      case "MEDIUM":
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-400 border border-amber-200 dark:border-amber-900/50">
            <span className="h-1.5 w-1.5 rounded-full bg-amber-500 mr-1.5"></span>
            Medium
          </span>
        )
      case "LOW":
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-900/50">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 mr-1.5"></span>
            Low
          </span>
        )
    }
  }

  // Status Badge colors
  const getStatusBadge = (status: string) => {
    const defaultClasses = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border"
    switch (status.toUpperCase()) {
      case "DONE":
        return (
          <span className={`${defaultClasses} bg-green-100 text-green-800 dark:bg-green-950/50 dark:text-green-400 border-green-200 dark:border-green-900/50`}>
            Done
          </span>
        )
      case "IN_PROGRESS":
        return (
          <span className={`${defaultClasses} bg-blue-100 text-blue-800 dark:bg-blue-950/50 dark:text-blue-400 border-blue-200 dark:border-blue-900/50`}>
            In Progress
          </span>
        )
      case "IN_REVIEW":
        return (
          <span className={`${defaultClasses} bg-indigo-100 text-indigo-800 dark:bg-indigo-950/50 dark:text-indigo-400 border-indigo-200 dark:border-indigo-900/50`}>
            In Review
          </span>
        )
      case "BLOCKED":
        return (
          <span className={`${defaultClasses} bg-red-100 text-red-800 dark:bg-red-950/50 dark:text-red-400 border-red-200 dark:border-red-900/50`}>
            Blocked
          </span>
        )
      case "TODO":
      default:
        return (
          <span className={`${defaultClasses} bg-slate-100 text-slate-800 dark:bg-slate-900/50 dark:text-slate-400 border-slate-200 dark:border-slate-800`}>
            Todo
          </span>
        )
    }
  }

  // Get dynamic styles for interactive status dropdown
  const getStatusSelectClasses = (status: string) => {
    const base = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border cursor-pointer transition-colors focus:outline-hidden focus:ring-1 focus:ring-primary/30"
    switch (status.toUpperCase()) {
      case "DONE":
        return `${base} bg-green-100 text-green-800 dark:bg-green-950/50 dark:text-green-400 border-green-200 dark:border-green-900/50 hover:bg-green-250`
      case "IN_PROGRESS":
        return `${base} bg-blue-100 text-blue-800 dark:bg-blue-950/50 dark:text-blue-400 border-blue-200 dark:border-blue-900/50 hover:bg-blue-200`
      case "IN_REVIEW":
        return `${base} bg-indigo-100 text-indigo-800 dark:bg-indigo-950/50 dark:text-indigo-400 border-indigo-200 dark:border-indigo-900/50 hover:bg-indigo-200`
      case "BLOCKED":
        return `${base} bg-red-100 text-red-800 dark:bg-red-950/50 dark:text-red-400 border-red-200 dark:border-red-900/50 hover:bg-red-200`
      case "TODO":
      default:
        return `${base} bg-slate-100 text-slate-800 dark:bg-slate-900/50 dark:text-slate-400 border-slate-200 dark:border-slate-800 hover:bg-slate-250`
    }
  }

  return (
    <div className="w-full max-w-4xl animate-in fade-in zoom-in-95 duration-500 relative">
      <Card className="border-border/70 shadow-2xl overflow-hidden backdrop-blur-sm bg-card/90">
        {/* Header with vibrant gradient banner */}
        <div className={`h-32 bg-gradient-to-r ${config.gradient} p-6 flex flex-col justify-end text-white relative`}>
          <div className="absolute top-4 right-4 bg-white/10 backdrop-blur-md px-3 py-1 rounded-full text-xs font-medium border border-white/20 tracking-wider">
            {roleName} CONSOLE
          </div>
          <h1 className="text-3xl font-bold tracking-tight">{config.title}</h1>
          <p className="text-white/80 text-sm font-medium mt-1">{config.subtitle}</p>
        </div>

        <CardContent className="p-6 md:p-8 space-y-8">
          {/* Welcome Message */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-border/50">
            <div className="space-y-1">
              <h2 className="text-xl font-semibold tracking-tight text-foreground">Welcome back, {user.email}</h2>
              <p className="text-muted-foreground text-sm max-w-xl">
                {config.description}
              </p>
            </div>
            <div className="flex flex-col sm:flex-row items-center gap-3 w-full md:w-auto self-start">
              {canCreateTask && (
                <Button 
                  onClick={() => setIsCreateModalOpen(true)}
                  className="w-full sm:w-auto inline-flex items-center gap-2 cursor-pointer transition-all duration-200 shadow-sm"
                >
                  <PlusCircle className="h-4.5 w-4.5" />
                  Create Task
                </Button>
              )}
              <Button 
                variant="destructive" 
                onClick={onLogout} 
                className="w-full sm:w-auto border-destructive/20 text-destructive hover:bg-destructive/10 cursor-pointer transition-all"
              >
                Sign out
              </Button>
            </div>
          </div>

          {/* Error banners */}
          {error ? (
            <div className="p-4 rounded-xl border border-destructive/30 bg-destructive/10 text-sm text-destructive flex items-start gap-2.5 animate-in fade-in duration-200">
              <AlertTriangle className="h-5 w-5 shrink-0 text-destructive" />
              <span>{error}</span>
            </div>
          ) : null}

          {/* Dynamic stats section */}
          {config.stats.length > 0 ? (
            <div className={`grid grid-cols-1 ${config.stats.length > 1 ? "md:grid-cols-3" : "md:grid-cols-1"} gap-4`}>
              {config.stats.map((stat, i) => {
                if (stat.clickable) {
                  const clickStat = stat as { 
                    label: string
                    value: string
                    icon?: ReactNode
                    clickable: true
                    action: () => void
                    active: boolean
                    helperText: string
                  }
                  return (
                    <button
                      key={i}
                      onClick={clickStat.action}
                      type="button"
                      className={`p-4 text-left rounded-xl border transition-all duration-300 cursor-pointer hover:-translate-y-0.5 hover:shadow-md space-y-2 relative overflow-hidden flex flex-col justify-between ${
                        clickStat.active 
                          ? "border-purple-500 bg-purple-50/40 dark:bg-purple-950/20" 
                          : "border-border/60 bg-muted/30 hover:bg-muted/50"
                      }`}
                    >
                      <div className="flex items-center justify-between w-full">
                        <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">
                          {clickStat.label}
                        </span>
                        {clickStat.icon}
                      </div>
                      <div>
                        <p className="text-2xl font-bold tracking-tight text-foreground">{clickStat.value}</p>
                        <span className="text-xs text-purple-600 dark:text-purple-400 font-medium inline-flex items-center gap-1.5 mt-1">
                          {clickStat.active ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
                          {clickStat.helperText}
                        </span>
                      </div>
                    </button>
                  )
                }

                const staticStat = stat as {
                  label: string
                  value: string
                  icon?: ReactNode
                  clickable: false
                }
                return (
                  <div 
                    key={i} 
                    className="p-4 rounded-xl border border-border/60 bg-muted/30 hover:bg-muted/50 transition-colors flex flex-col justify-between space-y-2"
                  >
                    <div className="flex items-center justify-between w-full">
                      <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">{staticStat.label}</span>
                      {staticStat.icon}
                    </div>
                    <p className="text-2xl font-bold tracking-tight text-foreground">{staticStat.value}</p>
                  </div>
                )
              })}
            </div>
          ) : null}

          {/* Interactive Tasks Panel */}
          {showTaskList ? (
            <div className="space-y-4 animate-in fade-in slide-in-from-top-3 duration-300">
              <div className="flex items-center justify-between pb-2 border-b border-border/50">
                <div className="space-y-1">
                  <h3 className="text-lg font-semibold tracking-tight text-foreground">
                    {isMember ? "My Assigned Tasks" : "Organization Task Backlog"}
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    {isMember 
                      ? "A list of tasks specifically assigned to your account."
                      : `Real-time list of all tasks assigned or unassigned across ${user.email.split("@")[1] || "your organization"}.`
                    }
                  </p>
                </div>
                {isLoading ? (
                  <span className="inline-flex items-center text-xs text-muted-foreground gap-1.5">
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    Refreshing...
                  </span>
                ) : null}
              </div>

              {isLoading && tasks.length === 0 ? (
                <div className="py-12 flex flex-col items-center justify-center space-y-2 border border-dashed border-border rounded-xl">
                  <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
                  <span className="text-sm text-muted-foreground font-medium">Fetching tasks...</span>
                </div>
              ) : tasks.length === 0 ? (
                <div className="py-12 text-center border border-dashed border-border rounded-xl space-y-1">
                  <p className="text-sm font-semibold text-foreground">No tasks registered</p>
                  <p className="text-xs text-muted-foreground">
                    {isMember ? "You do not have any tasks assigned to you." : "Create your first task using the action bar above."}
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-3.5 max-h-[420px] overflow-y-auto pr-1">
                  {tasks.map((task) => (
                    <div 
                      key={task.id} 
                      className="p-4 rounded-xl border border-border bg-card/65 hover:bg-card hover:shadow-sm transition-all space-y-3"
                    >
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div className="space-y-1">
                          <h4 className="font-semibold text-base text-foreground tracking-tight">
                            {task.title}
                          </h4>
                          <p className="text-xs text-muted-foreground line-clamp-2 max-w-2xl">
                            {task.description || "No description provided."}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          {getPriorityBadge(task.priority)}
                          {canCreateTask || (isMember && task.assignee_id === user.id) ? (
                            <select
                              value={task.status}
                              onChange={(e) => handleStatusChange(task.id, e.target.value)}
                              className={getStatusSelectClasses(task.status)}
                            >
                              <option value="TODO">Todo</option>
                              <option value="IN_PROGRESS">In Progress</option>
                              <option value="IN_REVIEW">In Review</option>
                              <option value="DONE">Done</option>
                              <option value="BLOCKED">Blocked</option>
                            </select>
                          ) : (
                            getStatusBadge(task.status)
                          )}
                        </div>
                      </div>

                      <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-border/40 text-xs text-muted-foreground">
                        <div className="flex items-center gap-1.5">
                          <UserIcon className="h-3.5 w-3.5 text-muted-foreground/75" />
                          <span>
                            Assignee:{" "}
                            <span className="font-medium text-foreground">
                              {task.assigned_to?.email ?? "Unassigned"}
                            </span>
                          </span>
                        </div>

                        {task.due_date ? (
                          <div className="flex items-center gap-1.5">
                            <Calendar className="h-3.5 w-3.5 text-muted-foreground/75" />
                            <span>
                              Due:{" "}
                              <span className="font-medium text-foreground">
                                {new Date(task.due_date).toLocaleDateString(undefined, {
                                  month: "short",
                                  day: "numeric",
                                  year: "numeric",
                                })}
                              </span>
                            </span>
                          </div>
                        ) : null}
                      </div>

                      {canCreateTask && (
                        <div className="flex justify-end pt-2.5 border-t border-border/40">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleStartEdit(task)}
                            className="h-8 px-3 text-xs font-semibold inline-flex items-center gap-1.5 cursor-pointer hover:bg-muted"
                          >
                            <Pencil className="h-3.5 w-3.5" />
                            Edit Task
                          </Button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : null}

          {/* Account Profile Card */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold tracking-wider text-muted-foreground uppercase">
              Profile Details
            </h3>
            <div className="p-5 rounded-2xl border border-border bg-muted/10">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 text-sm">
                <div className="space-y-1">
                  <span className="text-muted-foreground text-xs font-medium block">EMAIL ADDRESS</span>
                  <span className="font-semibold text-foreground">{user.email}</span>
                </div>
                <div className="space-y-1">
                  <span className="text-muted-foreground text-xs font-medium block">ROLE PERMISSION</span>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${config.accent}`}>
                    {roleName}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Task Creation Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in duration-200">
          <div className="w-full max-w-md bg-card border border-border rounded-2xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
            {/* Modal Header */}
            <div className={`p-5 text-white flex items-center justify-between bg-gradient-to-r ${config.gradient}`}>
              <div>
                <h3 className="text-lg font-bold">Create New Task</h3>
                <p className="text-white/80 text-xs mt-0.5">Define backlog parameters</p>
              </div>
              <button 
                onClick={() => {
                  setIsCreateModalOpen(false)
                  setTaskFormError("")
                }}
                className="text-white/80 hover:text-white hover:bg-white/10 p-1.5 rounded-full transition-all cursor-pointer"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Modal Form */}
            <form onSubmit={handleCreateTaskSubmit} className="p-6 space-y-4">
              {taskFormError && (
                <div className="p-3.5 rounded-xl border border-rose-500/30 bg-rose-500/10 text-xs text-rose-600 dark:text-rose-400 flex items-start gap-2 animate-in fade-in">
                  <AlertTriangle className="h-4.5 w-4.5 shrink-0 text-rose-500" />
                  <span>{taskFormError}</span>
                </div>
              )}

              {/* Task Title */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold tracking-wide text-foreground uppercase">
                  Task Title <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="Review code architecture..."
                  value={taskTitle}
                  onChange={(e) => setTaskTitle(e.target.value)}
                  className="w-full px-3.5 py-2.5 text-sm bg-muted/40 border border-border rounded-xl focus:outline-hidden focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-foreground placeholder-muted-foreground"
                />
              </div>

              {/* Task Description */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold tracking-wide text-foreground uppercase">
                  Description
                </label>
                <textarea
                  placeholder="Elaborate on objectives, standards, or key results..."
                  value={taskDescription}
                  onChange={(e) => setTaskDescription(e.target.value)}
                  rows={3}
                  className="w-full px-3.5 py-2.5 text-sm bg-muted/40 border border-border rounded-xl focus:outline-hidden focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-foreground placeholder-muted-foreground resize-none"
                />
              </div>

              {/* Grid: Priority & Assignee */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold tracking-wide text-foreground uppercase">
                    Priority
                  </label>
                  <select
                    value={taskPriority}
                    onChange={(e) => setTaskPriority(e.target.value)}
                    className="w-full px-3.5 py-2.5 text-sm bg-muted/40 border border-border rounded-xl focus:outline-hidden focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-foreground cursor-pointer"
                  >
                    <option value="LOW" className="bg-card text-foreground">Low</option>
                    <option value="MEDIUM" className="bg-card text-foreground">Medium</option>
                    <option value="HIGH" className="bg-card text-foreground">High</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold tracking-wide text-foreground uppercase">
                    Assignee
                  </label>
                  <select
                    value={taskAssigneeId}
                    onChange={(e) => setTaskAssigneeId(e.target.value)}
                    className="w-full px-3.5 py-2.5 text-sm bg-muted/40 border border-border rounded-xl focus:outline-hidden focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-foreground cursor-pointer"
                  >
                    <option value="" className="bg-card text-foreground">Unassigned</option>
                    {users
                      .filter((u) => u.role.toUpperCase() === "MEMBER")
                      .map((u) => (
                        <option key={u.id} value={u.id} className="bg-card text-foreground">
                          {u.email}
                        </option>
                      ))}
                  </select>
                </div>
              </div>

              {/* Due Date */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold tracking-wide text-foreground uppercase">
                  Due Date <span className="text-muted-foreground text-[10px] font-normal">(must be in future)</span>
                </label>
                <input
                  type="date"
                  min={tomorrowStr}
                  value={taskDueDate}
                  onChange={(e) => setTaskDueDate(e.target.value)}
                  className="w-full px-3.5 py-2.5 text-sm bg-muted/40 border border-border rounded-xl focus:outline-hidden focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-foreground cursor-pointer"
                />
              </div>

              {/* Form Buttons */}
              <div className="flex items-center justify-end gap-3 pt-3 border-t border-border/50">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setIsCreateModalOpen(false)
                    setTaskFormError("")
                  }}
                  disabled={isSubmittingTask}
                  className="px-5 cursor-pointer"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isSubmittingTask}
                  className="px-5 cursor-pointer inline-flex items-center gap-1.5"
                >
                  {isSubmittingTask ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    "Create Task"
                  )}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Task Edit Modal */}
      {editingTask && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in duration-200">
          <div className="w-full max-w-md bg-card border border-border rounded-2xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
            {/* Modal Header */}
            <div className={`p-5 text-white flex items-center justify-between bg-gradient-to-r ${config.gradient}`}>
              <div>
                <h3 className="text-lg font-bold">Edit Task</h3>
                <p className="text-white/80 text-xs mt-0.5">Modify task parameters</p>
              </div>
              <button 
                onClick={() => {
                  setEditingTask(null)
                  setEditFormError("")
                }}
                className="text-white/80 hover:text-white hover:bg-white/10 p-1.5 rounded-full transition-all cursor-pointer"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Modal Form */}
            <form onSubmit={handleEditTaskSubmit} className="p-6 space-y-4">
              {editFormError && (
                <div className="p-3.5 rounded-xl border border-rose-500/30 bg-rose-500/10 text-xs text-rose-600 dark:text-rose-400 flex items-start gap-2 animate-in fade-in">
                  <AlertTriangle className="h-4.5 w-4.5 shrink-0 text-rose-500" />
                  <span>{editFormError}</span>
                </div>
              )}

              {/* Task Title */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold tracking-wide text-foreground uppercase">
                  Task Title <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="Review code architecture..."
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="w-full px-3.5 py-2.5 text-sm bg-muted/40 border border-border rounded-xl focus:outline-hidden focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-foreground placeholder-muted-foreground"
                />
              </div>

              {/* Task Description */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold tracking-wide text-foreground uppercase">
                  Description
                </label>
                <textarea
                  placeholder="Elaborate on objectives, standards, or key results..."
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  rows={3}
                  className="w-full px-3.5 py-2.5 text-sm bg-muted/40 border border-border rounded-xl focus:outline-hidden focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-foreground placeholder-muted-foreground resize-none"
                />
              </div>

              {/* Grid: Priority & Assignee */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold tracking-wide text-foreground uppercase">
                    Priority
                  </label>
                  <select
                    value={editPriority}
                    onChange={(e) => setEditPriority(e.target.value)}
                    className="w-full px-3.5 py-2.5 text-sm bg-muted/40 border border-border rounded-xl focus:outline-hidden focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-foreground cursor-pointer"
                  >
                    <option value="LOW" className="bg-card text-foreground">Low</option>
                    <option value="MEDIUM" className="bg-card text-foreground">Medium</option>
                    <option value="HIGH" className="bg-card text-foreground">High</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold tracking-wide text-foreground uppercase">
                    Assignee
                  </label>
                  <select
                    value={editAssigneeId}
                    onChange={(e) => setEditAssigneeId(e.target.value)}
                    className="w-full px-3.5 py-2.5 text-sm bg-muted/40 border border-border rounded-xl focus:outline-hidden focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-foreground cursor-pointer"
                  >
                    <option value="" className="bg-card text-foreground">Unassigned</option>
                    {users
                      .filter((u) => u.role.toUpperCase() === "MEMBER")
                      .map((u) => (
                        <option key={u.id} value={u.id} className="bg-card text-foreground">
                          {u.email}
                        </option>
                      ))}
                  </select>
                </div>
              </div>

              {/* Grid: Status & Due Date */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold tracking-wide text-foreground uppercase">
                    Status
                  </label>
                  <select
                    value={editStatus}
                    onChange={(e) => setEditStatus(e.target.value)}
                    className="w-full px-3.5 py-2.5 text-sm bg-muted/40 border border-border rounded-xl focus:outline-hidden focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-foreground cursor-pointer"
                  >
                    <option value="TODO" className="bg-card text-foreground">Todo</option>
                    <option value="IN_PROGRESS" className="bg-card text-foreground">In Progress</option>
                    <option value="IN_REVIEW" className="bg-card text-foreground">In Review</option>
                    <option value="DONE" className="bg-card text-foreground">Done</option>
                    <option value="BLOCKED" className="bg-card text-foreground">Blocked</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold tracking-wide text-foreground uppercase">
                    Due Date <span className="text-muted-foreground text-[10px] font-normal">(must be in future)</span>
                  </label>
                  <input
                    type="date"
                    min={tomorrowStr}
                    value={editDueDate}
                    onChange={(e) => setEditDueDate(e.target.value)}
                    className="w-full px-3.5 py-2.5 text-sm bg-muted/40 border border-border rounded-xl focus:outline-hidden focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-foreground cursor-pointer"
                  />
                </div>
              </div>

              {/* Form Buttons */}
              <div className="flex items-center justify-end gap-3 pt-3 border-t border-border/50">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setEditingTask(null)
                    setEditFormError("")
                  }}
                  disabled={isUpdatingTask}
                  className="px-5 cursor-pointer"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isUpdatingTask}
                  className="px-5 cursor-pointer inline-flex items-center gap-1.5"
                >
                  {isUpdatingTask ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    "Save Changes"
                  )}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
