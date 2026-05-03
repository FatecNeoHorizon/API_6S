import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import LoginPage from "../pages/login/LoginPage";
import ConsentPage from "../pages/login/ConsentPage";
import ForgotPasswordPage from "../pages/login/ForgotPasswordPage";
import ResetPasswordPage from "../pages/login/ResetPasswordPage";
import PrimeiroAcessoPage from "../pages/login/PrimeiroAcessoPage";
import DashboardLayout from "../layouts/DashboardLayout";
import IndicadoresPage from "../pages/dashboard/indicadores-page/IndicadoresPage";
import EstruturaRedesPage from "../pages/dashboard/estrutura-redes-page/EstruturaRedesPage";
import UsuariosPage from "../pages/dashboard/user-management/UsuariosPage";
import TermsPage from "../pages/dashboard/terms-management/TermsPage";

function NotFoundPage() {
  return (
    <div className="p-8 text-center text-slate-600">Página não encontrada</div>
  );
}

export function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/consent" element={<ConsentPage />} />
        <Route path="/first-access" element={<PrimeiroAcessoPage />} />
        <Route path="/primeiro-acesso" element={<Navigate to="/first-access" replace />} />
        <Route path="/" element={<Navigate to="/dashboard/indicadores" replace />} />
        <Route path="/dashboard" element={<DashboardLayout />}>
          <Route path="indicadores" element={<IndicadoresPage />} />
          <Route path="estrutura-redes" element={<EstruturaRedesPage />} />
          <Route path="usuarios" element={<UsuariosPage />} />
          <Route path="termos" element={<TermsPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
