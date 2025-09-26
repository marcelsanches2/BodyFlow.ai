"""
Configuração do Google ADK para BodyFlow
"""

import os
from typing import Dict, Any
from app.adk.simple_adk import AgentDevelopmentKit
from anthropic import Anthropic

class ADKConfig:
    """Configuração centralizada do ADK"""
    
    # Configuração do Anthropic Claude
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    # Configuração de sessão
    SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
    
    # Configuração de confiança
    MIN_CONFIDENCE_THRESHOLD = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.7"))
    
    @classmethod
    def get_anthropic_client(cls) -> Anthropic:
        """Retorna cliente Anthropic configurado"""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY não configurada")
        return Anthropic(api_key=cls.ANTHROPIC_API_KEY)
    
    @classmethod
    def get_adk_config(cls) -> Dict[str, Any]:
        """Retorna configuração do ADK"""
        return {
            "llm_backend": "anthropic",
            "anthropic_config": {
                "api_key": cls.ANTHROPIC_API_KEY,
                "model": cls.ANTHROPIC_MODEL,
                "max_tokens": 4000,
                "temperature": 0.1
            },
            "session_config": {
                "timeout_minutes": cls.SESSION_TIMEOUT_MINUTES,
                "min_confidence": cls.MIN_CONFIDENCE_THRESHOLD
            },
            "tools": [
                "memory_tool",
                "observability_tool", 
                "multimodal_tool"
            ]
        }
