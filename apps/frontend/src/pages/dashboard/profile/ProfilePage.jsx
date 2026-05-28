import { Link } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import { AlertCircle, CheckCircle2, Download, Loader2, Mail, Save, Shield, ShieldCheck, Trash2, User } from "lucide-react";
import { toast } from "sonner";

import { exportMyData, getMyProfile, updateMyProfile } from "@/api/profile";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const dpoContact = {
  name: "Encarregado pelo Tratamento de Dados Pessoais",
  email: "dpo@tecsys.com.br",
  response_time: "Até 15 dias úteis, conforme LGPD Art. 18, §4",
};

function getApiErrorMessage(error, fallbackMessage) {
  const detail = error?.response?.data?.detail ?? error?.detail ?? error?.data?.detail;

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (Array.isArray(detail) && detail.length > 0) {
    const firstDetail = detail[0];

    if (typeof firstDetail === "string" && firstDetail.trim()) {
      return firstDetail;
    }

    if (typeof firstDetail?.msg === "string" && firstDetail.msg.trim()) {
      return firstDetail.msg;
    }
  }

  return fallbackMessage;
}

function formatDateTime(value) {
  if (!value) return "-";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(date);
}

export default function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const [form, setForm] = useState({ username: "", email: "" });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;

    async function loadProfile() {
      setIsLoading(true);
      setError("");

      try {
        const data = await getMyProfile();

        if (!mounted) return;

        setProfile(data);
        setForm({
          username: data.username || "",
          email: data.email || "",
        });
      } catch (err) {
        if (!mounted) return;
        setError(getApiErrorMessage(err, "Nao foi possivel carregar seu perfil."));
      } finally {
        if (mounted) setIsLoading(false);
      }
    }

    loadProfile();

    return () => {
      mounted = false;
    };
  }, []);

  const hasChanges = useMemo(() => {
    if (!profile) return false;

    return (
      form.username.trim() !== profile.username ||
      form.email.trim().toLowerCase() !== profile.email
    );
  }, [form.email, form.username, profile]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const data = await exportMyData();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "my-data-export.json";
      link.click();
      URL.revokeObjectURL(url);
      toast.success("Exportacao concluida.");
    } catch {
      toast.error("Nao foi possivel exportar seus dados. Tente novamente.");
    } finally {
      setIsExporting(false);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    const username = form.username.trim();
    const email = form.email.trim().toLowerCase();

    if (username.length < 3) {
      setError("Informe um nome com pelo menos 3 caracteres.");
      return;
    }

    if (!emailPattern.test(email)) {
      setError("Informe um email valido.");
      return;
    }

    setIsSaving(true);

    try {
      const updated = await updateMyProfile({ username, email });
      setProfile(updated);
      setForm({
        username: updated.username || "",
        email: updated.email || "",
      });
      window.dispatchEvent(new CustomEvent("profile:updated", { detail: updated }));
      toast.success("Perfil atualizado com sucesso.");
    } catch (err) {
      setError(getApiErrorMessage(err, "Nao foi possivel atualizar seu perfil."));
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-[360px] items-center justify-center">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span className="text-sm">Carregando perfil...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col gap-6">
      <div>
        <h2 className="text-2xl font-semibold text-foreground">Meu Perfil</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Consulte e atualize suas informacoes pessoais.
        </p>
      </div>

      {error ? (
        <div className="flex items-start gap-2 rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
        <Card className="rounded-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5 text-primary" />
              Dados pessoais
            </CardTitle>
            <CardDescription>
              Essas informacoes sao utilizadas para identificacao na plataforma.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground" htmlFor="username">
                  Nome de usuario
                </label>
                <Input
                  id="username"
                  name="username"
                  value={form.username}
                  onChange={handleChange}
                  placeholder="Seu nome"
                  disabled={isSaving}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground" htmlFor="email">
                  Email
                </label>
                <div className="relative">
                  <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="voce@email.com"
                    className="pl-9"
                    disabled={isSaving}
                  />
                </div>
              </div>

              <div className="flex justify-end">
                <Button
                  type="submit"
                  disabled={!hasChanges || isSaving}
                  className="min-w-36"
                >
                  {isSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                  {isSaving ? "Salvando..." : "Salvar alteracoes"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        <aside className="flex flex-col gap-4">
          <Card className="rounded-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Shield className="h-4 w-4 text-primary" />
                Acesso
              </CardTitle>
              <CardDescription>Estado atual da conta</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-3 text-sm">
              <div className="flex items-center justify-between gap-3">
                <span className="text-muted-foreground">Status</span>
                <span className="inline-flex items-center gap-1 rounded-full bg-chart-1/10 px-2 py-1 text-xs font-medium text-chart-1">
                  <CheckCircle2 className="h-3 w-3" />
                  {profile?.active ? "Ativo" : "Inativo"}
                </span>
              </div>
              <div className="flex items-center justify-between gap-3">
                <span className="text-muted-foreground">Perfil</span>
                <span className="rounded-full bg-primary/10 px-2 py-1 text-xs font-medium text-primary">
                  {profile?.profile_name || "-"}
                </span>
              </div>
              <div className="border-t border-border pt-3">
                <p className="text-xs text-muted-foreground">Criado em</p>
                <p className="mt-1 font-medium text-foreground">{formatDateTime(profile?.created_at)}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Ultima atualizacao</p>
                <p className="mt-1 font-medium text-foreground">{formatDateTime(profile?.updated_at)}</p>
              </div>
            </CardContent>
          </Card>

          <Card className="rounded-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <ShieldCheck className="h-4 w-4 text-primary" />
                Consentimentos
              </CardTitle>
              <CardDescription>
                Revise ou altere seus consentimentos individualmente a qualquer momento.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button asChild variant="outline" className="w-full border-border text-foreground hover:bg-muted">
                <Link to="/dashboard/consentimentos">
                  <ShieldCheck className="h-4 w-4" />
                  Gerenciar consentimentos
                </Link>
              </Button>
            </CardContent>
          </Card>

          <Card className="rounded-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Download className="h-4 w-4 text-primary" />
                Portabilidade de dados
              </CardTitle>
              <CardDescription>
                Exporte todos os seus dados pessoais armazenados na plataforma (LGPD Art. 18-V).
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                type="button"
                variant="outline"
                className="w-full border-border text-foreground hover:bg-muted hover:text-foreground disabled:opacity-60"
                onClick={handleExport}
                disabled={isExporting}
              >
                {isExporting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
                {isExporting ? "Exportando..." : "Exportar meus dados"}
              </Button>
            </CardContent>
          </Card>

          <Card className="rounded-lg border-destructive/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base text-destructive">
                <Trash2 className="h-4 w-4" />
                Exclusao da conta
              </CardTitle>
              <CardDescription>
                Acao reservada para a proxima etapa do fluxo de LGPD.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                type="button"
                variant="destructive"
                className="w-full"
                disabled
                title="Funcionalidade ainda nao implementada"
              >
                <Trash2 className="h-4 w-4" />
                Solicitar exclusao
              </Button>
            </CardContent>
          </Card>

          <div className="rounded-lg border border-border bg-muted/20 px-4 py-3 text-xs text-muted-foreground">
            <p className="font-medium text-foreground">Encarregado de Dados</p>
            <p className="mt-1">
              {dpoContact.name} ·{" "}
              <a className="font-medium text-primary hover:underline" href={`mailto:${dpoContact.email}`}>
                {dpoContact.email}
              </a>
            </p>
            <p className="mt-1">{dpoContact.response_time}</p>
          </div>
        </aside>
      </div>
    </div>
  );
}