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
    const code = params.get("code");
    const state = params.get("state");

    const storedState = sessionStorage.getItem("pkce_state");
    const codeVerifier = sessionStorage.getItem("pkce_verifier");

    sessionStorage.removeItem("pkce_state");
    sessionStorage.removeItem("pkce_verifier");

    if (!code || !state || state !== storedState || !codeVerifier) {
      navigate("/", { replace: true });
      return;
    }

    exchangeCodeForToken({
      code,
      code_verifier: codeVerifier,
      redirect_uri: `${window.location.origin}/auth/callback`,
    })
      .then((res) => {
        saveClientSession(res.data.access_token, {
          refreshToken: res.data.refresh_token,
        });

        if (res.data.pending_consent) {
          navigate("/consent", { replace: true });
        } else {
          navigate("/dashboard", { replace: true });
        }
      })
      .catch(() => {
        navigate("/", { replace: true });
      });
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-muted-foreground">Autenticando...</p>
    </div>
  );
}

export default CallbackPage;
