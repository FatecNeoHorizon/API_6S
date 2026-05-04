import { useState, useEffect, useRef } from "react";
import {
  Search,
  Filter,
  Building2,
  MapPin,
  Box,
  AlertTriangle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
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
import { apiClient } from "../../../api/client";

const PAGE_SIZE = 10;

const TIPO_LABEL = {
  transformer: "Transformador",
  substation: "Subestação",
};

const STATUS_LABEL = {
  Operational: "Operacional",
  Maintenance: "Em Manutenção",
  Alert: "Alerta",
  Inactive: "Inativo",
};

const STATUS_STYLE = {
  Operational: "bg-chart-1/20 text-chart-1",
  Maintenance: "bg-chart-3/20 text-chart-3",
  Alert: "bg-destructive/20 text-destructive",
  Inactive: "bg-muted text-muted-foreground",
};

const REGIOES = ["Todas", "Urbana", "Rural"];

export default function EstruturaRedesPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [apiSearch, setApiSearch] = useState("");
  const [selectedRegiao, setSelectedRegiao] = useState("Todas");
  const [selectedTipo, setSelectedTipo] = useState("Todos");
  const [selectedStatus, setSelectedStatus] = useState("Todos");
  const [showFilters, setShowFilters] = useState(false);

  const [summary, setSummary] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(true);

  const [assets, setAssets] = useState([]);
  const [total, setTotal] = useState(0);
  const [loadingAssets, setLoadingAssets] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);

  const searchTimerRef = useRef(null);

  useEffect(() => {
    apiClient
      .get("/network-structure/summary")
      .then((data) => setSummary(data))
      .catch(() => setSummary(null))
      .finally(() => setLoadingSummary(false));
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoadingAssets(true);

    const params = new URLSearchParams({ page: currentPage, page_size: PAGE_SIZE });
    if (selectedRegiao !== "Todas") params.set("region", selectedRegiao);
    if (selectedTipo !== "Todos") params.set("type", selectedTipo);
    if (selectedStatus !== "Todos") params.set("status", selectedStatus);
    if (apiSearch.trim()) params.set("search", apiSearch.trim());

    apiClient
      .get(`/network-structure/assets?${params}`)
      .then((data) => {
        if (!cancelled) {
          setAssets(data.data ?? []);
          setTotal(data.total ?? 0);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setAssets([]);
          setTotal(0);
        }
      })
      .finally(() => {
        if (!cancelled) setLoadingAssets(false);
      });

    return () => { cancelled = true; };
  }, [currentPage, selectedRegiao, selectedTipo, selectedStatus, apiSearch]);

  const handleSearchChange = (e) => {
    const val = e.target.value;
    setSearchTerm(val);
    clearTimeout(searchTimerRef.current);
    searchTimerRef.current = setTimeout(() => {
      setApiSearch(val);
      setCurrentPage(1);
    }, 400);
  };

  const handleRegiaoChange = (e) => {
    setSelectedRegiao(e.target.value);
    setCurrentPage(1);
  };

  const handleTipoChange = (e) => {
    setSelectedTipo(e.target.value);
    setCurrentPage(1);
  };

  const handleStatusChange = (e) => {
    setSelectedStatus(e.target.value);
    setCurrentPage(1);
  };

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const fmt = (val) => (loadingSummary ? "..." : (val ?? "-"));
  const equipamentoLabel = total === 1 ? "equipamento encontrado" : "equipamentos encontrados";

  const getStatusBadge = (status) => {
    if (!status) return <span className="text-muted-foreground text-xs">-</span>;
    return (
      <span
        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
          STATUS_STYLE[status] ?? "bg-muted text-muted-foreground"
        }`}
      >
        {STATUS_LABEL[status] ?? status}
      </span>
    );
  };

  const getTipoIcon = (tipo) =>
    tipo === "substation" ? <Building2 className="w-4 h-4" /> : <Box className="w-4 h-4" />;

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-semibold text-foreground">Estrutura das Redes</h2>
        <p className="text-sm text-muted-foreground">
          Visualize a infraestrutura fisica da rede por regiao
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Building2 className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">{fmt(summary?.substations)}</p>
                <p className="text-xs text-muted-foreground">Subestacoes</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-chart-2/10 rounded-lg">
                <Box className="w-5 h-5 text-chart-2" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">{fmt(summary?.transformers)}</p>
                <p className="text-xs text-muted-foreground">Transformadores</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-chart-1/10 rounded-lg">
                <CheckCircle2 className="w-5 h-5 text-chart-1" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">{fmt(summary?.operational)}</p>
                <p className="text-xs text-muted-foreground">Operacionais</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-destructive/10 rounded-lg">
                <AlertTriangle className="w-5 h-5 text-destructive" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">{fmt(summary?.alerts)}</p>
                <p className="text-xs text-muted-foreground">Em Alerta</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Buscar por descricao ou codigo..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="pl-10 bg-input border-border text-foreground placeholder:text-muted-foreground"
          />
        </div>
        <Button
          variant="outline"
          className="border-border text-foreground hover:bg-muted sm:hidden"
          onClick={() => setShowFilters(!showFilters)}
        >
          <Filter className="w-4 h-4 mr-2" />
          Filtros
        </Button>
        <div className={`flex-wrap gap-2 ${showFilters ? "flex" : "hidden"} sm:flex`}>
          <select
            value={selectedRegiao}
            onChange={handleRegiaoChange}
            className="px-3 py-2 bg-input border border-border rounded-lg text-foreground text-sm"
          >
            {REGIOES.map((r) => (
              <option key={r} value={r}>
                {r === "Todas" ? "Todas Regioes" : r}
              </option>
            ))}
          </select>
          <select
            value={selectedTipo}
            onChange={handleTipoChange}
            className="px-3 py-2 bg-input border border-border rounded-lg text-foreground text-sm"
          >
            <option value="Todos">Todos Tipos</option>
            <option value="substation">Subestacoes</option>
            <option value="transformer">Transformadores</option>
          </select>
          <select
            value={selectedStatus}
            onChange={handleStatusChange}
            className="px-3 py-2 bg-input border border-border rounded-lg text-foreground text-sm"
          >
            <option value="Todos">Todos Status</option>
            <option value="Operational">Operacional</option>
            <option value="Maintenance">Em Manutencao</option>
            <option value="Alert">Alerta</option>
            <option value="Inactive">Inativo</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <Card className="bg-card border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-foreground text-base">Equipamentos da Rede</CardTitle>
          <CardDescription className="text-muted-foreground">
            {loadingAssets ? "Carregando..." : `${total} ${equipamentoLabel}`}
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0 sm:p-6 sm:pt-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-3 text-sm font-medium text-muted-foreground w-[45%]">
                    Equipamento
                  </th>
                  <th className="text-left py-3 px-3 text-sm font-medium text-muted-foreground hidden sm:table-cell w-[20%]">
                    Tipo
                  </th>
                  <th className="text-left py-3 px-3 text-sm font-medium text-muted-foreground hidden sm:table-cell w-[20%]">
                    Regiao
                  </th>
                  <th className="text-center py-3 px-3 text-sm font-medium text-muted-foreground w-[15%]">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {assets.map((asset) => (
                  <tr
                    key={asset.code}
                    className="border-b border-border/50 transition-colors"
                  >
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-3">
                        <div
                          className={`p-1.5 rounded ${
                            asset.type === "substation"
                              ? "bg-primary/10 text-primary"
                              : "bg-chart-2/10 text-chart-2"
                          }`}
                        >
                          {getTipoIcon(asset.type)}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-foreground">
                            {asset.description ?? "-"}
                          </p>
                          <p className="text-xs text-muted-foreground">{asset.code}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-3 text-sm text-muted-foreground hidden sm:table-cell">
                      {TIPO_LABEL[asset.type] ?? asset.type}
                    </td>
                    <td className="py-3 px-3 text-sm text-muted-foreground hidden sm:table-cell">
                      {asset.region ? (
                        <div className="flex items-center gap-1">
                          <MapPin className="w-3 h-3" />
                          {asset.region}
                        </div>
                      ) : (
                        "-"
                      )}
                    </td>
                    <td className="py-3 px-3 text-center">{getStatusBadge(asset.status)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {!loadingAssets && assets.length === 0 && (
            <div className="text-center py-12 px-4">
              <Search className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">
                Nenhum equipamento encontrado com os filtros selecionados
              </p>
            </div>
          )}

          {loadingAssets && (
            <div className="text-center py-12 px-4">
              <p className="text-muted-foreground text-sm">Carregando equipamentos...</p>
            </div>
          )}

          {!loadingAssets && totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t border-border">
              <span className="text-xs text-muted-foreground">
                Página {currentPage} de {totalPages}
              </span>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="p-1.5 rounded hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft className="w-4 h-4 text-foreground" />
                </button>
                <button
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="p-1.5 rounded hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronRight className="w-4 h-4 text-foreground" />
                </button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
