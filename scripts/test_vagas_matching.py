import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')

mapaVagas = {
    1000: ["vendedor de motos (showroom)", "vendedor de motos", "consultor de vendas", "consultor de negocios", "executivo de vendas", "vendedor de salao", "consultor de motocicletas", "showroom", "motos", "vendedor"],
    1002: ["vendedor de acessorios / pecas", "vendedor de acessorios", "consultor de pecas", "balconista de pecas", "vendedor de boutique", "acessorios", "pecas", "boutique"],
    1004: ["recepcionista oficina", "recepcionista", "consultor tecnico", "atendente de oficina", "agendador", "recepcao", "oficina"],
    1006: ["entregador tecnico", "consultor de entrega tecnica", "preparador de motos", "entregador", "entrega", "consultor de entrega"],
    1008: ["estoquista", "almoxarife", "auxiliar de estoque", "repositor", "separador", "estoque"],
    1010: ["mecanico", "tecnico em motocicletas", "reparador de motos", "oficina mecanica"],
    1012: ["aux. mecanico", "aux mecanico", "auxiliar de mecanico", "auxiliar de oficina", "meio-oficial", "ajudante oficina"],
    1014: ["ajudante de mecanico (montador)", "montador de motos", "preparador de motos novas", "ajudante de mecanico", "montador"],
    1016: ["lavador", "preparador estetico", "detalhador", "auxiliar de limpeza", "estetico", "limpeza"],
    1018: ["gerente", "gerente de loja", "gerente comercial", "gerente de vendas", "gerencia"],
    1020: ["supervisor", "supervisor de vendas", "lider de equipe", "encarregado", "supervisao"],
    1022: ["administrativo (financeiro)", "administrativo financeiro", "assistente financeiro", "auxiliar financeiro", "analista de credito", "financeiro", "financas"],
    1024: ["t.i.", "ti", "analista de suporte", "assistente de ti", "tecnico de informatica", "help desk", "suporte ti", "informatica", "tecnologia"],
    1026: ["administrativo (comercial)", "administrativo comercial", "assistente comercial", "auxiliar comercial", "faturista", "apoio de vendas", "administrativo", "comercial"],
    1028: ["caixa", "operador de caixa", "recebedor", "caixa registradora"],
    1030: ["motorista", "motorista entregador", "condutor", "delivery"],
    1032: ["estagio t.i.", "estagio ti", "estagiario de suporte", "estagiario de tecnologia", "estagiario ti"],
    1034: ["estagio adm", "estagio administracao", "estagiario de administracao", "estagiario de escritorio", "estagiario adm"],
    1036: ["assistente de marketing", "analista de marketing", "social media", "produtor de conteudo", "mkt", "marketing"],
    1038: ["jovem aprendiz", "menor aprendiz", "aprendiz administrativo", "aprendiz"],
    1040: ["vendedor online", "consultor de vendas digitais", "tratador de leads", "sdr", "vendedor web", "ecommerce", "e-commerce", "digital"],
    1110: ["assistente de recrutamento", "auxiliar de recursos humanos", "assistente de departamento pessoal", "analista de rh", "auxiliar de dp", "rh", "recrutamento"],
    1112: ["auxiliar de vendas", "assistente de vendas", "suporte comercial", "atendente de vendas", "apoio vendas"],
    1142: ["atendente sac", "atendente de sac", "atendimento", "sac", "servico de atendimento"],
    1144: ["dev junior", "desenvolvedor", "dev junior 1", "programador", "desenvolvedor junior", "dev jr", "dev junior."]
}

def remove_acentos(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def match_vaga(vaga_input):
    vaga_raw = (vaga_input or "").lower().strip()
    vaga_norm = remove_acentos(vaga_raw)
    id_vaga = 1026
    melhor_score = 0
    for id_val, palavras in mapaVagas.items():
        for palavra in palavras:
            palavra_norm = remove_acentos(palavra.lower())
            if vaga_norm == palavra_norm:
                return id_val, 100
            if vaga_norm in palavra_norm or palavra_norm in vaga_norm:
                score = max(len(vaga_norm), len(palavra_norm))
                if score > melhorScore if 'melhorScore' in locals() else score > melhor_score:
                    id_vaga = id_val
                    melhor_score = score
    return id_vaga, melhor_score

# Official bitrix values
bitrix_options = [
    (1000, "Vendedor de Motos (Showroom)"),
    (1002, "Vendedor de Acessórios / Peças"),
    (1004, "Recepcionista Oficina"),
    (1006, "Entregador Técnico"),
    (1008, "Estoquista"),
    (1010, "Mecânico"),
    (1012, "Aux. Mecânico"),
    (1014, "Ajudante de Mecânico (Montador)"),
    (1016, "Lavador"),
    (1018, "Gerente"),
    (1020, "Supervisor"),
    (1026, "Administrativo (Comercial)"),
    (1022, "Administrativo (Financeiro)"),
    (1024, "T.I."),
    (1028, "Caixa"),
    (1030, "Motorista"),
    (1032, "Estágio T.I."),
    (1034, "Estágio ADM"),
    (1036, "MKT"),
    (1038, "Jovem Aprendiz"),
    (1040, "Vendedor Online"),
    (1110, "Assistente de recrutamento"),
    (1112, "Auxiliar de Vendas"),
    (1142, "Atendente SAC"),
    (1144, "Dev Junior")
]

print("=== TESTING BITRIX 24 VACANCIES MATCHING ===")
failed = 0
for expected_id, label in bitrix_options:
    matched_id, score = match_vaga(label)
    ok = (matched_id == expected_id)
    if not ok:
        failed += 1
        print(f"❌ MISMATCH: '{label}' -> got {matched_id}, expected {expected_id} (score {score})")
    else:
        print(f"✅ OK: '{label}' -> ID {matched_id}")

prompt_synonyms = [
    ("Dev Junior.", 1144),
    ("Atendente de SAC", 1142),
    ("Consultor de Vendas Digitais", 1040),
    ("Auxiliar de Limpeza", 1016),
    ("Balconista de Peças", 1002),
    ("Almoxarife", 1008),
    ("Técnico em Motocicletas", 1010),
    ("Meio-Oficial", 1012),
    ("Analista de RH", 1110),
    ("Montador de Motos", 1014),
    ("Faturista", 1026),
    ("Analista de Crédito", 1022),
    ("Help Desk", 1024),
    ("Social Media", 1036)
]

print("\n=== TESTING PROMPT SYNONYMS ===")
for syn, expected_id in prompt_synonyms:
    matched_id, score = match_vaga(syn)
    ok = (matched_id == expected_id)
    if not ok:
        failed += 1
        print(f"❌ MISMATCH: '{syn}' -> got {matched_id}, expected {expected_id}")
    else:
        print(f"✅ OK: '{syn}' -> ID {matched_id}")

if failed == 0:
    print("\n🎉 ALL 100% MATCHED!")
else:
    print(f"\n⚠️ {failed} tests failed.")
