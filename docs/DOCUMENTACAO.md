# 📚 Guia de Documentação: Commits, Branches e Issues

> Índice centralizado da documentação de padrões do projeto com descrição clara de cada documento.

---

## 📄 Documentos Principais

### 1. **[PADROES-COMMITS-BRANCHES.md](PADROES-COMMITS-BRANCHES.md)**

**Para quem?** Todos os envolvidos (Devs, Scrum, DevOps)

**O quê?** Padrão completo de commits e branches do projeto

**Contém:**
- ✅ Padrão Conventional Commits (tipos, formato, validação)
- ✅ Padrão de Branches (tipo/numero-descricao)
- ✅ Automações (todos os hooks e workflows)
- ✅ Fluxo visual completo (issue → branch → commit → PR → fechamento)
- ✅ Exemplos práticos (Feature, Bugfix, Hotfix)
- ✅ Boas práticas por role (Devs, Scrum, DevOps)
- ✅ Troubleshooting

**Quando ler?**
- 🆕 Primeiro dia no projeto
- 📖 Referência geral de padrões
- 🔧 Quando precisa lembrar da sintaxe de commit

---

### 2. **[RASTREIO-ISSUES.md](RASTREIO-ISSUES.md)**

**Para quem?** Principalmente Scrum Masters e DevOps (visualizações de tracking)

**O quê?** Como rastrear a relação entre Issues, Branches e PRs

**Contém:**
- ✅ Nomenclatura de branches (tipo/numero-descricao)
- ✅ Como GitHub relaciona issue → branch → PR
- ✅ Fluxo de automação (workflows)
- ✅ Como encontrar issues por branch
- ✅ Linking de commits e PRs
- ✅ Labels disponíveis
- ✅ Exemplo prático de rastreio completo

**Quando ler?**
- 👀 Visualização de status de uma issue
- 📊 Scrum Master acompanhando progresso
- 🔍 Encontrar qual branch está relacionada a qual issue
- 📈 DevOps entendendo o rastreio

---

## 🔄 Diferenças Rápidas

| Aspecto | PADROES-COMMITS-BRANCHES.md | RASTREIO-ISSUES.md |
|---------|----------------------------|-------------------|
| **Foco Principal** | Padrões de commits e branches | Rastreio de issues |
| **Público** | Todos | Scrum + DevOps |
| **Detalhe em Commits** | ✅ Completo (tipos, validação, exemplos) | ❌ Apenas referência |
| **Detalhe em Branches** | ✅ Completo | ✅ Completo |
| **Automações** | ✅ Design e funcionamento | ✅ Funcionamento |
| **Labels** | ✅ Lista | ✅ Lista |
| **Exemplos** | ✅ 3 exemplos detalhados | ✅ 1 exemplo de rastreio |

---

## 🎯 Fluxo por Persona

### 👨‍💻 Desenvolvedor

**Ler primeiro:**
1. [PADROES-COMMITS-BRANCHES.md](PADROES-COMMITS-BRANCHES.md) - Entender padrões
2. [RASTREIO-ISSUES.md](RASTREIO-ISSUES.md) - Entender o workflow

**Referência rápida:**
```bash
# Padrão de commit
feat(escopo): descrição
fix(escopo): Bug fixado
docs: Atualizações de documentação

# Padrão de branch
feature/123-descricao-kebab-case
bugfix/456-fix-erro
hotfix/789-crash

# Referenciar issue no commit
git commit -m "feat: descrição

Ref: #123"

# Fechar issue no PR
Closes #456
```

---

### 👨‍💼 Scrum Master

**Ler primeiro:**
1. [RASTREIO-ISSUES.md](RASTREIO-ISSUES.md) - Rastreio de progresso
2. [PADROES-COMMITS-BRANCHES.md](PADROES-COMMITS-BRANCHES.md) - Entender fluxo completo

**O que acompanhar:**
- ✅ Issue #123 tem branch criada?
- ✅ Branch tem commits com `Ref: #123`?
- ✅ PR tem `Closes #123`?
- ✅ PR foi mergeado? (Issue fecha automaticamente)

**Onde encontrar:**
- GitHub Issue → aba "Development" → ver branch e PR
- GitHub Branch → mostram qual issue está vinculada

---

### 🔧 DevOps / Release Manager

**Ler primeiro:**
1. [PADROES-COMMITS-BRANCHES.md](PADROES-COMMITS-BRANCHES.md) - Automações e workflows
2. [RASTREIO-ISSUES.md](RASTREIO-ISSUES.md) - Rastreio para relatórios

**Responsabilidades:**
- ✅ Validar padrão de commits (hook valida automático)
- ✅ Garantir branches seguem padrão
- ✅ Monitorar workflows (auto-create-branch, auto-fill-pr)
- ✅ Gerar relatórios de progresso por tipo de mudança

**Comandos úteis:**
```bash
# Ver commits por tipo
git log --oneline | grep "^feat"
git log --oneline | grep "^fix"

# Ver commits de uma issue
git log --grep "#123"

# Ver histórico de uma branch
git log feature/123-descricao
```

---

## 🔗 Cross-Reference

**Se você está em PADROES-COMMITS-BRANCHES.md e quer entender rastreio:**
→ Veja seção "🔄 Fluxo Completo" ou acesse [RASTREIO-ISSUES.md](RASTREIO-ISSUES.md)

**Se você está em RASTREIO-ISSUES.md e quer detalhes de commits:**
→ Veja seção "📌 Linking no Commit e Pull Request" ou acesse [PADROES-COMMITS-BRANCHES.md](PADROES-COMMITS-BRANCHES.md)

---

## ✅ Validação Rápida

**Está tudo certo?** Verifique:

```bash
# 1. Commit valida pelo hook
✅ git commit funciona
❌ Mesagem "ERRO: Commit inválido!" = padrão errado

# 2. Branch está correta
✅ feature/123-descricao (tipo/numero-descricao)
❌ my-feature, minha_feature, Feature/123 = padrão errado

# 3. PR tem Closes
✅ Descrição contém "Closes #123"
❌ Sem referência = issue não fecha automático

# 4. GitHub vinculou
✅ Na issue, aba "Development" mostra branch e PR
❌ Nada apareça = padrão não seguido
```

---

## 📞 Dúvidas?

| Dúvida | Documento |
|--------|-----------|
| "Como fazer commit?" | [PADROES-COMMITS-BRANCHES.md](PADROES-COMMITS-BRANCHES.md#-padrão-de-commits) |
| "Como nomear branch?" | [PADROES-COMMITS-BRANCHES.md](PADROES-COMMITS-BRANCHES.md#-padrão-de-branches) |
| "Como rastrear issues?" | [RASTREIO-ISSUES.md](RASTREIO-ISSUES.md) |
| "Por que merge fecha issue?" | [RASTREIO-ISSUES.md](RASTREIO-ISSUES.md#-pull-request---fechar-a-issue) |
| "Quais são os tipos de commit?" | [PADROES-COMMITS-BRANCHES.md](PADROES-COMMITS-BRANCHES.md#tipos-aceitos) |
| "Como linkar issue no commit?" | [PADROES-COMMITS-BRANCHES.md](PADROES-COMMITS-BRANCHES.md#5️⃣-rodapé-opcional) |

---

**Última atualização:** 28 de fevereiro de 2026  
**Coerência:** ✅ Validada
