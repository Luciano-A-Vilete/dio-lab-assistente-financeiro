import streamlit as st
from agente import (
    load_perfil, load_produtos, load_transacoes, load_historico,
    build_context, chat_stream,
)

st.set_page_config(page_title="Brigham Buffet", page_icon="💰", layout="wide")

QUICK_ACTIONS = [
    "Quanto gastei esse mês?",
    "Como está minha reserva de emergência?",
    "Qual investimento combina com meu perfil?",
    "Me explica o que é Tesouro Selic.",
    "Onde posso cortar gastos?",
]

# ── Data (loaded once per session) ────────────────────────────────────────────

@st.cache_resource
def get_data():
    perfil     = load_perfil()
    produtos   = load_produtos()
    transacoes = load_transacoes()
    historico  = load_historico()
    return perfil, produtos, transacoes, historico


@st.cache_resource
def get_context() -> str:
    return build_context(*get_data())


# ── Sidebar ───────────────────────────────────────────────────────────────────

perfil, _, transacoes, _ = get_data()

with st.sidebar:
    st.header("Perfil do Cliente")
    st.markdown(f"**{perfil['nome']}**, {perfil['idade']} anos")
    st.markdown(f"Renda mensal: **R$ {perfil['renda_mensal']:,.2f}**")

    perfil_badge = {"conservador": "🟢", "moderado": "🟡", "arrojado": "🔴"}
    badge = perfil_badge.get(perfil["perfil_investidor"], "⚪")
    st.markdown(f"Perfil: {badge} **{perfil['perfil_investidor'].capitalize()}**")

    st.divider()

    # Emergency reserve progress
    reserva_atual   = perfil["reserva_emergencia_atual"]
    reserva_meta    = next(
        (m["valor_necessario"] for m in perfil["metas"]
         if "emergência" in m["meta"].lower() or "emergencia" in m["meta"].lower()),
        reserva_atual,
    )
    progresso = min(reserva_atual / reserva_meta, 1.0)
    st.markdown("**Reserva de Emergência**")
    st.progress(progresso, text=f"R$ {reserva_atual:,.0f} / R$ {reserva_meta:,.0f}")

    st.divider()

    # Top spending categories
    totais: dict[str, float] = {}
    for t in transacoes:
        if t["tipo"] == "saida":
            totais[t["categoria"]] = totais.get(t["categoria"], 0) + float(t["valor"])
    top3 = sorted(totais.items(), key=lambda x: -x[1])[:3]
    st.markdown("**Maiores gastos do mês**")
    for cat, val in top3:
        st.markdown(f"- {cat.capitalize()}: R$ {val:,.2f}")

    st.divider()

    # Quick action buttons
    st.markdown("**Perguntas rápidas**")
    for label in QUICK_ACTIONS:
        if st.button(label, use_container_width=True):
            st.session_state["quick_action"] = label

    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.messages = []

# ── Main chat ─────────────────────────────────────────────────────────────────

st.title("💰 Brigham Buffet")
st.caption("Seu assistente financeiro educativo — simples, honesto e sem julgamentos.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Resolve input: typed message or quick-action button
chat_input = st.chat_input("Como posso ajudar com suas finanças hoje?")
if "quick_action" in st.session_state:
    prompt = st.session_state.pop("quick_action")
elif chat_input:
    prompt = chat_input
else:
    prompt = None

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            context = get_context()
            full_reply = st.write_stream(
                chat_stream(st.session_state.messages, context)
            )
        except Exception as e:
            full_reply = f"⚠️ Erro ao conectar com o modelo: {e}"
            st.markdown(full_reply)

    st.session_state.messages.append({"role": "assistant", "content": full_reply})
