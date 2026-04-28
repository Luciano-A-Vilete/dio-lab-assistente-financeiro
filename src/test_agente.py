"""
Run the 4 test scenarios from docs/04-metricas.md and print results.
Usage: python test_agente.py
"""
import sys
from agente import load_perfil, load_produtos, load_transacoes, load_historico, build_context, chat

TESTS = [
    {
        "id": 1,
        "nome": "Consulta de gastos",
        "pergunta": "Quanto gastei com alimentação?",
        "criterio": "Deve mencionar R$ 570 (ou os valores individuais R$ 450 e R$ 120)",
    },
    {
        "id": 2,
        "nome": "Recomendação de produto",
        "pergunta": "Qual investimento você recomenda para mim?",
        "criterio": "Deve sugerir Tesouro Selic ou CDB (compatíveis com perfil moderado)",
    },
    {
        "id": 3,
        "nome": "Pergunta fora do escopo",
        "pergunta": "Qual a previsão do tempo para amanhã?",
        "criterio": "Deve recusar e redirecionar para finanças",
    },
    {
        "id": 4,
        "nome": "Produto inexistente",
        "pergunta": "Quanto rende o produto XYZ?",
        "criterio": "Deve admitir que não tem essa informação",
    },
]


def run_tests():
    print("Carregando dados e contexto...")
    context = build_context(
        load_perfil(), load_produtos(), load_transacoes(), load_historico()
    )

    passed = 0
    for test in TESTS:
        print(f"\n{'='*60}")
        print(f"Teste {test['id']}: {test['nome']}")
        print(f"Pergunta: {test['pergunta']}")
        print(f"Critério: {test['criterio']}")
        print("-" * 60)

        try:
            resposta = chat([{"role": "user", "content": test["pergunta"]}], context)
            print(f"Resposta:\n{resposta}")
        except Exception as e:
            print(f"ERRO: {e}")
            continue

        resultado = input("\nPassou? (s/n): ").strip().lower()
        if resultado == "s":
            passed += 1
            print("✅ Aprovado")
        else:
            print("❌ Reprovado")

    print(f"\n{'='*60}")
    print(f"Resultado: {passed}/{len(TESTS)} testes aprovados")
    score = passed / len(TESTS) * 100
    print(f"Score: {score:.0f}%")
    return passed


if __name__ == "__main__":
    try:
        run_tests()
    except KeyboardInterrupt:
        print("\nTestes interrompidos.")
        sys.exit(0)
