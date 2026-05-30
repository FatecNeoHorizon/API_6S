import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import { WelcomePage } from "../pages/login/WelcomePage";
import CallbackPage from "../pages/login/CallbackPage";
import ConsentPage from "../pages/login/ConsentPage";
import GoodbyePage from "../pages/login/GoodbyePage";
import DashboardLayout from "../layouts/DashboardLayout";
import ProtectedRoute, { TokenRequiredRoute, RoleRequiredRoute } from "@/components/auth/ProtectedRoute";
import IndicadoresPage from "../pages/dashboard/indicadores-page/IndicadoresPage";
import EstruturaRedesPage from "../pages/dashboard/estrutura-redes-page/EstruturaRedesPage";
import UsuariosPage from "../pages/dashboard/user-management/UsuariosPage";
import TermsPage from "../pages/dashboard/terms-management/TermsPage";
import { HeatmapFilters } from "../pages/dashboard/heatmap/HeatmapFilters";
import ProfilePage from "../pages/dashboard/profile/ProfilePage";
import ConsentManagementPage from "../pages/dashboard/consent-management/ConsentManagementPage";
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
        {/* Rotas públicas — resolvidas antes do ProtectedRoute */}
        <Route path="/" element={<WelcomePage />} />
        <Route path="/login" element={<Navigate to="/" replace />} />
        <Route path="/auth/callback" element={<CallbackPage />} />
        <Route path="/consent" element={<TokenRequiredRoute><ConsentPage /></TokenRequiredRoute>} />
        <Route path="/goodbye" element={<GoodbyePage />} />

        {/* Rotas protegidas — captura tudo que não casou acima */}
        <Route path="*" element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route path="indicators" element={<IndicadoresPage />} />
            <Route path="network-structure" element={<EstruturaRedesPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="consents" element={<ConsentManagementPage />} />
            <Route path="users" element={<RoleRequiredRoute allowedProfiles={["ADMIN", "MANAGER"]}><UsuariosPage /></RoleRequiredRoute>} />
            <Route path="terms" element={<RoleRequiredRoute allowedProfiles={["ADMIN"]}><TermsPage /></RoleRequiredRoute>} />
            <Route path="incident-notification" element={<RoleRequiredRoute allowedProfiles={["ADMIN"]}><IncidentNotificationPage /></RoleRequiredRoute>} />
            <Route path="heatmap" element={<HeatmapFilters />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
