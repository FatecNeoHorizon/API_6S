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
import { apiClient } from "@/api/client";

// ─── Constantes ───────────────────────────────────────────────────────────────
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
const DAY_NAMES_SHORT = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];

// ─── MonthRangePicker — usado na aba DEC/FEC ──────────────────────────────────
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
    return cur > from.year * 12 + from.month && cur < to.year * 12 + to.month;
  };

  const handleClick = (year, month) => {
    if (!from || (from && to)) {
      onChange({ from: { year, month }, to: null });
    } else {
      const cur = year * 12 + month;
      const lo = from.year * 12 + from.month;
      if (cur < lo) onChange({ from: { year, month }, to: from });
      else onChange({ from, to: { year, month } });
    }
  };

  const formatLabel = (m) =>
    m ? `${MONTH_NAMES[m.month - 1]} ${m.year}` : "—";

  return (
    <div className="p-4 select-none" style={{ minWidth: 300 }}>
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

// ─── DayRangePicker — usado na aba Perdas ─────────────────────────────────────
function isSameDay(a, b) {
  return a && b && a.toDateString() === b.toDateString();
}

function DayRangePicker({ value, onChange }) {
  const today = new Date();
  const [viewYear, setViewYear] = useState(today.getFullYear());
  const [viewMonth, setViewMonth] = useState(today.getMonth());
  const [hovered, setHovered] = useState(null);

  const from = value?.from ?? null;
  const to = value?.to ?? null;
  const selecting = from && !to;

  const prevMonth = () => {
    if (viewMonth === 0) {
      setViewMonth(11);
      setViewYear((y) => y - 1);
    } else setViewMonth((m) => m - 1);
  };
  const nextMonth = () => {
    if (viewMonth === 11) {
      setViewMonth(0);
      setViewYear((y) => y + 1);
    } else setViewMonth((m) => m + 1);
  };

  const month2 = viewMonth === 11 ? 0 : viewMonth + 1;
  const year2 = viewMonth === 11 ? viewYear + 1 : viewYear;

  const handleDayClick = (day) => {
    if (!from || (from && to)) {
      onChange({ from: day, to: null });
    } else {
      const [lo, hi] = day < from ? [day, from] : [from, day];
      onChange({ from: lo, to: hi });
    }
  };

  const renderMonth = (year, month) => {
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const cells = [];
    for (let i = 0; i < firstDay; i++) cells.push(null);
    for (let d = 1; d <= daysInMonth; d++) cells.push(new Date(year, month, d));
    const rangeEnd = to || (selecting ? hovered : null);

    return (
      <div>
        <p className="text-xs font-semibold text-foreground text-center mb-2">
          {MONTH_NAMES[month]} {year}
        </p>
        <div className="grid grid-cols-7 mb-1">
          {DAY_NAMES_SHORT.map((d) => (
            <div
              key={d}
              className="text-center text-xs text-muted-foreground py-1"
            >
              {d}
            </div>
          ))}
        </div>
        <div className="grid grid-cols-7">
          {cells.map((day, i) => {
            if (!day) return <div key={`e-${i}`} />;
            const isStart = from && isSameDay(day, from);
            const isEnd = rangeEnd && isSameDay(day, rangeEnd);
            let inRange = false;
            if (from && rangeEnd) {
              const [lo, hi] =
                from < rangeEnd ? [from, rangeEnd] : [rangeEnd, from];
              inRange = day > lo && day < hi;
            }
            const isSelected = isStart || isEnd;
            return (
              <div
                key={day.toISOString()}
                className="relative flex items-center justify-center h-8"
                style={{
                  background: inRange
                    ? "hsl(var(--primary) / 0.12)"
                    : "transparent",
                  borderRadius: isStart
                    ? "9999px 0 0 9999px"
                    : isEnd
                      ? "0 9999px 9999px 0"
                      : "0",
                }}
              >
                <button
                  onClick={() => handleDayClick(day)}
                  onMouseEnter={() => setHovered(day)}
                  onMouseLeave={() => setHovered(null)}
                  className="w-8 h-8 flex items-center justify-center text-xs rounded-full transition-colors z-10"
                  style={{
                    background: isSelected
                      ? "hsl(var(--primary))"
                      : "transparent",
                    color: isSelected
                      ? "hsl(var(--primary-foreground))"
                      : "hsl(var(--foreground))",
                    fontWeight: isSelected ? 700 : 400,
                  }}
                >
                  {day.getDate()}
                </button>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const fmt = (d) => (d ? d.toLocaleDateString("pt-BR") : "—");

  return (
    <div className="p-4 select-none" style={{ minWidth: 580 }}>
      <div className="flex items-center justify-between mb-3">
        <button
          onClick={prevMonth}
          className="p-1 rounded hover:bg-muted transition-colors text-foreground"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        <button
          onClick={nextMonth}
          className="p-1 rounded hover:bg-muted transition-colors text-foreground"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
      <div className="flex gap-6">
        <div className="flex-1">{renderMonth(viewYear, viewMonth)}</div>
        <div className="w-px bg-border" />
        <div className="flex-1">{renderMonth(year2, month2)}</div>
      </div>
      <div className="mt-3 pt-3 border-t border-border text-xs text-muted-foreground text-center">
        {!from
          ? "Clique para escolher a data inicial"
          : !to
            ? `Início: ${fmt(from)} — clique para escolher o fim`
            : `${fmt(from)} → ${fmt(to)}`}
      </div>
    </div>
  );
}

// ─── Períodos rápidos ─────────────────────────────────────────────────────────
const DEC_FEC_QUICK_PERIODS = [
  { label: "3 meses", months: 3 },
  { label: "6 meses", months: 6 },
  { label: "9 meses", months: 9 },
  { label: "1 ano", months: 12 },
];

const PERDAS_QUICK_PERIODS = [
  { label: "6 meses", days: 180 },
  { label: "1 ano", days: 365 },
  { label: "2 anos", days: 730 },
  { label: "5 anos", days: 1825 },
];

// ─── Helpers DEC/FEC ──────────────────────────────────────────────────────────
const monthsAgo = (months) => {
  const d = new Date();
  d.setMonth(d.getMonth() - months);
  return { year: d.getFullYear(), month: d.getMonth() + 1 };
};

const currentMonth = () => {
  const d = new Date();
  return { year: d.getFullYear(), month: d.getMonth() + 1 };
};

const buildDecFecUrl = (from, to) => {
  const params = new URLSearchParams({
    year_min: from.year,
    period_min: from.month,
    year_max: to.year,
    period_max: to.month,
  });
  return `/get-dec-fec?${params.toString()}`;
};

const formatMonthLabel = (m) =>
  m ? `${MONTH_NAMES[m.month - 1]}/${m.year}` : "—";

const calcAverage = (records) => {
  if (!records.length) return null;
  return parseFloat(
    (records.reduce((acc, r) => acc + r.value, 0) / records.length).toFixed(2),
  );
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
    .sort((a, b) => b.dec - a.dec || b.fec - a.fec);
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

const buildPreviewChartData = (data) => {
  const map = {};
  data.forEach((item) => {
    const key = `${item.forecast_year}-${String(item.forecast_period).padStart(2, "0")}`;
    if (!map[key])
      map[key] = {
        key,
        year: item.forecast_year,
        month: item.forecast_period,
        decValues: [],
        fecValues: [],
      };
    if (item.indicator === "DEC") map[key].decValues.push(item.value);
    if (item.indicator === "FEC") map[key].fecValues.push(item.value);
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

// ─── Helpers Perdas ───────────────────────────────────────────────────────────
const toISODate = (d) => d.toISOString().split("T")[0];

const buildPerdasUrl = (from, to) => {
  const params = new URLSearchParams({
    process_date_min: toISODate(from),
    process_date_max: toISODate(to),
  });
  return `/get-energy-losses?${params.toString()}`;
};

const daysAgoDate = (days) => {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d;
};

const formatDateLabel = (d) => (d ? d.toLocaleDateString("pt-BR") : "—");

const formatMWh = (v) => {
  if (v == null) return "—";
  if (v >= 1_000_000)
    return `${(v / 1_000_000).toLocaleString("pt-BR", { maximumFractionDigits: 2 })} TWh`;
  if (v >= 1_000)
    return `${(v / 1_000).toLocaleString("pt-BR", { maximumFractionDigits: 2 })} GWh`;
  return `${v.toLocaleString("pt-BR", { maximumFractionDigits: 2 })} MWh`;
};

const formatBRL = (v) => {
  if (v == null) return "—";
  if (v >= 1_000_000_000)
    return `R$ ${(v / 1_000_000_000).toLocaleString("pt-BR", { maximumFractionDigits: 2 })} bi`;
  if (v >= 1_000_000)
    return `R$ ${(v / 1_000_000).toLocaleString("pt-BR", { maximumFractionDigits: 2 })} mi`;
  return `R$ ${v.toLocaleString("pt-BR", { maximumFractionDigits: 2 })}`;
};

const sumField = (data, field) =>
  data.reduce((acc, item) => acc + (item[field] ?? 0), 0);

// ─── Componente principal ─────────────────────────────────────────────────────
export default function IndicadoresPage() {
  const [selectedTab, setSelectedTab] = useState("dec_fec");

  // DEC/FEC
  const [selectedPeriod, setSelectedPeriod] = useState(null);
  const [monthRange, setMonthRange] = useState({ from: null, to: null });
  const [decFecPopoverOpen, setDecFecPopoverOpen] = useState(false);
  const [decAvg, setDecAvg] = useState(null);
  const [fecAvg, setFecAvg] = useState(null);
  const [rankingData, setRankingData] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [decFecLoading, setDecFecLoading] = useState(false);

  // Perdas
  const [perdasPeriod, setPerdasPeriod] = useState(null);
  const [dateRange, setDateRange] = useState({ from: null, to: null });
  const [perdasPopoverOpen, setPerdasPopoverOpen] = useState(false);
  const [perdasData, setPerdasData] = useState([]);
  const [perdasLoading, setPerdasLoading] = useState(false);

  // TAM/SAM
  const [tamTotal, setTamTotal] = useState(null);
  const [samTotal, setSamTotal] = useState(null);

  //ML Preview
  const [previewChartData, setpreviewChartData] = useState([])

  const fetchTamTotal = async () => {
    const url = `/tam-sam/tam`;
    setDecFecLoading(true);
    try {
      const data = await apiClient.get(url);
      if (typeof data === "string") {
        console.error("[tam-sam] Expected JSON, got text:", data);
        setTamTotal(null);
        return;
      }
      setTamTotal(data.tam_total)
    } catch (error) {
      console.error("[tam-sam] Erro:", error);
    } finally {
      setDecFecLoading(false);
    }
  }

  const fetchSamTotal = async (from, to) => {

    const params = new URLSearchParams({ year: from.year })
    const url = `/tam-sam/sam?${params.toString()}`;
    setDecFecLoading(true);
    try {
      const data = await apiClient.get(url);
      if (typeof data === "string") {
        console.error("[tam-sam] Expected JSON, got text:", data);
        setSamTotal(null);
        return;
      }
      setSamTotal(data)
    } catch (error) {
      console.error("[tam-sam] Erro:", error);
    } finally {
      setDecFecLoading(false);
    }
  }

  // ── DEC/FEC handlers ─────────────────────────────────────────────────────────
  const fetchDecFec = async (from, to) => {
    const url = buildDecFecUrl(from, to);
    console.log("[get-dec-fec] Fetching:", url);
    setDecFecLoading(true);
    try {
      const data = await apiClient.get(url);
      if (typeof data === "string") {
        console.error("[get-dec-fec] Expected JSON, got text:", data);
        setDecAvg(null);
        setFecAvg(null);
        setRankingData([]);
        setChartData([]);
        setpreviewChartData([])
        return;
      }
      setDecAvg(
        calcAverage(data.filter((d) => d.indicator_type_code === "DEC")),
      );
      setFecAvg(
        calcAverage(data.filter((d) => d.indicator_type_code === "FEC")),
      );
      setRankingData(buildRanking(data));
      setChartData(buildChartData(data));
      setpreviewChartData(buildPreviewChartData(data))
    } catch (error) {
      console.error("[get-dec-fec] Erro:", error);
    } finally {
      setDecFecLoading(false);
    }
  };

  // ── Preview DEC/FEC handlers ─────────────────────────────────────────────────────────
  const fetchPreviewDecFec = async (from, to) => {

    const params = new URLSearchParams({
      consumer_unit_set_id: 16648,
      year_start: from.year,
      year_end: to.year,
    });

    const url = `/get-dec-fec?${params.toString()}`;
    console.log("[get-dec-fec] Fetching:", url);
    setDecFecLoading(true);
    try {
      const data = await apiClient.get(url);
      if (typeof data === "string") {
        console.error("[get-preview-dec-fec] Expected JSON, got text:", data);
        setpreviewChartData([])
        return;
      }
      setpreviewChartData(buildPreviewChartData(data))
    } catch (error) {
      console.error("[get-preview-dec-fec] Erro:", error);
    } finally {
      setDecFecLoading(false);
    }
  };

  const handleQuickPeriod = (period) => {
    setSelectedPeriod(period.label);
    const from = monthsAgo(period.months);
    const to = currentMonth();
    setMonthRange({ from, to });
    fetchDecFec(from, to);
    fetchTamTotal();
    fetchSamTotal(from, to);
  };

  const handleMonthRangeChange = (range) => {
    setMonthRange(range);
    setSelectedPeriod(null);
    if (range.from && range.to) {
      fetchDecFec(range.from, range.to);
      setDecFecPopoverOpen(false);
      fetchTamTotal();
      fetchSamTotal(range.from, range.to);
    }
  };

  const decFecPeriodLabel =
    selectedPeriod ??
    (monthRange.from && monthRange.to
      ? `${formatMonthLabel(monthRange.from)} → ${formatMonthLabel(monthRange.to)}`
      : null);

  // ── Perdas handlers ───────────────────────────────────────────────────────────
  const fetchPerdas = async (from, to) => {
    const url = buildPerdasUrl(from, to);
    console.log("[get-energy-losses] Fetching:", url);
    setPerdasLoading(true);
    try {
      const data = await apiClient.get(url);
      if (typeof data === "string") {
        console.error("[get-energy-losses] Expected JSON, got text:", data);
        setPerdasData([]);
        return;
      }
      setPerdasData(data);
    } catch (error) {
      console.error("[get-energy-losses] Erro:", error);
    } finally {
      setPerdasLoading(false);
    }
  };

  const handlePerdasQuickPeriod = (period) => {
    setPerdasPeriod(period.label);
    const to = new Date();
    const from = daysAgoDate(period.days);
    setDateRange({ from, to });
    fetchPerdas(from, to);
  };

  const handleDateRangeChange = (range) => {
    setDateRange(range);
    setPerdasPeriod(null);
    if (range.from && range.to) {
      fetchPerdas(range.from, range.to);
      setPerdasPopoverOpen(false);
    }
  };

  const perdasPeriodLabel =
    perdasPeriod ??
    (dateRange.from && dateRange.to
      ? `${formatDateLabel(dateRange.from)} → ${formatDateLabel(dateRange.to)}`
      : null);

  // ── Totais perdas ─────────────────────────────────────────────────────────────
  const perdasCards = [
    {
      id: "tech_mwh",
      titulo: "Perdas Técnicas (MWh)",
      valor: formatMWh(sumField(perdasData, "technical_loss_mwh")),
      icon: <TrendingDown className="w-4 h-4 text-chart-1" />,
      cor: "text-chart-1",
    },
    {
      id: "ntech_mwh",
      titulo: "Perdas Não Técnicas (MWh)",
      valor: formatMWh(sumField(perdasData, "non_technical_loss_mwh")),
      icon: <TrendingUp className="w-4 h-4 text-destructive" />,
      cor: "text-destructive",
    },
    {
      id: "tech_brl",
      titulo: "Custo Perdas Técnicas",
      valor: formatBRL(sumField(perdasData, "technical_loss_cost_brl")),
      icon: <TrendingDown className="w-4 h-4 text-chart-1" />,
      cor: "text-chart-1",
    },
    {
      id: "ntech_brl",
      titulo: "Custo Perdas Não Técnicas",
      valor: formatBRL(sumField(perdasData, "non_technical_loss_cost_brl")),
      icon: <TrendingUp className="w-4 h-4 text-destructive" />,
      cor: "text-destructive",
    },
  ];

  return (
    <div className="flex flex-col gap-4">
      {/* ── Header ── */}
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

        {/* Filtros — diferentes por aba */}
        {selectedTab === "dec_fec" ? (
          <div className="flex gap-2 flex-wrap items-center">
            {DEC_FEC_QUICK_PERIODS.map((period) => (
              <Button
                key={period.label}
                variant={
                  selectedPeriod === period.label ? "secondary" : "ghost"
                }
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
            <Popover
              open={decFecPopoverOpen}
              onOpenChange={setDecFecPopoverOpen}
            >
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
        ) : (
          <div className="flex gap-2 flex-wrap items-center">
            {PERDAS_QUICK_PERIODS.map((period) => (
              <Button
                key={period.label}
                variant={perdasPeriod === period.label ? "secondary" : "ghost"}
                size="sm"
                onClick={() => handlePerdasQuickPeriod(period)}
                className={
                  perdasPeriod === period.label
                    ? "bg-secondary text-secondary-foreground"
                    : "text-muted-foreground hover:text-foreground"
                }
              >
                {period.label}
              </Button>
            ))}
            <Popover
              open={perdasPopoverOpen}
              onOpenChange={setPerdasPopoverOpen}
            >
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  className="border-border text-foreground hover:bg-muted"
                >
                  <CalendarIcon className="w-4 h-4 mr-2" />
                  {dateRange.from && dateRange.to && !perdasPeriod
                    ? `${formatDateLabel(dateRange.from)} → ${formatDateLabel(dateRange.to)}`
                    : "Personalizado"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="end">
                <DayRangePicker
                  value={dateRange}
                  onChange={handleDateRangeChange}
                />
              </PopoverContent>
            </Popover>
          </div>
        )}
      </div>

      {/* ── DEC/FEC Tab ── */}
      {selectedTab === "dec_fec" ? (
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_400px] gap-4">
          <div className="flex flex-col gap-6">
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <Card className="bg-card border-border">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    DEC Médio
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-foreground">
                    {decFecLoading
                      ? "..."
                      : decAvg !== null
                        ? `${decAvg}h`
                        : "—"}
                  </div>
                  <div className="flex items-center gap-1 mt-1">
                    <span className="text-sm text-muted-foreground">
                      {decFecPeriodLabel
                        ? `${decFecPeriodLabel}`
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
                    {decFecLoading ? "..." : fecAvg !== null ? fecAvg : "—"}
                  </div>
                  <div className="flex items-center gap-1 mt-1">
                    <span className="text-sm text-muted-foreground">
                      {decFecPeriodLabel
                        ? `${decFecPeriodLabel}`
                        : "Selecione um período"}
                    </span>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-card border-border">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    TAM Calculado
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-foreground">
                    {decFecLoading ? "..." : tamTotal !== null ? tamTotal : "—"}
                  </div>
                  <div className="flex items-center gap-1 mt-1">
                    <span className="text-sm text-muted-foreground">
                      {decFecPeriodLabel ? decFecPeriodLabel : "Selecione um período"}
                    </span>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-card border-border">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    SAM Calculado
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-foreground">
                    {decFecLoading ? "..." : samTotal !== null ? samTotal : "—"}
                  </div>
                  <div className="flex items-center gap-1 mt-1">
                    <span className="text-sm text-muted-foreground">
                      {decFecPeriodLabel ? decFecPeriodLabel : "Selecione um período"}
                    </span>
                  </div>
                </CardContent>
              </Card>
            </div>
            <Card className="bg-card border-border flex-1">
              <CardHeader className="pb-2">
                <CardTitle className="text-foreground">
                  Evolução DEC/FEC
                </CardTitle>
                <CardDescription className="text-muted-foreground">
                  {decFecPeriodLabel
                    ? `Histórico · ${decFecPeriodLabel}`
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
                          0,
                          Math.ceil(dataMax * 1.2),
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

            <Card className="bg-card border-border flex-1">
              <CardHeader className="pb-2">
                <CardTitle className="text-foreground">
                  Previsão DEC/FEC
                </CardTitle>
                <CardDescription className="text-muted-foreground">
                  {decFecPeriodLabel
                    ? `Previsão · ${decFecPeriodLabel}`
                    : "Selecione um período"}
                </CardDescription>
              </CardHeader>
              <CardContent className="pb-4">
                <div className="h-40 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={previewChartData}
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
                          const item = previewChartData[index];
                          if (!item) return label;
                          const years = [
                            ...new Set(previewChartData.map((d) => d.year)),
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
                          0,
                          Math.ceil(dataMax * 1.2),
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
                              ...new Set(previewChartData.map((d) => d.year)),
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
                      Previsão DEC (horas)
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-[#22c55e]" />
                    <span className="text-sm text-muted-foreground">
                      Previsão FEC (interrupções)
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card
            className="bg-card border-border lg:row-span-2 flex flex-col"
            style={{ maxHeight: 875 }}
          >
            <CardHeader className="flex-shrink-0">
              <CardTitle className="text-foreground">
                Ranking de Distribuidoras
              </CardTitle>
              <CardDescription className="text-muted-foreground">
                Ordenado por indicador DEC
              </CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-auto max-h-[780px]">
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
                    {decFecLoading ? (
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
        /* ── Perdas Tab ── */
        <div className="flex flex-col gap-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
            {perdasCards.map((card) => (
              <Card key={card.id} className="bg-card border-border">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Total {card.titulo}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-foreground">
                    {perdasLoading
                      ? "..."
                      : perdasData.length
                        ? card.valor
                        : "—"}
                  </div>
                  <div className="flex items-center gap-1 mt-1">
                    <span className={`text-sm`}>
                      {perdasPeriodLabel
                        ? `Total · ${perdasPeriodLabel}`
                        : "Selecione um período"}
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Tabela detalhada por distribuidora */}
          <Card
            className="bg-card border-border flex flex-col"
            style={{ maxHeight: 340 }}
          >
            <CardHeader className="flex-shrink-0">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-foreground">
                    Distribuidoras
                  </CardTitle>
                  <CardDescription className="text-muted-foreground">
                    {perdasPeriodLabel
                      ? `Dados do período · ${perdasPeriodLabel}`
                      : "Selecione um período para ver os dados"}
                  </CardDescription>
                </div>
                <Popover>
                  <PopoverTrigger asChild>
                    <button className="p-1.5 rounded-full hover:bg-muted transition-colors">
                      <Info className="w-4 h-4 text-muted-foreground" />
                    </button>
                  </PopoverTrigger>
                  <PopoverContent className="w-80" align="end">
                    <div className="space-y-3">
                      <div>
                        <h4 className="font-semibold text-sm mb-2 text-foreground">
                          Unidades de Energia
                        </h4>
                        <div className="space-y-1.5 text-xs text-muted-foreground">
                          <div>
                            <span className="font-medium">MWh</span>{" "}
                            (Megawatt-hora) = 1.000 kWh
                          </div>
                          <div>
                            <span className="font-medium">GWh</span>{" "}
                            (Gigawatt-hora) = 1.000 MWh
                          </div>
                          <div>
                            <span className="font-medium">TWh</span>{" "}
                            (Terawatt-hora) = 1.000 GWh
                          </div>
                        </div>
                      </div>
                      <div className="border-t border-border pt-3">
                        <h4 className="font-semibold text-sm mb-2 text-foreground">
                          Tipos de Perdas
                        </h4>
                        <div className="space-y-2 text-xs text-muted-foreground">
                          <div>
                            <span className="font-medium text-chart-1">
                              Perdas Técnicas:
                            </span>{" "}
                            Energia perdida naturalmente na transmissão e
                            distribuição devido à resistência dos condutores e
                            transformadores.
                          </div>
                          <div>
                            <span className="font-medium text-destructive">
                              Perdas Não Técnicas:
                            </span>{" "}
                            Perdas causadas por furtos de energia, erros de
                            medição, fraudes e irregularidades.
                          </div>
                        </div>
                      </div>
                    </div>
                  </PopoverContent>
                </Popover>
              </div>
            </CardHeader>
            <CardContent className="flex-1 overflow-auto p-0">
              <div className="overflow-auto h-full">
                <table className="w-full">
                  <thead className="sticky top-0 z-10 bg-card">
                    <tr className="border-b border-border">
                      <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                        Distribuidora
                      </th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                        UF
                      </th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                        Perd. Técnica
                      </th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                        Perd. Não Técnica
                      </th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                        Custo Perd. Técnica
                      </th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                        Custo Perd. Não Técnica
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {perdasLoading ? (
                      <tr>
                        <td
                          colSpan={6}
                          className="py-8 text-center text-sm text-muted-foreground"
                        >
                          Carregando...
                        </td>
                      </tr>
                    ) : perdasData.length > 0 ? (
                      perdasData.map((row, i) => (
                        <tr
                          key={i}
                          className="border-b border-border/50 hover:bg-muted/50 transition-colors"
                        >
                          <td className="py-3 px-4 text-sm text-foreground font-medium">
                            {row.distributor}
                          </td>
                          <td className="py-3 px-4 text-sm text-muted-foreground">
                            {row.uf}
                          </td>
                          <td className="py-3 px-4 text-sm text-foreground text-right">
                            {formatMWh(row.technical_loss_mwh)}
                          </td>
                          <td className="py-3 px-4 text-sm text-foreground text-right">
                            {formatMWh(row.non_technical_loss_mwh)}
                          </td>
                          <td className="py-3 px-4 text-sm text-foreground text-right">
                            {formatBRL(row.technical_loss_cost_brl)}
                          </td>
                          <td className="py-3 px-4 text-sm text-foreground text-right">
                            {formatBRL(row.non_technical_loss_cost_brl)}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td
                          colSpan={6}
                          className="py-8 text-center text-sm text-muted-foreground"
                        >
                          Selecione um período para ver os dados
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
