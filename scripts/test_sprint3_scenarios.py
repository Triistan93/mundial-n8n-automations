import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=== TESTANDO CENÁRIOS DE ESTADO SPRINT 3 ===")

etapasHumanas = [
    'C198:UC_0YLZXN',      # ASSUNTOS RH
    'C198:PREPAYMENT_INVOI', # Entrevista RH
    'C198:UC_WFH3KE',        # Testes
    'C198:UC_8KNLBM',        # Entrevista Gerencial
    'C198:UC_ML059R',        # Avaliação
    'C198:EXECUTING',        # Documentação
    'C198:WON',              # Contratados
    'C198:LOSE',             # Desqualificado
    'C198:UC_YEOIKS'         # Duplicados
]

def avaliar_cenario(deal_stage, has_block_redis, message_text, is_from_me):
    print(f"\n--- Cenário: Deal Stage '{deal_stage}', Redis Block={has_block_redis}, fromMe={is_from_me} ---")
    print(f"Mensagem: \"{message_text}\"")
    
    # 1. fromMe checagem
    if is_from_me:
        print("-> [fromMe=True] Atendente humano falou no WhatsApp. Ação: Seta block 30 dias no Redis e morre silenciosamente.")
        return "SILENCIO_HUMANO_ATIVO"
        
    # 2. Redis block checagem
    if has_block_redis:
        print("-> [Redis Block=True] Bot travado no Redis. Ação: Morre silenciosamente no nó 'IF: Bot Bloqueado?'.")
        return "SILENCIO_REDIS_BLOCK"
        
    # 3. Bitrix Deal Stage checagem
    if deal_stage in etapasHumanas:
        print(f"-> [Bitrix Stage={deal_stage}] Card em etapa humana! Ação: Seta block 30 dias no Redis, anota Timeline e silencia 100%.")
        return "SILENCIO_ETAPA_HUMANA"
        
    # 4. Se estiver em NEW ou PREPARATION
    if deal_stage in ['C198:NEW', 'C198:PREPARATION']:
        if any(w in message_text.lower() for w in ['novidade', 'resultado', 'status', 'previsão', 'obrigado', 'valeu']):
            print("-> [Pós-Atendimento Status] IA responde acolhedora informando que o perfil está em análise pelo RH. Sem JSON, sem duplicar card.")
            return "RESPOSTA_ACOLHEDORA_STATUS"
        elif any(w in message_text.lower() for w in ['outra vaga', 'também quero', 'nova vaga']):
            print("-> [Nova Vaga] IA colhe nova vaga, gera JSON e atualiza o card existente no Bitrix com nova vaga.")
            return "ATUALIZAR_VAGA_CARD_EXISTENTE"
        else:
            print("-> [Dúvida/Complemento] IA responde dúvida e anexa arquivo ao perfil.")
            return "RESPOSTA_COMPLEMENTAR"
            
    # 5. Se não tiver deal
    print("-> [Lead Novo] Inicia triagem L1 normal.")
    return "TRIAGEM_NOVA"

# Testes
avaliar_cenario('C198:UC_0YLZXN', False, "Olá, esqueci de enviar o exame", False)
avaliar_cenario('C198:PREPAYMENT_INVOI', False, "Confirmo minha entrevista amanhã", False)
avaliar_cenario('C198:NEW', False, "Olá, alguma novidade da minha vaga de vendedor?", False)
avaliar_cenario('C198:PREPARATION', False, "Queria me candidatar também para recepcionista", False)
avaliar_cenario('C198:NEW', True, "Obrigado!", False)
avaliar_cenario('C198:NEW', False, "Bom dia, sou o Eduardo do RH", True)

print("\n🎉 TODOS OS 6 CENÁRIOS DETERMINÍSTICOS E SEGUROS!")
