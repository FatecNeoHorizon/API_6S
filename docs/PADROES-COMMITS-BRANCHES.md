# 📋 Padrão de Commits e Branches

> Guia oficial de padrões de commits e nomenclatura de branches para a API 6° Semestre.

**Data:** 28 de fevereiro de 2026  
**Versão:** 1.0  
**Status:** ✅ Aprovado

---

## 📑 Índice

1. [Visão Geral](#visão-geral)
2. [Padrão de Commits](#padrão-de-commits)
3. [Padrão de Branches](#padrão-de-branches)
4. [Fluxo Completo](#fluxo-completo)
5. [Automações](#automações)
6. [Exemplos Práticos](#exemplos-práticos)
7. [Boas Práticas](#boas-práticas)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

Este projeto utiliza **Conventional Commits** + **Git Flow** para manter um histórico de código limpo e rastreável.

### Objetivos

✅ Histórico de commits legível e organizado  
✅ Automação de changelog  
✅ Rastreio claro de issues → branches → commits → pull requests  
✅ Facilitar code review e onboarding de novos devs  
✅ DevOps com visibilidade completa do workflow  

---

## 📝 Padrão de Commits

### Convenção: Conventional Commits

**Formato:**
```
<tipo>(<escopo>): <descrição>

[corpo opcional]

[rodapé opcional]
```

### Tipos Aceitos

| Tipo | Emoji | Uso | Exemplo |
|------|-------|-----|---------|
| `feat` | ✨ | Nova funcionalidade | `feat(auth): implementar JWT` |
| `fix` | 🐛 | Correção de bug | `fix(api): corrigir erro 500` |
| `docs` | 📚 | Documentação | `docs: atualizar README` |
| `style` | 🎨 | Formatação/estilo (sem lógica) | `style: corrigir indentação` |
| `refactor` | ♻️ | Refatoração de código | `refactor(auth): reorganizar lógica` |
| `perf` | ⚡ | Melhorias de performance | `perf(api): otimizar busca` |
| `test` | 🧪 | Testes | `test(auth): adicionar testes JWT` |
| `chore` | 🔧 | Build, CI, dependências | `chore: atualizar deps` |
| `ci` | 🔄 | Integração Contínua | `ci: configurar GitHub Actions` |
| `revert` | ↩️ | Reverter commit | `revert: reverter 'feat(auth)'` |

### Estrutura Detalhada

#### 1️⃣ **Tipo** (Obrigatório)
Deve ser um dos listados acima.

```bash
✅ feat(auth): ...
❌ feature(auth): ...
❌ new(auth): ...
```

#### 2️⃣ **Escopo** (Opcional, mas recomendado)
Área ou módulo afetado.

```bash
✅ feat(auth): implementar JWT
✅ feat(users): adicionar validação
✅ fix(api): corrigir resposta
❌ feat: implementar JWT (sem escopo)
```

#### 3️⃣ **Descrição** (Obrigatório)
- Começar com minúscula
- Imperativo (não passado)
- Sem ponto final

```bash
✅ feat(auth): implementar login JWT
❌ feat(auth): Implementar login JWT
❌ feat(auth): implementou login JWT
❌ feat(auth): implementar login JWT.
```

#### 4️⃣ **Corpo** (Opcional, para detalhes)
Separado por linha em branco. Use para explicar "por quê".

```bash
feat(auth): implementar JWT

- Adicionar JWT para melhor segurança
- Implementar refresh token
- Validar token em middlewares

Closes #123
```

#### 5️⃣ **Rodapé** (Opcional)
- `Closes #123` - Fecha uma issue (usar no PR, não no commit)
- `Ref: #123` - Apenas referencia uma issue
- `Breaking change:` - Para mudanças que quebram compatibilidade

```bash
fix(auth): corrigir erro token

Agora o token expira corretamente.

Ref: #456
```

### Validação Automática

✅ **Git Hook ativado:** `.githooks/commit-msg`

Se o commit não segue o padrão, ele será **rejeitado**:

```
╔════════════════════════════════════════════════╗
║  ❌ ERRO: Commit inválido!                     ║
╚════════════════════════════════════════════════╝

Sua mensagem: "add login feature"

❌ Commit REJEITADO. Corrija e tente novamente:
   git commit --amend -m "feat(auth): implementar login"
```

---

## 🌳 Padrão de Branches

### Convenção: Tipo + Número Issue + Descri​ção

**Formato:**
```
<tipo>/<numero>-<descricao-kebab-case>
```

### Tipos de Branch

| Tipo | Uso | Exemplo |
|------|-----|---------|
| `feature` | Nova funcionalidade | `feature/123-adicionar-login-jwt` |
| `bugfix` | Correção de bug | `bugfix/456-corrigir-autenticacao` |
| `hotfix` | Fix crítico em produção | `hotfix/789-crash-api` |
| `docs` | Documentação | `docs/234-guia-setup` |
| `refactor` | Refatoração | `refactor/567-reorganizar-auth` |
| `perf` | Performance | `perf/890-otimizar-queries` |
| `test` | Testes | `test/345-adicionar-testes-jwt` |
| `chore` | Build/Config | `chore/678-atualizar-deps` |

### Regras

✅ **Deve conter:**
- Tipo válido
- Número da issue (obrigatório para rastreio)
- Descrição em kebab-case (minúsculas, hífens)

```bash
✅ feature/123-adicionar-autenticacao
✅ bugfix/456-fix-erro-login
❌ feature/adicionar-autenticacao (sem número)
❌ feature/123-AdicionarAutenticacao (CamelCase)
❌ feature/123-adicionar_autenticacao (underscore)
```

### Criação Automática

✅ **Workflow ativado:** `auto-create-branch.yml`

Quando você cria um issue:

1. **Adicione label** (`type:feature`, `type:bug`, etc)
2. **GitHub Action dispara automaticamente**
3. Branch é criada: `tipo/123-descricao`
4. Comment adicionado com comando para checkout

```bash
git checkout feature/123-adicionar-login
```

---

## 🔄 Fluxo Completo

```
┌─────────────────────────────────────────────────────────┐
│ 1️⃣  CRIAR ISSUE NO GITHUB                              │
│                                                         │
│ Título: Implementar validação de email                │
│ Número: #42                                             │
│ Label: type:feature                                     │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 2️⃣  AUTO-CREATE-BRANCH WORKFLOW                         │
│                                                         │
│ ✅ Extrai numero: 42                                   │
│ ✅ Extrai tipo: feature                                │
│ ✅ Converte para kebab-case                            │
│ ✅ Cria branch: feature/42-implementar-validacao       │
│ ✅ Comment no issue com checkout command               │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 3️⃣  DESENVOLVER LOCALMENTE                              │
│                                                         │
│ $ git checkout feature/42-implementar-validacao        │
│ $ # Fazer mudanças                                      │
│ $ git add .                                             │
│ $ git commit -m "feat(validation): adicionar email"    │
│                                                         │
│ ✅ Hook valida mensagem                                │
│ ✅ Se inválido, commit é rejeitado                     │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 4️⃣  CRIAR PULL REQUEST                                  │
│                                                         │
│ - Branch: feature/42-implementar-validacao            │
│ - Título: feat(validation): adicionar validação email │
│ - Descrição:                                           │
│   Implementa validação de email no registro            │
│                                                         │
│   Closes #42                                           │
│                                                         │
│ ✅ Auto-fill workflow detecta issue #42               │
│ ✅ Comment informativo adicionado                      │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 5️⃣  REVIEW & MERGE                                      │
│                                                         │
│ ✅ Code review                                         │
│ ✅ Tests passing                                       │
│ ✅ Approve PR                                          │
│ ✅ Merge no main/develop                               │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 6️⃣  FECHAMENTO AUTOMÁTICO                               │
│                                                         │
│ ✅ GitHub detecta "Closes #42" no PR                   │
│ ✅ Issue #42 fecha automaticamente                     │
│ ✅ Branch pode ser deletada                            │
│ ✅ História completa rastreável                        │
└─────────────────────────────────────────────────────────┘
```

---

## 🤖 Automações

### 1. `commit-msg` Hook

**Arquivo:** `.githooks/commit-msg`

- Valida padrão de commit
- Rejeita commits inválidos
- Mensagens de erro detalhadas

**Ativação:**
```bash
git config core.hooksPath .githooks
```

### 2. `post-checkout` Hook

**Arquivo:** `.githooks/post-checkout`

- Valida nome da branch quando você muda de branch
- Apenas aviso (não bloqueia)

### 3. `pre-push` Hook

**Arquivo:** `.githooks/pre-push`

- Impede push de branches com nomes inválidos
- Mensagem de erro clara

**Ativação:** Automática após configurar `core.hooksPath`

### 4. `auto-create-branch` Workflow

**Arquivo:** `.github/workflows/auto-create-branch.yml`

Dispara: Quando issue é criado ou recebe label

```yaml
on:
  issues:
    types: [opened, labeled]
```

**Ações:**
- Extrai numero e tipo da issue
- Cria branch automática
- Comenta no issue
- Usa labels `type:feature`, `type:bug`, etc

### 5. `auto-fill-pr-from-branch` Workflow

**Arquivo:** `.github/workflows/auto-fill-pr-from-branch.yml`

Dispara: Quando PR é aberto

**Ações:**
- Extrai numero da branch
- Detecta tipo de mudança
- Pre-preenche "Closes #123"
- Adiciona comment informativo

---

## 💡 Exemplos Práticos

### Exemplo 1: Feature de Login

**Issue criado:**
```
Título: [FEATURE] - Implementar autenticação com JWT
Número: #42
Label: type:feature
```

**Branch criada automaticamente:**
```
feature/42-implementar-autenticacao-jwt
```

**Você localmente:**
```bash
# Checkout branch
git checkout feature/42-implementar-autenticacao-jwt

# Fazer mudanças...

# Commit seguindo padrão
git commit -m "feat(auth): implementar JWT

- Adicionar JWT para autenticação
- Implementar refresh token
- Validar token em middlewares

Ref: #42"

# Push
git push origin feature/42-implementar-autenticacao-jwt
```

**Pull Request:**
```markdown
## Descrição
Implementação de autenticação com JWT

## Tipo
Feature (Nova funcionalidade)

## Testes
- [x] Testes unitários
- [x] Testes de integração

Closes #42
```

**Resultado:**
- PR é mergeado
- GitHub detecta "Closes #42"
- Issue #42 fecha automaticamente ✅

---

### Exemplo 2: Bugfix de Erro na API

**Issue criado:**
```
Título: [BUG] - Erro 500 ao fazer login
Número: #456
Label: type:bug
```

**Branch criada:**
```
bugfix/456-erro-500-login
```

**Commit:**
```bash
git commit -m "fix(api): corrigir erro 500 no login

O erro ocorria quando email tinha espaços.
Agora fazemos trim() antes de validar.

Ref: #456"
```

**PR com "Closes #456"** → Issue fechada ao merge ✅

---

### Exemplo 3: Hotfix de Produção

**Issue criado:**
```
Título: [HOTFIX] - API fora do ar
Número: #789
Label: type:hotfix, urgent
```

**Branch criada:**
```
hotfix/789-api-fora-do-ar
```

⚠️ **Prioridade máxima!** Merge rápido após testes.

---

## ✅ Boas Práticas

### Para Desenvolvedores

#### ✅ DO's

```bash
# ✅ Commits pequenos e focados
git commit -m "feat(auth): implementar JWT"

# ✅ Mensagens descritivas
git commit -m "feat(auth): implementar JWT

Adicionar autenticação stateless com JWT
para melhorar segurança da API"

# ✅ Referenciar issues
git commit -m "feat: adicionar validação

Ref: #123"

# ✅ Usar branches nomeadas corretamente
git checkout -b feature/123-descricao

# ✅ Um feature por branch
```

#### ❌ DON'Ts

```bash
# ❌ Mensagens genéricas
git commit -m "fix stuff"
git commit -m "update"

# ❌ Commits gigantes
# (Quebrar em múltiplos commits pequenos)

# ❌ Branch com nome errado
git checkout -b my-feature
git checkout -b minha_feature
git checkout -b Feature/123

# ❌ Multiple features em uma branch
# (Criar branch separada para cada feature)
```

### Para Scrum Masters

#### 📊 Rastreio

- **Issue #123** → Branch `feature/123-*` → PR → Merge
- Cada issue tem rastreamento complete
- História clara no GitHub

#### 📈 Métricas

- **Lead Time:** Tempo do commit até produção
- **Deployment Freq:** Quantas vezes por dia/semana
- **Change Failure Rate:** Taxa de falhas em produção
- **MTTR:** Tempo para recovar de falhas

#### 📋 Relatórios

```bash
# Ver commits por tipo
git log --oneline | grep "^feat"
git log --oneline | grep "^fix"
git log --oneline | grep "^bugfix"

# Ver issues fechadas
git log --grep "Closes #"

# Ver histórico de uma branch
git log feature/123-descricao
```

### Para DevOps

#### 🔄 CI/CD

- **Trigger:** Commit em branch → CI rodaqueda
- **Validações:** Lint, Testes, Build, Security Scan
- **Deploy:** Automático para staging após merge

#### 📊 Observabilidade

- Commits linkados a issues
- PR descriptomente documentadas
- Rollback fácil via revert

#### 🔐 Segurança

- Validação de commits
- Branch protection rules
- Require PR review

---

## 🆘 Troubleshooting

### Problema 1: Commit Rejeitado

```
❌ ERRO: Commit inválido!
Sua mensagem: "add login"
```

**Solução:**
```bash
git commit --amend -m "feat(auth): implementar login"
```

### Problema 2: Branch Name Invalid

```
⚠️  Aviso: Nome de branch inválido!
Sua branch: "my-feature"
```

**Solução:**
```bash
git branch -m feature/123-meu-recurso
```

### Problema 3: Issue Não Fecha

**Causa:** PR não tem `Closes #123` na descrição

**Solução:**
```markdown
Closes #123
```

Adicione na descrição do PR e faça merge.

### Problema 4: Branch não foi Criada Automaticamente

**Causa:** Issue sem label

**Solução:**
```bash
1. Adicione label type:feature ao issue
2. Workflow dispara automaticamente
3. Ou crie manualmente:
   git checkout -b feature/123-descricao
```

### Problema 5: Esqueci do Número da Issue

**Solução:** Use o nome da branch!

A branch já tem o número: `feature/123-descricao`

```bash
git branch # Ver branch atual
# feature/123-descricao → Issue é #123
```

---

## 📚 Documentação Relacionada

- **[RASTREIO-ISSUES.md](RASTREIO-ISSUES.md)** - Como rastrear issues, branches e PRs
- **[Conventional Commits](https://www.conventionalcommits.org/)** - Especificação oficial
- **[Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)** - Modelo de branching
- **[DORA Metrics](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-devops-performance)** - Métricas DevOps

---

## 🔐 Configuração Inicial (First Time Setup)

Se você é novo no projeto:

```bash
# 1. Ativar git hooks
git config core.hooksPath .githooks

# 2. Verificar se funciona
git commit --allow-empty -m "test"
# Deve validar a mensagem

# 3. Cancelar commit de teste
git reset --soft HEAD~1
```

---

## ❓ Dúvidas?

📖 Veja: [RASTREIO-ISSUES.md](docs/RASTREIO-ISSUES.md)

---

**Última atualização:** 28 de fevereiro de 2026  
**Mantido por:** Equipe DevOps + Scrum
