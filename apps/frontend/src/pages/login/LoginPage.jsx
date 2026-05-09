import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { Zap, Eye, EyeOff } from "lucide-react"
import { login } from "@/api/auth"
import { saveClientSession } from "@/api/consent"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [rememberMe, setRememberMe] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [emailError, setEmailError] = useState("")
  const [passwordError, setPasswordError] = useState("")
  const [submissionError, setSubmissionError] = useState("")
  const navigate = useNavigate()

  const validateForm = () => {
    let valid = true
    setEmailError("")
    setPasswordError("")

    if (!email.trim()) {
      setEmailError("Informe o email.")
      valid = false
    } else if (!emailPattern.test(email)) {
      setEmailError("Informe um email válido.")
      valid = false
    }

    if (!password) {
      setPasswordError("Informe a senha.")
      valid = false
    }

    return valid
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    setSubmissionError("")

    if (!validateForm()) {
      return
    }

    setIsLoading(true)

    try {
      const response = await login({ email: email.trim(), password })
      saveClientSession(response.access_token, { remember: rememberMe })

      if (response.pending_consent) {
        navigate("/consent")
      } else {
        navigate("/dashboard/indicadores")
      }
    } catch (error) {
      const detail = error?.data?.detail || ""

      if (detail === "invalid_credentials" || error?.status === 401) {
        setSubmissionError("Email ou senha inválidos. Verifique e tente novamente.")
      } else if (detail === "first_access_required") {
        navigate("/first-access")
      } else {
        setSubmissionError("Não foi possível autenticar. Tente novamente mais tarde.")
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent/5 rounded-full blur-3xl" />
      </div>

      <Card className="w-full max-w-md relative z-10 border-border bg-card/80 backdrop-blur-sm">
        <CardHeader className="text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Zap className="w-8 h-8 text-primary" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-foreground">Zeus</CardTitle>
          <CardDescription className="text-muted-foreground">
            Plataforma de Análise de Dados ANEEL
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleLogin} className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <label htmlFor="email" className="text-sm font-medium text-foreground">
                Email
              </label>
              <Input
                id="email"
                type="email"
                placeholder="seu@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="bg-input border-border text-foreground placeholder:text-muted-foreground"
                required
              />
              {emailError && (
                <p className="text-sm text-destructive">{emailError}</p>
              )}
            </div>

            <div className="flex flex-col gap-2">
              <label htmlFor="password" className="text-sm font-medium text-foreground">
                Senha
              </label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="********"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-input border-border text-foreground placeholder:text-muted-foreground pr-10"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {passwordError && (
                <p className="text-sm text-destructive">{passwordError}</p>
              )}
            </div>

            {submissionError && (
              <div className="rounded-md border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                {submissionError}
              </div>
            )}

            <div className="flex items-center justify-between">
              <label htmlFor="rememberMe" className="flex items-center gap-2 text-sm text-muted-foreground">
                <input
                  id="rememberMe"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded border-border"
                />
                Lembrar de mim
              </label>

              <Link to="/forgot-password" className="text-sm text-primary hover:underline">
                Esqueceu a senha?
              </Link>
            </div>

            <Button
              type="submit"
              className="w-full bg-primary text-primary-foreground hover:bg-primary/90"
              disabled={isLoading}
            >
              {isLoading ? "Entrando..." : "Entrar"}
            </Button>
          </form>

          <div className="mt-6 pt-6 border-t border-border text-center">
            <p className="text-xs text-muted-foreground">
              Tecsys do Brasil - Todos os direitos reservados
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
