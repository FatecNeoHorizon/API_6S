import { useState, useRef, useCallback, useEffect } from "react";
import { Link, useLocation, Outlet } from "react-router-dom";
import {
  BarChart3,
  LogOut,
  Menu,
  X,
  ChevronDown,
  Network,
  Upload,
  CheckCircle2,
  AlertCircle,
  FileText,
  FileSpreadsheet,
  FileArchive,
  Loader2,
  Users, 
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "../utils/utils";
import { getSessionToken, clearClientSession, logoutUser } from "@/api/consent";

const menuItems = [
  {
    label: "Indicadores DEC/FEC e Perdas",
    href: "/dashboard/indicadores",
    icon: BarChart3,
    allowedProfiles: [],
  },
  {
    label: "Estrutura das Redes",
    href: "/dashboard/estrutura-redes",
    icon: Network,
    allowedProfiles: [],
  },
  {
    label: "Gestão de Usuários",
    href: "/dashboard/usuarios",
    icon: Users,
    allowedProfiles: ["ADMIN", "MANAGER"],
  },
  {
    label: "Gestão de Termos",
    href: "/dashboard/termos",
    icon: FileText,
    allowedProfiles: ["ADMIN"],
  },
];

function decodeJwtPayload(token) {
  try {
    const parts = token.split(".");
    if (parts.length < 2) return null;
    const payload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const json = JSON.parse(decodeURIComponent(atob(payload).split("").map(function(c) {
      return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
    }).join("")));
    return json;
  } catch {
    return null;
  }
}

function getUserDisplayName(token) {
  const payload = decodeJwtPayload(token);
  if (!payload) return null;

  const candidate = payload.name || payload.preferred_username || payload.username || payload.sub || payload.email;
  if (typeof candidate === "string" && candidate.trim()) {
    return candidate;
  }

  return null;
}

function getUserInitials(name) {
  if (!name) return "AD";
  const initials = name
    .split(" ")
    .filter(Boolean)
    .map((word) => word[0].toUpperCase())
    .slice(0, 2)
    .join("");

  return initials || "AD";
}

function getUserProfile(token) {
  const payload = decodeJwtPayload(token);
  return typeof payload?.profile === "string" ? payload.profile.toUpperCase() : "";
}

function canAccessMenuItem(item, userProfile) {
  if (!item.allowedProfiles || item.allowedProfiles.length === 0) {
    return true;
  }

  return item.allowedProfiles.includes(userProfile);
}

const allowedExtensions = [".csv", ".xlsx", ".zip"];

const REQUIRED_FILES = [
  "Base de Dados das Perdas de Energia nos Processos Tarifários.xlsx",
  "EDP_SP_391_2016-12-31_M6_20170707-0903.gdb.zip",
  "indicadores-continuidade-coletivos-2020-2029.csv",
  "indicadores-continuidade-coletivos-limite.csv",
];
const REQUIRED_COUNT = REQUIRED_FILES.length;

// Status por arquivo: idle | uploading | done | error
function getFileIcon(name) {
  const ext = "." + name.split(".").pop().toLowerCase();
  if (ext === ".csv") return FileText;
  if (ext === ".xlsx") return FileSpreadsheet;
  if (ext === ".zip") return FileArchive;
  return FileText;
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function uploadFormDataWithProgress(formData, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener("progress", (e) => {
      if (e.lengthComputable) {
        const pct = Math.round((e.loaded / e.total) * 100);
        onProgress(pct);
      }
    });

    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const data = JSON.parse(xhr.responseText);
          resolve(data);
        } catch {
          resolve({ message: "Upload concluído" });
        }
      } else {
        try {
          const errorData = JSON.parse(xhr.responseText);
          reject({ status: xhr.status, data: errorData });
        } catch {
          reject({ status: xhr.status, message: `Falha no upload: status ${xhr.status}` });
        }
      }
    });

    xhr.addEventListener("error", () => reject({ status: 0, message: "Erro de rede" }));
    xhr.addEventListener("abort", () => reject({ status: 0, message: "Upload cancelado" }));

    xhr.open("POST", "http://localhost:8000/upload/");
    xhr.send(formData);
  });
}

export default function DashboardLayout() {
  const location = useLocation();
  const pathname = location.pathname;
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [appLoadIds, setAppLoadIds] = useState(null);

  const userDisplayName = getUserDisplayName(getSessionToken()) || "Admin";
  const userInitials = getUserInitials(userDisplayName);
  const userProfile = getUserProfile(getSessionToken());

  const handleLogout = async () => {
    try {
      await logoutUser();
    } catch {}
    clearClientSession();
    window.location.href = "/login";
  };

  // Lista de arquivos: [{ file, status: 'idle'|'uploading'|'processing'|'done'|'error', progress: 0-100, error: null }]
  const [fileList, setFileList] = useState([]);

  const inputRef = useRef(null);

  const resetModal = () => {
    if (isUploading) return;
    setUploadModalOpen(false);
    setFileList([]);
    setDragActive(false);
  };

  const validateAndAddFiles = useCallback((newFiles) => {
    const invalid = [];
    const valid = [];

    Array.from(newFiles).forEach((file) => {
      const ext = "." + file.name.split(".").pop().toLowerCase();
      if (allowedExtensions.includes(ext)) {
        valid.push({ file, status: "idle", progress: 0, error: null });
      } else {
        invalid.push(file.name);
      }
    });

    if (invalid.length > 0) {
      toast.error(
        `${invalid.length} arquivo(s) com extensão inválida: ${invalid.join(", ")}. Apenas .csv, .xlsx e .zip são permitidos.`,
      );
    }

    if (valid.length > 0) {
      const existingNames = new Set(fileList.map((f) => f.file.name));
      const toAdd = valid.filter((v) => !existingNames.has(v.file.name));
      
      if (toAdd.length < valid.length) {
        toast.warning(
          "Alguns arquivos já foram adicionados e foram ignorados.",
          { id: "duplicate-file-warning" }
        );
      }
      
      if (toAdd.length > 0) {
        setFileList([...fileList, ...toAdd]);
      }
    }
  }, [fileList]);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
    else if (e.type === "dragleave") setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndAddFiles(e.dataTransfer.files);
    }
  };

  const handleInputChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndAddFiles(e.target.files);
      // Limpa o input para permitir selecionar o mesmo arquivo de novo
      e.target.value = "";
    }
  };

  const removeFile = (index) => {
    setFileList((prev) => prev.filter((_, i) => i !== index));
  };

  const startPolling = (fileName, loadId) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/upload/status/${loadId}`);
        if (!res.ok) throw new Error("Erro ao verificar status");
        
        const data = await res.json();
        
        if (data.status === "SUCCESS") {
          clearInterval(interval);
          setFileList((prev) => prev.map(entry => 
            entry.file.name === fileName ? { ...entry, status: "done", progress: 100 } : entry
          ));
        } else if (data.status === "ERROR") {
          clearInterval(interval);
          setFileList((prev) => prev.map(entry => 
            entry.file.name === fileName ? { ...entry, status: "error", error: data.error_message || "Erro no processamento" } : entry
          ));
        }
        // Se for STARTED ou PROCESSING, continua aguardando
      } catch (err) {
        clearInterval(interval);
        setFileList((prev) => prev.map(entry => 
          entry.file.name === fileName ? { ...entry, status: "error", error: err.message } : entry
        ));
      }
    }, 2000);
  };

  const handleFileUpload = async () => {
    if (fileList.length === 0) return;
    setIsUploading(true);

    const formData = new FormData();
    
    setFileList((prev) => prev.map(entry => ({ ...entry, status: "uploading", progress: 0, error: null })));

    fileList.forEach((entry) => {
      const fileName = entry.file.name;
      let key = null;
      if (fileName.includes("Perdas de Energia")) key = "energy_losses";
      else if (fileName.includes("gdb") || fileName.includes("EDP_SP_391")) key = "gdb";
      else if (fileName.includes("limite")) key = "indicadores_continuidade_limite";
      else if (fileName.includes("indicadores-continuidade-coletivos")) key = "indicadores_continuidade";
      
      if (key) {
        formData.append(key, entry.file);
      }
    });

    try {
      const response = await uploadFormDataWithProgress(formData, (pct) => {
        setFileList((prev) => prev.map(entry => 
          (entry.status === "uploading" ? { ...entry, progress: pct } : entry)
        ));
      });

      if (response.load_ids) {
        setAppLoadIds(response.load_ids);
        
        setFileList((prev) => prev.map((entry) => {
          const fileName = entry.file.name;
          let key = null;
          if (fileName.includes("Perdas de Energia")) key = "energy_losses";
          else if (fileName.includes("gdb") || fileName.includes("EDP_SP_391")) key = "gdb";
          else if (fileName.includes("limite")) key = "indicadores_continuidade_limite";
          else if (fileName.includes("indicadores-continuidade-coletivos")) key = "indicadores_continuidade";
          
          if (key && response.load_ids[key]) {
             startPolling(entry.file.name, response.load_ids[key]);
             return { ...entry, status: "processing", progress: 100 };
          } else {
             return { ...entry, status: "error", error: "Arquivo não processado pelo servidor" };
          }
        }));
      }

    } catch (err) {
      let errMsg = "Erro ao enviar arquivos.";
      if (err.data && err.data.detail) {
        if (typeof err.data.detail === "string") {
           errMsg = err.data.detail;
        } else if (Array.isArray(err.data.detail)) {
           errMsg = err.data.detail.map(e => e.msg || JSON.stringify(e)).join(", ");
        }
      } else if (err.message) {
        errMsg = err.message;
      }
      
      setFileList((prev) => prev.map(entry => ({ ...entry, status: "error", error: errMsg })));
      setIsUploading(false);
      toast.error("Erro no envio dos arquivos.");
    }
  };

  useEffect(() => {
    if (isUploading && fileList.length > 0) {
      const allFinished = fileList.every(f => f.status === "done" || f.status === "error");
      const hasProcessing = fileList.some(f => f.status === "uploading" || f.status === "processing");
      
      if (allFinished && !hasProcessing) {
        setIsUploading(false);
        const errCount = fileList.filter((f) => f.status === "error").length;
        const doneCount = fileList.filter((f) => f.status === "done").length;
        
        if (errCount === 0) {
          toast.success(`${doneCount} arquivo(s) processado(s) com sucesso!`);
          setTimeout(() => {
            setUploadModalOpen(false);
            setFileList([]);
          }, 2000);
        } else {
          toast.error(`${errCount} arquivo(s) falharam no processamento.`);
        }
      }
    }
  }, [fileList, isUploading]);

  const allDone =
    fileList.length > 0 && fileList.every((f) => f.status === "done");
  const hasUploading = fileList.some((f) => f.status === "uploading");
  const hasValidFiles = fileList.some(
    (f) => f.status === "idle" || f.status === "error",
  );

  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar Mobile Overlay */}
      {sidebarOpen && (
        <button
          type="button"
          aria-label="Fechar menu"
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40 lg:hidden w-full cursor-default"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed lg:static inset-y-0 left-0 z-50 w-64 bg-sidebar border-r border-sidebar-border transform transition-transform duration-200 ease-in-out lg:transform-none",
          sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
        )}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center gap-2 px-4 py-5 border-b border-sidebar-border">
            <img
              src="/zeus-logo.png"
              alt="Zeus Logo"
              className="w-8 h-8 object-contain"
            />
            <span className="text-lg font-bold text-sidebar-foreground">
              Zeus
            </span>
            <button
              className="ml-auto lg:hidden text-sidebar-foreground"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-4">
            <ul className="flex flex-col gap-1">
              {menuItems.map((item) => {
                const isActive = pathname === item.href;
                const canAccess = canAccessMenuItem(item, userProfile);

                if (!canAccess) return null;
                
                return (
                  <li key={item.href}>
                    <Link
                      to={item.href}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                        !canAccess && "text-sidebar-foreground/60",
                        isActive
                          ? "bg-sidebar-primary text-sidebar-primary-foreground"
                          : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                      )}
                      onClick={() => setSidebarOpen(false)}
                    >
                      {canAccess ? <item.icon className="w-5 h-5" /> : <span className="w-5 h-5" aria-hidden="true" />}
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Header */}
        <header className="sticky top-0 z-30 bg-background/80 backdrop-blur-sm border-b border-border px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                className="lg:hidden p-2 hover:bg-muted rounded-lg transition-colors"
                onClick={() => setSidebarOpen(true)}
              >
                <Menu className="w-5 h-5 text-foreground" />
              </button>
              <h1 className="text-lg font-semibold text-foreground">
                {pathname === "/dashboard/perfil"
                  ? "Meu Perfil"
                  : menuItems.find((item) => item.href === pathname)?.label ||
                    "Dashboard"}
              </h1>
            </div>

            <div className="flex items-center gap-2">
              <button
                className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-muted transition-colors text-foreground"
                onClick={() => setUploadModalOpen(true)}
              >
                <Upload className="w-4 h-4" />
                <span className="hidden sm:block text-sm font-medium">
                  Upload de Arquivos
                </span>
              </button>

              <div className="relative">
                <button
                  className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-muted transition-colors"
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                >
                  <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                    <span className="text-sm font-medium text-primary">{userInitials}</span>
                  </div>
                  <span className="hidden sm:block text-sm font-medium text-foreground">
                    {userDisplayName}
                  </span>
                  <ChevronDown className="w-4 h-4 text-muted-foreground" />
                </button>

                {userMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-card border border-border rounded-lg shadow-lg py-1">
                    <Link
                      to="/dashboard/perfil"
                      className="flex items-center gap-2 px-4 py-2 text-sm text-foreground hover:bg-muted"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      Meu Perfil
                    </Link>
                    <div className="border-t border-border my-1" />
                    <button
                      onClick={() => {
                        setUserMenuOpen(false);
                        handleLogout();
                      }}
                      className="w-full flex items-center gap-2 px-4 py-2 text-sm text-destructive hover:bg-muted transition-colors text-left"
                    >
                      <LogOut className="w-4 h-4" />
                      Sair
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-4 lg:p-6">
          <Outlet />
        </main>
      </div>

      {/* Upload Modal */}
      {uploadModalOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-card border border-border rounded-xl shadow-2xl w-full max-w-lg flex flex-col max-h-[90vh]">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-border shrink-0">
              <div>
                <h2 className="text-lg font-semibold text-foreground">
                  Upload de Arquivos
                </h2>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Selecione os {REQUIRED_COUNT} arquivos necessários
                </p>
              </div>
              <button
                onClick={resetModal}
                disabled={isUploading}
                className="text-muted-foreground hover:text-foreground disabled:opacity-40 disabled:cursor-not-allowed transition-colors p-1 rounded"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Drop Zone */}
            <div className="px-6 py-4 shrink-0">
              <input
                ref={inputRef}
                type="file"
                id="fileInput"
                accept=".csv,.xlsx,.zip"
                multiple
                onChange={handleInputChange}
                className="hidden"
                disabled={isUploading}
              />

              <label
                htmlFor="fileInput"
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={cn(
                  "border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center gap-2 transition-all",
                  isUploading
                    ? "border-border opacity-50 cursor-not-allowed"
                    : "cursor-pointer",
                  !isUploading && dragActive
                    ? "border-primary bg-primary/5 scale-[1.01]"
                    : !isUploading
                      ? "border-border hover:border-primary/50 hover:bg-muted/30"
                      : "",
                )}
              >
                <Upload
                  className={cn(
                    "w-8 h-8 transition-colors",
                    dragActive ? "text-primary" : "text-muted-foreground",
                  )}
                />
                <p className="text-sm text-foreground font-medium text-center">
                  {dragActive
                    ? "Solte os arquivos aqui"
                    : "Clique ou arraste para selecionar"}
                </p>
                <p className="text-xs text-muted-foreground">
                  Múltiplos arquivos permitidos · .csv, .xlsx, .zip
                </p>
              </label>
            </div>

            {/* File List */}
            {fileList.length > 0 && (
              <div className="flex-1 overflow-y-auto px-6 py-3 min-h-0">
                <p className="text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wide">
                  {fileList.length}/{REQUIRED_COUNT} arquivo
                  {REQUIRED_COUNT !== 1 ? "s" : ""} selecionado
                  {REQUIRED_COUNT !== 1 ? "s" : ""}
                </p>
                <ul className="flex flex-col gap-2">
                  {fileList.map((entry, index) => {
                    const Icon = getFileIcon(entry.file.name);
                    const isDone = entry.status === "done";
                    const isErr = entry.status === "error";
                    const isUp = entry.status === "uploading";
                    const isProc = entry.status === "processing";

                    return (
                      <li
                        key={`${entry.file.name}-${index}`}
                        className={cn(
                          "rounded-lg border px-3 py-2.5 transition-colors",
                          isDone
                            ? "border-green-500/30 bg-green-500/5"
                            : isErr
                              ? "border-destructive/30 bg-destructive/5"
                              : (isUp || isProc)
                                ? "border-primary/30 bg-primary/5"
                                : "border-border bg-muted/20",
                        )}
                      >
                        <div className="flex items-center gap-2">
                          <Icon
                            className={cn(
                              "w-4 h-4 shrink-0",
                              isDone
                                ? "text-green-500"
                                : isErr
                                  ? "text-destructive"
                                  : (isUp || isProc)
                                    ? "text-primary"
                                    : "text-muted-foreground",
                            )}
                          />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-foreground truncate">
                              {entry.file.name}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {formatSize(entry.file.size)}
                              {isErr && (
                                <span className="text-destructive ml-1">
                                  · {entry.error}
                                </span>
                              )}
                            </p>
                          </div>

                          {/* Status icon / remove */}
                          <div className="shrink-0 flex items-center gap-1">
                            {isDone && (
                              <CheckCircle2 className="w-4 h-4 text-green-500" />
                            )}
                            {isErr && (
                              <AlertCircle className="w-4 h-4 text-destructive" />
                            )}
                            {(isUp || isProc) && (
                              <Loader2 className="w-4 h-4 text-primary animate-spin" />
                            )}
                            {!isUploading && !isDone && !isProc && !isUp && (
                              <button
                                onClick={() => removeFile(index)}
                                className="ml-1 p-0.5 rounded hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
                                title="Remover"
                              >
                                <X className="w-3.5 h-3.5" />
                              </button>
                            )}
                          </div>
                        </div>

                        {/* Progress bar */}
                        {(isUp || isProc || isDone) && (
                          <div className="mt-2">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-xs text-muted-foreground">
                                {isDone ? "Concluído" : isProc ? "Processando..." : "Enviando..."}
                              </span>
                              <span
                                className={cn(
                                  "text-xs font-semibold tabular-nums",
                                  isDone ? "text-green-500" : "text-primary",
                                )}
                              >
                                {isDone ? 100 : isProc ? 100 : entry.progress}%
                              </span>
                            </div>
                            <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
                              <div
                                className={cn(
                                  "h-full rounded-full transition-all duration-300",
                                  isDone ? "bg-green-500" : isProc ? "bg-primary animate-pulse" : "bg-primary",
                                )}
                                style={{
                                  width: `${isDone || isProc ? 100 : entry.progress}%`,
                                }}
                              />
                            </div>
                          </div>
                        )}
                      </li>
                    );
                  })}
                </ul>
              </div>
            )}

            {/* Actions */}
            <div className="px-6 py-4 border-t border-border shrink-0 flex gap-2">
              <button
                onClick={resetModal}
                disabled={isUploading}
                className="flex-1 px-4 py-2 text-sm font-medium text-foreground border border-border rounded-lg hover:bg-muted transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancelar
              </button>
              <button
                onClick={handleFileUpload}
                disabled={
                  fileList.length < REQUIRED_COUNT || isUploading || allDone
                }
                className="flex-1 px-4 py-2 text-sm font-medium text-card-foreground bg-primary rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isUploading && <Loader2 className="w-4 h-4 animate-spin" />}
                {isUploading
                  ? "Enviando..."
                  : allDone
                    ? "Concluído!"
                    : fileList.length < REQUIRED_COUNT
                      ? `Enviar (${fileList.length}/${REQUIRED_COUNT})`
                      : `Enviar (${fileList.length})`}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
