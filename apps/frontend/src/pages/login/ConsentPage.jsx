import { useEffect, useMemo, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { ChevronDown, Loader2, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { getPendingConsent, submitConsent, getSessionToken } from "@/api/consent"
import { getTerms } from "@/api/terms"

function filterCurrentTerms(terms) {
  const now = new Date()
  const grouped = {}

  for (const term of terms) {
    const policyType = term.policy_type
    const effectiveFrom = new Date(term.effective_from)

    if (effectiveFrom > now) continue

    if (!grouped[policyType] || new Date(grouped[policyType].effective_from) < effectiveFrom) {
      grouped[policyType] = term
    }
  }

  return Object.values(grouped)
}

function flattenTerms(terms) {
  const currentTerms = filterCurrentTerms(terms)

  return currentTerms.flatMap((policyVersion) =>
    (policyVersion.clauses || []).map((clause) => ({
      ...clause,
      policy_version_id: policyVersion.policy_version_id,
      policy_type: policyVersion.policy_type,
      version: policyVersion.version,
      content: policyVersion.content,
    })),
  )
}

function formatPolicyType(policyType) {
  if (policyType === "TERMS_OF_USE") return "Termos de Uso"
  if (policyType === "PRIVACY_POLICY") return "Política de Privacidade"
  return String(policyType || "Documento").replaceAll("_", " ")
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

export default function ConsentPage() {
  const navigate = useNavigate()
  const [terms, setTerms] = useState([])
  const [pendingClauses, setPendingClauses] = useState([])
  const [selectedClauseIds, setSelectedClauseIds] = useState(() => new Set())
  const [expandedVersionIds, setExpandedVersionIds] = useState(() => new Set())
  const [loadingTerms, setLoadingTerms] = useState(true)
  const [loadError, setLoadError] = useState("")
  const [submissionError, setSubmissionError] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [sessionToken, setSessionToken] = useState("")

  useEffect(() => {
    async function fetchData() {
      try {
        setLoadingTerms(true)
        setLoadError("")

        const token = getSessionToken()
        if (!token) {
          setLoadError("Sessão expirada. Faça login novamente.")
          return
        }

        setSessionToken(token)

        const [termsResponse, pendingResponse] = await Promise.all([
          getTerms(),
          getPendingConsent().catch(() => ({ pending_clauses: [] })),
        ])

        setTerms(termsResponse.terms || [])
        setPendingClauses(pendingResponse.pending_clauses || [])
      } catch {
        setLoadError("Não foi possível carregar os termos.")
      } finally {
        setLoadingTerms(false)
      }
    }

    fetchData()
  }, [])

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

  useEffect(() => {
    if (terms.length === 0) {
      return
    }

    const currentTerms = filterCurrentTerms(terms)
    if (currentTerms.length > 0) {
      setExpandedVersionIds(new Set([String(currentTerms[0].policy_version_id)]))
      
      // Auto-select mandatory clauses from ALL current terms
      const allFlatClauses = flattenTerms(terms)
      const mandatoryClauses = allFlatClauses.filter((clause) => clause.mandatory)
      const mandatoryIds = new Set(mandatoryClauses.map((c) => String(c.clause_uuid)))
      
      setSelectedClauseIds((current) => {
        const updated = new Set(current)
        mandatoryIds.forEach((id) => updated.add(id))
        return updated
      })
    }
  }, [terms])

  const pendingConsent = pendingClauseIds.size > 0
  const hasToken = Boolean(sessionToken)

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

  async function handleSubmit() {
    if (!hasToken) {
      return
    }

    if (!allClausesAccepted || loadingTerms || submitting || loadError) {
      return
    }

    try {
      setSubmitting(true)
      setSubmissionError("")
      
      const actions = buildConsentActions(terms, selectedClauseIds)
      
      if (actions.length === 0) {
        setSubmissionError("Nenhuma cláusula foi selecionada. Selecione pelo menos as cláusulas obrigatórias.")
        setSubmitting(false)
        return
      }
      
      await submitConsent(actions)
      navigate("/dashboard/indicadores")
    } catch (error) {
      const serverError = error.data?.detail ? JSON.stringify(error.data.detail) : "Erro desconhecido"
      setSubmissionError(`Não foi possível concluir o consentimento: ${serverError}`)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent/5 rounded-full blur-3xl" />
      </div>

      <Card className="w-full max-w-3xl relative z-10 border-border bg-card/80 backdrop-blur-sm">
        <CardHeader className="text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Zap className="w-8 h-8 text-primary" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-foreground">Consentimento pendente</CardTitle>
          <CardDescription className="text-muted-foreground">
            Você precisa aceitar os termos para continuar usando a plataforma.
          </CardDescription>
        </CardHeader>

        <CardContent>
          {hasToken ? (
            <div className="space-y-6">
              {!pendingConsent && !loadingTerms && !loadError ? (
                <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">
                  Não há consentimento pendente no momento.
                </div>
              ) : null}

              {loadError ? (
                <div className="rounded-xl border border-destructive/20 bg-destructive/10 p-4 text-sm text-destructive">
                  {loadError}
                </div>
              ) : null}

              {submissionError ? (
                <div className="rounded-xl border border-destructive/20 bg-destructive/10 p-4 text-sm text-destructive">
                  {submissionError}
                </div>
              ) : null}

              <div className="rounded-xl border border-border bg-muted/30 px-4 py-3 text-sm text-muted-foreground">
                <span className="font-medium text-foreground">Progresso:</span> {selectedClauseIds.size}/{allClauses.length} cláusulas aceitas
              </div>

              <div className="space-y-4">
                {loadingTerms ? (
                  <div className="flex items-center justify-center gap-2 rounded-xl border border-border bg-card p-6 text-muted-foreground">
                    <Loader2 className="h-5 w-5 animate-spin" />
                    <span>Carregando termos...</span>
                  </div>
                ) : (
                  filterCurrentTerms(terms).map((policyVersion) => {
                    const versionId = String(policyVersion.policy_version_id)
                    const isExpanded = expandedVersionIds.has(versionId)
                    const versionClauses = policyVersion.clauses || []

                    return (
                      <section key={versionId} className="overflow-hidden rounded-xl border border-border bg-card">
                        <button
                          type="button"
                          onClick={() => toggleVersion(versionId)}
                          className="flex w-full items-center justify-between gap-4 border-b border-border px-4 py-3 text-left transition-colors hover:bg-muted/50"
                        >
                          <div>
                            <p className="text-sm font-semibold text-foreground">
                              {formatPolicyType(policyVersion.policy_type)}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              Versão {policyVersion.version} · {versionClauses.length} cláusulas
                            </p>
                          </div>
                          <ChevronDown className={`h-4 w-4 text-muted-foreground transition-transform ${isExpanded ? "rotate-180" : ""}`} />
                        </button>

                        {isExpanded && (
                          <div className="space-y-4 p-4">
                            {policyVersion.content && (
                              <div className="whitespace-pre-line rounded-lg bg-muted/40 p-3 text-sm leading-6 text-muted-foreground">
                                {policyVersion.content}
                              </div>
                            )}

                            <div className="space-y-3">
                              {versionClauses.map((clause) => {
                                const clauseId = String(clause.clause_uuid)
                                const checked = selectedClauseIds.has(clauseId)
                                const isPending = pendingClauseIds.has(clauseId)

                                return (
                                  <label
                                    key={clauseId}
                                    htmlFor={`clause-${clauseId}`}
                                    className={`flex cursor-pointer gap-3 rounded-lg border p-4 transition-colors ${
                                      checked ? "border-primary/40 bg-primary/5" : "border-border hover:bg-muted/40"
                                    }`}
                                  >
                                    <input
                                      id={`clause-${clauseId}`}
                                      type="checkbox"
                                      className="mt-1 h-4 w-4 rounded border-border text-primary focus:ring-primary"
                                      checked={checked}
                                      onChange={() => toggleClause(clauseId)}
                                      aria-labelledby={`clause-${clauseId}-label`}
                                    />
                                    <div className="min-w-0 flex-1">
                                      <div className="flex flex-wrap items-center gap-2">
                                        <span id={`clause-${clauseId}-label`} className="text-sm font-semibold text-foreground">
                                          {clause.title}
                                        </span>
                                        <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                                          {clause.mandatory ? "Obrigatória" : "Opcional"}
                                        </span>
                                        {isPending && (
                                          <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
                                            Pendente
                                          </span>
                                        )}
                                      </div>
                                      <p className="mt-1 text-sm leading-6 text-muted-foreground">
                                        {clause.description || "Sem descrição informada."}
                                      </p>
                                    </div>
                                  </label>
                                )
                              })}
                            </div>
                          </div>
                        )}
                      </section>
                    )
                  })
                )}
              </div>

              <div className="flex flex-col-reverse gap-3 border-t border-border pt-6 sm:flex-row sm:justify-end">
                <Link
                  to="/login"
                  className="inline-flex items-center justify-center rounded-md border border-border px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-muted"
                >
                  Voltar
                </Link>
                <Button
                  type="button"
                  onClick={handleSubmit}
                  className="w-full sm:w-auto bg-primary text-primary-foreground hover:bg-primary/90"
                  disabled={!pendingConsent || !allClausesAccepted || loadingTerms || submitting || Boolean(loadError)}
                >
                  {submitting ? "Finalizando..." : "Aceitar termos"}
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">
                É necessário fazer login antes de aceitar os termos.
              </div>
              <div className="flex justify-center">
                <Button
                  type="button"
                  className="bg-primary text-primary-foreground hover:bg-primary/90"
                  onClick={() => navigate("/login")}
                >
                  Voltar para Login
                </Button>
              </div>
            </div>
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
