import { useState } from "react";
import {
    TrendingUp,
    TrendingDown,
    Calendar as CalendarIcon,
    Filter,
    BarChart2,
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
import { Heatmap } from "../../../components/heatmap";

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

export function HeatmapFilters() {
    const [selectedTab, setSelectedTab] = useState("dec");
    const [monthRange, setMonthRange] = useState({ from: null, to: null });

    const handleMonthRangeChange = (range) => {
    setMonthRange(range);
    // setSelectedPeriod(null);
    // if (range.from && range.to) {
    //   fetchDecFec(range.from, range.to);
    //   setDecFecPopoverOpen(false);
    //   fetchTamTotal();
    //   fetchSamTotal(range.from, range.to);
    //   fetchPreviewDecFec(range.from, range.to);
    // }
  };

    return (
        <div className="flex flex-col gap-4">
            <div className="flex flex-col sm:flex-row gap-4 justify-between">
                <div className="flex gap-2">
                    <Button
                        variant={selectedTab === "dec" ? "default" : "outline"}
                        onClick={() => setSelectedTab("dec")}
                        className={
                            selectedTab === "dec"
                                ? "bg-primary text-primary-foreground"
                                : "border-border text-foreground hover:bg-muted"
                        }
                    >
                        <BarChart3 className="w-4 h-4 mr-2" />
                        DEC
                    </Button>
                    <Button
                        variant={selectedTab === "fec" ? "default" : "outline"}
                        onClick={() => setSelectedTab("fec")}
                        className={
                            selectedTab === "fec"
                                ? "bg-primary text-primary-foreground"
                                : "border-border text-foreground hover:bg-muted"
                        }
                    >
                        <BarChart2 className="w-4 h-4 mr-2" />
                        FEC
                    </Button>
                </div>

                <MonthRangePicker
                  value={monthRange}
                  onChange={handleMonthRangeChange}
                />
            </div>

            <Heatmap/>
        </div>
    )

}