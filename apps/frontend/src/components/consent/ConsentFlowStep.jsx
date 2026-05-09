import { AlertTriangle, ChevronDown, Loader2, ShieldCheck } from "lucide-react";
import PropTypes from "prop-types";
import { Button } from "@/components/ui/button";

function formatPolicyType(policyType) {
  if (policyType === "TERMS_OF_USE") return "Termos de Uso";
  if (policyType === "PRIVACY_POLICY") return "Política de Privacidade";

  return String(policyType || "Documento").replaceAll("_", " ");
}

export default function ConsentFlowStep({
  terms,
  pendingClauseIds,
  selectedClauseIds,
  expandedVersionIds,
  allClauses,
  allClausesAccepted,
  loadingTerms,
  loadError,
  submittingConsent,
  onBack,
  onRetry,
  onToggleClause,
  onToggleVersion,
  onSubmit,
  submitLabel,
}) {
  let termsSection = null;

  if (loadingTerms) {
    termsSection = (
      <div className="flex items-center justify-center gap-2 rounded-xl border border-border bg-card p-6 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" />
        <span>Carregando termos...</span>
      </div>
    );
  } else if (loadError) {
    termsSection = (
      <div className="rounded-xl border border-destructive/20 bg-destructive/10 p-4 text-sm text-destructive">
        <p>{loadError}</p>
        <Button
          type="button"
          variant="outline"
          onClick={onRetry}
          className="mt-3 border-destructive/20 text-destructive hover:bg-destructive/10"
        >
          Tentar novamente
        </Button>
      </div>
    );
  } else if (allClauses.length === 0) {
    termsSection = (
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">
        Não há cláusulas ativas para aceitar no momento.
      </div>
    );
  } else {
    termsSection = (
      <div className="space-y-3">
        {terms.map((policyVersion) => {
          const versionId = String(policyVersion.policy_version_id);
          const versionClauses = policyVersion.clauses || [];
          const isExpanded = expandedVersionIds.has(versionId);

          return (
            <section key={versionId} className="overflow-hidden rounded-xl border border-border bg-card">
              <button
                type="button"
                onClick={() => onToggleVersion(versionId)}
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

                <ChevronDown
                  className={`h-4 w-4 text-muted-foreground transition-transform ${isExpanded ? "rotate-180" : ""}`}
                />
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
                      const clauseId = String(clause.clause_uuid);
                      const checked = selectedClauseIds.has(clauseId);
                      const isPending = pendingClauseIds.has(clauseId);
                      const checkboxId = `clause-${clauseId}`;

                      return (
                        <div
                          key={clauseId}
                          className={`flex gap-3 rounded-lg border p-4 transition-colors ${
                            checked ? "border-primary/40 bg-primary/5" : "border-border hover:bg-muted/40"
                          }`}
                        >
                          <input
                            id={checkboxId}
                            type="checkbox"
                            className="mt-1 h-4 w-4 rounded border-border text-primary focus:ring-primary"
                            checked={checked}
                            onChange={() => onToggleClause(clauseId)}
                          />

                          <div className="min-w-0 flex-1">
                            <label htmlFor={checkboxId} className="cursor-pointer">
                              <div className="flex flex-wrap items-center gap-2">
                                <span className="text-sm font-semibold text-foreground">{clause.title}</span>
                                <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                                  {clause.mandatory ? "Obrigatória" : "Opcional"}
                                </span>
                                {isPending && (
                                  <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
                                    Pendente
                                  </span>
                                )}
                              </div>
                            </label>

                            <p className="mt-1 text-sm leading-6 text-muted-foreground">
                              {clause.description || "Sem descrição informada."}
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </section>
          );
        })}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-start gap-3 rounded-xl border border-border bg-card p-4">
        <div className="rounded-full bg-primary/10 p-2">
          <ShieldCheck className="h-5 w-5 text-primary" />
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-base font-semibold text-foreground">Aceite os termos</h2>
            {allClausesAccepted ? (
              <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                <span className="inline-block h-3.5 w-3.5 rounded-full bg-green-600" aria-hidden="true" />
                <span className="ml-1">Tudo aceito</span>
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
                <AlertTriangle className="h-3.5 w-3.5" />
                Pendente
              </span>
            )}
          </div>

          <p className="mt-1 text-sm text-muted-foreground">
            Leia os documentos ativos e marque as caixas para concluir o cadastro.
          </p>
        </div>
      </div>

      <div className="rounded-xl border border-border bg-muted/30 px-4 py-3 text-sm text-muted-foreground">
        <span className="font-medium text-foreground">Progresso:</span> {selectedClauseIds.size}/{allClauses.length} cláusulas aceitas
      </div>

      {termsSection}

      <div className="flex flex-col-reverse gap-3 border-t border-border pt-6 sm:flex-row sm:justify-end">
        {onBack ? (
          <Button
            type="button"
            variant="outline"
            onClick={onBack}
            className="border-border text-foreground hover:bg-muted"
            disabled={submittingConsent}
          >
            Voltar
          </Button>
        ) : null}

        <Button
          type="button"
          onClick={onSubmit}
          className="bg-primary text-primary-foreground hover:bg-primary/90"
          disabled={!allClausesAccepted || loadingTerms || submittingConsent || Boolean(loadError)}
        >
          {submittingConsent ? "Finalizando..." : submitLabel}
        </Button>
      </div>
    </div>
  );
}

ConsentFlowStep.propTypes = {
  terms: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  pendingClauseIds: PropTypes.instanceOf(Set).isRequired,
  selectedClauseIds: PropTypes.instanceOf(Set).isRequired,
  expandedVersionIds: PropTypes.instanceOf(Set).isRequired,
  allClauses: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  allClausesAccepted: PropTypes.bool.isRequired,
  loadingTerms: PropTypes.bool.isRequired,
  loadError: PropTypes.string.isRequired,
  submittingConsent: PropTypes.bool.isRequired,
  onBack: PropTypes.func,
  onRetry: PropTypes.func.isRequired,
  onToggleClause: PropTypes.func.isRequired,
  onToggleVersion: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  submitLabel: PropTypes.string,
};

ConsentFlowStep.defaultProps = {
  onBack: undefined,
  submitLabel: "Concluir Cadastro",
};
