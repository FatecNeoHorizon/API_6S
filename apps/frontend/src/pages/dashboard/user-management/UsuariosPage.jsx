import { useState } from "react"
import { Search, Edit, Trash2, User } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

const usuarios = [
  { 
    id: 1, 
    nome: "Admin Principal", 
    email: "admin@tecsys.com.br", 
    perfil: "Administrador", 
    status: "ativo",
    ultimoAcesso: "2026-03-15 10:30",
    criadoEm: "2024-01-15"
  },
  { 
    id: 2, 
    nome: "Maria Silva", 
    email: "maria.silva@tecsys.com.br", 
    perfil: "Analista", 
    status: "ativo",
    ultimoAcesso: "2026-03-14 16:45",
    criadoEm: "2024-03-20"
  },
  { 
    id: 3, 
    nome: "Joao Santos", 
    email: "joao.santos@tecsys.com.br", 
    perfil: "Visualizador", 
    status: "ativo",
    ultimoAcesso: "2026-03-13 09:15",
    criadoEm: "2024-06-10"
  },
  { 
    id: 4, 
    nome: "Ana Costa", 
    email: "ana.costa@tecsys.com.br", 
    perfil: "Analista", 
    status: "inativo",
    ultimoAcesso: "2026-02-28 14:20",
    criadoEm: "2024-08-05"
  },
  { 
    id: 5, 
    nome: "Carlos Oliveira", 
    email: "carlos.oliveira@tecsys.com.br", 
    perfil: "Visualizador", 
    status: "ativo",
    ultimoAcesso: "2026-03-15 08:00",
    criadoEm: "2025-01-12"
  },
]

const getPerfilClassName = (perfil) => {
  if (perfil === "Administrador") return "bg-primary/10 text-primary"
  if (perfil === "Analista") return "bg-chart-2/10 text-chart-2"
  return "bg-muted text-muted-foreground"
}

const getStatusClassName = (status) => {
  return status === "ativo" ? "bg-chart-1/10 text-chart-1" : "bg-muted text-muted-foreground"
}

export default function UsuariosPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState(null)

  const filteredUsers = usuarios.filter(user => {
    const matchSearch = user.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchStatus = statusFilter ? user.status === statusFilter : true
    
    return matchSearch && matchStatus
  })

  const totalUsers = usuarios.length
  const activeUsers = usuarios.filter(u => u.status === "ativo").length
  const inactiveUsers = usuarios.filter(u => u.status === "inativo").length

  return (
    <div className="flex flex-col gap-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="bg-card border-border cursor-pointer hover:shadow-lg transition-shadow" onClick={() => setStatusFilter(null)}>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total de Usuarios</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{totalUsers}</div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border cursor-pointer hover:shadow-lg transition-shadow" onClick={() => setStatusFilter("ativo")}>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Usuarios Ativos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-chart-1">{activeUsers}</div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border cursor-pointer hover:shadow-lg transition-shadow" onClick={() => setStatusFilter("inativo")}>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Usuarios Inativos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-muted-foreground">{inactiveUsers}</div>
          </CardContent>
        </Card>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder="Buscar por nome ou email..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10 bg-input border-border text-foreground placeholder:text-muted-foreground"
        />
      </div>

      {/* Users Table */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-foreground">Lista de Usuarios</CardTitle>
          <CardDescription className="text-muted-foreground">
            Gerencie os usuarios do sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-2 text-sm font-medium text-muted-foreground">Usuario</th>
                  <th className="text-left py-3 px-2 text-sm font-medium text-muted-foreground">Email</th>
                  <th className="text-center py-3 px-2 text-sm font-medium text-muted-foreground">Perfil</th>
                  <th className="text-center py-3 px-2 text-sm font-medium text-muted-foreground">Status</th>
                  <th className="text-center py-3 px-2 text-sm font-medium text-muted-foreground">Ultimo Acesso</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((user) => (
                  <tr key={user.id} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                    <td className="py-3 px-2">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                          <span className="text-sm font-medium text-primary">
                            {user.nome.split(" ").map(n => n[0]).join("").slice(0, 2)}
                          </span>
                        </div>
                        <span className="text-sm font-medium text-foreground">{user.nome}</span>
                      </div>
                    </td>
                    <td className="py-3 px-2 text-sm text-muted-foreground">{user.email}</td>
                    <td className="py-3 px-2 text-center">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getPerfilClassName(user.perfil)}`}>
                        {user.perfil}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-center">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusClassName(user.status)}`}>
                        {user.status === "ativo" ? "Ativo" : "Inativo"}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-sm text-muted-foreground text-center">{user.ultimoAcesso}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
