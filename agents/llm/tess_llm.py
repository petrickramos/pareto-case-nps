"""
Wrapper do TessClient para LangChain
Permite usar TessClient com toda a infraestrutura do LangChain
"""

from typing import Any, List, Optional, Dict
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from tess_client import TessClient
import logging

logger = logging.getLogger(__name__)


class TessLLM(LLM):
    """
    Wrapper do TessClient para compatibilidade com LangChain
    
    Este wrapper permite usar o TessClient (LLM proprietário) com toda
    a infraestrutura do LangChain, incluindo Chains, Memory, Callbacks, etc.
    
    Exemplo:
        >>> llm = TessLLM(temperature=0.7, max_tokens=300)
        >>> response = llm("Escreva uma mensagem de NPS")
        >>> print(response)
    """
    
    tess_client: Optional[TessClient] = None
    temperature: float = 0.7
    max_tokens: int = 300
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tess_client = TessClient()
        logger.info("TessLLM initialized with temperature=%.2f, max_tokens=%d", 
                   self.temperature, self.max_tokens)
    
    @property
    def _llm_type(self) -> str:
        """Identificador do tipo de LLM para logging"""
        return "tess"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Chama o TessClient para gerar resposta
        
        Args:
            prompt: Prompt para o LLM
            stop: Sequências de parada (não suportado pelo TessClient)
            run_manager: Callback manager do LangChain para logging
            **kwargs: Parâmetros adicionais (max_tokens, temperature, etc.)
            
        Returns:
            Resposta gerada pelo LLM
            
        Raises:
            Exception: Se houver erro na geração
        """
        try:
            # Chamar TessClient com parâmetros configurados
            response = self.tess_client.generate(
                prompt=prompt,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature)
            )
            
            logger.debug("TessLLM generated %d characters", len(response))
            return response.strip()
            
        except Exception as e:
            logger.error("TessLLM error: %s", str(e))
            raise
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Parâmetros de identificação para logging e debugging"""
        return {
            "llm_type": self._llm_type,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }


if __name__ == "__main__":
    # Teste básico do wrapper
    print("🧪 Testando TessLLM Wrapper")
    print("=" * 60)
    
    llm = TessLLM(temperature=0.8, max_tokens=100)
    
    test_prompt = "Escreva uma saudação amigável para um cliente chamado João."
    print(f"\nPrompt: {test_prompt}")
    print("-" * 60)
    
    response = llm(test_prompt)
    print(f"Resposta: {response}")
    print("=" * 60)
    print("✅ TessLLM funcionando corretamente!")
