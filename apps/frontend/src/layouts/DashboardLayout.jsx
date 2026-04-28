import { useState } from "react";
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
  Loader2,
  Users, 
  FileText,
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "../utils/utils";
import { processUploadFile } from "../utils/fileReader";

const menuItems = [
  {
    label: "Indicadores DEC/FEC e Perdas",
    href: "/dashboard/indicadores",
    icon: BarChart3,
  },
  {
    label: "Estrutura das Redes",
    href: "/dashboard/estrutura-redes",
    icon: Network,
  },
  { 
    label: "Gestão de Usuários", 
    href: "/dashboard/usuarios", 
    icon: Users,
  },
  { 
    label: "Gestão de Termos", 
    href: "/dashboard/termos", 
    icon: FileText 
  },
];

// idle | uploading | processing | done | error
const STATUS_LABEL = {
  idle: null,
  uploading: "Enviando arquivo...",
  processing: "Processando CSV...",
  done: "Concluído!",
  error: "Ocorreu um erro.",
};

export default function DashboardLayout() {
  const location = useLocation();
  const pathname = location.pathname;
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("idle");

  const allowedExtensions = [".csv", ".xlsx", ".zip"];

  const resetModal = () => {
    setUploadModalOpen(false);
    setSelectedFile(null);
    setDragActive(false);
    setUploadStatus("idle");
  };

  const handleFileSelect = (file) => {
    const fileExtension = "." + file.name.split(".").pop().toLowerCase();
    if (allowedExtensions.includes(fileExtension)) {
      setSelectedFile(file);
      processUploadFile(file);
    } else {
      toast.error("Apenas arquivos .csv, .xlsx e .zip são permitidos");
      setSelectedFile(null);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setUploadStatus("uploading");

    try {
      // 1. Faz o upload do arquivo
      const uploadResponse = await fetch("/api/upload", {
        method: "POST",
        headers: {
          "X-File-Name": encodeURIComponent(selectedFile.name),
        },
        body: selectedFile,
      });

      if (!uploadResponse.ok) {
        throw new Error("Falha no upload do arquivo");
      }

      const uploadData = await uploadResponse.json();
      console.log("Upload concluído. Salvo em:", uploadData.path);

      // 2. Processa o CSV
      setUploadStatus("processing");
      const processResponse = await fetch("/process-decfec");

      const contentType = processResponse.headers.get("content-type") || "";
      if (!contentType.includes("application/json")) {
        const text = await processResponse.text();
        console.error("Resposta inesperada do servidor:", text);
        throw new Error(
          `Endpoint /process-decfec retornou status ${processResponse.status}. Verifique se o servidor está rodando corretamente.`,
        );
      }

      if (!processResponse.ok) {
        const errData = await processResponse.json();
        throw new Error(
          errData?.detail || errData?.message || "Falha ao processar o CSV",
        );
      }

      const processData = await processResponse.json();
      console.log("Processamento concluído:", processData);

      setUploadStatus("done");

      const successMsg =
        processData.inserted_lines != null
          ? `CSV processado! ${processData.inserted_lines} linhas inseridas.`
          : processData.message || "Arquivo processado com sucesso!";

      toast.success(successMsg);

      // Fecha o modal após breve pausa para o usuário ver o "Concluído"
      setTimeout(resetModal, 1500);
    } catch (error) {
      console.error("Erro:", error);
      setUploadStatus("error");
      toast.error(error.message || "Houve um erro ao enviar o arquivo.");
    } finally {
      setIsUploading(false);
    }
  };

  const isProcessing =
    uploadStatus === "uploading" || uploadStatus === "processing";

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
                return (
                  <li key={item.href}>
                    <Link
                      to={item.href}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                        isActive
                          ? "bg-sidebar-primary text-sidebar-primary-foreground"
                          : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                      )}
                      onClick={() => setSidebarOpen(false)}
                    >
                      <item.icon className="w-5 h-5" />
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
                  Upload de Arquivo
                </span>
              </button>

              <div className="relative">
                <button
                  className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-muted transition-colors"
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                >
                  <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                    <span className="text-sm font-medium text-primary">AD</span>
                  </div>
                  <span className="hidden sm:block text-sm font-medium text-foreground">
                    Admin
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
                    <Link
                      to="/"
                      className="flex items-center gap-2 px-4 py-2 text-sm text-destructive hover:bg-muted"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <LogOut className="w-4 h-4" />
                      Sair
                    </Link>
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
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-card border border-border rounded-lg shadow-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-foreground">
                Upload de Arquivo
              </h2>
              <button
                onClick={resetModal}
                disabled={isProcessing}
                className="text-muted-foreground hover:text-foreground disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <input
              type="file"
              id="fileInput"
              accept=".csv,.xlsx,.zip"
              onChange={handleInputChange}
              className="hidden"
              disabled={isProcessing}
            />

            <label
              htmlFor="fileInput"
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={cn(
                "border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center gap-3 transition-colors",
                isProcessing
                  ? "border-border opacity-50 cursor-not-allowed"
                  : "cursor-pointer",
                !isProcessing && dragActive
                  ? "border-primary bg-primary/5"
                  : "border-border hover:border-primary/50",
              )}
            >
              {selectedFile ? (
                <>
                  <Upload className="w-10 h-10 text-primary" />
                  <p className="text-sm text-foreground font-medium">
                    {selectedFile.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Clique ou arraste para alterar
                  </p>
                </>
              ) : (
                <>
                  <Upload className="w-10 h-10 text-muted-foreground" />
                  <p className="text-sm text-foreground font-medium">
                    Clique para selecionar um arquivo
                  </p>
                  <p className="text-xs text-muted-foreground">
                    ou arraste e solte aqui
                  </p>
                  <p className="text-xs text-muted-foreground mt-2">
                    Formatos aceitos: .csv, .xlsx, .zip
                  </p>
                </>
              )}
            </label>

            {/* Status de progresso */}
            {uploadStatus !== "idle" && (
              <div
                className={cn(
                  "mt-4 flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium",
                  uploadStatus === "done"
                    ? "bg-green-500/10 text-green-600"
                    : uploadStatus === "error"
                      ? "bg-destructive/10 text-destructive"
                      : "bg-primary/10 text-primary",
                )}
              >
                {isProcessing && (
                  <Loader2 className="w-4 h-4 animate-spin shrink-0" />
                )}
                {uploadStatus === "done" && (
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                )}
                <span>{STATUS_LABEL[uploadStatus]}</span>

                {/* Barra de progresso animada nas etapas de envio/processamento */}
                {isProcessing && (
                  <div className="ml-auto w-24 h-1.5 rounded-full bg-primary/20 overflow-hidden">
                    <div className="h-full bg-primary rounded-full animate-pulse w-2/3" />
                  </div>
                )}
              </div>
            )}

            <div className="mt-4 flex gap-2">
              <button
                onClick={resetModal}
                disabled={isProcessing}
                className="flex-1 px-4 py-2 text-sm font-medium text-foreground border border-border rounded-lg hover:bg-muted transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancelar
              </button>
              <button
                onClick={handleFileUpload}
                disabled={!selectedFile || isProcessing}
                className="flex-1 px-4 py-2 text-sm font-medium text-card-foreground bg-primary rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isProcessing && <Loader2 className="w-4 h-4 animate-spin" />}
                {uploadStatus === "uploading"
                  ? "Enviando..."
                  : uploadStatus === "processing"
                    ? "Processando..."
                    : "Enviar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
