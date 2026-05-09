let pendingConsentHandler = null;

export function registerPendingConsentHandler(handler) {
  pendingConsentHandler = handler;

  return () => {
    if (pendingConsentHandler === handler) {
      pendingConsentHandler = null;
    }
  };
}

export function isPendingConsentError(error) {
  if (error?.status !== 403) {
    return false;
  }

  const data = error.data;
  const detail = data?.detail;

  if (detail === "pending_consent") {
    return true;
  }

  if (detail && typeof detail === "object" && detail.code === "pending_consent") {
    return true;
  }

  return data?.code === "pending_consent";
}

export async function waitForPendingConsentAcceptance(error) {
  if (!isPendingConsentError(error)) {
    return false;
  }

  if (!pendingConsentHandler) {
    throw error;
  }

  await pendingConsentHandler();
  return true;
}
