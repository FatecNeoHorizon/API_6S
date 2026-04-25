import { useEffect, useState } from "react";

import { PENDING_CONSENT_EVENT } from "../api/client";
import PendingConsentModal from "../components/consent/PendingConsentModal";

export function PendingConsentProvider({ children }) {
  const [open, setOpen] = useState(false);
  const [pendingClauses, setPendingClauses] = useState([]);

  useEffect(() => {
    function handlePendingConsent(event) {
      setPendingClauses(event.detail?.pending_clauses || []);
      setOpen(true);
    }

    window.addEventListener(PENDING_CONSENT_EVENT, handlePendingConsent);

    return () => {
      window.removeEventListener(PENDING_CONSENT_EVENT, handlePendingConsent);
    };
  }, []);

  function handleResolved() {
    setOpen(false);
    setPendingClauses([]);
  }

  return (
    <>
      {children}

      <PendingConsentModal
        open={open}
        pendingClauses={pendingClauses}
        onResolved={handleResolved}
      />
    </>
  );
}