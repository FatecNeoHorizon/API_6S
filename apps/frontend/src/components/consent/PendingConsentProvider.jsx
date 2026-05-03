import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import PropTypes from "prop-types";
import { toast } from "sonner";

import { getTerms } from "@/api/terms";
import { getPendingConsent, submitConsent } from "@/api/consent";
import { registerPendingConsentHandler } from "@/api/pendingConsentInterceptor";
import ConsentFlowStep from "@/components/consent/ConsentFlowStep";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

function flattenTerms(terms) {
  return terms.flatMap((policyVersion) =>
    (policyVersion.clauses || []).map((clause) => ({
      ...clause,
      policy_version_id: policyVersion.policy_version_id,
      policy_type: policyVersion.policy_type,
      version: policyVersion.version,
      content: policyVersion.content,
    })),
  );
}

function buildConsentActions(terms, selectedClauseIds) {
  return flattenTerms(terms)
    .filter((clause) => selectedClauseIds.has(String(clause.clause_uuid)))
    .map((clause) => ({
      clause_uuid: clause.clause_uuid,
      policy_version_id: clause.policy_version_id,
      action: "CONSENT",
    }));
}

export default function PendingConsentProvider({ children }) {
  const [isOpen, setIsOpen] = useState(false);
  const [terms, setTerms] = useState([]);
  const [pendingClauses, setPendingClauses] = useState([]);
  const [selectedClauseIds, setSelectedClauseIds] = useState(() => new Set());
  const [expandedVersionIds, setExpandedVersionIds] = useState(() => new Set());
  const [loadingTerms, setLoadingTerms] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [submittingConsent, setSubmittingConsent] = useState(false);
  const [submissionError, setSubmissionError] = useState("");

  const pendingPromiseRef = useRef(null);
  const pendingResolveRef = useRef(null);
  const pendingRejectRef = useRef(null);

  const allClauses = useMemo(() => flattenTerms(terms), [terms]);
  const pendingClauseIds = useMemo(
    () => new Set(pendingClauses.map((clause) => String(clause.clause_uuid))),
    [pendingClauses],
  );
  const allClausesAccepted =
    allClauses.length > 0 &&
    allClauses
      .filter((clause) => clause.mandatory)
      .every((clause) => selectedClauseIds.has(String(clause.clause_uuid)));

  const fetchTermsAndConsentData = useCallback(async () => {
    try {
      setLoadingTerms(true);
      setLoadError("");
      setSubmissionError("");

      const [termsResponse, pendingResponse] = await Promise.all([
        getTerms(),
        getPendingConsent().catch(() => ({ pending_clauses: [] })),
      ]);

      const nextTerms = termsResponse.terms || [];
      setTerms(nextTerms);
      setPendingClauses(pendingResponse.pending_clauses || []);

      if (nextTerms.length > 0) {
        setExpandedVersionIds(new Set([String(nextTerms[0].policy_version_id)]));
      }
    } catch {
      setLoadError("Não foi possível carregar os termos.");
    } finally {
      setLoadingTerms(false);
    }
  }, []);

  const openPendingConsentModal = useCallback(async () => {
    if (pendingPromiseRef.current) {
      return pendingPromiseRef.current;
    }

    setSelectedClauseIds(new Set());
    setExpandedVersionIds(new Set());
    setSubmissionError("");
    setIsOpen(true);

    fetchTermsAndConsentData();

    const pendingPromise = new Promise((resolve, reject) => {
      pendingResolveRef.current = resolve;
      pendingRejectRef.current = reject;
    }).finally(() => {
      pendingPromiseRef.current = null;
      pendingResolveRef.current = null;
      pendingRejectRef.current = null;
    });

    pendingPromiseRef.current = pendingPromise;
    return pendingPromise;
  }, [fetchTermsAndConsentData]);

  useEffect(() => {
    const unregister = registerPendingConsentHandler(openPendingConsentModal);

    return () => {
      unregister();
    };
  }, [openPendingConsentModal]);

  useEffect(() => {
    return () => {
      if (pendingRejectRef.current) {
        pendingRejectRef.current(new Error("pending_consent_unmounted"));
      }
    };
  }, []);

  function toggleClause(clauseUuid) {
    setSelectedClauseIds((current) => {
      const next = new Set(current);

      if (next.has(clauseUuid)) {
        next.delete(clauseUuid);
      } else {
        next.add(clauseUuid);
      }

      return next;
    });
  }

  function toggleVersion(versionId) {
    setExpandedVersionIds((current) => {
      const next = new Set(current);

      if (next.has(versionId)) {
        next.delete(versionId);
      } else {
        next.add(versionId);
      }

      return next;
    });
  }

  async function handleSubmit() {
    if (!allClausesAccepted || loadingTerms || submittingConsent || loadError) {
      return;
    }

    try {
      setSubmittingConsent(true);
      setSubmissionError("");

      const actions = buildConsentActions(terms, selectedClauseIds);
      await submitConsent(actions);

      setIsOpen(false);
      pendingResolveRef.current?.();
      toast.success("Termos aceitos com sucesso.");
    } catch {
      setSubmissionError("Não foi possível concluir o consentimento.");
      toast.error("Não foi possível concluir o consentimento.");
    } finally {
      setSubmittingConsent(false);
    }
  }

  return (
    <>
      {children}

      {isOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/90 p-4 backdrop-blur-sm">
          <Card className="max-h-[90vh] w-full max-w-3xl overflow-y-auto border-border bg-card">
            <CardHeader>
              <CardTitle>Consentimento pendente</CardTitle>
              <CardDescription>
                Sua sessão continua ativa. Aceite os termos pendentes para seguir no sistema.
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
              {submissionError ? (
                <div className="rounded-xl border border-destructive/20 bg-destructive/10 p-4 text-sm text-destructive">
                  {submissionError}
                </div>
              ) : null}

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
                onRetry={fetchTermsAndConsentData}
                onToggleClause={toggleClause}
                onToggleVersion={toggleVersion}
                onSubmit={handleSubmit}
                submitLabel="Aceitar termos"
              />
            </CardContent>
          </Card>
        </div>
      ) : null}
    </>
  );
}

PendingConsentProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
