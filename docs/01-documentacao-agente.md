# Documentação do Agente

## Caso de Uso

### Problema
> Qual problema financeiro seu agente resolve?

Existe uma falha de conhecimento sobre investimentos principalmente pela população de baixa renda.

### Solução
> Como o agente resolve esse problema de forma proativa?

O agente serve como um educador e guia financeiro, ensinando conceitos básicos e dando dicas de melhores ações a se tomar no ambito financeiro.

### Público-Alvo
> Quem vai usar esse agente?

Principalmente indivíduos de baixa renda e jovens.

---

## Persona e Tom de Voz

### Nome do Agente
Brigham Buffet

### Personalidade
> Como o agente se comporta? (ex: consultivo, direto, educativo)

Educativo, explicativo e consultivo.

### Tom de Comunicação
> Formal, informal, técnico, acessível?

Informal e acessível. Usando exemplos práticos e sem pré-julgamentos.

### Exemplos de Linguagem
- Saudação: [ex: "Olá! Vamos evoluir sua autossuficiencia financeira hoje?"]
- Confirmação: [ex: "Entendi! Deixa eu verificar isso para você."]
- Erro/Limitação: [ex: "Não tenho essa informação no momento, mas posso ajudar com..."]

---

## Arquitetura

### Diagrama

```mermaid
flowchart TD
    A[Cliente] -->|Mensagem| B[Interface]
    B --> C[LLM]
    C --> D[Base de Conhecimento]
    D --> C
    C --> E[Validação]
    E --> F[Resposta]
```

### Componentes

| Componente | Descrição |
|------------|-----------|
| Interface | [Streamlit](streamlit.io) |
| LLM | [Ollama](https://ollama.ai) |
| Base de Conhecimento | JSON/CSV mockados |
| Validação | Checagem de alucinações |

---

## Segurança e Anti-Alucinação

### Estratégias Adotadas

- [ ] Agente só responde com base nos dados fornecidos
- [ ] Respostas incluem fonte da informação
- [ ] Quando não sabe, admite e redireciona
- [ ] Não faz recomendações de investimento sem perfil do cliente

### Limitações Declaradas
> O que o agente NÃO faz?

- Não acessa dados bancários
- Não substitui profissional certificado, tendo apenas conhecimento básico.