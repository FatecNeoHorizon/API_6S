# Burndown Automatic Generator

Projeto Java/Spring Boot para gerar automaticamente um gráfico burndown com base em dados reais de Issues do GitHub Projects (GraphQL API).

## Visão Geral

Fluxo de execução:
1. `ProjectDataProvider` busca dados do GitHub Project via GraphQL.
2. `BurndownDataMapper` transforma Issues em série temporal da sprint ativa.
3. `BurndownChartGenerator` gera o PNG do gráfico.
4. `BurndownApplication` orquestra tudo e encerra a execução com `exit code`.

Saída padrão do gráfico:
- `src/main/resources/static/burndown.png`

## Autoria e Liderança do Projeto

Este projeto foi idealizado, arquitetado, implementado e operacionalizado integralmente por **Cesar Pelogia**.

Responsabilidade de ponta a ponta:
- concepção da ideia e definição do problema
- desenho da arquitetura e modelagem da solução
- desenvolvimento da aplicação e integração com GitHub GraphQL API
- automação de execução no GitHub Actions
- validação técnica, troubleshooting e estabilização da entrega

Perfis profissionais:
- GitHub: `https://github.com/cesarpelogia`
- LinkedIn: `http://www.linkedin.com/in/cesar-augusto-anselmo-pelogia-truyts-94a08a268/`

## Stack

- Java 21
- Spring Boot 4
- Maven Wrapper (`mvnw` / `mvnw.cmd`)
- JFreeChart
- GitHub GraphQL API
- GitHub Actions

## Estrutura Principal

- `src/main/java/com/zeus/burndown/BurndownApplication.java`: ponto de entrada e orquestração
- `src/main/java/com/zeus/burndown/integration/github/`: cliente e provedor da API do GitHub
- `src/main/java/com/zeus/burndown/service/`: regras de mapeamento e geração do gráfico
- `src/main/resources/application.properties`: configurações de ambiente
- `.github/workflows/burndowngenerate.yml`: automação CI para gerar e publicar o gráfico

## Configuração

### Variáveis/propriedades relevantes

Em `application.properties`:

```properties
github.api.url=https://api.github.com/graphql
github.api.token=${GITHUB_TOKEN:}
github.org={Nome_da_Organização}
github.project-number={Numero_do_Projeto}

burndown.output.path=src/main/resources/static/burndown.png
burndown.logo.path=
```

### Token

A aplicação lê o token da variável de ambiente `GITHUB_TOKEN`.

No GitHub Actions, o secret `ISSUE_TOKEN_API` é mapeado para `GITHUB_TOKEN` no workflow.

## Execução Local

### Windows (cmd)

```bat
cd burndown
set GITHUB_TOKEN=seu_token_aqui
mvnw.cmd spring-boot:run
```

### Windows (PowerShell)

```powershell
cd burndown
$env:GITHUB_TOKEN="seu_token_aqui"
./mvnw.cmd spring-boot:run
```

### Execução via JAR (mesmo padrão do CI)

```bat
cd burndown
mvnw.cmd clean package -DskipTests
set GITHUB_TOKEN=seu_token_aqui
java -jar target/burndown-0.0.1-SNAPSHOT.jar
```

## Testes

```bat
cd burndown
mvnw.cmd test
```

## GitHub Actions (Automação)

Workflow:
- `/.github/workflows/burndowngenerate.yml`

Comportamento:
- roda diariamente por `cron` e também manualmente (`workflow_dispatch`)
- compila o módulo `burndown`
- executa o JAR para gerar o PNG
- faz commit/push de `src/main/resources/static/burndown.png` quando houver alteração

## Troubleshooting rápido

- Erro de autenticação no GitHub:
  - verifique se `GITHUB_TOKEN` foi definido com o valor real do PAT.
- Sem dados no gráfico:
  - confirme `github.org` e `github.project-number`.
- Workflow não commita:
  - pode ser que o gráfico não tenha mudado naquele dia.

## Resultado esperado

Ao executar com sucesso:
- os logs informam início/fim da geração
- o arquivo `src/main/resources/static/burndown.png` é atualizado
- no CI, o gráfico pode ser versionado automaticamente via commit
