import { useState, useEffect } from "react";
import {
  Plus,
  Search,
  Loader2,
  FileText,
  Check,
  X,
  Clock,
  ChevronDown,
  AlertCircle,
  Eye,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { toast } from "sonner";
import { createTermsVersion, getAdminPolicyVersion, getAdminTermsVersions, getVersionClauses, createClause, getTerms } from "@/api/terms";

const DEFAULT_PAGE_SIZE = 5;
const PAGE_SIZE_OPTIONS = [5, 10, 25, 50];

const TermType = {
  PRIVACY_POLICY: "Política de Privacidade",
  TERMS_OF_USE: "Termos de Uso",
};

const StatusFilter = {
  all: "all",
  current: "current",
  scheduled: "scheduled",
  expired: "expired",
};

const PolicyTypeOptions = [
  { value: "PRIVACY_POLICY", label: "PRIVACY_POLICY" },
  { value: "TERMS_OF_USE", label: "TERMS_OF_USE" },
];

const normalizeTerm = (term) => ({
  policy_version_id: term.policy_version_id,
  version: term.version,
  policy_type: term.policy_type,
  effective_from: term.effective_from,
  created_at: term.created_at,
  clauses: term.clauses ?? [],
  content: term.content ?? "",
  clause_count: term.clause_count ?? term.clauses?.length ?? 0,
});

const getApiErrorMessage = (error, fallbackMessage) => {
  const detail =
    error?.response?.data?.detail ?? error?.detail ?? error?.data?.detail;

  if (typeof detail === "string" && detail.trim()) return detail;

  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0];
    if (typeof first === "string" && first.trim()) return first;
    if (typeof first?.msg === "string" && first.msg.trim()) return first.msg;
  }

  return fallbackMessage;
};

const toDatetimeLocalString = (date) => {
  const offsetInMs = date.getTimezoneOffset() * 60 * 1000;
  return new Date(date.getTime() - offsetInMs).toISOString().slice(0, 16);
};

const getStatus = (effectiveFrom, allVersionsOfSameType) => {
  const today = new Date();
  const date = new Date(effectiveFrom);

  if (date > today) {
    return {
      key: StatusFilter.scheduled,
      label: "Agendado",
      className: "bg-muted text-muted-foreground",
      icon: <Clock className="w-3 h-3" />,
    };
  }

  const isCurrent = !allVersionsOfSameType.some(
    (v) =>
      new Date(v.effective_from) > date &&
      new Date(v.effective_from) <= today
  );

  if (isCurrent) {
    return {
      key: StatusFilter.current,
      label: "Vigente",
      className: "bg-chart-1/10 text-chart-1",
      icon: <Check className="w-3 h-3" />,
    };
  }

  return {
    key: StatusFilter.expired,
    label: "Expirado",
    className: "bg-muted text-muted-foreground",
    icon: <X className="w-3 h-3" />,
  };
};

const buildPaginatedTermsResponse = ({ page, pageSize, searchTerm, statusFilter, sourceTerms }) => {
  const normalizedSearch = searchTerm.trim().toLowerCase();

  const filtered = sourceTerms.filter((term) => {
    const termTypeLabel = TermType[term.policy_type] || term.policy_type;
    const sameType = sourceTerms.filter((t) => t.policy_type === term.policy_type);
    const status = getStatus(term.effective_from, sameType);
    const matchesStatus = statusFilter === StatusFilter.all || status.key === statusFilter;

    const matchesSearch =
      termTypeLabel.toLowerCase().includes(normalizedSearch) ||
      term.version.toLowerCase().includes(normalizedSearch);

    return matchesSearch && matchesStatus;
  });

  const total = filtered.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const safePage = Math.min(Math.max(1, page), totalPages);
  const startIndex = (safePage - 1) * pageSize;

  return {
    data: filtered.slice(startIndex, startIndex + pageSize),
    meta: {
      page: safePage,
      pageSize,
      total,
      totalPages,
      hasNext: safePage < totalPages,
      hasPrev: safePage > 1,
    },
  };
};

export default function TermsPage() {
  const [allTerms, setAllTerms] = useState([]);
  const [termsPage, setTermsPage] = useState({ data: [], meta: {} });
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState(StatusFilter.all);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);
  const [openRowId, setOpenRowId] = useState(null);
  const [clausesByVersion, setClausesByVersion] = useState({});
  const [loadingClausesFor, setLoadingClausesFor] = useState(null);
  const [showAddClauseModal, setShowAddClauseModal] = useState(false);
  const [addClauseVersionId, setAddClauseVersionId] = useState(null);
  const [addClauseForm, setAddClauseForm] = useState({
    code: "",
    title: "",
    description: "",
    mandatory: false,
    display_order: 1,
  });
  const [isAddingClause, setIsAddingClause] = useState(false);
  const [addClauseError, setAddClauseError] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [isCreatingVersion, setIsCreatingVersion] = useState(false);
  const [createError, setCreateError] = useState("");
  const [createForm, setCreateForm] = useState({
    policy_type: "PRIVACY_POLICY",
    version: "",
    effective_from: "",
    content: "",
  });
  const [showViewContentModal, setShowViewContentModal] = useState(false);
  const [viewContentTitle, setViewContentTitle] = useState("");
  const [viewContentText, setViewContentText] = useState("");

  const [showViewClauseModal, setShowViewClauseModal] = useState(false);
  const [viewClause, setViewClause] = useState(null);
  const [showTempClauseForm, setShowTempClauseForm] = useState(false);
  const [tempClauses, setTempClauses] = useState([]);
  const [tempClauseForm, setTempClauseForm] = useState({
    code: "",
    title: "",
    description: "",
    mandatory: false,
    display_order: 1,
  });

  const loadTerms = async () => {
    setLoading(true);
    try {
      const response = await getAdminTermsVersions();
      const terms = response?.versions ?? response?.data?.versions ?? [];
      setAllTerms(terms.map(normalizeTerm));
    } catch (error) {
      if (!navigator.onLine || error instanceof TypeError) {
        toast.error("Sem conexão com a internet. Verifique sua rede e tente novamente.");
      } else if (error?.response?.status === 403 || error?.status === 403) {
        toast.error("Acesso negado. Você não tem permissão para visualizar estes dados.");
      } else {
        toast.error(getApiErrorMessage(error, "Erro ao carregar os termos. Tente novamente."));
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTerms();
  }, []);

  useEffect(() => {
    const response = buildPaginatedTermsResponse({
      page: currentPage,
      pageSize,
      searchTerm,
      statusFilter,
      sourceTerms: allTerms,
    });
    setTermsPage(response);

    if (response.meta.page !== currentPage) {
      setCurrentPage(response.meta.page);
    }
  }, [currentPage, pageSize, searchTerm, statusFilter, allTerms]);

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  const handleStatusFilterChange = (e) => {
    setStatusFilter(e.target.value);
    setCurrentPage(1);
  };

  const handlePageSizeChange = (e) => {
    setPageSize(Number(e.target.value));
    setCurrentPage(1);
  };

  const handleToggleRow = async (versionId) => {
    // Se a linha está aberta, fecha
    if (openRowId === versionId) {
      setOpenRowId(null);
      return;
    }

    // Abre a linha e carrega cláusulas se ainda não foram carregadas
    setOpenRowId(versionId);

    if (!clausesByVersion[versionId]) {
      setLoadingClausesFor(versionId);
      try {
        const response = await getVersionClauses(versionId);
        const clauses = response?.clauses ?? response?.data?.clauses ?? [];
        setClausesByVersion((prev) => ({
          ...prev,
          [versionId]: clauses,
        }));
      } catch (error) {
        toast.error(getApiErrorMessage(error, "Erro ao carregar cláusulas. Tente novamente."));
      } finally {
        setLoadingClausesFor(null);
      }
    }
  };

  const handleStatusCardClick = (nextStatus) => {
    setStatusFilter(nextStatus);
    setCurrentPage(1);
  };

  const handleOpenCreateModal = () => {
    setCreateForm({
      policy_type: "PRIVACY_POLICY",
      version: "",
      effective_from: "",
      content: "",
    });
    setCreateError("");
    setTempClauses([]);
    setShowTempClauseForm(false);
    setTempClauseForm({
      code: "",
      title: "",
      description: "",
      mandatory: false,
      display_order: 1,
    });
    setShowCreateModal(true);
  };

  const handleCloseCreateModal = () => {
    if (isCreatingVersion) return;

    setShowCreateModal(false);
    setCreateError("");
    setTempClauses([]);
    setShowTempClauseForm(false);
  };

  const handleCreateFormChange = (event) => {
    const { name, value } = event.target;
    setCreateError("");
    setCreateForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const openTempClauseForm = () => {
    setShowTempClauseForm(true);
  };

  const closeTempClauseForm = () => {
    setShowTempClauseForm(false);
    setTempClauseForm({
      code: "",
      title: "",
      description: "",
      mandatory: false,
      display_order: 1,
    });
  };

  const handleTempClauseFormChange = (event) => {
    const { name, value, type, checked } = event.target;
    let finalValue;

    if (type === "checkbox") {
      finalValue = checked;
    } else if (name === "display_order") {
      finalValue = Number.parseInt(value, 10) || 1;
    } else {
      finalValue = value;
    }

    setTempClauseForm((prev) => ({
      ...prev,
      [name]: finalValue,
    }));
  };

  const addTempClause = () => {
    const code = tempClauseForm.code.trim();
    const title = tempClauseForm.title.trim();
    const displayOrder = Math.max(1, tempClauseForm.display_order);

    if (!code || !title) {
      toast.error("Código e título são obrigatórios para a cláusula.");
      return;
    }

    setTempClauses((prev) => [
      ...prev,
      {
        ...tempClauseForm,
        code,
        title,
        display_order: displayOrder,
      },
    ]);
    closeTempClauseForm();
  };

  const removeTempClause = (index) => {
    setTempClauses((prev) => prev.filter((_, i) => i !== index));
  };

  const handleCreateVersion = async () => {
    const version = createForm.version.trim();
    const content = createForm.content.trim();
    const effectiveFrom = createForm.effective_from;
    const policyType = createForm.policy_type;

    if (!version || !policyType || !effectiveFrom || !content) {
      setCreateError("Preencha os campos obrigatórios.");
      return;
    }

    const parsedEffectiveFrom = new Date(effectiveFrom);

    if (Number.isNaN(parsedEffectiveFrom.getTime())) {
      setCreateError("Informe uma data de vigência válida.");
      return;
    }

    if (parsedEffectiveFrom <= new Date()) {
      setCreateError("A data de vigência precisa ser futura.");
      return;
    }

    setIsCreatingVersion(true);
    setCreateError("");

    try {
      const versionResponse = await createTermsVersion({
        version,
        policy_type: policyType,
        content,
        effective_from: parsedEffectiveFrom.toISOString(),
      });

      const createdVersionId = versionResponse?.policy_version_id || versionResponse?.data?.policy_version_id;

      if (tempClauses.length > 0 && createdVersionId) {
        const createClausePromises = tempClauses.map((clause) =>
          createClause(createdVersionId, {
            code: clause.code,
            title: clause.title,
            description: clause.description || null,
            mandatory: clause.mandatory,
            display_order: clause.display_order,
          })
        );
        await Promise.all(createClausePromises);
      }

      await loadTerms();
      setCurrentPage(1);
      setOpenRowId(null);
      setShowCreateModal(false);
      setTempClauses([]);
      toast.success("Nova versão criada com sucesso." + (tempClauses.length > 0 ? " Cláusulas adicionadas." : ""));
    } catch (error) {
      const status = error?.response?.status || error?.status;

      if (status === 409) {
        setCreateError(getApiErrorMessage(error, "Já existe uma versão com esse número e tipo."));
      } else if (status === 422) {
        setCreateError(getApiErrorMessage(error, "A data de vigência precisa ser futura."));
      } else {
        setCreateError(getApiErrorMessage(error, "Não foi possível criar a nova versão. Tente novamente."));
      }
    } finally {
      setIsCreatingVersion(false);
    }
  };

  // ---- Add Clause handlers (task 6.4.4) ----
  const openAddClauseModal = (versionId) => {
    setAddClauseVersionId(versionId);
    setAddClauseForm({ code: "", title: "", description: "", mandatory: false, display_order: 1 });
    setAddClauseError("");
    setShowAddClauseModal(true);
  };

  const closeAddClauseModal = () => {
    if (isAddingClause) return;
    setShowAddClauseModal(false);
    setAddClauseError("");
  };

  const handleAddClauseFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setAddClauseError("");
    setAddClauseForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleAddClauseSubmit = async () => {
    const { code, title, description, mandatory, display_order } = addClauseForm;

    if (!code.trim() || !title.trim() || !display_order) {
      setAddClauseError("Preencha código, título e ordem de exibição.");
      return;
    }

    const order = Number(display_order);
    if (Number.isNaN(order) || order < 1) {
      setAddClauseError("Ordem deve ser um número inteiro maior que zero.");
      return;
    }

    setIsAddingClause(true);
    setAddClauseError("");

    try {
      await createClause(addClauseVersionId, {
        code: code.trim(),
        title: title.trim(),
        description: description.trim() || null,
        mandatory: !!mandatory,
        display_order: order,
      });

      // reload clauses for this version
      const response = await getVersionClauses(addClauseVersionId);
      const clauses = response?.clauses ?? response?.data?.clauses ?? [];
      setClausesByVersion((prev) => ({ ...prev, [addClauseVersionId]: clauses }));

      // If the version is scheduled, refresh the versions list so clause_count updates
      try {
        const term = allTerms.find((t) => t.policy_version_id === addClauseVersionId);
        if (term && new Date(term.effective_from) > new Date()) {
          await loadTerms();
        }
      } catch (e) {
        console.warn("Falha ao recarregar versões após adicionar cláusula:", e);
      }

      setShowAddClauseModal(false);
      toast.success("Cláusula adicionada com sucesso.");
    } catch (error) {
      setAddClauseError(getApiErrorMessage(error, "Erro ao adicionar cláusula. Tente novamente."));
    } finally {
      setIsAddingClause(false);
    }
  };

  const openViewContentModal = async (term) => {
    setViewContentTitle(`${term.version} — ${TermType[term.policy_type] || term.policy_type}`);

    let finalContent = "";

    // Try admin endpoint first, but don't abort on failure — fall back to public
    if (term.policy_version_id) {
      try {
        const resp = await getAdminPolicyVersion(term.policy_version_id);
        const data = resp?.data ?? resp;
        const content = data?.content ?? data?.data?.content ?? data?.terms?.content;

        if (content) {
          finalContent = content;
        }
      } catch (err) {
        console.warn("admin policy fetch failed, will try public /terms:", err);
      }
    }

    if (!finalContent) {
      try {
        const respPublic = await getTerms();
        const terms = respPublic?.terms ?? respPublic?.data?.terms ?? [];
        const found = terms.find((t) => t.policy_version_id === term.policy_version_id) || terms.find((t) => t.version === term.version);
        finalContent = found?.content ?? term.content ?? "";
      } catch (err) {
        console.warn("public terms fetch failed:", err);
        finalContent = term.content ?? "";
        toast.error(getApiErrorMessage(err, "Não foi possível carregar o conteúdo do termo."));
      }
    }

    setViewContentText(finalContent);
    setShowViewContentModal(true);
  };

  const closeViewContentModal = () => {
    setShowViewContentModal(false);
    setViewContentText("");
    setViewContentTitle("");
  };

  const openViewClauseModal = (clause) => {
    setViewClause(clause);
    setShowViewClauseModal(true);
  };

  const closeViewClauseModal = () => {
    setViewClause(null);
    setShowViewClauseModal(false);
  };

  const stats = allTerms.reduce(
    (acc, term) => {
      acc.total += 1;
      const sameType = allTerms.filter((t) => t.policy_type === term.policy_type);
      const { label } = getStatus(term.effective_from, sameType);
      if (label === "Vigente") acc.vigentes += 1;
      if (label === "Agendado") acc.agendados += 1;
      if (label === "Expirado") acc.expirados += 1;
      return acc;
    },
    { total: 0, vigentes: 0, agendados: 0, expirados: 0 }
  );

  const statusCardClassName = (value) =>
    "cursor-pointer border-border bg-card transition-shadow hover:shadow-lg";

  return (
    <div className="flex flex-col gap-6">

      {/* Cards de estatísticas */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
        <Card
          className={statusCardClassName(StatusFilter.all)}
          onClick={() => handleStatusCardClick(StatusFilter.all)}
          role="button"
          tabIndex={0}
          aria-pressed={statusFilter === StatusFilter.all}
        >
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total de Termos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{stats.total}</div>
          </CardContent>
        </Card>
        <Card
          className={statusCardClassName(StatusFilter.current)}
          onClick={() => handleStatusCardClick(StatusFilter.current)}
          role="button"
          tabIndex={0}
          aria-pressed={statusFilter === StatusFilter.current}
        >
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Termos Vigentes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-chart-1">{stats.vigentes}</div>
          </CardContent>
        </Card>
        <Card
          className={statusCardClassName(StatusFilter.scheduled)}
          onClick={() => handleStatusCardClick(StatusFilter.scheduled)}
          role="button"
          tabIndex={0}
          aria-pressed={statusFilter === StatusFilter.scheduled}
        >
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Termos Agendados
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-chart-3">{stats.agendados}</div>
          </CardContent>
        </Card>
        <Card
          className={statusCardClassName(StatusFilter.expired)}
          onClick={() => handleStatusCardClick(StatusFilter.expired)}
          role="button"
          tabIndex={0}
          aria-pressed={statusFilter === StatusFilter.expired}
        >
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Termos Expirados
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-muted-foreground">
              {stats.expirados}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Busca */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Buscar por tipo ou versão..."
          value={searchTerm}
          onChange={handleSearchChange}
          className="border-border bg-input pl-10 text-foreground placeholder:text-muted-foreground"
        />
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <label htmlFor="terms-status-filter" className="text-sm text-muted-foreground">
            Filtrar por status
          </label>
          <select
            id="terms-status-filter"
            value={statusFilter}
            onChange={handleStatusFilterChange}
            className="w-full rounded-md border border-border bg-input px-3 py-2 text-foreground sm:w-56"
          >
            <option value={StatusFilter.all}>Todos</option>
            <option value={StatusFilter.current}>Vigentes</option>
            <option value={StatusFilter.scheduled}>Agendados</option>
            <option value={StatusFilter.expired}>Expirados</option>
          </select>
        </div>

        {/* Botão nova versão — desabilitado até a task 6.4.2 */}
        <Button
          type="button"
          className="bg-primary text-primary-foreground hover:bg-primary/90"
          onClick={handleOpenCreateModal}
        >
          <Plus className="mr-2 h-4 w-4" />
          Nova Versão
        </Button>
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 p-4 backdrop-blur-sm">
          <Card className="w-full max-w-md border-border bg-card">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-foreground">Nova Versão</CardTitle>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={handleCloseCreateModal}
                  className="text-muted-foreground hover:text-foreground"
                  aria-label="Fechar modal de nova versão"
                  disabled={isCreatingVersion}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <CardDescription className="text-muted-foreground">
                Cadastre uma nova versão de termo com vigência futura.
              </CardDescription>
            </CardHeader>

            <CardContent className="flex flex-col gap-4">
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground" htmlFor="create-policy-type">
                  Tipo
                </label>
                <select
                  id="create-policy-type"
                  name="policy_type"
                  value={createForm.policy_type}
                  onChange={handleCreateFormChange}
                  className="w-full rounded-md border border-border bg-input px-3 py-2 text-foreground"
                  disabled={isCreatingVersion}
                >
                  {PolicyTypeOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground" htmlFor="create-version-number">
                  Número da versão
                </label>
                <Input
                  id="create-version-number"
                  name="version"
                  value={createForm.version}
                  onChange={handleCreateFormChange}
                  placeholder="Ex: 1.0.0"
                  className="border-border bg-input text-foreground"
                  disabled={isCreatingVersion}
                />
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground" htmlFor="create-effective-from">
                  Data de vigência
                </label>
                <Input
                  id="create-effective-from"
                  name="effective_from"
                  type="datetime-local"
                  value={createForm.effective_from}
                  onChange={handleCreateFormChange}
                  min={toDatetimeLocalString(new Date(Date.now() + 60 * 1000))}
                  className="border-border bg-input text-foreground"
                  disabled={isCreatingVersion}
                />
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground" htmlFor="create-content">
                  Conteúdo dos termos
                </label>
                <textarea
                  id="create-content"
                  name="content"
                  value={createForm.content}
                  onChange={handleCreateFormChange}
                  placeholder="Digite o conteúdo completo da versão"
                  className="min-h-32 w-full rounded-md border border-border bg-input px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground"
                  disabled={isCreatingVersion}
                />
              </div>

              {/* Cláusulas temporárias */}
              <div className="flex flex-col gap-3 border-t border-border pt-4">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-foreground">
                    Cláusulas ({tempClauses.length})
                  </label>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={openTempClauseForm}
                    disabled={isCreatingVersion || showTempClauseForm}
                    className="border-border text-foreground hover:bg-muted"
                  >
                    <Plus className="mr-1 h-4 w-4" />
                    Adicionar
                  </Button>
                </div>

                {/* Lista de cláusulas temporárias */}
                {tempClauses.length > 0 && (
                  <div className="max-h-48 space-y-2 overflow-y-auto rounded-md border border-border bg-muted/30 p-2">
                    {tempClauses.map((clause, index) => (
                      <div key={`${clause.code}-${index}`} className="flex items-start justify-between gap-2 rounded border border-border bg-card p-2">
                        <div className="flex-1 text-sm">
                          <p className="font-medium text-foreground">{clause.code}</p>
                          <p className="text-xs text-muted-foreground">{clause.title}</p>
                          {clause.description && (
                            <p className="mt-1 text-xs text-muted-foreground">{clause.description}</p>
                          )}
                          <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                            <span>Obrigatória: {clause.mandatory ? "Sim" : "Não"}</span>
                            <span>•</span>
                            <span>Ordem: {clause.display_order}</span>
                          </div>
                        </div>
                        <Button
                          type="button"
                          size="icon"
                          variant="ghost"
                          onClick={() => removeTempClause(index)}
                          disabled={isCreatingVersion}
                          className="text-destructive hover:bg-destructive/10"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Formulário temporário agora é exibido em modal sobreposto (ver abaixo) */}
              </div>

              {createError && (
                <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                  {createError}
                </p>
              )}

              <div className="mt-2 flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1 border-border text-foreground hover:bg-muted"
                  onClick={handleCloseCreateModal}
                  disabled={isCreatingVersion}
                >
                  Cancelar
                </Button>
                <Button
                  type="button"
                  className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                  onClick={handleCreateVersion}
                  disabled={isCreatingVersion}
                >
                  {isCreatingVersion ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Salvando...
                    </>
                  ) : (
                    "Salvar Versão"
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {showViewContentModal && (
        <div className="fixed inset-0 z-60 flex items-center justify-center bg-background/80 p-4 backdrop-blur-sm">
          <Card className="w-full max-w-2xl border-border bg-card">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-foreground">{viewContentTitle}</CardTitle>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={closeViewContentModal}
                  className="text-muted-foreground hover:text-foreground"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <CardDescription className="text-muted-foreground">Conteúdo completo da versão</CardDescription>
            </CardHeader>

            <CardContent>
              <pre className="whitespace-pre-wrap max-h-96 overflow-auto rounded border border-border bg-muted/10 p-4 text-sm text-foreground">
                {viewContentText || "(Vazio)"}
              </pre>
            </CardContent>
          </Card>
        </div>
      )}

      {showViewClauseModal && viewClause && (
        <div className="fixed inset-0 z-70 flex items-center justify-center bg-background/80 p-4 backdrop-blur-sm">
          <Card className="w-full max-w-md border-border bg-card">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-foreground">{viewClause.code} — {viewClause.title}</CardTitle>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={closeViewClauseModal}
                  className="text-muted-foreground hover:text-foreground"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <CardDescription className="text-muted-foreground">Descrição da cláusula</CardDescription>
            </CardHeader>

            <CardContent>
              <p className="whitespace-pre-wrap text-sm text-foreground">{viewClause.description || "(Sem descrição)"}</p>
              <div className="mt-4 flex justify-end">
                <Button type="button" onClick={closeViewClauseModal} className="bg-primary text-primary-foreground hover:bg-primary/90">Fechar</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {showAddClauseModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 p-4 backdrop-blur-sm">
          <Card className="w-full max-w-md border-border bg-card">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-foreground">Adicionar Cláusula</CardTitle>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={closeAddClauseModal}
                  className="text-muted-foreground hover:text-foreground"
                  aria-label="Fechar modal de adicionar cláusula"
                  disabled={isAddingClause}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <CardDescription className="text-muted-foreground">
                Adicione uma nova cláusula para a versão selecionada.
              </CardDescription>
            </CardHeader>

            <CardContent className="flex flex-col gap-4">
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground" htmlFor="clause-code">
                  Código
                </label>
                <Input
                  id="clause-code"
                  name="code"
                  value={addClauseForm.code}
                  onChange={handleAddClauseFormChange}
                  placeholder="Ex: CLA-001"
                  className="border-border bg-input text-foreground"
                  disabled={isAddingClause}
                />
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground" htmlFor="clause-title">
                  Título
                </label>
                <Input
                  id="clause-title"
                  name="title"
                  value={addClauseForm.title}
                  onChange={handleAddClauseFormChange}
                  placeholder="Título da cláusula"
                  className="border-border bg-input text-foreground"
                  disabled={isAddingClause}
                />
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground" htmlFor="clause-description">
                  Descrição (opcional)
                </label>
                <textarea
                  id="clause-description"
                  name="description"
                  value={addClauseForm.description}
                  onChange={handleAddClauseFormChange}
                  placeholder="Descrição da cláusula"
                  className="min-h-24 w-full rounded-md border border-border bg-input px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground"
                  disabled={isAddingClause}
                />
              </div>

              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    name="mandatory"
                    checked={addClauseForm.mandatory}
                    onChange={handleAddClauseFormChange}
                    disabled={isAddingClause}
                  />
                  <span className="text-sm text-foreground">Obrigatória</span>
                </label>

                <div className="flex items-center gap-2">
                  <label htmlFor="clause-order" className="text-sm text-muted-foreground">Ordem</label>
                  <Input
                    id="clause-order"
                    name="display_order"
                    type="number"
                    min={1}
                    value={addClauseForm.display_order}
                    onChange={handleAddClauseFormChange}
                    className="w-24 border-border bg-input text-foreground"
                    disabled={isAddingClause}
                  />
                </div>
              </div>

              {addClauseError && (
                <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                  {addClauseError}
                </p>
              )}

              <div className="mt-2 flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1 border-border text-foreground hover:bg-muted"
                  onClick={closeAddClauseModal}
                  disabled={isAddingClause}
                >
                  Cancelar
                </Button>
                <Button
                  type="button"
                  className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                  onClick={handleAddClauseSubmit}
                  disabled={isAddingClause}
                >
                  {isAddingClause ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Salvando...
                    </>
                  ) : (
                    "Salvar Cláusula"
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {showTempClauseForm && (
        <div className="fixed inset-0 z-60 flex items-center justify-center bg-background/80 p-4 backdrop-blur-sm">
          <Card className="w-full max-w-md border-border bg-card">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-foreground">Nova Cláusula (Versão)</CardTitle>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={closeTempClauseForm}
                  className="text-muted-foreground hover:text-foreground"
                  aria-label="Fechar modal de cláusula temporária"
                  disabled={isCreatingVersion}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <CardDescription className="text-muted-foreground">
                Adicione uma cláusula que será incluída na nova versão após salvar.
              </CardDescription>
            </CardHeader>

            <CardContent className="flex flex-col gap-4">
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground" htmlFor="temp-modal-clause-code">
                  Código
                </label>
                <Input
                  id="temp-modal-clause-code"
                  name="code"
                  value={tempClauseForm.code}
                  onChange={handleTempClauseFormChange}
                  placeholder="Ex: CLA-001"
                  className="border-border bg-input text-foreground"
                  disabled={isCreatingVersion}
                />
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground" htmlFor="temp-modal-clause-title">
                  Título
                </label>
                <Input
                  id="temp-modal-clause-title"
                  name="title"
                  value={tempClauseForm.title}
                  onChange={handleTempClauseFormChange}
                  placeholder="Título da cláusula"
                  className="border-border bg-input text-foreground"
                  disabled={isCreatingVersion}
                />
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground" htmlFor="temp-modal-clause-description">
                  Descrição (opcional)
                </label>
                <textarea
                  id="temp-modal-clause-description"
                  name="description"
                  value={tempClauseForm.description}
                  onChange={handleTempClauseFormChange}
                  placeholder="Descrição da cláusula"
                  className="min-h-24 w-full rounded-md border border-border bg-input px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground"
                  disabled={isCreatingVersion}
                />
              </div>

              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    name="mandatory"
                    checked={tempClauseForm.mandatory}
                    onChange={handleTempClauseFormChange}
                    disabled={isCreatingVersion}
                  />
                  <span className="text-sm text-foreground">Obrigatória</span>
                </label>

                <div className="flex items-center gap-2">
                  <label className="text-sm text-muted-foreground" htmlFor="temp-modal-clause-order">Ordem</label>
                  <Input
                    id="temp-modal-clause-order"
                    name="display_order"
                    type="number"
                    min={1}
                    value={tempClauseForm.display_order}
                    onChange={handleTempClauseFormChange}
                    className="w-24 border-border bg-input text-foreground"
                    disabled={isCreatingVersion}
                  />
                </div>
              </div>

              <div className="mt-2 flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1 border-border text-foreground hover:bg-muted"
                  onClick={closeTempClauseForm}
                  disabled={isCreatingVersion}
                >
                  Cancelar
                </Button>
                <Button
                  type="button"
                  className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                  onClick={addTempClause}
                  disabled={isCreatingVersion}
                >
                  Adicionar
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tabela */}
      <Card className="border-border bg-card">
        <CardHeader>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <CardTitle className="text-foreground">Versões Publicadas</CardTitle>
              <CardDescription className="text-muted-foreground">
                Gerencie os Termos de Uso e Políticas de Privacidade.
              </CardDescription>
            </div>
            <div className="flex flex-wrap items-center justify-end gap-2 self-end sm:self-auto">
              <label htmlFor="terms-page-size" className="text-sm text-muted-foreground">
                Mostrar
              </label>
              <select
                id="terms-page-size"
                value={pageSize}
                onChange={handlePageSizeChange}
                className="w-24 rounded-md border border-border bg-input px-2 py-1.5 text-sm text-foreground"
              >
                {PAGE_SIZE_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="px-2 py-3 text-left text-sm font-medium text-muted-foreground">Tipo</th>
                  <th className="px-2 py-3 text-center text-sm font-medium text-muted-foreground">Versão</th>
                  <th className="px-2 py-3 text-center text-sm font-medium text-muted-foreground">Data de Vigência</th>
                  <th className="px-2 py-3 text-center text-sm font-medium text-muted-foreground">Nº de Cláusulas</th>
                  <th className="px-2 py-3 text-center text-sm font-medium text-muted-foreground">Status</th>
                </tr>
              </thead>
              <tbody>
                {loading && (
                  <tr>
                    <td colSpan={5} className="py-10">
                      <div className="flex items-center justify-center gap-2 text-muted-foreground">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Carregando termos...</span>
                      </div>
                    </td>
                  </tr>
                )}

                {!loading && termsPage.data.length === 0 && (
                  <tr>
                    <td colSpan={5} className="py-10 text-center text-muted-foreground">
                      Nenhum termo encontrado.
                    </td>
                  </tr>
                )}

                {!loading &&
                  termsPage.data.map((term) => {
                    const sameType = allTerms.filter(
                      (t) => t.policy_type === term.policy_type
                    );
                    const status = getStatus(term.effective_from, sameType);
                    const isOpen = openRowId === term.policy_version_id;

                    return (
                      <>
                        <tr
                          key={term.policy_version_id}
                          className="border-b border-border/50 transition-colors hover:bg-muted/50 cursor-pointer"
                          onClick={() => handleToggleRow(term.policy_version_id)}
                        >
                          <td className="px-2 py-3">
                            <div className="flex items-center gap-3">
                              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/20">
                                <FileText className="h-4 w-4 text-primary" />
                              </div>
                              <div className="flex items-center gap-2 text-sm font-medium text-foreground">
                                {TermType[term.policy_type] || term.policy_type}
                                <ChevronDown
                                  className={`h-4 w-4 transition-transform ${isOpen ? "rotate-180" : ""}`}
                                />
                              </div>
                            </div>
                          </td>
                          <td className="px-2 py-3 text-center text-sm text-muted-foreground">{term.version}</td>
                          <td className="px-2 py-3 text-center text-sm text-muted-foreground">
                            {new Date(term.effective_from).toLocaleDateString("pt-BR")}
                          </td>
                          <td className="px-2 py-3 text-center text-sm text-muted-foreground">{term.clause_count}</td>
                          <td className="px-2 py-3 text-center">
                            <span className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium ${status.className}`}>
                              {status.icon} {status.label}
                            </span>
                          </td>
                        </tr>

                        {/* Expansão — detalhes da versão e tabela de cláusulas (Task 6.4.3) */}
                        {isOpen && (
                          <tr key={`${term.policy_version_id}-detail`}>
                            <td colSpan={5} className="p-0">
                              <div className="border-t border-border bg-muted/20 p-6">
                                {/* Dados da Versão */}
                                <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
                                  <div className="flex-1">
                                    <h3 className="mb-3 text-sm font-semibold text-foreground">Detalhes da Versão</h3>
                                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                                      <div>
                                        <p className="text-xs text-muted-foreground">Tipo</p>
                                        <p className="text-sm font-medium text-foreground">
                                          {TermType[term.policy_type] || term.policy_type}
                                        </p>
                                      </div>
                                      <div>
                                        <p className="text-xs text-muted-foreground">Versão</p>
                                        <p className="text-sm font-medium text-foreground">{term.version}</p>
                                      </div>
                                      <div>
                                        <p className="text-xs text-muted-foreground">Data de Vigência</p>
                                        <p className="text-sm font-medium text-foreground">
                                          {new Date(term.effective_from).toLocaleDateString("pt-BR", {
                                            day: "2-digit",
                                            month: "2-digit",
                                            year: "numeric",
                                            hour: "2-digit",
                                            minute: "2-digit",
                                          })}
                                        </p>
                                      </div>
                                    </div>
                                  </div>
                                </div>

                                {/* Aviso de Versão em Vigência ou Expirada */}
                                {(() => {
                                  const sameType = allTerms.filter((t) => t.policy_type === term.policy_type);
                                  const status = getStatus(term.effective_from, sameType);

                                  if (status.key === StatusFilter.current) {
                                    return (
                                      <div className="mb-4 flex gap-2 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
                                        <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
                                        <p>
                                          Esta versão está em vigência. Não é possível adicionar ou modificar cláusulas de termos já ativos.
                                        </p>
                                      </div>
                                    );
                                  }

                                  if (status.key === StatusFilter.expired) {
                                    return (
                                      <div className="mb-4 flex gap-2 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">
                                        <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
                                        <p>
                                          Esta versão está expirada. Não é possível adicionar ou modificar cláusulas de termos expirados.
                                        </p>
                                      </div>
                                    );
                                  }

                                  return null;
                                })()}

                                {/* Tabela de Cláusulas */}
                                <div className="mb-4">
                                  <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                                    <h3 className="text-sm font-semibold text-foreground">Cláusulas</h3>
                                    <div className="flex flex-wrap items-center gap-2">
                                      <Button
                                        type="button"
                                        size="sm"
                                        variant="outline"
                                        onClick={() => openViewContentModal(term)}
                                        className="border-border text-foreground hover:bg-muted"
                                      >
                                        <Eye className="mr-2 h-4 w-4" />
                                        Visualizar Conteúdo
                                      </Button>

                                      {(() => {
                                        const today = new Date();
                                        const effectiveDate = new Date(term.effective_from);
                                        const canAddClauses = effectiveDate > today;
                                        return canAddClauses ? (
                                          <Button
                                            type="button"
                                            size="sm"
                                            className="bg-primary text-primary-foreground hover:bg-primary/90"
                                            onClick={() => openAddClauseModal(term.policy_version_id)}
                                          >
                                            <Plus className="mr-1 h-4 w-4" />
                                            Adicionar Cláusula
                                          </Button>
                                        ) : null;
                                      })()}
                                    </div>
                                  </div>

                                  {loadingClausesFor === term.policy_version_id ? (
                                    <div className="flex items-center justify-center gap-2 py-4 text-muted-foreground">
                                      <Loader2 className="h-4 w-4 animate-spin" />
                                      <span>Carregando cláusulas...</span>
                                    </div>
                                  ) : (
                                    <div className="overflow-x-auto rounded-md border border-border bg-card">
                                      <table className="w-full text-sm">
                                        <thead>
                                          <tr className="border-b border-border bg-muted/50">
                                            <th className="px-3 py-2 text-left font-medium text-muted-foreground">Código</th>
                                                <th className="px-3 py-2 text-left font-medium text-muted-foreground">Título</th>
                                                <th className="px-3 py-2 text-center font-medium text-muted-foreground">Obrigatória</th>
                                                <th className="px-3 py-2 text-center font-medium text-muted-foreground">Ordem</th>
                                                <th className="px-3 py-2 text-center font-medium text-muted-foreground">Ações</th>
                                          </tr>
                                        </thead>
                                        <tbody className="divide-y divide-border">
                                          {(!clausesByVersion[term.policy_version_id] ||
                                            clausesByVersion[term.policy_version_id].length === 0) && (
                                            <tr>
                                              <td colSpan={4} className="py-4 text-center text-muted-foreground">
                                                Nenhuma cláusula cadastrada.
                                              </td>
                                            </tr>
                                          )}
                                          {clausesByVersion[term.policy_version_id]?.map((clause) => (
                                            <tr key={clause.clause_uuid} className="hover:bg-muted/30">
                                              <td className="px-3 py-2 font-mono text-xs">{clause.code}</td>
                                              <td className="px-3 py-2">{clause.title}</td>
                                              <td className="px-3 py-2 text-center">
                                                {clause.mandatory ? (
                                                  <span className="inline-flex items-center gap-1 text-xs text-green-600">
                                                    <Check className="h-3 w-3" />
                                                    Sim
                                                  </span>
                                                ) : (
                                                  <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                                                    <X className="h-3 w-3" />
                                                    Não
                                                  </span>
                                                )}
                                              </td>
                                              <td className="px-3 py-2 text-center text-sm">{clause.display_order}</td>
                                              <td className="px-3 py-2 text-center text-sm">
                                                <Button
                                                  type="button"
                                                  size="icon"
                                                  variant="ghost"
                                                  onClick={() => openViewClauseModal(clause)}
                                                  className="text-foreground hover:bg-muted/50"
                                                  aria-label="Visualizar descrição da cláusula"
                                                >
                                                  <Eye className="h-4 w-4" />
                                                </Button>
                                              </td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </>
                    );
                  })}
              </tbody>
            </table>
          </div>

          {/* Paginação */}
          <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-muted-foreground">
              Mostrando {termsPage.data.length} de {termsPage.meta.total} termos
            </p>
            <div className="flex items-center gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={!termsPage.meta.hasPrev || loading}
                onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
              >
                Anterior
              </Button>
              <span className="min-w-24 text-center text-sm text-muted-foreground">
                Página {termsPage.meta.page} de {termsPage.meta.totalPages}
              </span>
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={!termsPage.meta.hasNext || loading}
                onClick={() => setCurrentPage((prev) => prev + 1)}
              >
                Próxima
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
