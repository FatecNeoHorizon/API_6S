import { useState } from "react";
import {
  Search,
  Filter,
  X,
  Building2,
  Zap,
  MapPin,
  Calendar,
  ChevronRight,
  Download,
  RefreshCw,
  Box,
  Gauge,
  ThermometerSun,
  AlertTriangle,
  CheckCircle2,
  Info,
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

// Dados mockados de subestacoes e transformadores
const ativos = [
  {
    id: 1,
    tipo: "subestacao",
    codigo: "SE-001",
    nome: "Subestacao Centro",
    regiao: "Centro",
    cidade: "Sao Paulo",
    estado: "SP",
    tensao: "138/13.8 kV",
    potencia: "60 MVA",
    status: "operacional",
    ultimaManutencao: "2026-01-15",
    proximaManutencao: "2026-07-15",
    transformadores: 3,
    alimentadores: 8,
    carga: 78,
    temperatura: 45,
    coordenadas: { lat: -23.5505, lng: -46.6333 },
  },
  {
    id: 2,
    tipo: "subestacao",
    codigo: "SE-002",
    nome: "Subestacao Norte",
    regiao: "Norte",
    cidade: "Sao Paulo",
    estado: "SP",
    tensao: "138/13.8 kV",
    potencia: "40 MVA",
    status: "operacional",
    ultimaManutencao: "2025-11-20",
    proximaManutencao: "2026-05-20",
    transformadores: 2,
    alimentadores: 6,
    carga: 65,
    temperatura: 42,
    coordenadas: { lat: -23.4905, lng: -46.6233 },
  },
  {
    id: 3,
    tipo: "transformador",
    codigo: "TR-001-A",
    nome: "Transformador Principal A",
    regiao: "Centro",
    cidade: "Sao Paulo",
    estado: "SP",
    subestacao: "SE-001",
    tensao: "138/13.8 kV",
    potencia: "20 MVA",
    status: "operacional",
    ultimaManutencao: "2026-02-10",
    proximaManutencao: "2026-08-10",
    fabricante: "WEG",
    anoFabricacao: 2018,
    carga: 82,
    temperatura: 52,
    oleo: { nivel: 95, qualidade: "bom" },
  },
  {
    id: 4,
    tipo: "transformador",
    codigo: "TR-001-B",
    nome: "Transformador Principal B",
    regiao: "Centro",
    cidade: "Sao Paulo",
    estado: "SP",
    subestacao: "SE-001",
    tensao: "138/13.8 kV",
    potencia: "20 MVA",
    status: "manutencao",
    ultimaManutencao: "2026-03-01",
    proximaManutencao: "2026-09-01",
    fabricante: "WEG",
    anoFabricacao: 2018,
    carga: 0,
    temperatura: 25,
    oleo: { nivel: 92, qualidade: "bom" },
  },
  {
    id: 5,
    tipo: "subestacao",
    codigo: "SE-003",
    nome: "Subestacao Sul",
    regiao: "Sul",
    cidade: "Sao Paulo",
    estado: "SP",
    tensao: "69/13.8 kV",
    potencia: "30 MVA",
    status: "alerta",
    ultimaManutencao: "2025-09-05",
    proximaManutencao: "2026-03-05",
    transformadores: 2,
    alimentadores: 4,
    carga: 92,
    temperatura: 58,
    coordenadas: { lat: -23.6105, lng: -46.6433 },
  },
  {
    id: 6,
    tipo: "transformador",
    codigo: "TR-002-A",
    nome: "Transformador Norte A",
    regiao: "Norte",
    cidade: "Sao Paulo",
    estado: "SP",
    subestacao: "SE-002",
    tensao: "138/13.8 kV",
    potencia: "20 MVA",
    status: "operacional",
    ultimaManutencao: "2025-12-15",
    proximaManutencao: "2026-06-15",
    fabricante: "ABB",
    anoFabricacao: 2020,
    carga: 70,
    temperatura: 48,
    oleo: { nivel: 98, qualidade: "excelente" },
  },
  {
    id: 7,
    tipo: "subestacao",
    codigo: "SE-004",
    nome: "Subestacao Leste",
    regiao: "Leste",
    cidade: "Sao Paulo",
    estado: "SP",
    tensao: "138/13.8 kV",
    potencia: "50 MVA",
    status: "operacional",
    ultimaManutencao: "2026-02-28",
    proximaManutencao: "2026-08-28",
    transformadores: 2,
    alimentadores: 5,
    carga: 55,
    temperatura: 40,
    coordenadas: { lat: -23.5405, lng: -46.4733 },
  },
  {
    id: 8,
    tipo: "transformador",
    codigo: "TR-003-A",
    nome: "Transformador Sul A",
    regiao: "Sul",
    cidade: "Sao Paulo",
    estado: "SP",
    subestacao: "SE-003",
    tensao: "69/13.8 kV",
    potencia: "15 MVA",
    status: "alerta",
    ultimaManutencao: "2025-08-20",
    proximaManutencao: "2026-02-20",
    fabricante: "Siemens",
    anoFabricacao: 2015,
    carga: 95,
    temperatura: 62,
    oleo: { nivel: 88, qualidade: "regular" },
  },
];

const regioes = ["Todas", "Centro", "Norte", "Sul", "Leste", "Oeste"];
const tipos = ["Todos", "subestacao", "transformador"];
const statusOptions = [
  "Todos",
  "operacional",
  "manutencao",
  "alerta",
  "inativo",
];

export default function EstruturaRedesPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedRegiao, setSelectedRegiao] = useState("Todas");
  const [selectedTipo, setSelectedTipo] = useState("Todos");
  const [selectedStatus, setSelectedStatus] = useState("Todos");
  const [selectedAtivo, setSelectedAtivo] = useState(null);
  const [showFilters, setShowFilters] = useState(false);

  const filteredAtivos = ativos.filter((ativo) => {
    const matchSearch =
      ativo.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ativo.codigo.toLowerCase().includes(searchTerm.toLowerCase());
    const matchRegiao =
      selectedRegiao === "Todas" || ativo.regiao === selectedRegiao;
    const matchTipo = selectedTipo === "Todos" || ativo.tipo === selectedTipo;
    const matchStatus =
      selectedStatus === "Todos" || ativo.status === selectedStatus;
    return matchSearch && matchRegiao && matchTipo && matchStatus;
  });

  const getStatusBadge = (status) => {
    const styles = {
      operacional: "bg-chart-1/20 text-chart-1",
      manutencao: "bg-chart-3/20 text-chart-3",
      alerta: "bg-destructive/20 text-destructive",
      inativo: "bg-muted text-muted-foreground",
    };
    const labels = {
      operacional: "Operacional",
      manutencao: "Em Manutencao",
      alerta: "Alerta",
      inativo: "Inativo",
    };
    return (
      <span
        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}
      >
        {labels[status]}
      </span>
    );
  };

  const getTipoIcon = (tipo) => {
    return tipo === "subestacao" ? (
      <Building2 className="w-4 h-4" />
    ) : (
      <Box className="w-4 h-4" />
    );
  };

  const stats = {
    totalSubestacoes: ativos.filter((a) => a.tipo === "subestacao").length,
    totalTransformadores: ativos.filter((a) => a.tipo === "transformador")
      .length,
    operacionais: ativos.filter((a) => a.status === "operacional").length,
    alertas: ativos.filter((a) => a.status === "alerta").length,
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between">
        <div>
          <h2 className="text-xl font-semibold text-foreground">
            Estrutura das Redes
          </h2>
          <p className="text-sm text-muted-foreground">
            Visualize a infraestrutura fisica da rede por regiao
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            className="border-border text-foreground hover:bg-muted"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Atualizar
          </Button>
          <Button
            variant="outline"
            className="border-border text-foreground hover:bg-muted"
          >
            <Download className="w-4 h-4 mr-2" />
            Exportar
          </Button>
        </div>
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
                  {stats.totalSubestacoes}
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
                  {stats.totalTransformadores}
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
                  {stats.operacionais}
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
                  {stats.alertas}
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
            placeholder="Buscar por nome ou codigo..."
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
        <div
          className={`flex-wrap gap-2 ${showFilters ? "flex" : "hidden"} sm:flex`}
        >
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
            <option value="subestacao">Subestacoes</option>
            <option value="transformador">Transformadores</option>
          </select>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 bg-input border border-border rounded-lg text-foreground text-sm"
          >
            <option value="Todos">Todos Status</option>
            <option value="operacional">Operacional</option>
            <option value="manutencao">Em Manutencao</option>
            <option value="alerta">Alerta</option>
            <option value="inativo">Inativo</option>
          </select>
        </div>
      </div>

      {/* Main Content - Table + Detail Panel */}
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Table */}
        <Card
          className={`bg-card border-border flex-1 ${selectedAtivo ? "lg:flex-[2]" : ""}`}
        >
          <CardHeader className="pb-3">
            <CardTitle className="text-foreground text-base">
              Ativos da Rede
            </CardTitle>
            <CardDescription className="text-muted-foreground">
              {filteredAtivos.length}{" "}
              {filteredAtivos.length === 1
                ? "ativo encontrado"
                : "ativos encontrados"}
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0 sm:p-6 sm:pt-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-3 px-3 text-sm font-medium text-muted-foreground">
                      Ativo
                    </th>
                    <th className="text-left py-3 px-3 text-sm font-medium text-muted-foreground hidden sm:table-cell">
                      Regiao
                    </th>
                    <th className="text-left py-3 px-3 text-sm font-medium text-muted-foreground hidden md:table-cell">
                      Tensao
                    </th>
                    <th className="text-center py-3 px-3 text-sm font-medium text-muted-foreground">
                      Status
                    </th>
                    <th className="text-center py-3 px-3 text-sm font-medium text-muted-foreground hidden lg:table-cell">
                      Carga
                    </th>
                    <th className="text-right py-3 px-3 text-sm font-medium text-muted-foreground"></th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAtivos.map((ativo) => (
                    <tr
                      key={ativo.id}
                      className={`border-b border-border/50 hover:bg-muted/50 transition-colors cursor-pointer ${
                        selectedAtivo?.id === ativo.id ? "bg-muted/70" : ""
                      }`}
                      onClick={() => setSelectedAtivo(ativo)}
                    >
                      <td className="py-3 px-3">
                        <div className="flex items-center gap-3">
                          <div
                            className={`p-1.5 rounded ${
                              ativo.tipo === "subestacao"
                                ? "bg-primary/10 text-primary"
                                : "bg-chart-2/10 text-chart-2"
                            }`}
                          >
                            {getTipoIcon(ativo.tipo)}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-foreground">
                              {ativo.nome}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {ativo.codigo}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-3 text-sm text-muted-foreground hidden sm:table-cell">
                        <div className="flex items-center gap-1">
                          <MapPin className="w-3 h-3" />
                          {ativo.regiao}
                        </div>
                      </td>
                      <td className="py-3 px-3 text-sm text-muted-foreground hidden md:table-cell">
                        {ativo.tensao}
                      </td>
                      <td className="py-3 px-3 text-center">
                        {getStatusBadge(ativo.status)}
                      </td>
                      <td className="py-3 px-3 text-center hidden lg:table-cell">
                        <div className="flex items-center justify-center gap-2">
                          <div className="w-16 h-2 bg-muted rounded-full overflow-hidden">
                            {(() => {
                              let cargaClass = "bg-chart-1";
                              if (ativo.carga > 90)
                                cargaClass = "bg-destructive";
                              else if (ativo.carga > 75)
                                cargaClass = "bg-chart-3";
                              return (
                                <div
                                  className={`h-full rounded-full ${cargaClass}`}
                                  style={{ width: `${ativo.carga}%` }}
                                />
                              );
                            })()}
                          </div>
                          <span className="text-xs text-muted-foreground w-8">
                            {ativo.carga}%
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-3 text-right">
                        <ChevronRight className="w-4 h-4 text-muted-foreground inline-block" />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {filteredAtivos.length === 0 && (
              <div className="text-center py-12 px-4">
                <Search className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">
                  Nenhum ativo encontrado com os filtros selecionados
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Detail Panel */}
        {selectedAtivo && (
          <Card className="bg-card border-border lg:w-96 lg:sticky lg:top-20 lg:self-start">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className={`p-2 rounded-lg ${
                      selectedAtivo.tipo === "subestacao"
                        ? "bg-primary/10"
                        : "bg-chart-2/10"
                    }`}
                  >
                    {selectedAtivo.tipo === "subestacao" ? (
                      <Building2 className="w-5 h-5 text-primary" />
                    ) : (
                      <Box className="w-5 h-5 text-chart-2" />
                    )}
                  </div>
                  <div>
                    <CardTitle className="text-foreground text-base">
                      {selectedAtivo.nome}
                    </CardTitle>
                    <CardDescription className="text-muted-foreground">
                      {selectedAtivo.codigo}
                    </CardDescription>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-muted-foreground hover:text-foreground -mr-2 -mt-2"
                  onClick={() => setSelectedAtivo(null)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              {/* Status */}
              <div className="flex items-center justify-between p-3 bg-secondary/50 rounded-lg">
                <span className="text-sm text-muted-foreground">Status</span>
                {getStatusBadge(selectedAtivo.status)}
              </div>

              {/* Info Grid */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-secondary/50 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <MapPin className="w-3 h-3 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">
                      Localizacao
                    </span>
                  </div>
                  <p className="text-sm font-medium text-foreground">
                    {selectedAtivo.regiao}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {selectedAtivo.cidade}, {selectedAtivo.estado}
                  </p>
                </div>
                <div className="p-3 bg-secondary/50 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <Zap className="w-3 h-3 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">
                      Tensao
                    </span>
                  </div>
                  <p className="text-sm font-medium text-foreground">
                    {selectedAtivo.tensao}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {selectedAtivo.potencia}
                  </p>
                </div>
              </div>

              {/* Carga e Temperatura */}
              <div className="flex flex-col gap-3">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Gauge className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">
                        Carga Atual
                      </span>
                    </div>
                    {(() => {
                      let cargaTextClass = "text-chart-1";
                      if (selectedAtivo.carga > 90)
                        cargaTextClass = "text-destructive";
                      else if (selectedAtivo.carga > 75)
                        cargaTextClass = "text-chart-3";
                      return (
                        <span
                          className={`text-sm font-medium ${cargaTextClass}`}
                        >
                          {selectedAtivo.carga}%
                        </span>
                      );
                    })()}
                  </div>
                  <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                    {(() => {
                      let cargaBarClass = "bg-chart-1";
                      if (selectedAtivo.carga > 90)
                        cargaBarClass = "bg-destructive";
                      else if (selectedAtivo.carga > 75)
                        cargaBarClass = "bg-chart-3";
                      return (
                        <div
                          className={`h-full rounded-full transition-all ${cargaBarClass}`}
                          style={{ width: `${selectedAtivo.carga}%` }}
                        />
                      );
                    })()}
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <ThermometerSun className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">
                        Temperatura
                      </span>
                    </div>
                    {(() => {
                      let tempTextClass = "text-foreground";
                      if (selectedAtivo.temperatura > 55)
                        tempTextClass = "text-destructive";
                      else if (selectedAtivo.temperatura > 45)
                        tempTextClass = "text-chart-3";
                      return (
                        <span
                          className={`text-sm font-medium ${tempTextClass}`}
                        >
                          {selectedAtivo.temperatura}°C
                        </span>
                      );
                    })()}
                  </div>
                  <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                    {(() => {
                      let tempBarClass = "bg-chart-1";
                      if (selectedAtivo.temperatura > 55)
                        tempBarClass = "bg-destructive";
                      else if (selectedAtivo.temperatura > 45)
                        tempBarClass = "bg-chart-3";
                      return (
                        <div
                          className={`h-full rounded-full transition-all ${tempBarClass}`}
                          style={{
                            width: `${(selectedAtivo.temperatura / 80) * 100}%`,
                          }}
                        />
                      );
                    })()}
                  </div>
                </div>
              </div>

              {/* Subestacao specific info */}
              {selectedAtivo.tipo === "subestacao" && (
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-secondary/50 rounded-lg text-center">
                    <p className="text-xl font-bold text-foreground">
                      {selectedAtivo.transformadores}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Transformadores
                    </p>
                  </div>
                  <div className="p-3 bg-secondary/50 rounded-lg text-center">
                    <p className="text-xl font-bold text-foreground">
                      {selectedAtivo.alimentadores}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Alimentadores
                    </p>
                  </div>
                </div>
              )}

              {/* Transformador specific info */}
              {selectedAtivo.tipo === "transformador" && (
                <div className="p-3 bg-secondary/50 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Info className="w-3 h-3 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">
                      Informacoes do Equipamento
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <p className="text-muted-foreground">Subestacao</p>
                      <p className="font-medium text-foreground">
                        {selectedAtivo.subestacao}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Fabricante</p>
                      <p className="font-medium text-foreground">
                        {selectedAtivo.fabricante}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Ano Fabricacao</p>
                      <p className="font-medium text-foreground">
                        {selectedAtivo.anoFabricacao}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Nivel Oleo</p>
                      <p className="font-medium text-foreground">
                        {selectedAtivo.oleo?.nivel}%
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Manutencao */}
              <div className="p-3 bg-secondary/50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Calendar className="w-3 h-3 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">
                    Manutencao
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <div>
                    <p className="text-muted-foreground">Ultima</p>
                    <p className="font-medium text-foreground">
                      {selectedAtivo.ultimaManutencao}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-muted-foreground">Proxima</p>
                    <p className="font-medium text-foreground">
                      {selectedAtivo.proximaManutencao}
                    </p>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-2">
                <Button
                  variant="outline"
                  className="flex-1 border-border text-foreground hover:bg-muted"
                >
                  Ver Historico
                </Button>
                <Button className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90">
                  Ver no Mapa
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
