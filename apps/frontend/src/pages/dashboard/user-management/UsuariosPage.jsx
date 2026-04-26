import { useEffect, useState } from "react"
import { Search, Edit, Trash2, User, Loader2, X, AlertTriangle } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { toast } from "sonner"
import { apiClient } from "@/api/client"

const mockProfiles = [
  {
    profile_uuid: "11111111-1111-1111-1111-111111111111",
    profile_name: "ADMIN",
  },
  {
    profile_uuid: "22222222-2222-2222-2222-222222222222",
    profile_name: "ANALYST",
  },
  {
    profile_uuid: "33333333-3333-3333-3333-333333333333",
    profile_name: "MANAGER",
  },
]

const mockUsers = [
  {
    user_uuid: "a28e4f8b-948f-4f72-b173-6cfc64ac0011",
    username: "admin.principal",
    profile_id: "11111111-1111-1111-1111-111111111111",
    active: true,
    created_at: "2024-01-15T10:30:00Z",
    updated_at: "2026-03-15T10:30:00Z",
  },
  {
    user_uuid: "b28e4f8b-948f-4f72-b173-6cfc64ac0022",
    username: "maria.silva",
    profile_id: "22222222-2222-2222-2222-222222222222",
    active: true,
    created_at: "2024-03-20T16:45:00Z",
    updated_at: "2026-03-14T16:45:00Z",
  },
  {
    user_uuid: "c28e4f8b-948f-4f72-b173-6cfc64ac0033",
    username: "joao.santos",
    profile_id: "33333333-3333-3333-3333-333333333333",
    active: true,
    created_at: "2024-06-10T09:15:00Z",
    updated_at: "2026-03-13T09:15:00Z",
  },
  {
    user_uuid: "d28e4f8b-948f-4f72-b173-6cfc64ac0044",
    username: "ana.costa",
    profile_id: "22222222-2222-2222-2222-222222222222",
    active: false,
    created_at: "2024-08-05T14:20:00Z",
    updated_at: "2026-02-28T14:20:00Z",
  },
  {
    user_uuid: "e28e4f8b-948f-4f72-b173-6cfc64ac0055",
    username: "carlos.oliveira",
    profile_id: "33333333-3333-3333-3333-333333333333",
    active: true,
    created_at: "2025-01-12T08:00:00Z",
    updated_at: "2026-03-15T08:00:00Z",
  },
  {
    user_uuid: "f28e4f8b-948f-4f72-b173-6cfc64ac0066",
    username: "fernanda.rocha",
    profile_id: "22222222-2222-2222-2222-222222222222",
    active: true,
    created_at: "2025-02-08T13:25:00Z",
    updated_at: "2026-03-11T13:25:00Z",
  },
  {
    user_uuid: "a38e4f8b-948f-4f72-b173-6cfc64ac0077",
    username: "bruno.almeida",
    profile_id: "33333333-3333-3333-3333-333333333333",
    active: false,
    created_at: "2025-03-01T17:40:00Z",
    updated_at: "2026-02-20T17:40:00Z",
  },
  {
    user_uuid: "b38e4f8b-948f-4f72-b173-6cfc64ac0088",
    username: "patricia.lima",
    profile_id: "11111111-1111-1111-1111-111111111111",
    active: true,
    created_at: "2025-03-22T11:10:00Z",
    updated_at: "2026-03-15T11:10:00Z",
  },
  {
    user_uuid: "c38e4f8b-948f-4f72-b173-6cfc64ac0099",
    username: "ricardo.mendes",
    profile_id: "22222222-2222-2222-2222-222222222222",
    active: true,
    created_at: "2025-04-14T09:05:00Z",
    updated_at: "2026-03-10T09:05:00Z",
  },
  {
    user_uuid: "d38e4f8b-948f-4f72-b173-6cfc64ac0100",
    username: "juliana.pereira",
    profile_id: "33333333-3333-3333-3333-333333333333",
    active: true,
    created_at: "2025-05-06T15:55:00Z",
    updated_at: "2026-03-09T15:55:00Z",
  },
  {
    user_uuid: "e38e4f8b-948f-4f72-b173-6cfc64ac0111",
    username: "thiago.barbosa",
    profile_id: "22222222-2222-2222-2222-222222222222",
    active: false,
    created_at: "2025-06-18T10:00:00Z",
    updated_at: "2026-01-18T10:00:00Z",
  },
]

const DEFAULT_PAGE_SIZE = 5
const PAGE_SIZE_OPTIONS = [5, 10, 25, 50, 100]

const normalizeUser = (user) => ({
  user_uuid: user.user_uuid,
  username: user.username,
  profile_id: user.profile_id,
  active: Boolean(user.active),
  created_at: user.created_at,
  updated_at: user.updated_at,
})

const normalizeProfiles = (profiles) =>
  profiles.map((profile) => ({
    profile_uuid: profile.profile_uuid,
    profile_name: profile.profile_name,
  }))

const resolvePayloadArray = (payload) => {
  if (Array.isArray(payload)) return payload
  if (Array.isArray(payload?.data)) return payload.data
  return []
}

const formatDate = (value) => {
  if (!value) return "-"

  const parsedDate = new Date(value)
  if (Number.isNaN(parsedDate.getTime())) return value

  return parsedDate.toLocaleDateString("pt-BR")
}

const getProfileName = (profileId, profiles) => {
  const found = profiles.find((profile) => profile.profile_uuid === profileId)
  return found?.profile_name || profileId
}

const buildPaginatedUsersResponse = ({ page, pageSize, username, status, sourceUsers }) => {
  const normalizedSearch = username.trim().toLowerCase()

  const filtered = sourceUsers.filter((user) => {
    const matchesUsername = normalizedSearch
      ? user.username.toLowerCase().includes(normalizedSearch)
      : true

    let matchesStatus = true
    if (status === "active") {
      matchesStatus = user.active
    } else if (status === "inactive") {
      matchesStatus = !user.active
    }

    return matchesUsername && matchesStatus
  })

  const total = filtered.length
  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  const safePage = Math.min(Math.max(1, page), totalPages)
  const startIndex = (safePage - 1) * pageSize
  const endIndex = startIndex + pageSize

  return {
    data: filtered.slice(startIndex, endIndex),
    meta: {
      page: safePage,
      pageSize,
      total,
      totalPages,
      hasNext: safePage < totalPages,
      hasPrev: safePage > 1,
    },
  }
}

const getPerfilClassName = (perfil) => {
  if (perfil === "ADMIN") return "bg-primary/10 text-primary"
  if (perfil === "ANALYST") return "bg-chart-2/10 text-chart-2"
  return "bg-muted text-muted-foreground"
}

const getStatusClassName = (active) => {
  return active ? "bg-chart-1/10 text-chart-1" : "bg-muted text-muted-foreground"
}

export default function UsuariosPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE)
  const [profiles, setProfiles] = useState(mockProfiles)
  const [allUsers, setAllUsers] = useState(mockUsers)
  const [usersPage, setUsersPage] = useState({
    data: [],
    meta: {
      page: 1,
      pageSize: DEFAULT_PAGE_SIZE,
      total: 0,
      totalPages: 1,
      hasNext: false,
      hasPrev: false,
    },
  })
  const [isLoading, setIsLoading] = useState(true)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)
  const [editForm, setEditForm] = useState({
    username: "",
    profile_id: "",
  })

  useEffect(() => {
    let isMounted = true

    const loadInitialData = async () => {
      setIsLoading(true)

      try {
        const [profilesResponse, usersResponse] = await Promise.all([
          apiClient.get("/users/profiles"),
          apiClient.get("/users/"),
        ])

        const apiProfiles = normalizeProfiles(resolvePayloadArray(profilesResponse))
        const apiUsers = resolvePayloadArray(usersResponse).map(normalizeUser)

        if (!isMounted) return

        if (apiProfiles.length > 0) {
          setProfiles(apiProfiles)
        }

        if (apiUsers.length > 0) {
          setAllUsers(apiUsers)
        }
      } catch {
        if (!isMounted) return

        setProfiles(mockProfiles)
        setAllUsers(mockUsers)
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    loadInitialData()

    return () => {
      isMounted = false
    }
  }, [])

  useEffect(() => {
    const response = buildPaginatedUsersResponse({
      page: currentPage,
      pageSize,
      username: searchTerm,
      status: statusFilter,
      sourceUsers: allUsers,
    })

    setUsersPage(response)

    if (response.meta.page !== currentPage) {
      setCurrentPage(response.meta.page)
    }
  }, [currentPage, pageSize, searchTerm, statusFilter, allUsers])

  const totalUsers = allUsers.length
  const activeUsers = allUsers.filter((u) => u.active).length
  const inactiveUsers = allUsers.filter((u) => !u.active).length

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value)
    setCurrentPage(1)
  }

  const handleStatusFilterChange = (event) => {
    setStatusFilter(event.target.value)
    setCurrentPage(1)
  }

  const handlePageSizeChange = (event) => {
    setPageSize(Number(event.target.value))
    setCurrentPage(1)
  }

  const openEditModal = (user) => {
    setSelectedUser(user)
    setEditForm({
      username: user.username,
      profile_id: user.profile_id,
    })
    setShowEditModal(true)
  }

  const openDeleteModal = (user) => {
    setSelectedUser(user)
    setShowDeleteModal(true)
  }

  const closeEditModal = () => {
    setShowEditModal(false)
    setSelectedUser(null)
  }

  const closeDeleteModal = () => {
    setShowDeleteModal(false)
    setSelectedUser(null)
  }

  const handleEditFormChange = (event) => {
    const { name, value } = event.target
    setEditForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSaveEdit = async () => {
    if (!selectedUser) return

    const payload = {
      username: editForm.username,
      profile_id: editForm.profile_id,
    }

    setAllUsers((prev) =>
      prev.map((user) =>
        user.user_uuid === selectedUser.user_uuid
          ? {
              ...user,
              ...payload,
              updated_at: new Date().toISOString(),
            }
          : user,
      ),
    )

    toast.success("Usuário editado com sucesso")
    closeEditModal()
  }

  const handleConfirmDelete = async () => {
    if (!selectedUser) return

    const nextActive = !selectedUser.active

    setAllUsers((prev) =>
      prev.map((user) =>
        user.user_uuid === selectedUser.user_uuid
          ? {
              ...user,
              active: nextActive,
              updated_at: new Date().toISOString(),
            }
          : user,
      ),
    )

    toast.success(nextActive ? "Usuário reativado com sucesso" : "Usuário desativado com sucesso")
    closeDeleteModal()
  }

  return (
    <>
      <div className="flex flex-col gap-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Card
            className="cursor-pointer border-border bg-card transition-shadow hover:shadow-lg"
            onClick={() => setStatusFilter("all")}
          >
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total de Usuários</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{totalUsers}</div>
            </CardContent>
          </Card>
          <Card
            className="cursor-pointer border-border bg-card transition-shadow hover:shadow-lg"
            onClick={() => setStatusFilter("active")}
          >
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Usuários Ativos</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-chart-1">{activeUsers}</div>
            </CardContent>
          </Card>
          <Card
            className="cursor-pointer border-border bg-card transition-shadow hover:shadow-lg"
            onClick={() => setStatusFilter("inactive")}
          >
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Usuários Inativos</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-muted-foreground">{inactiveUsers}</div>
            </CardContent>
          </Card>
        </div>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Buscar por username..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="border-border bg-input pl-10 text-foreground placeholder:text-muted-foreground"
          />
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <label className="text-sm text-muted-foreground" htmlFor="status-filter">
            Filtrar por status
          </label>
          <select
            id="status-filter"
            value={statusFilter}
            onChange={handleStatusFilterChange}
            className="w-full rounded-md border border-border bg-input px-3 py-2 text-foreground sm:w-56"
          >
            <option value="all">Todos</option>
            <option value="active">Ativos</option>
            <option value="inactive">Inativos</option>
          </select>
        </div>

        <Card className="border-border bg-card">
          <CardHeader>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <CardTitle className="text-foreground">Lista de Usuários</CardTitle>
                <CardDescription className="text-muted-foreground">
                  Gerencie os usuários do sistema
                </CardDescription>
              </div>

              <div className="flex items-center gap-2 self-end sm:self-auto">
                <label htmlFor="users-page-size" className="text-sm text-muted-foreground">
                  Mostrar
                </label>
                <select
                  id="users-page-size"
                  value={pageSize}
                  onChange={handlePageSizeChange}
                  className="w-24 rounded-md border border-border bg-input px-2 py-1.5 text-sm text-foreground"
                >
                  {PAGE_SIZE_OPTIONS.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="px-2 py-3 text-left text-sm font-medium text-muted-foreground">Username</th>
                    <th className="px-2 py-3 text-center text-sm font-medium text-muted-foreground">Perfil</th>
                    <th className="px-2 py-3 text-center text-sm font-medium text-muted-foreground">Status</th>
                    <th className="px-2 py-3 text-center text-sm font-medium text-muted-foreground">Data de Criação</th>
                    <th className="px-2 py-3 text-center text-sm font-medium text-muted-foreground">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {isLoading && (
                    <tr>
                      <td colSpan={5} className="py-10">
                        <div className="flex items-center justify-center gap-2 text-muted-foreground">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          <span>Carregando usuários...</span>
                        </div>
                      </td>
                    </tr>
                  )}

                  {!isLoading && usersPage.data.length === 0 && (
                    <tr>
                      <td colSpan={5} className="py-10 text-center text-muted-foreground">
                        Nenhum usuário encontrado para os filtros aplicados.
                      </td>
                    </tr>
                  )}

                  {!isLoading &&
                    usersPage.data.map((user) => (
                      <tr key={user.user_uuid} className="border-b border-border/50 transition-colors hover:bg-muted/50">
                        <td className="px-2 py-3">
                          <div className="flex items-center gap-3">
                            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/20">
                              <User className="h-4 w-4 text-primary" />
                            </div>
                            <span className="text-sm font-medium text-foreground">{user.username}</span>
                          </div>
                        </td>
                        <td className="px-2 py-3 text-center">
                          <span
                            className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${getPerfilClassName(getProfileName(user.profile_id, profiles))}`}
                          >
                            {getProfileName(user.profile_id, profiles)}
                          </span>
                        </td>
                        <td className="px-2 py-3 text-center">
                          <span
                            className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${getStatusClassName(user.active)}`}
                          >
                            {user.active ? "Ativo" : "Inativo"}
                          </span>
                        </td>
                        <td className="px-2 py-3 text-center text-sm text-muted-foreground">{formatDate(user.created_at)}</td>
                        <td className="px-2 py-3 text-center">
                          <div className="flex items-center justify-center gap-1">
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 text-muted-foreground hover:text-foreground"
                              aria-label={`Editar ${user.username}`}
                              onClick={() => openEditModal(user)}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 text-muted-foreground hover:text-destructive"
                              aria-label={user.active ? `Desativar ${user.username}` : `Reativar ${user.username}`}
                              onClick={() => openDeleteModal(user)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>

            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm text-muted-foreground">
                Mostrando {usersPage.data.length} de {usersPage.meta.total} usuarios
              </p>
              <div className="flex items-center gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={!usersPage.meta.hasPrev || isLoading}
                  onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                >
                  Anterior
                </Button>
                <span className="min-w-24 text-center text-sm text-muted-foreground">
                  Página {usersPage.meta.page} de {usersPage.meta.totalPages}
                </span>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={!usersPage.meta.hasNext || isLoading}
                  onClick={() => setCurrentPage((prev) => prev + 1)}
                >
                  Próxima
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {showEditModal && selectedUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 p-4 backdrop-blur-sm">
          <Card className="w-full max-w-md border-border bg-card">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-foreground">Editar Usuário</CardTitle>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={closeEditModal}
                  className="text-muted-foreground hover:text-foreground"
                  aria-label="Fechar modal de edição"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <CardDescription className="text-muted-foreground">
                Atualize as informações do usuário
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground" htmlFor="edit-user-name">
                  Username
                </label>
                <Input
                  id="edit-user-name"
                  name="username"
                  value={editForm.username}
                  onChange={handleEditFormChange}
                  className="border-border bg-input text-foreground"
                />
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground" htmlFor="edit-user-profile">
                  Perfil de Acesso
                </label>
                <select
                  id="edit-user-profile"
                  name="profile_id"
                  value={editForm.profile_id}
                  onChange={handleEditFormChange}
                  className="w-full rounded-md border border-border bg-input px-3 py-2 text-foreground"
                >
                  {profiles.map((profile) => (
                    <option key={profile.profile_uuid} value={profile.profile_uuid}>
                      {profile.profile_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="mt-2 flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1 border-border text-foreground hover:bg-muted"
                  onClick={closeEditModal}
                >
                  Cancelar
                </Button>
                <Button
                  type="button"
                  className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                  onClick={handleSaveEdit}
                >
                  Salvar Alterações
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {showDeleteModal && selectedUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 p-4 backdrop-blur-sm">
          <Card className="w-full max-w-sm border-border bg-card">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-destructive/10 p-2">
                  <AlertTriangle className="h-5 w-5 text-destructive" />
                </div>
                <div>
                  <CardTitle className="text-foreground">
                    {selectedUser.active ? "Confirmar Desativação" : "Confirmar Reativação"}
                  </CardTitle>
                  <CardDescription className="text-muted-foreground">
                    {selectedUser.active
                      ? "O usuário será marcado como inativo"
                      : "O usuário voltará para status ativo"}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <p className="text-sm text-muted-foreground">
                {selectedUser.active
                  ? "Tem certeza que deseja desativar o usuário "
                  : "Tem certeza que deseja reativar o usuário "}
                <strong className="text-foreground">{selectedUser.username}</strong>?
              </p>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1 border-border text-foreground hover:bg-muted"
                  onClick={closeDeleteModal}
                >
                  Cancelar
                </Button>
                <Button
                  type="button"
                  variant={selectedUser.active ? "destructive" : "default"}
                  className="flex-1"
                  onClick={handleConfirmDelete}
                >
                  {selectedUser.active ? "Desativar Usuário" : "Reativar Usuário"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </>
  )
}
