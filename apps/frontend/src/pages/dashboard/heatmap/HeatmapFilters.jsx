import { useState, useEffect, useMemo } from "react";
import {
  BarChart2,
  BarChart3,
  ChevronLeft,
  ChevronRight,
  Map,
  Search,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getConj } from "../../../api/heatmap";
import { Heatmap } from "../../../components/heatmap";

const YEAR_MIN = 2020;
const YEAR_MAX = 2029;

const CRITICALITY_OPTIONS = [
  { value: null,       label: "Todos" },
  { value: "normal",   label: "Normal" },
  { value: "attention",label: "Atenção" },
  { value: "critical", label: "Crítico" },
];

function getCriticality(conj) {
  if (!conj.limit || !conj.accumulated_value) return "no-data";
  const ratio = conj.accumulated_value / conj.limit;
  if (ratio >= 1) return "critical";
  if (ratio >= 0.5) return "attention";
  return "normal";
}

export function HeatmapFilters() {
  const [selectedTab, setSelectedTab] = useState("DEC");
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedCriticality, setSelectedCriticality] = useState(null);
  const [conjSearch, setConjSearch] = useState("");
  const [convertedConjs, setConvertedConjs] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchConj = async () => {
    setLoading(true);
    try {
      const data = await getConj({ year: selectedYear, indicator_type_code: selectedTab });
      setConvertedConjs(Array.isArray(data) ? data : null);
    } catch (error) {
      console.error("[geo/conj] Erro:", error);
      setConvertedConjs(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConj();
  }, [selectedTab, selectedYear]);

  const filteredConjs = useMemo(() => {
    if (!convertedConjs) return null;
    return convertedConjs.filter((conj) => {
      if (selectedCriticality && getCriticality(conj) !== selectedCriticality) return false;
      if (conjSearch.trim() && !conj.name?.toLowerCase().includes(conjSearch.toLowerCase())) return false;
      return true;
    });
  }, [convertedConjs, selectedCriticality, conjSearch]);

  const totalCount = convertedConjs?.length ?? 0;
  const filteredCount = filteredConjs?.length ?? 0;

  return (
    <div className="flex gap-4 h-[calc(100vh-8rem)]">
      {/* Painel de filtros */}
      <Card className="w-56 shrink-0 h-fit">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <Map className="w-4 h-4" />
            Filtros
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">

          {/* Indicador */}
          <div className="flex flex-col gap-1">
            <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
              Indicador
            </span>
            <div className="flex flex-col gap-1.5">
              <Button
                size="sm"
                variant={selectedTab === "DEC" ? "default" : "outline"}
                onClick={() => setSelectedTab("DEC")}
                className="justify-start"
              >
                <BarChart3 className="w-4 h-4 mr-2" />
                DEC
              </Button>
              <Button
                size="sm"
                variant={selectedTab === "FEC" ? "default" : "outline"}
                onClick={() => setSelectedTab("FEC")}
                className="justify-start"
              >
                <BarChart2 className="w-4 h-4 mr-2" />
                FEC
              </Button>
            </div>
          </div>

          {/* Período */}
          <div className="flex flex-col gap-1">
            <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
              Período
            </span>
            <div className="flex items-center justify-between gap-1">
              <Button
                size="icon"
                variant="outline"
                className="h-8 w-8"
                disabled={selectedYear <= YEAR_MIN}
                onClick={() => setSelectedYear((y) => y - 1)}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <span className="text-sm font-semibold tabular-nums w-12 text-center">
                {selectedYear}
              </span>
              <Button
                size="icon"
                variant="outline"
                className="h-8 w-8"
                disabled={selectedYear >= YEAR_MAX}
                onClick={() => setSelectedYear((y) => y + 1)}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Criticidade */}
          <div className="flex flex-col gap-1">
            <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
              Criticidade
            </span>
            <div className="flex flex-col gap-1">
              {CRITICALITY_OPTIONS.map((opt) => (
                <button
                  key={String(opt.value)}
                  onClick={() => setSelectedCriticality(opt.value)}
                  className={`flex items-center gap-2 px-2 py-1.5 rounded-md text-sm transition-colors text-left ${
                    selectedCriticality === opt.value
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-muted text-foreground"
                  }`}
                >
                  {opt.value === "critical"  && <span className="w-2.5 h-2.5 rounded-full bg-red-500 shrink-0" />}
                  {opt.value === "attention" && <span className="w-2.5 h-2.5 rounded-full bg-orange-400 shrink-0" />}
                  {opt.value === "normal"    && <span className="w-2.5 h-2.5 rounded-full bg-green-500 shrink-0" />}
                  {opt.value === null        && <span className="w-2.5 h-2.5 rounded-full bg-border shrink-0" />}
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Região / CONJ */}
          <div className="flex flex-col gap-1">
            <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
              Região / CONJ
            </span>
            <div className="relative">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
              <Input
                placeholder="Buscar conjunto..."
                value={conjSearch}
                onChange={(e) => setConjSearch(e.target.value)}
                className="pl-8 h-8 text-sm"
              />
            </div>
          </div>

          {/* Legenda */}
          <div className="flex flex-col gap-1">
            <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
              Legenda
            </span>
            <div className="flex flex-col gap-1.5 text-sm">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-sm bg-green-500 shrink-0" />
                <span className="text-muted-foreground">Normal</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-sm bg-orange-400 shrink-0" />
                <span className="text-muted-foreground">Atenção</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-sm bg-red-500 shrink-0" />
                <span className="text-muted-foreground">Crítico</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-sm bg-gray-400 shrink-0" />
                <span className="text-muted-foreground">Sem dados</span>
              </div>
            </div>
          </div>

          {/* Contador */}
          {totalCount > 0 && (
            <p className="text-xs text-muted-foreground border-t border-border pt-3">
              {filteredCount} de {totalCount} conjuntos
            </p>
          )}

        </CardContent>
      </Card>

      {/* Mapa — isolate cria stacking context próprio, confinando os z-indexes do Leaflet */}
      <div className="flex-1 rounded-xl overflow-hidden border border-border isolate">
        <Heatmap convertedConjs={filteredConjs} loading={loading} />
      </div>
    </div>
  );
}
