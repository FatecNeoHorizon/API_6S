import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

import TermsAcceptanceFlow from "../../components/consent/TermsAcceptanceFlow";
import { logoutUser } from "../../api/consent";

export default function ConsentPage() {
  const navigate = useNavigate();

  async function handleDecline() {
    await logoutUser();
    toast.info("Sessão encerrada.");

    navigate("/login", { replace: true });
  }

  function handleAccept() {
    toast.info("O envio do aceite será implementado na subtarefa #185.");
  }

  return (
    <main className="min-h-screen bg-background px-4 py-8">
      <TermsAcceptanceFlow
        title="Aceite de Termos"
        description="Leia as cláusulas obrigatórias até o final para liberar o botão de aceite."
        acceptLabel="Aceitar e continuar"
        declineLabel="Recusar e sair"
        onAccept={handleAccept}
        onDecline={handleDecline}
      />
    </main>
  );
}