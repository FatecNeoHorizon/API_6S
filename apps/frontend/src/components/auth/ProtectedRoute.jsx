import React from "react";
import { Navigate, Outlet, Link } from "react-router-dom";
import { getSessionToken, clearClientSession } from "@/api/consent";

function decodeJwtPayload(token) {
  try {
    const parts = token.split(".");
    if (parts.length < 2) return null;
    const payload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const json = JSON.parse(decodeURIComponent(atob(payload).split("").map(function(c) {
      return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
    }).join("")));
    return json;
  } catch (e) {
    return null;
  }
}

function isTokenValid(token) {
  if (!token) return false;
  const payload = decodeJwtPayload(token);
  if (!payload) return false;
  if (payload.exp && typeof payload.exp === "number") {
    const now = Math.floor(Date.now() / 1000);
    return payload.exp > now;
  }
  return true;
}

function AuthRequiredScreen({ title = "Precisa logar para usar o sistema", message = "Por favor, faça login para acessar as páginas protegidas." }) {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md text-center">
        <h1 className="text-2xl font-bold mb-4">{title}</h1>
        <p className="mb-6 text-muted-foreground">{message}</p>
        <div className="flex justify-center">
          <Link to="/login" className="px-4 py-2 rounded bg-primary text-primary-foreground">Voltar ao login</Link>
        </div>
      </div>
    </div>
  );
}

export function ProtectedRoute({ children }) {
  const token = getSessionToken();

  if (!token) {
    clearClientSession();
    return <AuthRequiredScreen />;
  }

  if (!isTokenValid(token)) {
    clearClientSession();
    return <AuthRequiredScreen title="Sessão expirada" message="Sua sessão expirou. Faça login novamente." />;
  }

  // If children provided, render them (backwards-compatible). Otherwise render nested routes via Outlet.
  if (children) {
    return children;
  }

  return <Outlet />;
}

export function TokenRequiredRoute({ children }) {
  const token = getSessionToken();

  if (!token) {
    clearClientSession();
    return <AuthRequiredScreen />;
  }

  if (!isTokenValid(token)) {
    clearClientSession();
    return <AuthRequiredScreen title="Sessão expirada" message="Sua sessão expirou. Faça login novamente." />;
  }

  return children;
}

export function RoleRequiredRoute({ children, allowedProfiles = [] }) {
  const token = getSessionToken();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (!isTokenValid(token)) {
    clearClientSession();
    return <Navigate to="/login" replace />;
  }

  const payload = decodeJwtPayload(token);
  const profile = (payload?.profile || "").toUpperCase();

  const allowed = allowedProfiles.map((p) => p.toUpperCase());
  if (allowed.length === 0 || allowed.includes(profile)) {
    return children;
  }

  return (
    <div className="p-8 text-center text-slate-600">Acesso negado</div>
  );
}

export default ProtectedRoute;
