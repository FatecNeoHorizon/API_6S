<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Zeus — Redefinir senha</title>
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

      <h1 class="card-title">Redefinir senha</h1>
      <p class="card-subtitle">Informe seu e-mail para receber o link de redefinição.</p>

      <#if message?has_content>
        <div class="alert alert-${message.type}">
          ${kcSanitize(message.summary)?no_esc}
        </div>
      </#if>

      <form action="${url.loginAction}" method="post" class="login-form">
        <div class="field">
          <label for="username">E-mail</label>
          <input
            type="text"
            id="username"
            name="username"
            autofocus
            autocomplete="email"
            placeholder="seu@email.com"
          />
        </div>

        <button type="submit" class="btn-login">Enviar link de redefinição</button>
      </form>

      <div style="margin-top: 1rem; text-align: center;">
        <a href="${url.loginUrl}" class="forgot-password" style="margin-left: 0;">← Voltar ao login</a>
      </div>

      <footer class="card-footer">
        Tecsys do Brasil — Todos os direitos reservados
      </footer>

    </div>
  </main>

</body>
</html>
