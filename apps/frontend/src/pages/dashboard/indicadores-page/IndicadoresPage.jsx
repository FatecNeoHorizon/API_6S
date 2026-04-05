import { useState } from "react";
import {
  TrendingUp,
  TrendingDown,
  Calendar as CalendarIcon,
  Filter,
  BarChart3,
  Zap,
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
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

// ─── Seletor de mês ──────────────────────────────────────────────────────────
const MONTH_NAMES = [
  "Janeiro",
  "Fevereiro",
  "Março",
  "Abril",
  "Maio",
  "Junho",
  "Julho",
  "Agosto",
  "Setembro",
  "Outubro",
  "Novembro",
  "Dezembro",
];
const MONTH_LABELS = [
  "Jan",
  "Fev",
  "Mar",
  "Abr",
  "Mai",
  "Jun",
  "Jul",
  "Ago",
  "Set",
  "Out",
  "Nov",
  "Dez",
];

/**
 * MonthRangePicker
 * Selects a range of months (not days).
 * value: { from: { year, month } | null, to: { year, month } | null }
 * onChange: (value) => void
 */
function MonthRangePicker({ value, onChange }) {
  const today = new Date();
  const [viewYear, setViewYear] = useState(today.getFullYear());

  const from = value?.from ?? null;
  const to = value?.to ?? null;

  const isSelected = (year, month) => {
    if (from && from.year === year && from.month === month) return "start";
    if (to && to.year === year && to.month === month) return "end";
    return null;
  };

  const isInRange = (year, month) => {
    if (!from || !to) return false;
    const cur = year * 12 + month;
    const lo = from.year * 12 + from.month;
    const hi = to.year * 12 + to.month;
    return cur > lo && cur < hi;
  };

  const handleClick = (year, month) => {
    if (!from || (from && to)) {
      // Começa nova seleção
      onChange({ from: { year, month }, to: null });
    } else {
      // Finaliza seleção
      const cur = year * 12 + month;
      const lo = from.year * 12 + from.month;
      if (cur < lo) {
        onChange({ from: { year, month }, to: from });
      } else {
        onChange({ from, to: { year, month } });
      }
    }
  };

  const formatLabel = (m) =>
    m ? `${MONTH_NAMES[m.month - 1]} ${m.year}` : "—";

  return (
    <div className="p-4 select-none" style={{ minWidth: 300 }}>
      {/* Navegação de ano */}
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={() => setViewYear((y) => y - 1)}
          className="p-1 rounded hover:bg-muted transition-colors text-foreground"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        <span className="text-sm font-semibold text-foreground">
          {viewYear}
        </span>
        <button
          onClick={() => setViewYear((y) => y + 1)}
          className="p-1 rounded hover:bg-muted transition-colors text-foreground"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Grid de meses */}
      <div className="grid grid-cols-3 gap-2">
        {MONTH_NAMES.map((name, idx) => {
          const month = idx + 1;
          const sel = isSelected(viewYear, month);
          const inRange = isInRange(viewYear, month);

          return (
            <button
              key={month}
              onClick={() => handleClick(viewYear, month)}
              className="rounded-lg py-2 text-sm font-medium transition-colors"
              style={{
                background: sel
                  ? "hsl(var(--primary))"
                  : inRange
                    ? "hsl(var(--primary) / 0.15)"
                    : "transparent",
                color: sel
                  ? "hsl(var(--primary-foreground))"
                  : "hsl(var(--foreground))",
                fontWeight: sel ? 700 : 400,
              }}
              onMouseOver={(e) => {
                if (!sel)
                  e.currentTarget.style.background = "hsl(var(--muted))";
              }}
              onMouseOut={(e) => {
                if (!sel)
                  e.currentTarget.style.background = inRange
                    ? "hsl(var(--primary) / 0.15)"
                    : "transparent";
              }}
            >
              {MONTH_LABELS[idx]}
            </button>
          );
        })}
      </div>

      {/* Legenda */}
      <div className="mt-4 pt-3 border-t border-border text-xs text-muted-foreground text-center">
        {!from
          ? "Clique para escolher o mês inicial"
          : !to
            ? `Início: ${formatLabel(from)} — clique para escolher o fim`
            : `${formatLabel(from)} → ${formatLabel(to)}`}
      </div>
    </div>
  );
}
// ─────────────────────────────────────────────────────────────────────────────

const QUICK_PERIODS = [
  { label: "3 meses", months: 3 },
  { label: "6 meses", months: 6 },
  { label: "9 meses", months: 9 },
  { label: "1 ano", months: 12 },
];

/** Subtrai `months` meses da data atual e retorna { year, month } */
const monthsAgo = (months) => {
  const d = new Date();
  d.setMonth(d.getMonth() - months);
  return { year: d.getFullYear(), month: d.getMonth() + 1 };
};

/** Mês atual como { year, month } */
const currentMonth = () => {
  const d = new Date();
  return { year: d.getFullYear(), month: d.getMonth() + 1 };
};

/** Monta a URL do endpoint */
const buildUrl = (from, to) => {
  const params = new URLSearchParams({
    year_min: from.year,
    period_min: from.month,
    year_max: to.year,
    period_max: to.month,
  });
  return `http://localhost:8000/get-dec-fec?${params.toString()}`;
};

/** Formata { year, month } para exibição */
const formatMonthLabel = (m) =>
  m ? `${MONTH_NAMES[m.month - 1]}/${m.year}` : "—";

// ─── Cálculos ────────────────────────────────────────────────────────────────
const calcAverage = (records, type) => {
  if (!records.length) return null;
  const sum = records.reduce((acc, r) => acc + r.value, 0);
  return parseFloat((sum / records.length).toFixed(2));
};

const buildRanking = (data) => {
  const agentMap = {};
  data.forEach((item) => {
    if (!agentMap[item.agent_acronym])
      agentMap[item.agent_acronym] = { decValues: [], fecValues: [] };
    if (item.indicator_type_code === "DEC")
      agentMap[item.agent_acronym].decValues.push(item.value);
    if (item.indicator_type_code === "FEC")
      agentMap[item.agent_acronym].fecValues.push(item.value);
  });

  return Object.entries(agentMap)
    .filter(([, v]) => v.decValues.length && v.fecValues.length)
    .map(([nome, { decValues, fecValues }]) => ({
      nome,
      dec: parseFloat(
        (decValues.reduce((a, v) => a + v, 0) / decValues.length).toFixed(2),
      ),
      fec: parseFloat(
        (fecValues.reduce((a, v) => a + v, 0) / fecValues.length).toFixed(2),
      ),
    }))
    .sort((a, b) => a.dec - b.dec);
};

const buildChartData = (data) => {
  const map = {};
  data.forEach((item) => {
    const key = `${item.year}-${String(item.period).padStart(2, "0")}`;
    if (!map[key])
      map[key] = {
        key,
        year: item.year,
        month: item.period,
        decValues: [],
        fecValues: [],
      };
    if (item.indicator_type_code === "DEC") map[key].decValues.push(item.value);
    if (item.indicator_type_code === "FEC") map[key].fecValues.push(item.value);
  });

  return Object.values(map)
    .sort((a, b) => (a.year !== b.year ? a.year - b.year : a.month - b.month))
    .map(({ month, year, decValues, fecValues }) => ({
      mes: MONTH_LABELS[month - 1],
      year,
      dec: decValues.length
        ? parseFloat(
            (decValues.reduce((s, v) => s + v, 0) / decValues.length).toFixed(
              2,
            ),
          )
        : null,
      fec: fecValues.length
        ? parseFloat(
            (fecValues.reduce((s, v) => s + v, 0) / fecValues.length).toFixed(
              2,
            ),
          )
        : null,
    }));
};
// ─────────────────────────────────────────────────────────────────────────────

const perdas = [
  {
    id: "kwh",
    tipo: "Perdas quilowatt-hora (kWh)",
    valor: 7.8,
    meta: 8,
    trend: "down",
  },
  { id: "brl", tipo: "Perdas R$ (BRL)", valor: 12.5, meta: 10, trend: "up" },
  { id: "total", tipo: "Perdas Totais", valor: 20.3, meta: 18, trend: "up" },
];

export default function IndicadoresPage() {
  const [selectedPeriod, setSelectedPeriod] = useState(null);
  const [selectedTab, setSelectedTab] = useState("dec_fec");
  const [monthRange, setMonthRange] = useState({ from: null, to: null });
  const [popoverOpen, setPopoverOpen] = useState(false);

  const [apiData, setApiData] = useState([]);
  const [decAvg, setDecAvg] = useState(null);
  const [fecAvg, setFecAvg] = useState(null);
  const [rankingData, setRankingData] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchAndProcess = async (from, to) => {
    const url = buildUrl(from, to);
    console.log("[get-dec-fec] Fetching:", url);
    setLoading(true);
    try {
      const response = await fetch(url);
      const data = await response.json();
      console.log("[get-dec-fec] Response:", data);
      setApiData(data);

      const decRecords = data.filter((d) => d.indicator_type_code === "DEC");
      const fecRecords = data.filter((d) => d.indicator_type_code === "FEC");

      setDecAvg(calcAverage(decRecords, "DEC"));
      setFecAvg(calcAverage(fecRecords, "FEC"));
      setRankingData(buildRanking(data));
      setChartData(buildChartData(data));
    } catch (error) {
      console.error("[get-dec-fec] Erro:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickPeriod = (period) => {
    setSelectedPeriod(period.label);
    const from = monthsAgo(period.months);
    const to = currentMonth();
    setMonthRange({ from, to });
    fetchAndProcess(from, to);
  };

  const handleMonthRangeChange = (range) => {
    setMonthRange(range);
    setSelectedPeriod(null);
    if (range.from && range.to) {
      fetchAndProcess(range.from, range.to);
      setPopoverOpen(false);
    }
  };

  const periodLabel = selectedPeriod
    ? selectedPeriod
    : monthRange.from && monthRange.to
      ? `${formatMonthLabel(monthRange.from)} → ${formatMonthLabel(monthRange.to)}`
      : null;

  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between">
        <div className="flex gap-2">
          <Button
            variant={selectedTab === "dec_fec" ? "default" : "outline"}
            onClick={() => setSelectedTab("dec_fec")}
            className={
              selectedTab === "dec_fec"
                ? "bg-primary text-primary-foreground"
                : "border-border text-foreground hover:bg-muted"
            }
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            DEC / FEC
          </Button>
          <Button
            variant={selectedTab === "perdas" ? "default" : "outline"}
            onClick={() => setSelectedTab("perdas")}
            className={
              selectedTab === "perdas"
                ? "bg-primary text-primary-foreground"
                : "border-border text-foreground hover:bg-muted"
            }
          >
            <Zap className="w-4 h-4 mr-2" />
            Perdas
          </Button>
        </div>

        <div className="flex gap-2 flex-wrap items-center">
          {QUICK_PERIODS.map((period) => (
            <Button
              key={period.label}
              variant={selectedPeriod === period.label ? "secondary" : "ghost"}
              size="sm"
              onClick={() => handleQuickPeriod(period)}
              className={
                selectedPeriod === period.label
                  ? "bg-secondary text-secondary-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }
            >
              {period.label}
            </Button>
          ))}

          <Popover open={popoverOpen} onOpenChange={setPopoverOpen}>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                className="border-border text-foreground hover:bg-muted"
              >
                <CalendarIcon className="w-4 h-4 mr-2" />
                {monthRange.from && monthRange.to && !selectedPeriod
                  ? `${formatMonthLabel(monthRange.from)} → ${formatMonthLabel(monthRange.to)}`
                  : "Personalizado"}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="end">
              <MonthRangePicker
                value={monthRange}
                onChange={handleMonthRangeChange}
              />
            </PopoverContent>
          </Popover>
        </div>
      </div>

      {selectedTab === "dec_fec" ? (
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_400px] gap-4">
          {/* Left Column */}
          <div className="flex flex-col gap-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Card className="bg-card border-border">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    DEC Médio
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-foreground">
                    {loading ? "..." : decAvg !== null ? `${decAvg}h` : "—"}
                  </div>
                  <div className="flex items-center gap-1 mt-1">
                    <TrendingDown className="w-4 h-4 text-chart-1" />
                    <span className="text-sm text-muted-foreground">
                      {periodLabel
                        ? `Média · ${periodLabel}`
                        : "Selecione um período"}
                    </span>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-card border-border">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    FEC Médio
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-foreground">
                    {loading ? "..." : fecAvg !== null ? fecAvg : "—"}
                  </div>
                  <div className="flex items-center gap-1 mt-1">
                    <TrendingDown className="w-4 h-4 text-chart-1" />
                    <span className="text-sm text-muted-foreground">
                      {periodLabel
                        ? `Média · ${periodLabel}`
                        : "Selecione um período"}
                    </span>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Chart */}
            <Card className="bg-card border-border flex-1">
              <CardHeader className="pb-2">
                <CardTitle className="text-foreground">
                  Evolução DEC/FEC
                </CardTitle>
                <CardDescription className="text-muted-foreground">
                  {periodLabel
                    ? `Histórico · ${periodLabel}`
                    : "Selecione um período"}
                </CardDescription>
              </CardHeader>
              <CardContent className="pb-4">
                <div className="h-40 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={chartData}
                      margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
                    >
                      <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="hsl(var(--border))"
                      />
                      <XAxis
                        dataKey="mes"
                        axisLine={false}
                        tickLine={false}
                        tick={{
                          fill: "hsl(var(--muted-foreground))",
                          fontSize: 12,
                        }}
                        tickFormatter={(label, index) => {
                          const item = chartData[index];
                          if (!item) return label;
                          const years = [
                            ...new Set(chartData.map((d) => d.year)),
                          ];
                          return years.length > 1
                            ? `${label}/${String(item.year).slice(2)}`
                            : label;
                        }}
                      />
                      <YAxis
                        axisLine={false}
                        tickLine={false}
                        tick={{
                          fill: "hsl(var(--muted-foreground))",
                          fontSize: 12,
                        }}
                        domain={([dataMin, dataMax]) => [
                          Math.max(0, Math.floor(dataMin - 2)),
                          Math.ceil(dataMax + 2),
                        ]}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "hsl(var(--background))",
                          border: "1px solid hsl(var(--border))",
                          borderRadius: "8px",
                        }}
                        labelStyle={{ color: "hsl(var(--foreground))" }}
                        labelFormatter={(label, payload) => {
                          if (payload && payload[0]) {
                            const item = payload[0].payload;
                            const years = [
                              ...new Set(chartData.map((d) => d.year)),
                            ];
                            return years.length > 1
                              ? `${label}/${item.year}`
                              : label;
                          }
                          return label;
                        }}
                      />
                      <Line
                        type="monotone"
                        dataKey="dec"
                        name="DEC (horas)"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        dot={{ fill: "#3b82f6", strokeWidth: 2, r: 4 }}
                        activeDot={{ r: 6, fill: "#3b82f6" }}
                        connectNulls
                      />
                      <Line
                        type="monotone"
                        dataKey="fec"
                        name="FEC (interrupções)"
                        stroke="#22c55e"
                        strokeWidth={2}
                        dot={{ fill: "#22c55e", strokeWidth: 2, r: 4 }}
                        activeDot={{ r: 6, fill: "#22c55e" }}
                        connectNulls
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex items-center justify-center gap-4 mt-2">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-[#3b82f6]" />
                    <span className="text-sm text-muted-foreground">
                      DEC (horas)
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-[#22c55e]" />
                    <span className="text-sm text-muted-foreground">
                      FEC (interrupções)
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Ranking */}
          <Card
            className="bg-card border-border lg:row-span-2 flex flex-col"
            style={{ maxHeight: 520 }}
          >
            <CardHeader className="flex-shrink-0">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-foreground">
                    Ranking de Distribuidoras
                  </CardTitle>
                  <CardDescription className="text-muted-foreground">
                    Ordenado por indicador DEC
                  </CardDescription>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="border-border text-foreground hover:bg-muted"
                >
                  <Filter className="w-4 h-4 mr-2" />
                  Filtrar
                </Button>
              </div>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden p-0">
              <div className="overflow-auto h-full">
                <table className="w-full">
                  <thead className="sticky top-0 z-10 bg-card">
                    <tr className="border-b border-border">
                      <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                        Distribuidora
                      </th>
                      <th className="text-center py-3 px-4 text-sm font-medium text-muted-foreground">
                        DEC
                      </th>
                      <th className="text-center py-3 px-4 text-sm font-medium text-muted-foreground">
                        FEC
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {loading ? (
                      <tr>
                        <td
                          colSpan={3}
                          className="py-8 text-center text-sm text-muted-foreground"
                        >
                          Carregando...
                        </td>
                      </tr>
                    ) : rankingData.length > 0 ? (
                      rankingData.map((dist) => (
                        <tr
                          key={dist.nome}
                          className="border-b border-border/50 hover:bg-muted/50 transition-colors"
                        >
                          <td className="py-3 px-4 text-sm text-foreground font-medium">
                            {dist.nome}
                          </td>
                          <td className="py-3 px-4 text-sm text-foreground text-center">
                            {dist.dec}
                          </td>
                          <td className="py-3 px-4 text-sm text-foreground text-center">
                            {dist.fec}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td
                          colSpan={3}
                          className="py-8 text-center text-sm text-muted-foreground"
                        >
                          Selecione um período para ver o ranking
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {perdas.map((perda) => (
              <Card key={perda.id} className="bg-card border-border">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {perda.tipo}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-foreground">
                    {perda.valor}%
                  </div>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-sm text-muted-foreground">
                      Meta: {perda.meta}%
                    </span>
                    <div className="flex items-center gap-1">
                      {perda.trend === "up" ? (
                        <TrendingUp className="w-4 h-4 text-destructive" />
                      ) : (
                        <TrendingDown className="w-4 h-4 text-chart-1" />
                      )}
                      <span
                        className={`text-sm ${perda.trend === "up" ? "text-destructive" : "text-chart-1"}`}
                      >
                        {perda.trend === "up" ? "Acima" : "Abaixo"} da meta
                      </span>
                    </div>
                  </div>
                  <div className="mt-3 h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${perda.valor > perda.meta ? "bg-destructive" : "bg-chart-1"}`}
                      style={{
                        width: `${Math.min((perda.valor / (perda.meta * 1.5)) * 100, 100)}%`,
                      }}
                    />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
