import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import DashboardLayout from "../layouts/DashboardLayout";
import IndicadoresPage from "../pages/dashboard/indicadores-page/IndicadoresPage";
import EstruturaRedesPage from "../pages/dashboard/estrutura-redes-page/EstruturaRedesPage";
import ConsentPage from "../pages/consent/ConsentPage";

function NotFoundPage() {
  return (
    <div className="p-8 text-center text-slate-600">Página não encontrada</div>
  );
}

export function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/consent" element={<ConsentPage />} />
        <Route path="/" element={<Navigate to="/dashboard/indicadores" replace />} />
        <Route path="/dashboard" element={<DashboardLayout />}>
          <Route path="indicadores" element={<IndicadoresPage />} />
          <Route path="estrutura-redes" element={<EstruturaRedesPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
