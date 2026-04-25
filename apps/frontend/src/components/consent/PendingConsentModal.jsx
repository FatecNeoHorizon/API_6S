import { useState } from "react";
import { X } from "lucide-react";
import { toast } from "sonner";

import TermsAcceptanceFlow from "./TermsAcceptanceFlow";
import { logoutUser, postConsent } from "../../api/consent";
import { buildConsentActions } from "../../utils/consentActions";

export default function PendingConsentModal({
  open,
  pendingClauses = [],
  onResolved,
}) {
  const [submitting, setSubmitting] = useState(false);

  if (!open) {
    return null;
  }

  async function handleDecline() {
    await logoutUser();
    toast.info("Sessão encerrada.");

    window.location.replace("/login");
  }

  async function handleAccept({
    mandatoryClauses,
    optionalClauses,
    selectedOptionalIds,
  }) {
    try {
      setSubmitting(true);

      const actions = buildConsentActions({
        mandatoryClauses,
        optionalClauses,
        selectedOptionalIds,
      });

      await postConsent(actions);

      toast.success("Termos aceitos com sucesso.");
      onResolved?.();
    } catch (error) {
      const detail = error?.payload?.detail;

      if (detail?.code === "missing_mandatory_clauses") {
        toast.error("Ainda existem cláusulas obrigatórias pendentes.");
        return;
      }

      toast.error("Não foi possível registrar o aceite dos termos.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 px-4 py-6 backdrop-blur-sm">
      <div className="relative max-h-[92vh] w-full max-w-5xl overflow-y-auto rounded-xl bg-background shadow-xl">
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-border bg-background px-5 py-4">
          <div>
            <h2 className="text-lg font-semibold text-foreground">
              Aceite obrigatório de termos
            </h2>
            <p className="text-sm text-muted-foreground">
              Para continuar usando o sistema, aceite as cláusulas obrigatórias.
            </p>
          </div>

          <button
            type="button"
            onClick={handleDecline}
            className="rounded-lg p-2 text-muted-foreground hover:bg-muted hover:text-foreground"
            aria-label="Recusar termos e sair"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="p-5">
          <TermsAcceptanceFlow
            title="Termos pendentes"
            description="Sua sessão continua ativa, mas o acesso ao sistema ficará bloqueado até o aceite das cláusulas obrigatórias."
            acceptLabel="Aceitar e continuar"
            declineLabel="Recusar e sair"
            submitting={submitting}
            initialPendingClauses={pendingClauses}
            onAccept={handleAccept}
            onDecline={handleDecline}
          />
        </div>
      </div>
    </div>
  );
}