import { useEffect, useState } from "react"
import { Search, Edit, Trash2, User, Loader2, X, AlertTriangle, Plus, Eye, EyeOff } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { toast } from "sonner"
import { apiClient } from "@/api/client"

const DEFAULT_PAGE_SIZE = 5
const PAGE_SIZE_OPTIONS = [5, 10, 25, 50, 100]
const ALLOWED_PROFILE_NAMES = new Set(["ADMIN", "ANALYST", "MANAGER"])
const API_BASE_URL = import.meta.env.VITE_API_URL

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

const createUserRequest = async (payload) => {
  if (!API_BASE_URL) {
    const error = new Error("VITE_API_URL não configurada")
    error.status = 500
    error.data = { detail: "Configuração da API ausente (VITE_API_URL)." }
    throw error
  }

  const response = await fetch(`${API_BASE_URL}/users/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })

  const contentType = response.headers.get("content-type")
  const responseBody = contentType?.includes("application/json")
    ? await response.json()
    : await response.text()

  if (!response.ok) {
    const error = new Error(`Erro na API: ${response.status}`)
    error.status = response.status
    error.data = responseBody
    throw error
  }

  return responseBody
}

export default function UsuariosPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE)
  const [profiles, setProfiles] = useState([])
  const [allUsers, setAllUsers] = useState([])
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
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [createForm, setCreateForm] = useState({
    username: "",
    email: "",
    password: "",
    profile_id: "",
  })
  const [createError, setCreateError] = useState("")
  const [isCreatingUser, setIsCreatingUser] = useState(false)
  const [showCreatePassword, setShowCreatePassword] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)
  const [editForm, setEditForm] = useState({
    username: "",
    profile_id: "",
  })

  const loadUsersAndProfiles = async () => {
    setIsLoading(true)

    try {
      const [profilesResponse, usersResponse] = await Promise.all([
        apiClient.get("/users/profiles"),
        apiClient.get("/users/"),
      ])

      const apiProfiles = normalizeProfiles(resolvePayloadArray(profilesResponse))
      const apiUsers = resolvePayloadArray(usersResponse).map(normalizeUser)

      setProfiles(apiProfiles)
      setAllUsers(apiUsers)
    } catch (error) {
      if (!navigator.onLine || error instanceof TypeError) {
        toast.error("Sem conexão com a internet. Verifique sua rede e tente novamente.")
      } else if (error?.response?.status === 403 || error?.status === 403) {
        toast.error("Acesso negado. Você não tem permissão para visualizar estes dados.")
      } else {
        toast.error("Erro ao carregar dados. Tente novamente.")
      }
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadUsersAndProfiles()
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

  const handleCreateFormChange = (event) => {
    const { name, value } = event.target
    setCreateForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleOpenCreateModal = () => {
    setCreateForm({
      username: "",
      email: "",
      password: "",
      profile_id: "",
    })
    setCreateError("")
    setShowCreatePassword(false)
    setShowCreateModal(true)
  }

  const handleCloseCreateModal = () => {
    setShowCreateModal(false)
    setCreateError("")
    setShowCreatePassword(false)
  }

  const isValidEmail = (value) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
  }

  const getApiErrorMessage = (error, fallbackMessage) => {
    const detail = error?.response?.data?.detail ?? error?.detail ?? error?.data?.detail

    if (typeof detail === "string" && detail.trim()) {
      return detail
    }

    if (Array.isArray(detail) && detail.length > 0) {
      const firstDetail = detail[0]

      if (typeof firstDetail === "string" && firstDetail.trim()) {
        return firstDetail
      }

      if (typeof firstDetail?.msg === "string" && firstDetail.msg.trim()) {
        return firstDetail.msg
      }
    }

    return fallbackMessage
  }

  const handleCreateUser = async () => {
    const username = createForm.username.trim()
    const email = createForm.email.trim()
    const password = createForm.password
    const profile_id = createForm.profile_id

    if (!username || !email || !password || !profile_id) {
      setCreateError("Preencha todos os campos obrigatórios.")
      return
    }

    if (!isValidEmail(email)) {
      setCreateError("Informe um email válido.")
      return
    }

    setCreateError("")
    setIsCreatingUser(true)

    try {
      await createUserRequest({
        username,
        email,
        password,
        profile_id,
      })

      toast.success("Usuário criado com sucesso")
      handleCloseCreateModal()
      await loadUsersAndProfiles()
      setCurrentPage(1)
    } catch (error) {
      const status = error?.status

      if (status === 409) {
        setCreateError(getApiErrorMessage(error, "Username ou email já cadastrado."))
      } else if (status === 404) {
        setCreateError(getApiErrorMessage(error, "Perfil selecionado não existe."))
      } else {
        setCreateError(getApiErrorMessage(error, "Não foi possível criar o usuário. Tente novamente."))
      }
    } finally {
      setIsCreatingUser(false)
    }
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

  const profileOptions = profiles.filter((profile) =>
    ALLOWED_PROFILE_NAMES.has(profile.profile_name.toUpperCase()),
  )

  const createProfileOptions = profileOptions.length > 0 ? profileOptions : profiles

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

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
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

          <Button
            type="button"
            className="bg-primary text-primary-foreground hover:bg-primary/90"
            onClick={handleOpenCreateModal}
          >
            <Plus className="mr-2 h-4 w-4" />
            Novo Usuário
          </Button>
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

              <div className="flex flex-wrap items-center justify-end gap-2 self-end sm:self-auto">
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

      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 p-4 backdrop-blur-sm">
          <Card className="w-full max-w-md border-border bg-card">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-foreground">Novo Usuário</CardTitle>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={handleCloseCreateModal}
                  className="text-muted-foreground hover:text-foreground"
                  aria-label="Fechar modal de criação"
                  disabled={isCreatingUser}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <CardDescription className="text-muted-foreground">
                Cadastre um usuário com perfil e senha temporária.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground" htmlFor="create-user-username">
                  Username
                </label>
                <Input
                  id="create-user-username"
                  name="username"
                  value={createForm.username}
                  onChange={handleCreateFormChange}
                  placeholder="Digite o username"
                  className="border-border bg-input text-foreground"
                  disabled={isCreatingUser}
                />
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground" htmlFor="create-user-email">
                  Email
                </label>
                <Input
                  id="create-user-email"
                  name="email"
                  type="email"
                  value={createForm.email}
                  onChange={handleCreateFormChange}
                  placeholder="Digite o email"
                  className="border-border bg-input text-foreground"
                  disabled={isCreatingUser}
                />
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground" htmlFor="create-user-profile">
                  Perfil
                </label>
                <select
                  id="create-user-profile"
                  name="profile_id"
                  value={createForm.profile_id}
                  onChange={handleCreateFormChange}
                  className="w-full rounded-md border border-border bg-input px-3 py-2 text-foreground"
                  disabled={isCreatingUser}
                >
                  <option value="">Selecione um perfil</option>
                  {createProfileOptions.map((profile) => (
                    <option key={profile.profile_uuid} value={profile.profile_uuid}>
                      {profile.profile_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-foreground" htmlFor="create-user-password">
                  Senha Temporária
                </label>
                <div className="relative">
                  <Input
                    id="create-user-password"
                    name="password"
                    type={showCreatePassword ? "text" : "password"}
                    value={createForm.password}
                    onChange={handleCreateFormChange}
                    placeholder="Digite a senha temporária"
                    className="border-border bg-input pr-10 text-foreground"
                    disabled={isCreatingUser}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute right-1 top-1/2 h-8 w-8 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    onClick={() => setShowCreatePassword((prev) => !prev)}
                    aria-label={showCreatePassword ? "Ocultar senha" : "Mostrar senha"}
                    disabled={isCreatingUser}
                  >
                    {showCreatePassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>

              {createError && (
                <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                  {createError}
                </p>
              )}

              <div className="mt-2 flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1 border-border text-foreground hover:bg-muted"
                  onClick={handleCloseCreateModal}
                  disabled={isCreatingUser}
                >
                  Cancelar
                </Button>
                <Button
                  type="button"
                  className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                  onClick={handleCreateUser}
                  disabled={isCreatingUser}
                >
                  {isCreatingUser ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Criando...
                    </>
                  ) : (
                    "Criar Usuário"
                  )}
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
