import { useEffect, useState } from "react";
import { AlertTriangle, Loader2, Send, ShieldAlert } from "lucide-react";
import { toast } from "sonner";
import { getTemplates, sendNotification } from "@/api/incidentNotification";
import { cn } from "@/utils/utils";

function ConfirmModal({ open, templateName, onConfirm, onCancel, loading }) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-card border border-border rounded-xl shadow-2xl w-full max-w-md p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-full bg-destructive/10 flex items-center justify-center shrink-0">
            <AlertTriangle className="w-5 h-5 text-destructive" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-foreground">Confirmar envio</h2>
            <p className="text-sm text-muted-foreground">Esta ação não pode ser desfeita.</p>
          </div>
        </div>

        <p className="text-sm text-foreground mb-2">
          Você está prestes a enviar o template{" "}
          <span className="font-semibold">{templateName}</span> para{" "}
          <span className="font-semibold">todos os usuários ativos</span> da plataforma.
        </p>
        <p className="text-sm text-muted-foreground mb-6">
          O envio será processado em segundo plano.
        </p>

        <div className="flex gap-3">
          <button
            onClick={onCancel}
            disabled={loading}
            className="flex-1 px-4 py-2 text-sm font-medium text-foreground border border-border rounded-lg hover:bg-muted transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancelar
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            className="flex-1 px-4 py-2 text-sm font-medium bg-destructive text-destructive-foreground rounded-lg hover:bg-destructive/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            {loading ? "Enviando..." : "Confirmar envio"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function IncidentNotificationPage() {
  const [templates, setTemplates] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [loadingTemplates, setLoadingTemplates] = useState(true);
  const [sending, setSending] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);

  useEffect(() => {
    getTemplates()
      .then((data) => {
        setTemplates(data);
        if (data.length > 0) selectTemplate(data[0]);
      })
      .catch(() => toast.error("Falha ao carregar os templates."))
      .finally(() => setLoadingTemplates(false));
  }, []);

  function selectTemplate(tpl) {
    setSelectedId(tpl.template_id);
    setSubject(tpl.subject);
    setBody(tpl.body);
  }

  function handleTemplateClick(tpl) {
    if (tpl.template_id === selectedId) return;
    selectTemplate(tpl);
  }

  function handleSendClick() {
    if (!selectedId) return;
    setConfirmOpen(true);
  }

  async function handleConfirm() {
    setSending(true);
    const selected = templates.find((t) => t.template_id === selectedId);
    const payload = {
      template_id: selectedId,
      custom_subject: subject === selected?.subject ? undefined : subject,
      custom_body: body === selected?.body ? undefined : body,
    };

    try {
      const result = await sendNotification(payload);
      const plural = result.recipient_count === 1 ? "" : "s";
      toast.success(`Notificação agendada para ${result.recipient_count} usuário${plural}.`);
      setConfirmOpen(false);
    } catch {
      toast.error("Falha ao enviar a notificação. Tente novamente.");
    } finally {
      setSending(false);
    }
  }

  function handleCancelConfirm() {
    if (sending) return;
    setConfirmOpen(false);
  }

  const selectedTemplate = templates.find((t) => t.template_id === selectedId);
  const isBodyModified = selectedTemplate && body !== selectedTemplate.body;
  const isSubjectModified = selectedTemplate && subject !== selectedTemplate.subject;
  const isModified = isBodyModified || isSubjectModified;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Page header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-destructive/10 flex items-center justify-center shrink-0">
          <ShieldAlert className="w-5 h-5 text-destructive" />
        </div>
        <div>
          <h1 className="text-xl font-semibold text-foreground">Notificação de Incidente (LGPD Art. 48)</h1>
          <p className="text-sm text-muted-foreground">
            Envie comunicados de incidente de segurança a todos os usuários ativos.
          </p>
        </div>
      </div>

      {/* Template selector + editor */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Template list */}
        <div className="space-y-2">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide px-1">
            Templates disponíveis
          </p>
          {loadingTemplates ? (
            <div className="flex items-center gap-2 py-4 text-muted-foreground text-sm">
              <Loader2 className="w-4 h-4 animate-spin" />
              Carregando...
            </div>
          ) : (
            templates.map((tpl) => (
              <button
                key={tpl.template_id}
                onClick={() => handleTemplateClick(tpl)}
                className={cn(
                  "w-full text-left px-4 py-3 rounded-lg border text-sm transition-colors",
                  tpl.template_id === selectedId
                    ? "border-destructive/60 bg-destructive/5 text-foreground"
                    : "border-border bg-card text-foreground hover:bg-muted",
                )}
              >
                <span className="font-medium">{tpl.name}</span>
              </button>
            ))
          )}
        </div>

        {/* Editor */}
        <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between px-1">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Editar antes de enviar
            </p>
            {isModified && (
              <span className="text-xs text-amber-600 dark:text-amber-400 font-medium">
                Template modificado
              </span>
            )}
          </div>

          <div className="space-y-3 bg-card border border-border rounded-xl p-4">
            <div>
              <label
                htmlFor="notif-subject"
                className="block text-xs font-medium text-muted-foreground mb-1"
              >
                Assunto
              </label>
              <input
                id="notif-subject"
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                disabled={!selectedId}
                className="w-full px-3 py-2 text-sm border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50 disabled:cursor-not-allowed"
              />
            </div>
            <div>
              <label
                htmlFor="notif-body"
                className="block text-xs font-medium text-muted-foreground mb-1"
              >
                Corpo da mensagem
              </label>
              <textarea
                id="notif-body"
                value={body}
                onChange={(e) => setBody(e.target.value)}
                disabled={!selectedId}
                rows={14}
                className="w-full px-3 py-2 text-sm border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50 disabled:cursor-not-allowed resize-y font-mono"
              />
            </div>

            <div className="flex justify-end pt-1">
              <button
                onClick={handleSendClick}
                disabled={!selectedId || sending}
                className="flex items-center gap-2 px-5 py-2.5 text-sm font-medium bg-destructive text-destructive-foreground rounded-lg hover:bg-destructive/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-4 h-4" />
                Enviar notificação
              </button>
            </div>
          </div>
        </div>
      </div>

      <ConfirmModal
        open={confirmOpen}
        templateName={selectedTemplate?.name ?? ""}
        onConfirm={handleConfirm}
        onCancel={handleCancelConfirm}
        loading={sending}
      />
    </div>
  );
}
