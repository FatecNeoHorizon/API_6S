import { useEffect, useMemo, useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import {
  AlertCircle,
  Check,
  Eye,
  EyeOff,
  Zap,
} from "lucide-react"
import PropTypes from "prop-types"
import { toast } from "sonner"

import { firstAccess } from "@/api/auth"
import { getPendingConsent, submitConsent } from "@/api/consent"
import { getTerms } from "@/api/terms"
import ConsentFlowStep from "@/components/consent/ConsentFlowStep"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

function flattenTerms(terms) {
  return terms.flatMap((policyVersion) =>
    (policyVersion.clauses || []).map((clause) => ({
      ...clause,
      policy_version_id: policyVersion.policy_version_id,
      policy_type: policyVersion.policy_type,
      version: policyVersion.version,
      content: policyVersion.content,
    })),
  )
}

function buildConsentActions(terms, selectedClauseIds) {
  return flattenTerms(terms)
    .filter((clause) => selectedClauseIds.has(String(clause.clause_uuid)))
    .map((clause) => ({
      clause_uuid: clause.clause_uuid,
      policy_version_id: clause.policy_version_id,
      action: "CONSENT",
    }))
}

function PasswordStep({
  password,
  confirmPassword,
  passwordRequirements,
  allRequirementsMet,
  passwordsMatch,
  showPassword,
  showConfirmPassword,
  setShowPassword,
  setShowConfirmPassword,
  setPassword,
  setConfirmPassword,
  onSubmit,
  submitting,
  tokenMissing,
}) {
  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <label htmlFor="password" className="text-sm font-medium text-foreground">
          Nova Senha
        </label>

        <div className="relative">
          <Input
            id="password"
            type={showPassword ? "text" : "password"}
            placeholder="Digite sua nova senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="bg-input border-border text-foreground placeholder:text-muted-foreground pr-10"
            required
          />

          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
          >
            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
      </div>

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

      <div className="flex flex-col gap-2">
        <label htmlFor="confirmPassword" className="text-sm font-medium text-foreground">
          Confirmar Senha
        </label>

        <div className="relative">
          <Input
            id="confirmPassword"
            type={showConfirmPassword ? "text" : "password"}
            placeholder="Confirme sua nova senha"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className={`bg-input border-border text-foreground placeholder:text-muted-foreground pr-10 ${
              confirmPassword.length > 0 && !passwordsMatch ? "border-destructive" : ""
            }`}
            required
          />

          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
          >
            {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>

        {confirmPassword.length > 0 && !passwordsMatch && (
          <p className="flex items-center gap-1 text-xs text-destructive">
            <AlertCircle className="h-3 w-3" />
            As senhas nao coincidem
          </p>
        )}
      </div>

      <Button
        type="submit"
        className="mt-2 w-full bg-primary text-primary-foreground hover:bg-primary/90"
        disabled={!allRequirementsMet || !passwordsMatch || submitting || tokenMissing}
      >
        {submitting ? "Validando..." : "Continuar"}
      </Button>
    </form>
  )
}

PasswordStep.propTypes = {
  password: PropTypes.string.isRequired,
  confirmPassword: PropTypes.string.isRequired,
  passwordRequirements: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      valid: PropTypes.bool.isRequired,
    }),
  ).isRequired,
  allRequirementsMet: PropTypes.bool.isRequired,
  passwordsMatch: PropTypes.bool.isRequired,
  showPassword: PropTypes.bool.isRequired,
  showConfirmPassword: PropTypes.bool.isRequired,
  setShowPassword: PropTypes.func.isRequired,
  setShowConfirmPassword: PropTypes.func.isRequired,
  setPassword: PropTypes.func.isRequired,
  setConfirmPassword: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  submitting: PropTypes.bool.isRequired,
  tokenMissing: PropTypes.bool.isRequired,
}

export default function PrimeiroAcessoPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const emailLinkToken =
    searchParams.get("token") ||
    searchParams.get("session_uuid") ||
    searchParams.get("sessionUuid") ||
    searchParams.get("access_token") ||
    searchParams.get("accessToken") ||
    ""
  const [consentToken, setConsentToken] = useState("")
  const [step, setStep] = useState("senha")
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [terms, setTerms] = useState([])
  const [pendingClauses, setPendingClauses] = useState([])
  const [selectedClauseIds, setSelectedClauseIds] = useState(() => new Set())
  const [expandedVersionIds, setExpandedVersionIds] = useState(() => new Set())
  const [loadingTerms, setLoadingTerms] = useState(true)
  const [loadError, setLoadError] = useState("")
  const [submittingConsent, setSubmittingConsent] = useState(false)
  const [submittingFirstAccess, setSubmittingFirstAccess] = useState(false)
  const tokenMissing = !emailLinkToken

  const passwordRequirements = [
    { label: "Minimo 8 caracteres", valid: password.length >= 8 },
    { label: "Uma letra maiuscula", valid: /[A-Z]/.test(password) },
    { label: "Uma letra minuscula", valid: /[a-z]/.test(password) },
    { label: "Um numero", valid: /\d/.test(password) },
    { label: "Um caractere especial", valid: /[!@#$%^&*]/.test(password) },
  ]

  const allRequirementsMet = passwordRequirements.every(r => r.valid)
  const passwordsMatch = password === confirmPassword && confirmPassword.length > 0
  const allClauses = useMemo(() => flattenTerms(terms), [terms])
  const pendingClauseIds = useMemo(
    () => new Set(pendingClauses.map((clause) => String(clause.clause_uuid))),
    [pendingClauses],
  )
  const allClausesAccepted =
    allClauses.length > 0 &&
    allClauses
      .filter((clause) => clause.mandatory)
      .every((clause) => selectedClauseIds.has(String(clause.clause_uuid)))

  async function fetchTermsAndConsentData() {
    try {
      setLoadingTerms(true)
      setLoadError("")

      const [termsResponse, pendingResponse] = await Promise.all([
        getTerms(),
        getPendingConsent().catch(() => ({ pending_clauses: [] })),
      ])

      setTerms(termsResponse.terms || [])
      setPendingClauses(pendingResponse.pending_clauses || [])
    } catch {
      setLoadError("Não foi possível carregar os termos.")
      toast.error("Não foi possível carregar os termos.")
    } finally {
      setLoadingTerms(false)
    }
  }

  useEffect(() => {
    fetchTermsAndConsentData()
  }, [consentToken])

  useEffect(() => {
    if (terms.length === 0) {
      return
    }

    setExpandedVersionIds(new Set([String(terms[0].policy_version_id)]))
  }, [terms])

  const handlePasswordSubmit = async (e) => {
    e.preventDefault()

    if (tokenMissing) {
      toast.error("Abra o link de primeiro acesso enviado por e-mail.")
      return
    }

    if (!allRequirementsMet || !passwordsMatch || submittingFirstAccess) {
      return
    }

    try {
      setSubmittingFirstAccess(true)

      const response = await firstAccess({
        token: emailLinkToken,
        new_password: password,
      })

      const accessToken = response.access_token

      sessionStorage.setItem("access_token", accessToken)
      sessionStorage.setItem("token", accessToken)
      sessionStorage.setItem("session_uuid", accessToken)

      setConsentToken(accessToken)
      setPendingClauses(response.pending_clauses || [])
      setStep("termos")
    } catch {
      toast.error("Não foi possível concluir o primeiro acesso.")
    } finally {
      setSubmittingFirstAccess(false)
    }
  }

  function toggleClause(clauseUuid) {
    setSelectedClauseIds((current) => {
      const next = new Set(current)

      if (next.has(clauseUuid)) {
        next.delete(clauseUuid)
      } else {
        next.add(clauseUuid)
      }

      return next
    })
  }

  function toggleVersion(versionId) {
    setExpandedVersionIds((current) => {
      const next = new Set(current)

      if (next.has(versionId)) {
        next.delete(versionId)
      } else {
        next.add(versionId)
      }

      return next
    })
  }

  async function handleFinalSubmit() {
    if (!consentToken) {
      toast.error("Abra o link de primeiro acesso enviado por e-mail.")
      return
    }

    if (!allClausesAccepted || loadingTerms || submittingConsent || loadError) {
      return
    }

    try {
      setSubmittingConsent(true)

      const actions = buildConsentActions(terms, selectedClauseIds)
      await submitConsent(actions)

      toast.success("Cadastro concluído com sucesso.")
      navigate("/dashboard/indicadores")
    } catch {
      toast.error("Não foi possível concluir o cadastro.")
    } finally {
      setSubmittingConsent(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent/5 rounded-full blur-3xl" />
      </div>

      <Card className="w-full max-w-lg relative z-10 border-border bg-card/80 backdrop-blur-sm">
        <CardHeader className="text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Zap className="w-8 h-8 text-primary" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-foreground">
            {step === "senha" ? "Primeiro Acesso" : "Aceite os Termos"}
          </CardTitle>
          <CardDescription className="text-muted-foreground">
            {step === "senha" 
              ? "Configure sua senha de acesso" 
              : "Leia e aceite os termos para continuar"
            }
          </CardDescription>

          {/* Progress Steps */}
          <div className="flex items-center justify-center gap-2 mt-4">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              step === "senha" ? "bg-primary text-primary-foreground" : "bg-primary/20 text-primary"
            }`}>
              {step === "termos" ? <Check className="w-4 h-4" /> : "1"}
            </div>
            <div className={`w-12 h-1 rounded ${step === "termos" ? "bg-primary" : "bg-border"}`} />
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              step === "termos" ? "bg-primary text-primary-foreground" : "bg-border text-muted-foreground"
            }`}>
              2
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {tokenMissing && (
            <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">
              Este fluxo precisa ser aberto pelo link de primeiro acesso enviado por e-mail.
            </div>
          )}

          {step === "senha" ? (
            <PasswordStep
              password={password}
              confirmPassword={confirmPassword}
              passwordRequirements={passwordRequirements}
              allRequirementsMet={allRequirementsMet}
              passwordsMatch={passwordsMatch}
              showPassword={showPassword}
              showConfirmPassword={showConfirmPassword}
              setShowPassword={setShowPassword}
              setShowConfirmPassword={setShowConfirmPassword}
              setPassword={setPassword}
              setConfirmPassword={setConfirmPassword}
              onSubmit={handlePasswordSubmit}
              submitting={submittingFirstAccess}
              tokenMissing={tokenMissing}
            />
          ) : (
            <ConsentFlowStep
              terms={terms}
              pendingClauseIds={pendingClauseIds}
              selectedClauseIds={selectedClauseIds}
              expandedVersionIds={expandedVersionIds}
              allClauses={allClauses}
              allClausesAccepted={allClausesAccepted}
              loadingTerms={loadingTerms}
              loadError={loadError}
              submittingConsent={submittingConsent}
              onBack={() => setStep("senha")}
              onRetry={fetchTermsAndConsentData}
              onToggleClause={toggleClause}
              onToggleVersion={toggleVersion}
              onSubmit={handleFinalSubmit}
              submitLabel="Concluir Cadastro"
            />
          )}

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
