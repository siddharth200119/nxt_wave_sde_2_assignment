import { useEffect, useState } from "react"

import { AuthCard } from "@/components/AuthCard"
import { Dashboard } from "@/components/Dashboard"
import {
  API_BASE_URL,
  getErrorMessage,
  normalizeOrganizations,
} from "@/lib/api"
import type { ApiOutput, LoginData, Organization, UserSession } from "./types"

function App() {
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [organizationId, setOrganizationId] = useState("")
  const [isLoadingOrganizations, setIsLoadingOrganizations] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState("")
  const [successMessage, setSuccessMessage] = useState("")

  const [currentUser, setCurrentUser] = useState<UserSession | null>(() => {
    const savedUser = localStorage.getItem("user")
    const token = localStorage.getItem("access_token")
    if (savedUser && token) {
      try {
        return JSON.parse(savedUser) as UserSession
      } catch {
        return null
      }
    }
    return null
  })

  useEffect(() => {
    let isMounted = true

    async function loadOrganizations() {
      setIsLoadingOrganizations(true)
      setError("")

      try {
        const response = await fetch(`${API_BASE_URL}/api/organization/list`)
        const payload = (await response.json()) as ApiOutput<Organization[]> | Organization[]

        if (!response.ok) {
          throw new Error(
            getErrorMessage(payload, "Unable to load organizations.")
          )
        }

        const nextOrganizations = normalizeOrganizations(payload)

        if (!isMounted) {
          return
        }

        setOrganizations(nextOrganizations)
        setOrganizationId((current) => current || nextOrganizations[0]?.id || "")
      } catch (caughtError) {
        if (!isMounted) {
          return
        }

        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Unable to load organizations."
        )
      } finally {
        if (isMounted) {
          setIsLoadingOrganizations(false)
        }
      }
    }

    void loadOrganizations()

    return () => {
      isMounted = false
    }
  }, [])

  async function handleAuthSubmit(data: {
    email: string
    password: string
    role: string
    isLogin: boolean
  }) {
    setError("")
    setSuccessMessage("")

    if (!organizationId) {
      setError(
        data.isLogin
          ? "Select an organization before signing in."
          : "Select an organization to register."
      )
      return
    }

    setIsSubmitting(true)

    try {
      const endpoint = data.isLogin ? "/api/auth/login" : "/api/auth/register"
      const bodyPayload = data.isLogin
        ? { organization_id: organizationId, email: data.email, password: data.password }
        : { organization_id: organizationId, email: data.email, password: data.password, role: data.role }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(bodyPayload),
      })
      const payload = (await response.json()) as ApiOutput<LoginData>

      if (!response.ok || !payload.data) {
        throw new Error(
          getErrorMessage(payload, data.isLogin ? "Login failed." : "Registration failed.")
        )
      }

      localStorage.setItem("access_token", payload.data.access_token)
      localStorage.setItem("refresh_token", payload.data.refresh_token)
      localStorage.setItem("user", JSON.stringify(payload.data.user))

      setSuccessMessage(
        payload.message || (data.isLogin ? "Login successful." : "Registration successful.")
      )

      setCurrentUser(payload.data.user)
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : data.isLogin
          ? "Login failed."
          : "Registration failed."
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    localStorage.removeItem("user")
    setCurrentUser(null)
    setError("")
    setSuccessMessage("")
  }

  return (
    <main className="min-h-svh bg-[radial-gradient(circle_at_top_left,var(--muted),transparent_34%),linear-gradient(135deg,var(--background)_0%,var(--secondary)_100%)] px-6 py-10 text-foreground">
      <div className="mx-auto flex min-h-[calc(100svh-5rem)] w-full max-w-5xl items-center justify-center">
        {currentUser ? (
          <Dashboard user={currentUser} onLogout={handleLogout} />
        ) : (
          <AuthCard
            organizations={organizations}
            organizationId={organizationId}
            onOrganizationIdChange={setOrganizationId}
            isLoadingOrganizations={isLoadingOrganizations}
            isSubmitting={isSubmitting}
            error={error}
            setError={setError}
            successMessage={successMessage}
            setSuccessMessage={setSuccessMessage}
            onSubmit={handleAuthSubmit}
          />
        )}
      </div>
    </main>
  )
}

export default App
