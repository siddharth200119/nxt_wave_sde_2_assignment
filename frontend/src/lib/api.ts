import type { ApiOutput, Organization } from "../types"

const getApiBaseUrl = () => {
  let url = import.meta.env.VITE_API_BASE_URL ?? ""
  if (url) {
    if (!/^https?:\/\//i.test(url)) {
      url = `http://${url}`
    }
    url = url.replace(/\/+$/, "")
  }
  return url
}

export const API_BASE_URL = getApiBaseUrl()

export function getErrorMessage(payload: unknown, fallback: string): string {
  if (payload && typeof payload === "object") {
    const message = "message" in payload ? (payload as Record<string, unknown>).message : undefined
    if (typeof message === "string" && message.trim()) {
      return message
    }

    const detail = "detail" in payload ? (payload as Record<string, unknown>).detail : undefined
    if (typeof detail === "string" && detail.trim()) {
      return detail
    }
  }

  return fallback
}

export function normalizeOrganizations(
  payload: ApiOutput<Organization[]> | Organization[]
): Organization[] {
  return Array.isArray(payload) ? payload : (payload.data ?? [])
}

export async function refreshSession(): Promise<string> {
  const refreshToken = localStorage.getItem("refresh_token")
  if (!refreshToken) {
    throw new Error("No refresh token available")
  }

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
  } catch (err) {
    // If error, try direct fallback
    response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
  }

  // Double fallback logic
  if (!response.ok) {
    try {
      const fallbackResponse = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })
      if (fallbackResponse.ok) {
        response = fallbackResponse
      }
    } catch {
      // ignore and keep original
    }
  }

  const payload = await response.json()
  if (!response.ok || !payload.data) {
    throw new Error(getErrorMessage(payload, "Session expired"))
  }

  const { access_token, refresh_token: newRefreshToken, user } = payload.data
  localStorage.setItem("access_token", access_token)
  localStorage.setItem("refresh_token", newRefreshToken)
  localStorage.setItem("user", JSON.stringify(user))

  return access_token
}

export async function authenticatedFetch(
  url: string,
  options: RequestInit = {},
  onSessionExpired?: () => void
): Promise<Response> {
  let token = localStorage.getItem("access_token")

  const headers = new Headers(options.headers || {})
  if (token) {
    headers.set("Authorization", `Bearer ${token}`)
  }

  let response = await fetch(url, {
    ...options,
    headers,
  })

  if (response.status === 401) {
    try {
      const newAccessToken = await refreshSession()
      const newHeaders = new Headers(options.headers || {})
      newHeaders.set("Authorization", `Bearer ${newAccessToken}`)

      response = await fetch(url, {
        ...options,
        headers: newHeaders,
      })
    } catch (refreshErr) {
      localStorage.removeItem("access_token")
      localStorage.removeItem("refresh_token")
      localStorage.removeItem("user")
      if (onSessionExpired) {
        onSessionExpired()
      }
      throw new Error("Your session has expired. Please sign in again.")
    }
  }

  return response
}
