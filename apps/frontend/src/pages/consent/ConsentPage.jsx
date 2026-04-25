import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

import TermsAcceptanceFlow from "../../components/consent/TermsAcceptanceFlow";
import { logoutUser, postConsent } from "../../api/consent";
import { buildConsentActions } from "../../utils/consentActions";

export default function ConsentPage() {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);

  async function handleDecline() {
    await logoutUser();
    toast.info("Sessão encerrada.");

    navigate("/login", { replace: true });
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
      navigate("/dashboard/indicadores", { replace: true });
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
    <main className="min-h-screen bg-background px-4 py-8">
      <TermsAcceptanceFlow
        title="Aceite de Termos"
        description="Leia as cláusulas obrigatórias até o final para liberar o botão de aceite."
        acceptLabel="Aceitar e continuar"
        declineLabel="Recusar e sair"
        submitting={submitting}
        onAccept={handleAccept}
        onDecline={handleDecline}
      />
    </main>
  );
}