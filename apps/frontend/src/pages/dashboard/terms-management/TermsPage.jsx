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
import { getTerms } from "@/api/terms";

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

  const loadTerms = async () => {
    setLoading(true);
    try {
      const response = await getTerms();
      const terms = response?.terms ?? response?.data?.terms ?? [];
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

  const handleToggleRow = (id) => {
    setOpenRowId((prev) => (prev === id ? null : id));
  };

  const handleStatusCardClick = (nextStatus) => {
    setStatusFilter(nextStatus);
    setCurrentPage(1);
  };

  const stats = allTerms.reduce(
    (acc, term) => {
      const sameType = allTerms.filter((t) => t.policy_type === term.policy_type);
      const { label } = getStatus(term.effective_from, sameType);
      if (label === "Vigente") acc.vigentes += 1;
      if (label === "Agendado") acc.agendados += 1;
      if (label === "Expirado") acc.expirados += 1;
      return acc;
    },
    { vigentes: 0, agendados: 0, expirados: 0 }
  );

  const statusCardClassName = (value) =>
    "cursor-pointer border-border bg-card transition-shadow hover:shadow-lg";

  return (
    <div className="flex flex-col gap-6">

      {/* Cards de estatísticas */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
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
          disabled
        >
          <Plus className="mr-2 h-4 w-4" />
          Nova Versão
        </Button>
      </div>

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

                        {/* Expansão — placeholder para 6.4.3 */}
                        {isOpen && (
                          <tr key={`${term.policy_version_id}-detail`}>
                            <td colSpan={5} className="p-0">
                              <div className="p-6 bg-muted/30">
                                <p className="text-sm text-muted-foreground">
                                  Detalhes das cláusulas serão implementados na task 6.4.3.
                                </p>
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
