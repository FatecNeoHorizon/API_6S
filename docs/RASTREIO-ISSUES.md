# 📋 Padrão de Rastreio: Issues e Branches

> Guia de como rastrear a relação entre Issues no GitHub e Branches de desenvolvimento.
>
> 📖 **Relacionado:** [PADROES-COMMITS-BRANCHES.md](PADROES-COMMITS-BRANCHES.md) - Padrões completos de commits e branches

## 🔗 Padrão de Nomenclatura

### Formato da Branch
```
tipo/numero-descricao-em-kebab-case
```

### Exemplos
| Tipo | Branch | Issue | Descrição |
|------|--------|-------|-----------|
| Feature | `feature/123-adicionar-autenticacao` | #123 | Nova funcionalidade |
| Bugfix | `bugfix/456-corrigir-erro-login` | #456 | Correção de bug |
| Hotfix | `hotfix/789-crash-producao` | #789 | Fixes críticos em prod |
| Docs | `docs/234-guia-setup` | #234 | Documentação |

## 🤖 Automação com GitHub Actions

Quando você **cria um issue**, o workflow `auto-create-branch.yml` automaticamente:

1. ✅ Lê o tipo pela label (`type:feature`, `type:bug`, etc)
2. ✅ Extrai o número do issue (#123)
3. ✅ Converte o título para kebab-case
4. ✅ Cria a branch: `tipo/123-seu-descricao`
5. ✅ Comenta no issue com o comando para checkout

## 📊 Fluxo Completo

```
┌─────────────────┐
│  Criar Issue    │
│  (com label)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  GitHub Action Triggers        │
│  - Lê labels e título           │
│  - Extrai número do issue       │
│  - Converte para kebab-case     │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Branch Criada Automaticamente  │
│  feature/123-seu-descricao      │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Commit comentado no Issue      │
│  com comando de checkout        │
└─────────────────────────────────┘
```

## 🎯 Como Clonar a Branch do Issue

Quando você lê um issue e quer trabalhar nele:

```bash
# GitHub Actions comenta automaticamente com:
git checkout feature/123-seu-descricao

# Ou clonar desde zero:
git clone https://github.com/FatecNeoHorizon/API_6S.git
cd API_6S
git checkout feature/123-seu-descricao
```

## 📌 Linking no Commit e Pull Request

### ✅ No Commit - Apenas referenciar

```bash
# Referencia a issue (cria histórico, mas NÃO fecha)
git commit -m "feat(auth): implementar JWT

- Adicionar JWT para autenticação
- Validar token em middlewares
- Implementar refresh token

Ref: #123"
```

### ✅ No Pull Request - Fechar a issue

```markdown
## Descrição
Implementação de autenticação JWT

Closes #123

## Tipo de Mudança
- [x] Nova funcionalidade
- [ ] Correção de bug
- [ ] Breaking change

## Checklist
- [x] Testes implementados
- [x] Documentação atualizada
```

**O `Closes #123` no PR:**
- ✅ Vincula o PR à issue
- ✅ Mostra a branch no Development
- ✅ **FECHA a issue automaticamente ao fazer merge**

## 🔍 Encontrando Issues por Branch

No GitHub:

1. **Pelo Issue Number no nome da branch:**
   - `feature/123-*` → Issue #123
   - Está no próprio nome! 🎯

2. **Via GitHub UI:**
   - Clique na issue
   - Veja a aba "Development" 
   - Acompanhe a branch e PR associadas

3. **Via Git local:**
   ```bash
   # Ver todas as branches com número
   git branch -a | grep -E "feature/[0-9]+"
   
   # Verificar qual issue cada branch representa
   git branch -a | sed 's/.*\/\([0-9]*\)-.*/Issue #\1/'
   ```

## 📝 Checklist ao Trabalhar em Issue

- [ ] Issue criado com label (`type:feature`, `type:bug`, etc)
- [ ] Branch criada automaticamente
- [ ] Fez checkout na branch correta
- [ ] Commits seguem padrão Conventional Commits: `feat(escopo): descrição`
- [ ] Commits referenciam issue com `Ref: #123` no corpo
- [ ] PR criado com `Closes #123` na descrição
- [ ] PR mergeado para `main` ou `develop`
- [ ] Issue **fecha automaticamente** ao fazer merge do PR ✅

## 🏷️ Labels Disponíveis

### Tipos (obrigatório um)
- `type:feature` - Nova funcionalidade
- `type:bug` - Correção de bug
- `type:hotfix` - Fix crítico em produção
- `type:documentation` - Documentação
- `type:story` - User Story (Scrum)

### Prioridade (opcional)
- `priority:low` - Baixa
- `priority:medium` - Média
- `priority:high` - Alta
- `priority:critical` - Crítica

### Status (automático)
- `status:in-progress` - Em desenvolvimento
- `status:review` - Aguardando review
- `status:done` - Concluído

## 💡 Dicas

1. **Sempre use o número na branch** - Facilita rastreio
2. **Commits com #123** - Cria histório no issue
3. **Squash only if needed** - Não squash commits referenciam a issue
4. **PR description** - Coloque "Closes #123" para link automático
5. **Branch protection** - Exija review antes de merge

## 🚀 Exemplo Prático

**Issue criado:**
```
Título: [FEATURE] - Implementar validação de email
Número: #42
Label: type:feature
```

**GitHub Action:**
```
✅ Branch criada: feature/42-implementar-validacao-de-email
📝 Comentário adicionado com comando de checkout
```

**Você localmente:**
```bash
git checkout feature/42-implementar-validacao-de-email

# Trabalhar, fazer commits (apenas referencia a issue)
git commit -m "feat(validation): add email validation

- Add email format validation
- Add domain validation

Ref: #42"

# Push
git push origin feature/42-implementar-validacao-de-email

# Criar Pull Request com 'Closes #42'
```

**No Pull Request (descrição):**
```markdown
## Descrição
Implementação de validação de email para registro de usuários

Closes #42

## Tipo de Mudança
- [x] Nova funcionalidade

## Checklist
- [x] Testes implementados
- [x] Documentação atualizada
```

**GitHub automaticamente:**
- ✅ Vincula commits à issue #42
- ✅ Mostra branch no Development
- ✅ **FECHA a issue ao fazer merge do PR**

---

**Resultado:** Rastreamento completo da issue até production! 🎯
