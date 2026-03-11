# Skill: analisa-feedbacks-criativos

Analisa os criativos reprovados na lista **📲 Conteúdo** do ClickUp, lê os comentários do Felipe explicando o motivo da reprovação, e propõe melhorias concretas na skill `criador-vdscripts`.

## Uso

`/analisa-feedbacks-criativos` — executa a análise completa e propõe atualizações

---

## Passo a passo de execução

### 1. Buscar tarefas reprovadas

Usar `mcp__claude_ai_ClickUp__clickup_search` com filtro:
```
filters: {
  asset_types: ["task"],
  location: { subcategories: ["901312880763"] },
  task_statuses: ["unstarted"]  ← status "❌ reprovado" aparece como unstarted no filtro
}
keywords: ""
```

> Se o filtro por status não funcionar, buscar todas as tarefas da lista e filtrar manualmente pelo status `❌ reprovado`.

### 2. Para cada tarefa reprovada

Usar `mcp__claude_ai_ClickUp__clickup_get_task_comments` com o `task_id` de cada tarefa reprovada.

- **Ignorar** tarefas sem nenhum comentário — registrar na lista de "incompletas"
- **Considerar** apenas comentários do Felipe (user ID: `3195912`)
- Se houver comentários de outros usuários, ignorá-los na análise

### 3. Montar relatório de reprovações

Para cada tarefa com comentário do Felipe, extrair:
- **Ângulo usado** (identificado pelo título da tarefa)
- **Motivo da reprovação** (comentário do Felipe)
- **Categoria do problema** — classificar em:
  - `tom` — linguagem ou voz fora do padrão
  - `estrutura` — hook, corpo ou CTA mal construído
  - `ângulo` — abordagem que não ressoa com o ICP
  - `repetição` — muito parecido com outro criativo
  - `outro` — motivo não classificável

### 4. Propor melhorias

Com base no relatório, propor atualizações em dois arquivos:

**`angulos.md`** — para cada ângulo reprovado:
- Se reprovado por `ângulo`: sugerir desativar ou reescrever o ângulo
- Se reprovado por `repetição`: sugerir marcar como "usar com moderação"
- Se reprovado por `tom` ou `estrutura`: o ângulo pode ser mantido, mas registrar a observação

**`SKILL.md` do criador-vdscripts** — adicionar ou atualizar regras em:
- Seção "Regras de Copy > Nunca" — se o problema for recorrente
- Seção "Tom de Voz" — se o feedback indicar desvio de voz
- Seção "Estrutura" — se o feedback indicar problema de formato

### 5. Apresentar proposta para aprovação

Exibir o relatório completo e as mudanças propostas. **Não aplicar nenhuma alteração** nos arquivos sem confirmação explícita da usuária.

Formato de apresentação:
```
## Relatório de Reprovações

### Tarefas analisadas: X
### Tarefas sem comentário (incompletas): X

---

[Para cada reprovação:]
**Tarefa:** [nome]
**Motivo (Felipe):** "[comentário]"
**Categoria:** [tom / estrutura / ângulo / repetição / outro]

---

## Propostas de Melhoria

### angulos.md
- [mudança proposta]

### SKILL.md (criador-vdscripts)
- [mudança proposta]

---

Aplicar essas mudanças? (sim/não)
```

### 6. Aplicar mudanças aprovadas

Se a usuária confirmar, editar os arquivos conforme proposto usando as ferramentas `Edit` ou `Write`.

---

## Referências

- **Lista:** `📲 Conteúdo` (ID: `901312880763`)
- **Status reprovado:** `❌ reprovado`
- **Felipe ID:** `3195912`
- **Skill a melhorar:** `.claude/skills/criador-vdscripts/SKILL.md`
- **Banco de ângulos:** `.claude/skills/criador-vdscripts/angulos.md`
