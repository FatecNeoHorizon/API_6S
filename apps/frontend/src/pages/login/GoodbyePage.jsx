import { Link } from "react-router-dom";
import { ShieldAlert } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function GoodbyePage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-lg rounded-xl border border-border bg-card p-8 text-center shadow-sm">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10">
          <ShieldAlert className="h-6 w-6 text-destructive" />
        </div>

        <h1 className="text-2xl font-semibold text-foreground">
          Acesso à conta encerrado
        </h1>

        <p className="mt-3 text-sm leading-6 text-muted-foreground">
          Seu consentimento obrigatório foi revogado. Sua conta foi anonimizada
          e todas as sessões ativas foram invalidadas conforme o fluxo de
          gerenciamento de consentimentos da LGPD.
        </p>

        <Button asChild className="mt-6">
          <Link to="/login">Voltar ao login</Link>
        </Button>
      </div>
    </div>
  );
}
