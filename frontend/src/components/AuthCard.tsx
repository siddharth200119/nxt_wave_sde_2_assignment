import { useState, type FormEvent } from "react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type { Organization } from "../types"

interface AuthCardProps {
  organizations: Organization[]
  organizationId: string
  onOrganizationIdChange: (val: string) => void
  isLoadingOrganizations: boolean
  isSubmitting: boolean
  error: string
  setError: (val: string) => void
  successMessage: string
  setSuccessMessage: (val: string) => void
  onSubmit: (data: { email: string; password: string; role: string; isLogin: boolean }) => void
}

export function AuthCard({
  organizations,
  organizationId,
  onOrganizationIdChange,
  isLoadingOrganizations,
  isSubmitting,
  error,
  setError,
  successMessage,
  setSuccessMessage,
  onSubmit,
}: AuthCardProps) {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [role, setRole] = useState("MEMBER")
  const [isLogin, setIsLogin] = useState(true)

  const handleToggleMode = () => {
    setIsLogin((prev) => !prev)
    setError("")
    setSuccessMessage("")
  }

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    onSubmit({ email, password, role, isLogin })
  }

  return (
    <Card className="w-full max-w-md border-border/70 shadow-2xl transition-all duration-300">
      <CardHeader className="space-y-2 text-center">
        <CardTitle className="text-3xl font-semibold tracking-tight transition-all duration-300">
          {isLogin ? "Sign in" : "Create account"}
        </CardTitle>
        <CardDescription className="transition-all duration-300">
          {isLogin
            ? "Choose your organization and enter your credentials."
            : "Choose your organization, role, and set up your credentials."}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <form className="space-y-5" onSubmit={handleSubmit}>
          <div className="space-y-2 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <Label htmlFor="organization">Organization</Label>
            <Select
              value={organizationId}
              onValueChange={onOrganizationIdChange}
              disabled={isLoadingOrganizations || organizations.length === 0}
            >
              <SelectTrigger id="organization" className="w-full">
                <SelectValue
                  placeholder={
                    isLoadingOrganizations
                      ? "Loading organizations..."
                      : "Select organization"
                  }
                />
              </SelectTrigger>
              <SelectContent>
                {organizations.map((org) => (
                  <SelectItem key={org.id} value={org.id}>
                    {org.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {!isLogin ? (
            <div className="space-y-2 animate-in fade-in slide-in-from-bottom-2 duration-300">
              <Label htmlFor="role">Role</Label>
              <Select value={role} onValueChange={setRole}>
                <SelectTrigger id="role" className="w-full">
                  <SelectValue placeholder="Select role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="MEMBER">Member</SelectItem>
                  <SelectItem value="MANAGER">Manager</SelectItem>
                  <SelectItem value="ADMIN">Admin</SelectItem>
                </SelectContent>
              </Select>
            </div>
          ) : null}

          <div className="space-y-2 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              autoComplete="email"
              placeholder="name@example.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>

          <div className="space-y-2 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              autoComplete={isLogin ? "current-password" : "new-password"}
              placeholder={isLogin ? "Enter your password" : "Create a password"}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>

          {error ? (
            <p className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive animate-in fade-in duration-200">
              {error}
            </p>
          ) : null}

          {successMessage ? (
            <p className="rounded-lg border border-border bg-muted px-3 py-2 text-sm text-muted-foreground animate-in fade-in duration-200">
              {successMessage}
            </p>
          ) : null}

          <Button
            className="w-full transition-all duration-300 cursor-pointer"
            type="submit"
            disabled={isSubmitting || isLoadingOrganizations}
          >
            {isSubmitting
              ? isLogin
                ? "Signing in..."
                : "Registering..."
              : isLogin
              ? "Sign in"
              : "Create account"}
          </Button>
        </form>

        <div className="text-center text-sm border-t border-border/50 pt-4 animate-in fade-in duration-300">
          {isLogin ? (
            <span className="text-muted-foreground">
              Don't have an account?{" "}
              <button
                type="button"
                onClick={handleToggleMode}
                className="font-semibold text-primary underline-offset-4 hover:underline cursor-pointer transition-colors"
              >
                Sign up
              </button>
            </span>
          ) : (
            <span className="text-muted-foreground">
              Already have an account?{" "}
              <button
                type="button"
                onClick={handleToggleMode}
                className="font-semibold text-primary underline-offset-4 hover:underline cursor-pointer transition-colors"
              >
                Sign in
              </button>
            </span>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
