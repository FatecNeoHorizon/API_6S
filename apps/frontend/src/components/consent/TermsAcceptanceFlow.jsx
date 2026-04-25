import { useEffect, useMemo, useRef, useState } from "react";
import { AlertTriangle, CheckCircle2, Loader2, ShieldCheck } from "lucide-react";
import { toast } from "sonner";

import { getPendingConsent } from "../../api/consent";
import { getTerms } from "../../api/terms";

function flattenTerms(terms) {
  return terms.flatMap((policyVersion) =>
    (policyVersion.clauses || []).map((clause) => ({
      ...clause,
      policy_version_id: policyVersion.policy_version_id,
      policy_type: policyVersion.policy_type,
      version: policyVersion.version,
    })),
  );
}

export default function TermsAcceptanceFlow({
  title = "Aceite de Termos",
  description = "Para continuar usando o sistema, leia e aceite as cláusulas obrigatórias vigentes.",
  acceptLabel = "Aceitar e continuar",
  declineLabel = "Recusar e sair",
  onAccept,
  onDecline,
  submitting = false,
  initialPendingClauses = [],
}) {
  const mandatoryContainerRef = useRef(null);

  const [terms, setTerms] = useState([]);
  const [pendingClauses, setPendingClauses] = useState(initialPendingClauses);
  const [selectedOptionalIds, setSelectedOptionalIds] = useState(new Set());
  const [hasReadMandatory, setHasReadMandatory] = useState(false);
  const [loading, setLoading] = useState(true);

  const allClauses = useMemo(() => flattenTerms(terms), [terms]);

  const allMandatoryClauses = useMemo(
    () => allClauses.filter((clause) => clause.mandatory),
    [allClauses],
  );

  const optionalClauses = useMemo(
    () => allClauses.filter((clause) => !clause.mandatory),
    [allClauses],
  );

  const displayedMandatoryClauses = useMemo(() => {
    const pendingIds = new Set(
      pendingClauses.map((clause) => String(clause.clause_uuid)),
    );

    if (pendingIds.size === 0) {
      return allMandatoryClauses;
    }

    return allMandatoryClauses.filter((clause) =>
      pendingIds.has(String(clause.clause_uuid)),
    );
  }, [allMandatoryClauses, pendingClauses]);

  useEffect(() => {
    let active = true;

    async function loadData() {
      try {
        setLoading(true);

        const [termsResponse, pendingResponse] = await Promise.all([
          getTerms(),
          getPendingConsent().catch(() => ({ pending_clauses: [] })),
        ]);

        if (!active) return;

        setTerms(termsResponse.terms || []);
        setPendingClauses(pendingResponse.pending_clauses || []);
      } catch (error) {
        toast.error("Não foi possível carregar os termos.");
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadData();

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    setSelectedOptionalIds(new Set());
  }, [terms]);

  useEffect(() => {
    const element = mandatoryContainerRef.current;

    if (!element || displayedMandatoryClauses.length === 0) {
      setHasReadMandatory(true);
      return;
    }

    const doesNotNeedScroll = element.scrollHeight <= element.clientHeight + 8;
    setHasReadMandatory(doesNotNeedScroll);
  }, [displayedMandatoryClauses.length, loading]);

  function handleMandatoryScroll(event) {
    const element = event.currentTarget;
    const reachedBottom =
      element.scrollTop + element.clientHeight >= element.scrollHeight - 8;

    if (reachedBottom) {
      setHasReadMandatory(true);
    }
  }

  function toggleOptionalClause(clauseUuid) {
    setSelectedOptionalIds((current) => {
      const next = new Set(current);

      if (next.has(clauseUuid)) {
        next.delete(clauseUuid);
      } else {
        next.add(clauseUuid);
      }

      return next;
    });
  }

  function handleAcceptClick() {
    if (!hasReadMandatory || submitting) return;

    onAccept?.({
      mandatoryClauses: allMandatoryClauses,
      displayedMandatoryClauses,
      optionalClauses,
      selectedOptionalIds,
    });
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center gap-2 p-8 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" />
        <span>Carregando termos...</span>
      </div>
    );
  }

  return (
    <section className="w-full max-w-4xl mx-auto bg-card border border-border rounded-xl shadow-sm">
      <div className="p-6 border-b border-border">
        <div className="flex items-start gap-3">
          <div className="rounded-full bg-primary/10 p-2">
            <ShieldCheck className="h-6 w-6 text-primary" />
          </div>

          <div>
            <h1 className="text-2xl font-semibold text-foreground">{title}</h1>
            <p className="mt-1 text-sm text-muted-foreground">{description}</p>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {displayedMandatoryClauses.length > 0 ? (
          <div>
            <div className="flex items-center justify-between gap-4 mb-3">
              <h2 className="text-base font-semibold text-foreground">
                Cláusulas obrigatórias
              </h2>

              {hasReadMandatory ? (
                <span className="inline-flex items-center gap-1 text-xs font-medium text-green-600">
                  <CheckCircle2 className="h-4 w-4" />
                  Leitura concluída
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 text-xs font-medium text-amber-600">
                  <AlertTriangle className="h-4 w-4" />
                  Role até o final para liberar o aceite
                </span>
              )}
            </div>

            <div
              ref={mandatoryContainerRef}
              onScroll={handleMandatoryScroll}
              className="max-h-80 overflow-y-auto rounded-lg border border-border bg-background p-4 space-y-4"
            >
              {displayedMandatoryClauses.map((clause) => (
                <article
                  key={clause.clause_uuid}
                  className="rounded-lg border border-border bg-card p-4"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-xs uppercase tracking-wide text-muted-foreground">
                        {clause.policy_type} · versão {clause.version}
                      </p>

                      <h3 className="mt-1 font-semibold text-foreground">
                        {clause.title}
                      </h3>
                    </div>

                    <span className="rounded-full bg-destructive/10 px-2 py-1 text-xs font-medium text-destructive">
                      Obrigatória
                    </span>
                  </div>

                  <p className="mt-3 whitespace-pre-line text-sm leading-6 text-muted-foreground">
                    {clause.description || "Sem descrição informada."}
                  </p>
                </article>
              ))}
            </div>
          </div>
        ) : (
          <div className="rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-700">
            Não há cláusulas obrigatórias pendentes.
          </div>
        )}

        {optionalClauses.length > 0 && (
          <div>
            <h2 className="mb-3 text-base font-semibold text-foreground">
              Cláusulas opcionais
            </h2>

            <div className="space-y-3">
              {optionalClauses.map((clause) => (
                <label
                  key={clause.clause_uuid}
                  className="flex cursor-pointer gap-3 rounded-lg border border-border p-4 hover:bg-muted/50"
                >
                  <input
                    type="checkbox"
                    className="mt-1 h-4 w-4"
                    checked={selectedOptionalIds.has(clause.clause_uuid)}
                    onChange={() => toggleOptionalClause(clause.clause_uuid)}
                  />

                  <span>
                    <span className="block text-sm font-semibold text-foreground">
                      {clause.title}
                    </span>

                    <span className="mt-1 block text-sm leading-6 text-muted-foreground">
                      {clause.description || "Sem descrição informada."}
                    </span>
                  </span>
                </label>
              ))}
            </div>
          </div>
        )}

        <div className="flex flex-col-reverse gap-3 border-t border-border pt-6 sm:flex-row sm:justify-end">
          <button
            type="button"
            onClick={onDecline}
            disabled={submitting}
            className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-foreground hover:bg-muted disabled:opacity-60"
          >
            {declineLabel}
          </button>

          <button
            type="button"
            onClick={handleAcceptClick}
            disabled={!hasReadMandatory || submitting}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {submitting && <Loader2 className="h-4 w-4 animate-spin" />}
            {acceptLabel}
          </button>
        </div>
      </div>
    </section>
  );
}