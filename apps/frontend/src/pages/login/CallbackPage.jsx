import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { exchangeCodeForToken } from "@/api/auth";
import { saveClientSession } from "@/api/consent";

export function CallbackPage() {
  const navigate = useNavigate();
  const handled = useRef(false);

  useEffect(() => {
    if (handled.current) return;
    handled.current = true;

    const params = new URLSearchParams(window.location.search);
    const code  = params.get("code");
    const state = params.get("state");

    if (!code || !state) {
      if (window.opener) window.close();
      else navigate("/", { replace: true });
      return;
    }

    if (window.opener) {
      // Running inside popup — relay code+state to parent and close
      window.opener.postMessage(
        { type: "oauth_code", code, state },
        window.location.origin,
      );
      window.close();
      return;
    }

    // Fallback: direct navigation (popup was blocked or user navigated manually)
    const storedState  = sessionStorage.getItem("pkce_state");
    const codeVerifier = sessionStorage.getItem("pkce_verifier");
    sessionStorage.removeItem("pkce_state");
    sessionStorage.removeItem("pkce_verifier");

    if (!storedState || state !== storedState || !codeVerifier) {
      navigate("/", { replace: true });
      return;
    }

    exchangeCodeForToken({
      code,
      code_verifier: codeVerifier,
      redirect_uri: `${window.location.origin}/auth/callback`,
    })
      .then((res) => {
        saveClientSession(res.access_token, { refreshToken: res.refresh_token });
        navigate(res.pending_consent ? "/consent" : "/dashboard", { replace: true });
      })
      .catch(() => navigate("/", { replace: true }));
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-muted-foreground">Autenticando...</p>
    </div>
  );
}

export default CallbackPage;
