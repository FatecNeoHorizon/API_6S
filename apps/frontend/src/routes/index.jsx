import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import { WelcomePage } from "../pages/login/WelcomePage";
import ConsentPage from "../pages/login/ConsentPage";
import DashboardLayout from "../layouts/DashboardLayout";
import ProtectedRoute, { TokenRequiredRoute, RoleRequiredRoute } from "@/components/auth/ProtectedRoute";
import IndicadoresPage from "../pages/dashboard/indicadores-page/IndicadoresPage";
import EstruturaRedesPage from "../pages/dashboard/estrutura-redes-page/EstruturaRedesPage";
import UsuariosPage from "../pages/dashboard/user-management/UsuariosPage";
import TermsPage from "../pages/dashboard/terms-management/TermsPage";
import { HeatmapFilters } from "../pages/dashboard/heatmap/HeatmapFilters";
import ProfilePage from "../pages/dashboard/profile/ProfilePage";
import IncidentNotificationPage from "../pages/dashboard/incident-notification/IncidentNotificationPage";

function NotFoundPage() {
  return (
    <div className="p-8 text-center text-slate-600">Página não encontrada</div>
  );
}

export function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Navigate to="/" replace />} />
        <Route path="/consent" element={<TokenRequiredRoute><ConsentPage /></TokenRequiredRoute>} />
        <Route path="/" element={<WelcomePage />} />
        <Route path="/dashboard/*" element={<ProtectedRoute />}>
          <Route path="" element={<DashboardLayout />}>
            <Route index element={<Navigate to="indicadores" replace />} />
            <Route path="indicadores" element={<IndicadoresPage />} />
            <Route path="estrutura-redes" element={<EstruturaRedesPage />} />
            <Route path="perfil" element={<ProfilePage />} />
            <Route path="usuarios" element={<RoleRequiredRoute allowedProfiles={["ADMIN","MANAGER"]}><UsuariosPage /></RoleRequiredRoute>} />
            <Route path="termos" element={<RoleRequiredRoute allowedProfiles={["ADMIN"]}><TermsPage /></RoleRequiredRoute>} />
            <Route path="incident-notification" element={<RoleRequiredRoute allowedProfiles={["ADMIN"]}><IncidentNotificationPage /></RoleRequiredRoute>} />
            <Route path="*" element={<NotFoundPage />} />
            <Route path="heatmap" element={<HeatmapFilters/>} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
