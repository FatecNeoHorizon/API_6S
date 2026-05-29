import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  CheckCircle2,
  Loader2,
  RotateCcw,
  ShieldCheck,
  ShieldOff,
} from "lucide-react";
import { toast } from "sonner";

import {
  getMyConsentPreferences,
  getMyProfile,
  updateMyConsentPreferences,
} from "@/api/profile";
import { clearClientSession } from "@/api/consent";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

function formatPolicyType(policyType) {
  if (policyType === "TERMS_OF_USE") return "Termos de Uso";
  if (policyType === "PRIVACY_POLICY") return "Política de Privacidade";
  return String(policyType || "Documento").replaceAll("_", " ");
}

function formatDateTime(value) {
  if (!value) return "Sem registro";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(date);
}

function getStatusLabel(consent) {
  if (consent.accepted) return "Aceito";
  if (consent.current_status === "PENDING") return "Pendente";
  return "Revogado";
}

function ConfirmationModal({
  pendingChange,
  confirmationText,
  saving,
  onCancel,
  onConfirm,
  onConfirmationTextChange,
}) {
  if (!pendingChange) return null;

  const isMandatoryRevocation =
    pendingChange.mandatory && pendingChange.nextAccepted === false;

  const canConfirm = !isMandatoryRevocation || confirmationText === "DELETE";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 px-4 backdrop-blur-sm">
      <div className="w-full max-w-lg rounded-xl border border-border bg-card p-6 shadow-lg">
        <div className="flex items-start gap-3">
          <div
            className={
              isMandatoryRevocation
                ? "rounded-full bg-destructive/10 p-2 text-destructive"
                : "rounded-full bg-primary/10 p-2 text-primary"
            }
          >
            {isMandatoryRevocation ? (
              <AlertTriangle className="h-5 w-5" />
            ) : (
              <ShieldCheck className="h-5 w-5" />
            )}
          </div>

          <div>
            <h3 className="text-lg font-semibold text-foreground">
              {isMandatoryRevocation
                ? "Revogação de consentimento obrigatório"
                : "Confirmar alteração de consentimento"}
            </h3>
            <p className="mt-1 text-sm text-muted-foreground">
              {pendingChange.clause_title}
            </p>
          </div>
        </div>

        {isMandatoryRevocation ? (
          <div className="mt-5 rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm text-foreground">
            <p className="font-semibold text-destructive">
              Esta ação excluirá ou anonimizará permanentemente sua conta.
            </p>
            <ul className="mt-3 list-disc space-y-1 pl-5 text-muted-foreground">
              <li>Sua conta e seus dados pessoais serão removidos ou anonimizados permanentemente.</li>
              <li>Esta ação não poderá ser desfeita.</li>
              <li>Seu acesso de sessão será removido imediatamente.</li>
            </ul>

            <label className="mt-4 block text-xs font-medium text-foreground">
              Digite DELETE para confirmar
            </label>
            <Input
              className="mt-2"
              value={confirmationText}
              onChange={(event) => onConfirmationTextChange(event.target.value)}
              placeholder="DELETE"
              disabled={saving}
            />
          </div>
        ) : (
          <p className="mt-5 text-sm leading-6 text-muted-foreground">
            Esta ação registrará um novo evento de consentimento como{" "}
            <strong className="text-foreground">
              {pendingChange.nextAccepted ? "aceito" : "revogado"}
            </strong>
            . Os registros anteriores de consentimento não serão alterados.
          </p>
        )}

        <div className="mt-6 flex justify-end gap-3">
          <Button type="button" variant="outline" onClick={onCancel} disabled={saving}>
            Cancelar
          </Button>
          <Button
            type="button"
            variant={isMandatoryRevocation ? "destructive" : "default"}
            onClick={onConfirm}
            disabled={saving || !canConfirm}
          >
            {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            {isMandatoryRevocation ? "Confirmar exclusão" : "Confirmar alteração"}
          </Button>
        </div>
      </div>
    </div>
  );
}

export default function ConsentManagementPage() {
  const navigate = useNavigate();

  const [profile, setProfile] = useState(null);
  const [consents, setConsents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [loadError, setLoadError] = useState("");
  const [pendingChange, setPendingChange] = useState(null);
  const [confirmationText, setConfirmationText] = useState("");

  async function loadData() {
    setLoading(true);
    setLoadError("");

    try {
      const profileData = await getMyProfile();
      const consentData = await getMyConsentPreferences(profileData.user_uuid);

      setProfile(profileData);
      setConsents(consentData.consents || []);
    } catch {
      setLoadError("Não foi possível carregar suas preferências de consentimento.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const groupedConsents = useMemo(() => {
    return consents.reduce((groups, consent) => {
      const key = `${consent.policy_type}-${consent.policy_version}`;
      if (!groups[key]) {
        groups[key] = {
          policy_type: consent.policy_type,
          policy_version: consent.policy_version,
          items: [],
        };
      }
      groups[key].items.push(consent);
      return groups;
    }, {});
  }, [consents]);

  function requestConsentChange(consent, nextAccepted) {
    setPendingChange({
      ...consent,
      nextAccepted,
    });
    setConfirmationText("");
  }

  function cancelPendingChange() {
    setPendingChange(null);
    setConfirmationText("");
  }

  async function confirmPendingChange() {
    if (!pendingChange || !profile?.user_uuid) return;

    setSaving(true);

    try {
      const response = await updateMyConsentPreferences(profile.user_uuid, [
        {
          clause_id: pendingChange.clause_id,
          accepted: pendingChange.nextAccepted,
        },
      ]);

      if (response.account_deleted) {
        clearClientSession();
        navigate("/goodbye", { replace: true });
        return;
      }

      setConsents(response.consents || []);
      setPendingChange(null);
      setConfirmationText("");
      toast.success("Preferência de consentimento atualizada.");
    } catch {
      toast.error("Não foi possível atualizar a preferência de consentimento.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-[360px] items-center justify-center">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span className="text-sm">Carregando preferências de consentimento...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6">
      <div>
        <h2 className="text-2xl font-semibold text-foreground">
          Gerenciamento de Consentimentos
        </h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Revise, aceite ou revogue cláusulas de consentimento individualmente a qualquer momento.
        </p>
      </div>

      {loadError ? (
        <div className="rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive">
          {loadError}
        </div>
      ) : null}

      <Card className="rounded-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-primary" />
            Preferências atuais de consentimento
          </CardTitle>
          <CardDescription>
            Cada alteração cria um novo registro imutável no histórico de consentimentos.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {Object.values(groupedConsents).length === 0 ? (
            <div className="rounded-lg border border-border bg-muted/20 px-4 py-6 text-center text-sm text-muted-foreground">
              Nenhuma cláusula de consentimento atual foi encontrada.
            </div>
          ) : (
            Object.values(groupedConsents).map((group) => (
              <section key={`${group.policy_type}-${group.policy_version}`} className="space-y-3">
                <div>
                  <h3 className="text-base font-semibold text-foreground">
                    {formatPolicyType(group.policy_type)}
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    Versão {group.policy_version}
                  </p>
                </div>

                <div className="space-y-3">
                  {group.items.map((consent) => {
                    const statusLabel = getStatusLabel(consent);

                    return (
                      <div
                        key={consent.clause_id}
                        className="rounded-lg border border-border bg-background p-4"
                      >
                        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                          <div className="min-w-0 flex-1">
                            <div className="flex flex-wrap items-center gap-2">
                              <h4 className="font-medium text-foreground">
                                {consent.clause_title}
                              </h4>
                              <span
                                className={
                                  consent.mandatory
                                    ? "rounded-full bg-destructive/10 px-2 py-1 text-xs font-medium text-destructive"
                                    : "rounded-full bg-primary/10 px-2 py-1 text-xs font-medium text-primary"
                                }
                              >
                                {consent.mandatory ? "Obrigatório" : "Opcional"}
                              </span>
                              <span
                                className={
                                  consent.accepted
                                    ? "inline-flex items-center gap-1 rounded-full bg-chart-1/10 px-2 py-1 text-xs font-medium text-chart-1"
                                    : "inline-flex items-center gap-1 rounded-full bg-muted px-2 py-1 text-xs font-medium text-muted-foreground"
                                }
                              >
                                {consent.accepted ? (
                                  <CheckCircle2 className="h-3 w-3" />
                                ) : (
                                  <ShieldOff className="h-3 w-3" />
                                )}
                                {statusLabel}
                              </span>
                            </div>

                            {consent.clause_description ? (
                              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                                {consent.clause_description}
                              </p>
                            ) : null}

                            <p className="mt-3 text-xs text-muted-foreground">
                              Última ação: {formatDateTime(consent.last_action_at)}
                            </p>
                          </div>

                          <div className="flex shrink-0 gap-2">
                            <Button
                              type="button"
                              size="sm"
                              variant={consent.accepted ? "outline" : "default"}
                              disabled={saving || consent.accepted}
                              onClick={() => requestConsentChange(consent, true)}
                            >
                              Aceitar
                            </Button>
                            <Button
                              type="button"
                              size="sm"
                              variant={consent.accepted ? "destructive" : "outline"}
                              disabled={saving || !consent.accepted}
                              onClick={() => requestConsentChange(consent, false)}
                            >
                              Revogar
                            </Button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </section>
            ))
          )}
        </CardContent>
      </Card>

      <Button
        type="button"
        variant="outline"
        className="w-fit"
        onClick={loadData}
        disabled={loading || saving}
      >
        <RotateCcw className="h-4 w-4" />
        Recarregar preferências
      </Button>

      <ConfirmationModal
        pendingChange={pendingChange}
        confirmationText={confirmationText}
        saving={saving}
        onCancel={cancelPendingChange}
        onConfirm={confirmPendingChange}
        onConfirmationTextChange={setConfirmationText}
      />
    </div>
  );
}
