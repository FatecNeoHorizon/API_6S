import { useState } from "react";
import {
  TrendingUp,
  TrendingDown,
  Calendar,
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

const decFecData = [
  { mes: "Jan", dec: 12.5, fec: 7.2 },
  { mes: "Fev", dec: 11.8, fec: 6.9 },
  { mes: "Mar", dec: 13.2, fec: 7.8 },
  { mes: "Abr", dec: 12.1, fec: 7 },
  { mes: "Mai", dec: 11.5, fec: 6.5 },
  { mes: "Jun", dec: 10.8, fec: 6.2 },
];

const distribuidoras = [
  {
    nome: "CPFL Paulista",
    dec: 8.5,
    fec: 4.2,
  },
  {
    nome: "CEMIG-D",
    dec: 12.3,
    fec: 6.8,
  },
  {
    nome: "Light",
    dec: 15.2,
    fec: 8.5,
  },
  {
    nome: "COPEL-DIS",
    dec: 9.1,
    fec: 5.1,
  },
  {
    nome: "CELESC-DIS",
    dec: 10.5,
    fec: 5.8,
  },
  {
    nome: "ELEKTRO",
    dec: 11.8,
    fec: 6.5,
  },
  {
    nome: "COELBA",
    dec: 16.5,
    fec: 9.2,
  },
  {
    nome: "CELPE",
    dec: 14.2,
    fec: 7.9,
  },
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

const barData = [
  { id: "jan", val: 65 },
  { id: "fev", val: 70 },
  { id: "mar", val: 68 },
  { id: "abr", val: 72 },
  { id: "mai", val: 75 },
  { id: "jun", val: 73 },
  { id: "jul", val: 78 },
  { id: "ago", val: 76 },
  { id: "set", val: 80 },
  { id: "out", val: 78 },
  { id: "nov", val: 82 },
  { id: "dez", val: 85 },
];

export default function IndicadoresPage() {
  const [selectedPeriod, setSelectedPeriod] = useState("30 dias");
  const [selectedTab, setSelectedTab] = useState("dec_fec");

  return (
    <div className="flex flex-col gap-6">
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
              onClick={() => setSelectedPeriod(period)}
              className={
                selectedPeriod === period
                  ? "bg-secondary text-secondary-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }
            >
              {period}
            </Button>
          ))}
          <Button
            variant="outline"
            size="sm"
            className="border-border text-foreground hover:bg-muted"
          >
            <Calendar className="w-4 h-4 mr-2" />
            Personalizado
          </Button>
        </div>
      </div>

      {selectedTab === "dec_fec" ? (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="bg-card border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  DEC Medio
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground">12.4h</div>
                <div className="flex items-center gap-1 mt-1">
                  <TrendingDown className="w-4 h-4 text-chart-1" />
                  <span className="text-sm text-chart-1">-8%</span>
                  <span className="text-sm text-muted-foreground">
                    vs. periodo anterior
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
                <div className="text-2xl font-bold text-foreground">7.2</div>
                <div className="flex items-center gap-1 mt-1">
                  <TrendingDown className="w-4 h-4 text-chart-1" />
                  <span className="text-sm text-chart-1">-5%</span>
                  <span className="text-sm text-muted-foreground">
                    vs. periodo anterior
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Chart Area */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-foreground">
                  Evolucao DEC/FEC
                </CardTitle>
                <CardDescription className="text-muted-foreground">
                  Historico dos últimos 6 meses
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
                <div className="flex items-center justify-center gap-6 mt-4">
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

            {/* Distribuidoras Table */}
            <Card className="bg-card border-border">
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
