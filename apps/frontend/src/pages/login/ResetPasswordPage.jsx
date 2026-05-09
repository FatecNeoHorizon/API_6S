import { useMemo, useState } from "react"
import { Link, useNavigate, useSearchParams } from "react-router-dom"
import { Check, Eye, EyeOff, KeyRound, Loader2, ShieldCheck } from "lucide-react"

import { resetPassword } from "@/api/auth"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

const MIN_TOKEN_LENGTH = 20

function buildPasswordRequirements(password) {
  return [
    { label: "Minimo 8 caracteres", valid: password.length >= 8 },
    { label: "Uma letra maiuscula", valid: /[A-Z]/.test(password) },
    { label: "Uma letra minuscula", valid: /[a-z]/.test(password) },
    { label: "Um numero", valid: /\d/.test(password) },
    { label: "Um caractere especial", valid: /[!@#$%^&*]/.test(password) },
  ]
}

function PasswordRequirements({ passwordRequirements }) {
  return (
    <div className="rounded-lg bg-secondary/50 p-3">
      <p className="mb-2 text-xs font-medium text-muted-foreground">Requisitos da senha:</p>
      <div className="grid grid-cols-2 gap-1">
        {passwordRequirements.map((req) => (
          <div key={req.label} className="flex items-center gap-1.5">
            <div
              className={`flex h-3.5 w-3.5 items-center justify-center rounded-full ${
                req.valid ? "bg-primary" : "bg-muted"
              }`}
            >
              {req.valid && <Check className="h-2 w-2 text-primary-foreground" />}
            </div>
            <span className={`text-xs ${req.valid ? "text-foreground" : "text-muted-foreground"}`}>
              {req.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function ResetPasswordPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const token = searchParams.get("token") || ""
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState("")
  const [successMessage, setSuccessMessage] = useState("")

  const passwordRequirements = useMemo(() => buildPasswordRequirements(password), [password])
  const allRequirementsMet = passwordRequirements.every((requirement) => requirement.valid)
  const passwordsMatch = password === confirmPassword && confirmPassword.length > 0
  const tokenMissing = token.length < MIN_TOKEN_LENGTH

  const handleSubmit = async (event) => {
    event.preventDefault()
    setErrorMessage("")
    setSuccessMessage("")

    if (tokenMissing) {
      setErrorMessage("Abra o link de redefinição enviado por email.")
      return
    }

    if (!allRequirementsMet) {
      setErrorMessage("A nova senha não atende aos requisitos mínimos.")
      return
    }

    if (!passwordsMatch) {
      setErrorMessage("As senhas não coincidem.")
      return
    }

    setIsLoading(true)

    try {
      await resetPassword({ token, new_password: password })
      setSuccessMessage("Senha redefinida com sucesso. Você já pode entrar novamente.")
      setPassword("")
      setConfirmPassword("")
    } catch (error) {
      const detail = error?.data?.detail || ""

      if (detail === "invalid_or_expired_reset_token") {
        setErrorMessage("O link de redefinição está inválido ou expirado.")
      } else if (detail === "inactive_user") {
        setErrorMessage("Não foi possível redefinir a senha para este usuário.")
      } else if (error?.status === 422) {
        setErrorMessage("A nova senha não atende aos requisitos mínimos.")
      } else {
        setErrorMessage("Não foi possível redefinir a senha. Tente novamente mais tarde.")
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 h-96 w-96 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 h-96 w-96 rounded-full bg-accent/5 blur-3xl" />
      </div>

      <Card className="relative z-10 w-full max-w-md border-border bg-card/80 backdrop-blur-sm">
        <CardHeader className="text-center">
          <div className="mb-4 flex items-center justify-center gap-2">
            <div className="rounded-lg bg-primary/10 p-2">
              <KeyRound className="h-8 w-8 text-primary" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-foreground">Redefinir senha</CardTitle>
          <CardDescription className="text-muted-foreground">
            Defina uma nova senha para concluir a recuperação da conta.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <label htmlFor="password" className="text-sm font-medium text-foreground">
                Nova senha
              </label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Digite sua nova senha"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  className="bg-input border-border pr-10 text-foreground placeholder:text-muted-foreground"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <PasswordRequirements passwordRequirements={passwordRequirements} />

            <div className="flex flex-col gap-2">
              <label htmlFor="confirmPassword" className="text-sm font-medium text-foreground">
                Confirmar senha
              </label>
              <div className="relative">
                <Input
                  id="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  placeholder="Confirme sua nova senha"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  className={`bg-input border-border pr-10 text-foreground placeholder:text-muted-foreground ${
                    confirmPassword.length > 0 && !passwordsMatch ? "border-destructive" : ""
                  }`}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
                >
                  {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>

              {confirmPassword.length > 0 && !passwordsMatch && (
                <p className="text-xs text-destructive">As senhas não coincidem.</p>
              )}
            </div>

            {tokenMissing && (
              <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
                O link de redefinição está incompleto ou inválido.
              </div>
            )}

            {errorMessage && (
              <div className="rounded-md border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                {errorMessage}
              </div>
            )}

            {successMessage && (
              <div className="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
                {successMessage}
              </div>
            )}

            <Button
              type="submit"
              className="w-full bg-primary text-primary-foreground hover:bg-primary/90"
              disabled={isLoading || tokenMissing || !allRequirementsMet || !passwordsMatch}
            >
              {isLoading ? (
                <span className="inline-flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Redefinindo...
                </span>
              ) : (
                "Redefinir senha"
              )}
            </Button>
          </form>

          {successMessage ? (
            <div className="mt-6 flex items-center justify-between gap-3 border-t border-border pt-6">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <ShieldCheck className="h-4 w-4 text-primary" />
                Volte para acessar a plataforma.
              </div>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate("/login")}
                className="border-border text-foreground hover:bg-muted"
              >
                Ir para login
              </Button>
            </div>
          ) : (
            <div className="mt-6 border-t border-border pt-6 text-center text-sm text-muted-foreground">
              <Link to="/login" className="text-primary hover:underline">
                Voltar ao login
              </Link>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}