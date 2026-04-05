import { useState, useEffect } from "react";
import {
  Search,
  Filter,
  Building2,
  MapPin,
  Box,
  AlertTriangle,
  CheckCircle2,
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

export default function EstruturaRedesPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedRegiao, setSelectedRegiao] = useState("Todas");
  const [selectedTipo, setSelectedTipo] = useState("Todos");
  const [selectedStatus, setSelectedStatus] = useState("Todos");
  const [showFilters, setShowFilters] = useState(false);

  const [summary, setSummary] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(true);

  const [assets, setAssets] = useState([]);
  const [loadingAssets, setLoadingAssets] = useState(true);

  useEffect(() => {
    async function fetchSummary() {
      try {
        const data = await apiClient.get("/network-structure/summary");
        setSummary(data);
      } catch (err) {
        console.error("Erro ao buscar summary:", err);
        setSummary(null);
      } finally {
        setLoadingSummary(false);
      }
    }

    async function fetchAssets() {
      try {
        const data = await apiClient.get("/network-structure/assets");
        setAssets(data);
      } catch (err) {
        console.error("Erro ao buscar assets:", err);
        setAssets([]);
      } finally {
        setLoadingAssets(false);
      }
    }

    fetchSummary();
    fetchAssets();
  }, []);

  const fmt = (val) => (loadingSummary ? "..." : (val ?? "-"));

  // Regiões dinâmicas a partir da API, ignorando nulls
  const regioes = [
    "Todas",
    ...new Set(assets.map((a) => a.region).filter(Boolean)),
  ];

  const filteredAssets = assets.filter((asset) => {
    const matchSearch =
      asset.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      asset.code?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchRegiao =
      selectedRegiao === "Todas" || asset.region === selectedRegiao;
    const matchTipo =
      selectedTipo === "Todos" || asset.type === selectedTipo;
    const matchStatus =
      selectedStatus === "Todos" || asset.status === selectedStatus;
    return matchSearch && matchRegiao && matchTipo && matchStatus;
  });

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

  const getTipoIcon = (tipo) => {
    return tipo === "substation" ? (
      <Building2 className="w-4 h-4" />
    ) : (
      <Box className="w-4 h-4" />
    );
  };

  const equipamentoLabel = filteredAssets.length === 1
    ? "equipamento encontrado"
    : "equipamentos encontrados";

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-semibold text-foreground">
          Estrutura das Redes
        </h2>
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
                <p className="text-2xl font-bold text-foreground">
                  {fmt(summary?.substations)}
                </p>
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
                <p className="text-2xl font-bold text-foreground">
                  {fmt(summary?.transformers)}
                </p>
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
                <p className="text-2xl font-bold text-foreground">
                  {fmt(summary?.operational)}
                </p>
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
                <p className="text-2xl font-bold text-foreground">
                  {fmt(summary?.alerts)}
                </p>
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
            onChange={(e) => setSearchTerm(e.target.value)}
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
            onChange={(e) => setSelectedRegiao(e.target.value)}
            className="px-3 py-2 bg-input border border-border rounded-lg text-foreground text-sm"
          >
            {regioes.map((r) => (
              <option key={r} value={r}>
                {r === "Todas" ? "Todas Regioes" : r}
              </option>
            ))}
          </select>
          <select
            value={selectedTipo}
            onChange={(e) => setSelectedTipo(e.target.value)}
            className="px-3 py-2 bg-input border border-border rounded-lg text-foreground text-sm"
          >
            <option value="Todos">Todos Tipos</option>
            <option value="substation">Subestacoes</option>
            <option value="transformer">Transformadores</option>
          </select>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
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
          <CardTitle className="text-foreground text-base">
            Equipamentos da Rede
          </CardTitle>
            <CardDescription className="text-muted-foreground">
              {loadingAssets
                ? "Carregando..."
                : `${filteredAssets.length} ${equipamentoLabel}`}
            </CardDescription>
        </CardHeader>
        <CardContent className="p-0 sm:p-6 sm:pt-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-3 text-sm font-medium text-muted-foreground w-[30%]">
                    Equipamento
                  </th>
                  <th className="text-left py-3 px-3 text-sm font-medium text-muted-foreground hidden sm:table-cell w-[15%]">
                    Tipo
                  </th>
                  <th className="text-left py-3 px-3 text-sm font-medium text-muted-foreground hidden sm:table-cell w-[20%]">
                    Regiao
                  </th>
                  <th className="text-left py-3 px-3 text-sm font-medium text-muted-foreground hidden md:table-cell w-[15%]">
                    Tensao
                  </th>
                  <th className="text-center py-3 px-3 text-sm font-medium text-muted-foreground w-[20%]">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredAssets.map((asset) => (
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
                          <p className="text-xs text-muted-foreground">
                            {asset.code}
                          </p>
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
                    <td className="py-3 px-3 text-sm text-muted-foreground hidden md:table-cell">
                      {asset.tension ?? "-"}
                    </td>
                    <td className="py-3 px-3 text-center">
                      {getStatusBadge(asset.status)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {!loadingAssets && filteredAssets.length === 0 && (
            <div className="text-center py-12 px-4">
              <Search className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">
                Nenhum equipamento encontrado com os filtros selecionados
              </p>
            </div>
          )}

          {loadingAssets && (
            <div className="text-center py-12 px-4">
              <p className="text-muted-foreground text-sm">
                Carregando equipamentos...
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
