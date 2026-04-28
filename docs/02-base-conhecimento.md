# Base de Conhecimento

## Dados Utilizados

| Arquivo | Formato | Para que serve no Assistente? |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Contextualizar interações anteriores |
| `perfil_investidor.json` | JSON | Personalizar recomendações |
| `produtos_financeiros.json` | JSON | Sugerir produtos adequados ao perfil |
| `transacoes.csv` | CSV | Analisar padrão de gastos do cliente |


---

## Adaptações nos Dados

Os dados mockados foram utilizados sem modificações estruturais. A função
`build_context()` em `src/agente.py` é responsável por formatar esses dados
em texto legível para o LLM.

---

## Estratégia de Integração

### Como os dados são carregados?

Os arquivos JSON e CSV são lidos uma única vez no início da sessão via
`@st.cache_resource` no Streamlit. Isso evita releituras desnecessárias do
disco a cada mensagem.

### Como os dados são usados no prompt?

Os dados são convertidos em um bloco de texto pela função `build_context()` e
injetados diretamente no **system prompt** como contexto estático. O LLM
recebe esse contexto em cada chamada, garantindo que as respostas sejam sempre
baseadas nos dados reais do cliente — estratégia conhecida como *context stuffing*.

---

## Exemplo de Contexto Montado

```
PERFIL DO CLIENTE:
- Nome: João Silva | Idade: 32 | Profissão: Analista de Sistemas
- Renda mensal: R$ 5.000 | Patrimônio total: R$ 15.000
- Perfil de investidor: Moderado | Aceita risco: Não
- Objetivo: Construir reserva de emergência
- Metas:
  • Reserva de emergência: R$ 15.000 (atual: R$ 10.000) — prazo: jun/2026
  • Entrada do apartamento: R$ 50.000 — prazo: dez/2027

GASTOS POR CATEGORIA (out/2025):
- Moradia: R$ 1.380 | Alimentação: R$ 570 | Transporte: R$ 295
- Saúde: R$ 188 | Lazer: R$ 55,90

PRODUTOS ADEQUADOS AO PERFIL (baixo/médio risco):
- Tesouro Selic: 100% Selic | Aporte mín.: R$ 30
- CDB Liquidez Diária: 102% CDI | Aporte mín.: R$ 100
- LCI/LCA: 95% CDI | Aporte mín.: R$ 1.000 (isento de IR)
- Fundo Multimercado: CDI+2% | Aporte mín.: R$ 500

HISTÓRICO DE ATENDIMENTO:
- CDB (set/2025): cliente perguntou sobre rentabilidade e prazos
- Tesouro Selic (out/2025): cliente pediu explicação sobre funcionamento
- Metas financeiras (out/2025): acompanhou progresso da reserva de emergência
```
