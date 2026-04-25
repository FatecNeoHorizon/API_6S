import { getPendingConsent } from "../api/consent";

export async function redirectToConsentIfPending(navigate) {
  const response = await getPendingConsent();
  const pendingClauses = response.pending_clauses || [];

  if (pendingClauses.length > 0) {
    navigate("/consent", { replace: true });
    return true;
  }

  return false;
}