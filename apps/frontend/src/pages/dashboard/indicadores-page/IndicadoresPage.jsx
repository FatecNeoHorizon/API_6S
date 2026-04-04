import { useState, useEffect } from "react";
import {
  TrendingUp,
  TrendingDown,
  Calendar as CalendarIcon,
  Filter,
  BarChart3,
  Zap,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
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

const periods = ["3 meses", "6 meses", "9 meses", "1 ano"];

const periodMonths = {
  "3 meses": 3,
  "6 meses": 6,
  "9 meses": 9,
  "1 ano": 12,
};

const formatDate = (date) => date.toISOString().split("T")[0];

const getPeriodRange = (periodLabel) => {
  const today = new Date();
  const months = periodMonths[periodLabel];
  const past = new Date(today);
  past.setMonth(past.getMonth() - months);
  return { from: formatDate(past), to: formatDate(today) };
};

// Filter API records by generation_date within [from, to] and indicator type
const filterByPeriodAndType = (data, from, to, type) => {
  return data.filter((item) => {
    const d = item.generation_date;
    return item.indicator_type_code === type && d >= from && d <= to;
  });
};

// Calculate average and log the formula to console
const calcAverage = (records, type) => {
  if (!records.length) return null;
  const values = records.map((r) => r.value);
  const sum = values.reduce((acc, v) => acc + v, 0);
  const avg = sum / values.length;
  const formula = values.join(" + ");
  console.log(
    `Média do ${type}: ${formula} = ${sum.toFixed(2)} / ${values.length} = ${avg.toFixed(2)}`,
  );
  return parseFloat(avg.toFixed(2));
};

const decFecData = [
  { mes: "Jan", dec: 12.5, fec: 7.2 },
  { mes: "Fev", dec: 11.8, fec: 6.9 },
  { mes: "Mar", dec: 13.2, fec: 7.8 },
  { mes: "Abr", dec: 12.1, fec: 7 },
  { mes: "Mai", dec: 11.5, fec: 6.5 },
  { mes: "Jun", dec: 10.8, fec: 6.2 },
];

const distribuidoras = [
  { nome: "CPFL Paulista", dec: 8.5, fec: 4.2 },
  { nome: "CEMIG-D", dec: 12.3, fec: 6.8 },
  { nome: "Light", dec: 15.2, fec: 8.5 },
  { nome: "COPEL-DIS", dec: 9.1, fec: 5.1 },
  { nome: "CELESC-DIS", dec: 10.5, fec: 5.8 },
  { nome: "ELEKTRO", dec: 11.8, fec: 6.5 },
  { nome: "COELBA", dec: 16.5, fec: 9.2 },
  { nome: "CELPE", dec: 14.2, fec: 7.9 },
];

const perdas = [
  {
    id: "tecnicas quilowatt-hora",
    tipo: "Perdas quilowatt-hora (kWh)",
    valor: 7.8,
    meta: 8,
    trend: "down",
  },
  {
    id: "tecnicas reais brl",
    tipo: "Perdas R$ (BRL)",
    valor: 12.5,
    meta: 10,
    trend: "up",
  },
  {
    id: "totais",
    tipo: "Perdas Totais",
    valor: 20.3,
    meta: 18,
    trend: "up",
  },
];

export default function IndicadoresPage() {
  const [selectedPeriod, setSelectedPeriod] = useState(null);
  const [selectedTab, setSelectedTab] = useState("dec_fec");
  const [date, setDate] = useState({ from: undefined, to: undefined });
  const [apiData, setApiData] = useState([]);
  const [decAvg, setDecAvg] = useState(null);
  const [fecAvg, setFecAvg] = useState(null);

  // Fetch DEC/FEC data on mount
  useEffect(() => {
    const fetchDecFec = async () => {
      try {
        const response = await fetch("http://localhost:8000/get-dec-fec");
        const data = await response.json();
        console.log("[get-dec-fec] Response:", data);
        setApiData(data);
      } catch (error) {
        console.error("[get-dec-fec] Erro ao buscar dados:", error);
      }
    };

    fetchDecFec();
  }, []);

  const computeAverages = (period, data) => {
    const { from, to } = getPeriodRange(period);

    const decRecords = filterByPeriodAndType(data, from, to, "DEC");
    const fecRecords = filterByPeriodAndType(data, from, to, "FEC");

    console.log(`\n--- Dados filtrados para "${period}" (${from} → ${to}) ---`);
    console.log("Registros DEC encontrados:", decRecords);
    console.log("Registros FEC encontrados:", fecRecords);

    const avgDec = calcAverage(decRecords, "DEC");
    const avgFec = calcAverage(fecRecords, "FEC");

    setDecAvg(avgDec);
    setFecAvg(avgFec);
  };

  const handleSelectPeriod = (period) => {
    setSelectedPeriod(period);
    const { from, to } = getPeriodRange(period);
    console.log(`Período selecionado: ${to} - ${from}`);
    computeAverages(period, apiData);
  };

  const handleSelectDate = (newDate) => {
    setDate(newDate);
    if (newDate?.from) console.log("Data inicial:", formatDate(newDate.from));
    if (newDate?.to) console.log("Data final:", formatDate(newDate.to));
  };

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
        <div className="flex gap-2 flex-wrap">
          {periods.map((period) => (
            <Button
              key={period}
              variant={selectedPeriod === period ? "secondary" : "ghost"}
              size="sm"
              onClick={() => handleSelectPeriod(period)}
              className={
                selectedPeriod === period
                  ? "bg-secondary text-secondary-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }
            >
              {period}
            </Button>
          ))}
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                className="border-border text-foreground hover:bg-muted"
              >
                <CalendarIcon className="w-4 h-4 mr-2" />
                Personalizado
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="end">
              <Calendar
                mode="range"
                selected={date}
                onSelect={handleSelectDate}
                initialFocus
              />
            </PopoverContent>
          </Popover>
        </div>
      </div>

      {selectedTab === "dec_fec" ? (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_400px] gap-4">
            {/* Left Column */}
            <div className="flex flex-col gap-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Card className="bg-card border-border">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      DEC Medio
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-foreground">
                      {decAvg !== null ? `${decAvg}h` : "—"}
                    </div>
                    <div className="flex items-center gap-1 mt-1">
                      <TrendingDown className="w-4 h-4 text-chart-1" />
                      <span className="text-sm text-muted-foreground">
                        {selectedPeriod
                          ? `Média · ${selectedPeriod}`
                          : "Selecione um período"}
                      </span>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-card border-border">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      FEC Medio
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-foreground">
                      {fecAvg !== null ? fecAvg : "—"}
                    </div>
                    <div className="flex items-center gap-1 mt-1">
                      <TrendingDown className="w-4 h-4 text-chart-1" />
                      <span className="text-sm text-muted-foreground">
                        {selectedPeriod
                          ? `Média · ${selectedPeriod}`
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
                    Evolucao DEC/FEC
                  </CardTitle>
                  <CardDescription className="text-muted-foreground">
                    Historico dos últimos 6 meses
                  </CardDescription>
                </CardHeader>
                <CardContent className="pb-4">
                  <div className="h-40 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={decFecData}
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
                        />
                        <YAxis
                          axisLine={false}
                          tickLine={false}
                          tick={{
                            fill: "hsl(var(--muted-foreground))",
                            fontSize: 12,
                          }}
                          domain={[0, 15]}
                        />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: "hsl(var(--background))",
                            border: "1px solid hsl(var(--border))",
                            borderRadius: "8px",
                          }}
                          labelStyle={{ color: "hsl(var(--foreground))" }}
                        />
                        <Line
                          type="monotone"
                          dataKey="dec"
                          name="DEC (horas)"
                          stroke="#3b82f6"
                          strokeWidth={2}
                          dot={{ fill: "#3b82f6", strokeWidth: 2, r: 4 }}
                          activeDot={{ r: 6, fill: "#3b82f6" }}
                        />
                        <Line
                          type="monotone"
                          dataKey="fec"
                          name="FEC (interrupcoes)"
                          stroke="#22c55e"
                          strokeWidth={2}
                          dot={{ fill: "#22c55e", strokeWidth: 2, r: 4 }}
                          activeDot={{ r: 6, fill: "#22c55e" }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex items-center justify-center gap-4 mt-2">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-chart-1" />
                      <span className="text-sm text-muted-foreground">
                        DEC (horas)
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-chart-2" />
                      <span className="text-sm text-muted-foreground">
                        FEC (interrupcoes)
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Right Column - Distribuidoras Table */}
            <Card className="bg-card border-border h-fit lg:row-span-2">
              <CardHeader>
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
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left py-3 px-2 text-sm font-medium text-muted-foreground">
                          Distribuidora
                        </th>
                        <th className="text-center py-3 px-2 text-sm font-medium text-muted-foreground">
                          DEC
                        </th>
                        <th className="text-center py-3 px-2 text-sm font-medium text-muted-foreground">
                          FEC
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {distribuidoras.map((dist) => (
                        <tr
                          key={dist.nome}
                          className="border-b border-border/50 hover:bg-muted/50 transition-colors"
                        >
                          <td className="py-3 px-2 text-sm text-foreground font-medium">
                            {dist.nome}
                          </td>
                          <td className="py-3 px-2 text-sm text-foreground text-center">
                            {dist.dec}
                          </td>
                          <td className="py-3 px-2 text-sm text-foreground text-center">
                            {dist.fec}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      ) : (
        <>
          {/* Perdas Tab Content */}
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

          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-foreground">
                Evolucao das Perdas
              </CardTitle>
              <CardDescription className="text-muted-foreground">
                Historico mensal de perdas quilowatt-hora (kWh) e reais (BRL)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={decFecData}
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
                    />
                    <YAxis
                      axisLine={false}
                      tickLine={false}
                      tick={{
                        fill: "hsl(var(--muted-foreground))",
                        fontSize: 12,
                      }}
                      domain={[0, 15]}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "hsl(var(--background))",
                        border: "1px solid hsl(var(--border))",
                        borderRadius: "8px",
                      }}
                      labelStyle={{ color: "hsl(var(--foreground))" }}
                    />
                    <Line
                      type="monotone"
                      dataKey="dec"
                      name="Perdas quilowatt-hora (kWh)"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      dot={{ fill: "#3b82f6", strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6, fill: "#3b82f6" }}
                    />
                    <Line
                      type="monotone"
                      dataKey="fec"
                      name="Perdas reais (BRL)"
                      stroke="#22c55e"
                      strokeWidth={2}
                      dot={{ fill: "#22c55e", strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6, fill: "#22c55e" }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="flex items-center justify-center gap-6 mt-4">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-chart-1" />
                  <span className="text-sm text-muted-foreground">
                    Perdas quilowatt-hora (kWh)
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-chart-2" />
                  <span className="text-sm text-muted-foreground">
                    Perdas reais (BRL)
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
