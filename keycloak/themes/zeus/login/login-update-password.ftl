<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Zeus — Nova senha</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous"/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="${url.resourcesPath}/css/zeus.css"/>
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

      <h1 class="card-title">Nova senha</h1>
      <p class="card-subtitle">Escolha uma senha segura para sua conta.</p>

      <#if message?has_content>
        <div class="alert alert-${message.type}">
          ${kcSanitize(message.summary)?no_esc}
        </div>
      </#if>

      <form id="kc-passwd-update-form" action="${url.loginAction}" method="post" class="login-form">
        <input type="text" id="username" name="username" value="${username!''}" autocomplete="username"
               style="display: none;" readonly/>

        <div class="field">
          <label for="password-new">Nova senha</label>
          <div class="password-wrapper">
            <input
              type="password"
              id="password-new"
              name="password-new"
              autofocus
              autocomplete="new-password"
              placeholder="••••••••"
            />
            <button type="button" class="toggle-password" onclick="togglePwd('password-new','eye-new')" aria-label="Mostrar senha">
              <svg id="eye-new" xmlns="http://www.w3.org/2000/svg" width="16" height="16"
                   viewBox="0 0 24 24" fill="none" stroke="currentColor"
                   stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
            </button>
          </div>
        </div>

        <div class="field">
          <label for="password-confirm">Confirmar nova senha</label>
          <div class="password-wrapper">
            <input
              type="password"
              id="password-confirm"
              name="password-confirm"
              autocomplete="new-password"
              placeholder="••••••••"
            />
            <button type="button" class="toggle-password" onclick="togglePwd('password-confirm','eye-confirm')" aria-label="Mostrar confirmação">
              <svg id="eye-confirm" xmlns="http://www.w3.org/2000/svg" width="16" height="16"
                   viewBox="0 0 24 24" fill="none" stroke="currentColor"
                   stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
            </button>
          </div>
        </div>

        <button type="submit" class="btn-login">Salvar nova senha</button>
      </form>

      <footer class="card-footer">
        Tecsys do Brasil — Todos os direitos reservados
      </footer>

    </div>
  </main>

  <script>
    function togglePwd(fieldId, iconId) {
      var input = document.getElementById(fieldId);
      var icon  = document.getElementById(iconId);
      if (input.type === 'password') {
        input.type = 'text';
        icon.innerHTML =
          '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8' +
          'a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4' +
          'c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07' +
          'a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>';
      } else {
        input.type = 'password';
        icon.innerHTML =
          '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>' +
          '<circle cx="12" cy="12" r="3"/>';
      }
    }
  </script>

</body>
</html>
