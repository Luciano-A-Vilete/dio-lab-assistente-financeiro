import json
import csv
import os
import ollama
from config import OLLAMA_MODEL, OLLAMA_HOST, DATA_DIR


# ── Data loading ──────────────────────────────────────────────────────────────

def load_perfil() -> dict:
    path = os.path.join(DATA_DIR, "perfil_investidor.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_produtos() -> list[dict]:
    path = os.path.join(DATA_DIR, "produtos_financeiros.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_transacoes() -> list[dict]:
    path = os.path.join(DATA_DIR, "transacoes.csv")
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_historico() -> list[dict]:
    path = os.path.join(DATA_DIR, "historico_atendimento.csv")
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ── Context builder ───────────────────────────────────────────────────────────

def build_context(perfil: dict, produtos: list[dict],
                  transacoes: list[dict], historico: list[dict]) -> str:
    # ── Perfil ────────────────────────────────────────────────────────────────
    metas_txt = "\n".join(
        f"  • {m['meta']}: R$ {m['valor_necessario']:,.2f} — prazo {m['prazo']}"
        for m in perfil.get("metas", [])
    )
    perfil_txt = (
        f"Nome: {perfil['nome']} | Idade: {perfil['idade']} | "
        f"Profissão: {perfil['profissao']}\n"
        f"Renda mensal: R$ {perfil['renda_mensal']:,.2f} | "
        f"Patrimônio total: R$ {perfil['patrimonio_total']:,.2f}\n"
        f"Perfil de investidor: {perfil['perfil_investidor']} | "
        f"Aceita risco: {'Sim' if perfil['aceita_risco'] else 'Não'}\n"
        f"Reserva de emergência atual: R$ {perfil['reserva_emergencia_atual']:,.2f}\n"
        f"Metas:\n{metas_txt}"
    )

    # ── Transações agregadas por categoria ────────────────────────────────────
    totais: dict[str, float] = {}
    for t in transacoes:
        if t["tipo"] == "saida":
            totais[t["categoria"]] = totais.get(t["categoria"], 0) + float(t["valor"])
    gastos_txt = "\n".join(
        f"  • {cat.capitalize()}: R$ {valor:,.2f}"
        for cat, valor in sorted(totais.items(), key=lambda x: -x[1])
    )
    receita = sum(float(t["valor"]) for t in transacoes if t["tipo"] == "entrada")
    gastos_txt = f"  • Receita: R$ {receita:,.2f}\n" + gastos_txt

    # ── Produtos compatíveis com o perfil de risco ────────────────────────────
    risk_map = {"conservador": {"baixo"}, "moderado": {"baixo", "medio"}}
    allowed = risk_map.get(perfil["perfil_investidor"], {"baixo", "medio", "alto"})
    produtos_txt = "\n".join(
        f"  • {p['nome']}: {p['rentabilidade']} | "
        f"Aporte mín.: R$ {p['aporte_minimo']:.2f} | {p['indicado_para']}"
        for p in produtos if p["risco"] in allowed
    )

    # ── Histórico de atendimento ───────────────────────────────────────────────
    historico_txt = "\n".join(
        f"  • {h['data']} ({h['canal']}): {h['tema']} — {h['resumo']}"
        for h in historico
    )

    return (
        f"PERFIL DO CLIENTE:\n{perfil_txt}\n\n"
        f"TRANSAÇÕES (resumo por categoria):\n{gastos_txt}\n\n"
        f"PRODUTOS DISPONÍVEIS (compatíveis com perfil):\n{produtos_txt}\n\n"
        f"HISTÓRICO DE ATENDIMENTO:\n{historico_txt}"
    )


# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT_TEMPLATE = """\
Você é Brigham Buffet, um assistente financeiro educativo e acessível.
Seu objetivo é ensinar conceitos financeiros básicos e orientar pessoas de
baixa renda e jovens a tomarem decisões mais conscientes com seu dinheiro.

REGRAS OBRIGATÓRIAS:
1. Baseie TODAS as respostas nos dados do cliente fornecidos abaixo.
2. Nunca invente valores, taxas ou produtos que não estejam nos dados.
3. Se não souber ou não tiver dados suficientes, diga claramente:
   "Não tenho essa informação, mas posso ajudar com..."
4. Não faça recomendações de investimento sem considerar o perfil do cliente.
5. Use linguagem simples, sem jargões. Se usar um termo técnico, explique-o.
6. Nunca substitua um profissional certificado — sempre que necessário,
   oriente o cliente a buscar um consultor financeiro.

EXEMPLOS DE BOA CONDUTA (Few-Shot):

Usuário: Quanto eu gastei com alimentação esse mês?
Brigham: Com base nas suas transações, você gastou R$ 570,00 em alimentação
         (Supermercado R$ 450 + Restaurante R$ 120). Isso representa 11,4% da
         sua renda mensal. O ideal é manter esse gasto abaixo de 15%. Está
         indo bem!

Usuário: Onde devo investir meu dinheiro?
Brigham: Vendo seu perfil moderado e que sua reserva de emergência ainda não
         está completa (R$ 10.000 de R$ 15.000), eu sugiro priorizar o
         Tesouro Selic ou CDB com liquidez diária antes de pensar em outros
         investimentos. Posso explicar como cada um funciona?

Usuário: Qual a previsão do tempo para amanhã?
Brigham: Essa informação está fora do meu escopo — sou especializado em
         finanças pessoais. Posso ajudar com suas metas, gastos ou
         investimentos?

--- DADOS DO CLIENTE ---
{context}
--- FIM DOS DADOS ---
"""


def build_system_prompt(context: str) -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(context=context)


# ── Chat ──────────────────────────────────────────────────────────────────────

def chat(messages: list[dict], context: str) -> str:
    system = build_system_prompt(context)
    payload = [{"role": "system", "content": system}] + messages
    client = ollama.Client(host=OLLAMA_HOST)
    response = client.chat(model=OLLAMA_MODEL, messages=payload)
    return response["message"]["content"]


def chat_stream(messages: list[dict], context: str):
    """Yields text chunks as the model generates them (for st.write_stream)."""
    system = build_system_prompt(context)
    payload = [{"role": "system", "content": system}] + messages
    client = ollama.Client(host=OLLAMA_HOST)
    stream = client.chat(model=OLLAMA_MODEL, messages=payload, stream=True)
    for chunk in stream:
        yield chunk["message"]["content"]
