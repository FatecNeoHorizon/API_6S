import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import DashboardLayout from "./DashboardLayout";

// ─── mocks ───────────────────────────────────────────────────────────────────

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), warning: vi.fn(), error: vi.fn() },
}));

vi.mock("react-router-dom", async (orig) => ({
  ...(await orig()),
  Outlet: () => null,
}));

// ─── helpers ─────────────────────────────────────────────────────────────────

function makeFiles() {
  return [
    new File(["x"], "Base de Dados das Perdas de Energia nos Processos Tarifários.xlsx"),
    new File(["x"], "EDP_SP_391_2016-12-31_M6_20170707-0903.gdb.zip"),
    new File(["x"], "indicadores-continuidade-coletivos-2020-2029.csv"),
    new File(["x"], "indicadores-continuidade-coletivos-limite.csv"),
  ];
}

function setupXHR(batchId = "batch-test") {
  const handlers = {};
  const xhr = {
    upload: { addEventListener: vi.fn() },
    addEventListener: vi.fn((ev, cb) => {
      handlers[ev] = cb;
    }),
    open: vi.fn(),
    send: vi.fn(),
    status: 202,
    responseText: JSON.stringify({ batch_id: batchId }),
    triggerLoad: () => handlers.load?.(),
  };
  vi.spyOn(globalThis, "XMLHttpRequest").mockReturnValue(xhr);
  return xhr;
}

function renderLayout() {
  return render(
    <MemoryRouter>
      <DashboardLayout />
    </MemoryRouter>,
  );
}

async function openModalAndAddFiles() {
  fireEvent.click(screen.getByText(/upload de arquivos/i));
  await act(async () => {}); // flush React state so modal renders
  const input = document.getElementById("fileInput");
  Object.defineProperty(input, "files", {
    value: makeFiles(),
    configurable: true,
  });
  fireEvent.change(input);
}

async function clickSend() {
  fireEvent.click(screen.getByRole("button", { name: /enviar/i }));
}

// ─── acceptance criteria ─────────────────────────────────────────────────────

describe("[TEST] 4.8.3 – Processing feedback acceptance criteria", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  // Critério 1: polling único para todos os arquivos
  it("polls a single batch endpoint for all files, not per-file endpoints", async () => {
    const xhr = setupXHR();
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ batch_id: "batch-test", status: "PROCESSING", files: {} }),
    });

    renderLayout();
    await act(async () => { await openModalAndAddFiles(); });
    await act(async () => { await clickSend(); });
    act(() => xhr.triggerLoad());

    await act(async () => { vi.advanceTimersByTime(5000); });

    expect(globalThis.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/upload/batch/batch-test",
    );
    expect(globalThis.fetch).not.toHaveBeenCalledWith(
      expect.stringContaining("/upload/status/"),
    );
  });

  // Critério 2: para automaticamente em SUCCESS, SUCCESS_WITH_WARNINGS e ERROR
  it.each(["SUCCESS", "SUCCESS_WITH_WARNINGS", "ERROR"])(
    "stops polling automatically when batch status is %s",
    async (finalStatus) => {
      const xhr = setupXHR();
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ batch_id: "batch-test", status: finalStatus, files: {} }),
      });

      renderLayout();
      await act(async () => { await openModalAndAddFiles(); });
      await act(async () => { await clickSend(); });
      act(() => xhr.triggerLoad());

      await act(async () => { vi.advanceTimersByTime(5000); }); // tick 1 → status final recebido
      const callsAfterFinal = globalThis.fetch.mock.calls.length;

      await act(async () => { vi.advanceTimersByTime(5000); }); // tick 2 → não deve chamar novamente
      expect(globalThis.fetch.mock.calls.length).toBe(callsAfterFinal);
    },
  );

  // Critério 3: WARNING exibe ícone amarelo e detalhes de reconciliação
  it("shows reconciliation invalid count on SUCCESS_WITH_WARNINGS", async () => {
    const xhr = setupXHR();
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        batch_id: "batch-test",
        status: "SUCCESS_WITH_WARNINGS",
        files: {
          indicadores_continuidade: {
            status: "SUCCESS_WITH_WARNINGS",
            reconciliation: {
              status: "WARNING",
              results: {
                indicadores_conjunto: { checked: 100, valid: 10, invalid: 90 },
              },
            },
          },
        },
      }),
    });

    renderLayout();
    await act(async () => { await openModalAndAddFiles(); });
    await act(async () => { await clickSend(); });
    act(() => xhr.triggerLoad());

    await act(async () => { vi.advanceTimersByTime(5000); });

    expect(
      screen.getByText(/90 referências inválidas detectadas/i),
    ).toBeInTheDocument();
  });

  // Critério 4: falha de rede mantém estado anterior e continua polling
  it("keeps previous state on network failure and continues polling", async () => {
    const xhr = setupXHR();
    let callCount = 0;
    globalThis.fetch = vi.fn().mockImplementation(async () => {
      callCount++;
      if (callCount === 1) return { ok: false }; // falha de rede no 1º tick
      return {
        ok: true,
        json: async () => ({ batch_id: "batch-test", status: "PROCESSING", files: {} }),
      };
    });

    renderLayout();
    await act(async () => { await openModalAndAddFiles(); });
    await act(async () => { await clickSend(); });
    act(() => xhr.triggerLoad());

    // Após upload: arquivos em "processando"
    expect(screen.getAllByText(/processando/i).length).toBeGreaterThan(0);

    await act(async () => { vi.advanceTimersByTime(5000); }); // tick 1 → falha de rede

    // Estado mantido: ainda "processando"
    expect(screen.getAllByText(/processando/i).length).toBeGreaterThan(0);

    await act(async () => { vi.advanceTimersByTime(5000); }); // tick 2 → polling continua
    expect(callCount).toBe(2);
  });

  // Critério 5: modal bloqueado durante processamento
  it("disables cancel and close buttons while processing", async () => {
    setupXHR();
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ batch_id: "batch-test", status: "PROCESSING", files: {} }),
    });

    renderLayout();
    await act(async () => { await openModalAndAddFiles(); });
    await act(async () => { await clickSend(); });

    // XHR não resolveu ainda — isUploading = true
    expect(screen.getByRole("button", { name: /cancelar/i })).toBeDisabled();
  });
});
