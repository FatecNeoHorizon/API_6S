import { AppRoutes } from "./routes";
import { Toaster } from "sonner";
import PendingConsentProvider from "@/components/consent/PendingConsentProvider";

export default function App() {
  return (
    <PendingConsentProvider>
      <AppRoutes />
      <Toaster richColors position="top-right" />
    </PendingConsentProvider>
  );
}