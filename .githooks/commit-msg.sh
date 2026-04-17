#!/bin/bash

COMMIT_MSG_FILE="$1"
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

FIRST_LINE=$(echo "$COMMIT_MSG" | head -n 1)
LAST_LINE=$(echo "$COMMIT_MSG" | grep -v '^$' | tail -n 1)

TIPO_PATTERN="^(feat|fix|docs|style|refactor|perf|test|chore|ci|revert)(\(.+\))?!?: .+"
CARD_PATTERN="^#[0-9]+$"

# ----------------------------
# 🚫 IGNORAR CASOS AUTOMÁTICOS
# ----------------------------

# Comentários
if echo "$FIRST_LINE" | grep -q "^#"; then
  exit 0
fi

# Merge
if echo "$FIRST_LINE" | grep -qi "^Merge "; then
  exit 0
fi

# Revert automático
if echo "$FIRST_LINE" | grep -qi "^Revert \""; then
  exit 0
fi

# Initial commit
if echo "$FIRST_LINE" | grep -qi "^Initial commit"; then
  exit 0
fi

# Release/versionamento
if echo "$FIRST_LINE" | grep -qiE "^(chore\(release\)|release:)"; then
  exit 0
fi

# Bots
AUTHOR=$(git var GIT_AUTHOR_IDENT)
if echo "$AUTHOR" | grep -qiE "dependabot|renovate|bot|github-actions"; then
  exit 0
fi

# Burndown / automações específicas
if echo "$COMMIT_MSG" | grep -qi "burndown"; then
  exit 0
fi

# ----------------------------
# ✅ VALIDAÇÃO
# ----------------------------

# 1. Valida primeira linha
if ! echo "$FIRST_LINE" | grep -qE "$TIPO_PATTERN"; then
  echo ""
  echo "❌ ERRO: Primeira linha inválida!"
  echo ""
  echo "Formato esperado:"
  echo "  feat(escopo): descrição"
  echo ""
  echo "Exemplo:"
  echo "  feat(database): update database"
  echo ""
  exit 1
fi

# 2. Valida última linha (card)
if ! echo "$LAST_LINE" | grep -qE "$CARD_PATTERN"; then
  echo ""
  echo "❌ ERRO: Card obrigatório no final do commit!"
  echo ""
  echo "Formato esperado:"
  echo "  #123"
  echo ""
  echo "Exemplo completo:"
  echo ""
  echo "feat(database): update database"
  echo ""
  echo "update table from database 1"
  echo ""
  echo "#123"
  echo ""
  exit 1
fi

# Valida o padrão
if ! echo "$COMMIT_MSG" | grep -qE "$TIPO_PATTERN"; then
  echo ""
  echo "╔════════════════════════════════════════════════════════════════╗"
  echo "║          ❌ ERRO: Commit inválido!                            ║"
  echo "╚════════════════════════════════════════════════════════════════╝"
  echo ""
  echo "Sua mensagem: \"$COMMIT_MSG\""
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📝 Estrutura:"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "  <tipo>(<escopo>): <descrição>"
  echo ""
  echo "  <corpo opcional>"
  echo ""
  echo "  #<numero-do-card>"
  echo ""
  echo "  │      │          │"
  echo "  │      │          └─ Descrição breve em minúsculas"
  echo "  │      └─ Opcional: área/módulo afetado"
  echo "  └─ Obrigatório: feat, fix, docs, style, refactor, perf, test, chore, ci, revert"
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "✅ Exemplo válido:"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "  feat(database): update database"
  echo ""
  echo "  update table from database 1"
  echo ""
  echo "  #123"
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "❌ Commit REJEITADO. Corrija a mensagem e tente novamente:"
  echo ""
  echo "   git commit --amend -m \"<tipo>(<escopo>): <descrição>\""
  echo ""
  exit 1
fi

exit 0
