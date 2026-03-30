import { Link } from "react-router-dom";
import {
  Activity,
  Zap,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  MapPin,
  Users,
  BarChart3,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const statsCards = [
  {
    id: "distribuidoras",
    title: "Total de Distribuidoras",
    value: "53",
    change: "+2",
    trend: "up",
    icon: Zap,
    description: "distribuidoras ativas",
  },
  {
    id: "dec",
    title: "Indice DEC Medio",
    value: "12.4h",
    change: "-8%",
    trend: "down",
    icon: Activity,
    description: "vs. mes anterior",
  },
  {
    id: "fec",
    title: "Indice FEC Medio",
    value: "7.2",
    change: "-5%",
    trend: "down",
    icon: BarChart3,
    description: "interrupcoes/consumidor",
  },
  {
    id: "criticas",
    title: "Areas Criticas",
    value: "12",
    change: "+3",
    trend: "up",
    icon: AlertTriangle,
    description: "regioes identificadas",
  },
];

const recentActivities = [
  {
    id: "sp-norte",
    region: "SP Norte",
    type: "DEC Alto",
    value: "18.5h",
    status: "critico",
  },
  {
    id: "rj-centro",
    region: "RJ Centro",
    type: "FEC Alto",
    value: "12.3",
    status: "alerta",
  },
  {
    id: "mg-sul",
    region: "MG Sul",
    type: "Perda Tecnica",
    value: "8.2%",
    status: "alerta",
  },
  {
    id: "pr-oeste",
    region: "PR Oeste",
    type: "DEC Alto",
    value: "15.1h",
    status: "critico",
  },
  {
    id: "ba-norte",
    region: "BA Norte",
    type: "FEC Alto",
    value: "9.8",
    status: "normal",
  },
];

const topRegions = [
  { id: "sp", name: "Sao Paulo", distribuidoras: 12, dec: 10.2, fec: 5.8 },
  { id: "rj", name: "Rio de Janeiro", distribuidoras: 8, dec: 14.5, fec: 8.2 },
  { id: "mg", name: "Minas Gerais", distribuidoras: 10, dec: 11.8, fec: 6.5 },
  { id: "pr", name: "Parana", distribuidoras: 6, dec: 9.5, fec: 5.2 },
  { id: "ba", name: "Bahia", distribuidoras: 7, dec: 16.2, fec: 9.1 },
];

function getActivityDotColor(status) {
  if (status === "critico") return "bg-destructive";
  if (status === "alerta") return "bg-chart-3";
  return "bg-chart-1";
}

function getActivityTextColor(status) {
  if (status === "critico") return "text-destructive";
  if (status === "alerta") return "text-chart-3";
  return "text-chart-1";
}

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statsCards.map((stat) => (
          <Card key={stat.id} className="bg-card border-border">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <div className="p-2 bg-primary/10 rounded-lg">
                <stat.icon className="w-4 h-4 text-primary" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">
                {stat.value}
              </div>
              <div className="flex items-center gap-1 mt-1">
                {stat.trend === "up" ? (
                  <TrendingUp className="w-4 h-4 text-chart-1" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-chart-1" />
                )}
                <span className="text-sm text-chart-1">{stat.change}</span>
                <span className="text-sm text-muted-foreground">
                  {stat.description}
                </span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activities */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-foreground">
              Atividades Recentes
            </CardTitle>
            <CardDescription className="text-muted-foreground">
              Ultimas ocorrencias registradas no sistema
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-3">
              {recentActivities.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-2 h-2 rounded-full ${getActivityDotColor(activity.status)}`}
                    />
                    <div>
                      <p className="text-sm font-medium text-foreground">
                        {activity.region}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {activity.type}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-foreground">
                      {activity.value}
                    </p>
                    <p
                      className={`text-xs capitalize ${getActivityTextColor(activity.status)}`}
                    >
                      {activity.status}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Top Regions */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-foreground">Top Regioes</CardTitle>
            <CardDescription className="text-muted-foreground">
              Regioes com maior numero de distribuidoras
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-3">
              {topRegions.map((region) => (
                <div
                  key={region.id}
                  className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                      <MapPin className="w-4 h-4 text-primary" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-foreground">
                        {region.name}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {region.distribuidoras} distribuidoras
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4 text-right">
                    <div>
                      <p className="text-xs text-muted-foreground">DEC</p>
                      <p className="text-sm font-medium text-foreground">
                        {region.dec}h
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">FEC</p>
                      <p className="text-sm font-medium text-foreground">
                        {region.fec}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-foreground">Acoes Rapidas</CardTitle>
          <CardDescription className="text-muted-foreground">
            Acesse rapidamente as principais funcionalidades
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Link
              to="/dashboard/indicadores"
              className="flex items-center gap-3 p-4 bg-muted/50 rounded-lg hover:bg-muted transition-colors"
            >
              <div className="p-2 bg-chart-2/10 rounded-lg">
                <BarChart3 className="w-5 h-5 text-chart-2" />
              </div>
              <div>
                <p className="text-sm font-medium text-foreground">
                  Indicadores
                </p>
                <p className="text-xs text-muted-foreground">DEC e FEC</p>
              </div>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
