"""
Classe para gerenciar todas as mensagens apresentadas ao usuário
Centraliza todas as strings para facilitar manutenção e tradução
"""

class UserMessages:
    """
    Classe que contém todas as mensagens apresentadas ao usuário
    """
    
    # Mensagens de boas-vindas e primeiro contato
    FIRST_CONTACT_GREETING = "Ola! Bem-vindo ao BodyFlow!"
    
    # Mensagens de cadastro e ativação
    WELCOME_NOT_REGISTERED = "Ola! Bem-vindo ao BodyFlow! Para comecar, cadastre-se no nosso site."
    ACCOUNT_INACTIVE = "Sua conta esta inativa. Para ativar, envie: ATIVAR"
    ACCOUNT_ACTIVATED_SUCCESS = "Conta ativada com sucesso! Agora voce pode usar nossos servicos de treino e dieta."
    ACTIVATION_ERROR = "Erro ao ativar conta. Tente novamente ou entre em contato com o suporte."
    
    # Mensagens de erro genéricas
    PROCESSING_ERROR = "Desculpe, ocorreu um erro ao processar sua mensagem."
    USER_NOT_FOUND_ERROR = "Usuario nao encontrado no sistema."
    
    # Mensagens dos agentes - Treino
    class Treino:
        WELCOME_MESSAGE = "Ola! Sou seu assistente de treino. Como posso ajudar voce hoje?"
        
        PERNAS_RESPONSE = "Aqui esta um treino de pernas para voce!"
        PEITO_RESPONSE = "Aqui esta um treino de peito para voce!"
        COSTAS_RESPONSE = "Aqui esta um treino de costas para voce!"
        COMPLETO_RESPONSE = "Aqui esta um treino completo para voce!"
        
        # Dicas simples
        DICAS = [
            "\n\nDica: Mantenha a postura correta!",
            "\n\nDica: Hidrate-se bem!",
            "\n\nDica: Descanse entre os treinos!",
            "\n\nDica: Alongue-se antes e depois!"
        ]
    
    # Mensagens dos agentes - Dieta
    class Dieta:
        WELCOME_MESSAGE = "Ola! Sou seu assistente de nutricao. Como posso ajudar voce hoje?"
        
        PERDER_PESO_RESPONSE = "Aqui esta uma dieta para perder peso!"
        GANHAR_MASSA_RESPONSE = "Aqui esta uma dieta para ganhar massa!"
        MANTER_PESO_RESPONSE = "Aqui esta uma dieta para manter o peso!"
        DIETA_SAUDAVEL_RESPONSE = "Aqui esta uma dieta saudavel para voce!"
        
        # Dicas simples
        DICAS = [
            "\n\nDica: Beba bastante agua!",
            "\n\nDica: Faca refeicoes regulares!",
            "\n\nDica: Evite alimentos processados!",
            "\n\nDica: Consuma frutas e verduras!"
        ]
    
    # Mensagens de roteamento
    class Router:
        DEFAULT_RESPONSE = "Posso ajudar com treino ou dieta. Qual voce prefere?"
        UNKNOWN_COMMAND = "Nao entendi sua solicitacao. Digite treino para exercicios ou dieta para alimentacao."
