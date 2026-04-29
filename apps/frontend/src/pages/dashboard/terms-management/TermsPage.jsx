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
import { createTermsVersion, getAdminTermsVersions, getVersionClauses } from "@/api/terms";

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
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [isCreatingVersion, setIsCreatingVersion] = useState(false);
  const [createError, setCreateError] = useState("");
  const [createForm, setCreateForm] = useState({
    policy_type: "PRIVACY_POLICY",
    version: "",
    effective_from: "",
    content: "",
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
    setShowCreateModal(true);
  };

  const handleCloseCreateModal = () => {
    if (isCreatingVersion) return;

    setShowCreateModal(false);
    setCreateError("");
  };

  const handleCreateFormChange = (event) => {
    const { name, value } = event.target;
    setCreateError("");
    setCreateForm((prev) => ({
      ...prev,
      [name]: value,
    }));
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
      await createTermsVersion({
        version,
        policy_type: policyType,
        content,
        effective_from: parsedEffectiveFrom.toISOString(),
      });

      await loadTerms();
      setCurrentPage(1);
      setOpenRowId(null);
      setShowCreateModal(false);
      toast.success("Nova versão criada com sucesso.");
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
                                <div className="mb-6">
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
                                  <div className="mb-3 flex items-center justify-between">
                                    <h3 className="text-sm font-semibold text-foreground">Cláusulas</h3>
                                    {(() => {
                                      const today = new Date();
                                      const effectiveDate = new Date(term.effective_from);
                                      const canAddClauses = effectiveDate > today;
                                      return canAddClauses ? (
                                        <Button
                                          type="button"
                                          size="sm"
                                          className="bg-primary text-primary-foreground hover:bg-primary/90"
                                          onClick={() => {
                                            toast.info("Funcionalidade de adicionar cláusulas será implementada em breve.");
                                          }}
                                        >
                                          <Plus className="mr-1 h-4 w-4" />
                                          Adicionar Cláusula
                                        </Button>
                                      ) : null;
                                    })()}
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
