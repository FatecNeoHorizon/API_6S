<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Zeus — Confirmar Saída</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous"/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="${url.resourcesPath}/css/zeus.css"/>
  <style>
    .logout-actions {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      margin-top: 0.25rem;
    }
    .btn-cancel {
      width: 100%;
      padding: 0.75rem;
      background: transparent;
      color: #64748b;
      font-size: 0.875rem;
      font-weight: 500;
      font-family: inherit;
      border: 1px solid #e2e8f0;
      border-radius: 0.5rem;
      cursor: pointer;
      transition: background 0.15s, border-color 0.15s;
      text-align: center;
      text-decoration: none;
      display: block;
    }
    .btn-cancel:hover {
      background: #f1f5f9;
      border-color: #cbd5e1;
    }
    .logout-icon {
      display: flex;
      justify-content: center;
      margin-bottom: 1rem;
      color: #64748b;
    }
  </style>
</head>
<body>

  <div class="bg-overlay">
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
  </div>

  <main class="login-wrapper">
    <div class="card">

      <div class="logo-container">
        <div class="logo-ring">
          <div class="logo-inner">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24"
                 fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
          </div>
        </div>
      </div>

      <h1 class="card-title">Zeus</h1>

      <div class="logout-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24"
             fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
      </div>

      <p style="text-align:center; font-size:1rem; font-weight:600; color:#1e293b; margin-bottom:0.5rem;">
        Deseja encerrar a sessão?
      </p>
      <p style="text-align:center; font-size:0.875rem; color:#64748b; margin-bottom:1.5rem;">
        Você será desconectado de todas as aplicações Zeus.
      </p>

      <form method="POST" action="${logoutConfirm.actionUri!}" class="logout-actions">
        <input type="hidden" name="${logoutConfirm.code!}" value="${logoutConfirm.code!}"/>
        <button type="submit" name="confirmLogout" value="true" class="btn-login">
          Sair
        </button>
      </form>

      <div style="margin-top:0.75rem;">
        <button type="button" onclick="history.back()" class="btn-cancel">
          Voltar ao sistema
        </button>
      </div>

      <footer class="card-footer">
        Tecsys do Brasil — Todos os direitos reservados
      </footer>

    </div>
  </main>

</body>
</html>
