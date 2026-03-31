import { BrowserRouter, Route, Routes } from "react-router-dom";
import HomePage from "../pages/HomePage";
import LoginPageMock from "../pages/LoginPageMock";
import PrimeiroAcessoPageMock from "../pages/PrimeiroAcessoPageMock";
import DashboardPageMock from "../pages/DashboardPageMock";

function NotFoundPage() {
  return <div className="p-8 text-center text-slate-600">Página não encontrada</div>;
}

export function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPageMock />} />
        <Route path="/primeiro-acesso" element={<PrimeiroAcessoPageMock />} />
        <Route path="/dashboard" element={<DashboardPageMock />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}