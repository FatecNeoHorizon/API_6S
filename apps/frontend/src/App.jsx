import { AppRoutes } from "./routes";
import { Toaster } from "sonner";

import { PendingConsentProvider } from "./providers/PendingConsentProvider";

export default function App() {
  return (
    <>
      <PendingConsentProvider>
        <AppRoutes />
      </PendingConsentProvider>

      <Toaster richColors position="top-right" />
    </>
  );
}