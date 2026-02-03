"""
Teste do wrapper TessLLM
Valida integração entre TessClient e LangChain
"""

from agents.llm.tess_llm import TessLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


def test_tess_llm_basic():
    """Teste básico do wrapper TessLLM"""
    print("\n🧪 Teste 1: TessLLM Básico")
    print("=" * 60)
    
    llm = TessLLM(temperature=0.7, max_tokens=100)
    prompt = "Escreva uma saudação amigável para um cliente."
    
    response = llm(prompt)
    
    assert isinstance(response, str), "Resposta deve ser string"
    assert len(response) > 0, "Resposta não pode ser vazia"
    
    print(f"✅ Prompt: {prompt}")
    print(f"✅ Resposta: {response}")
    print("=" * 60)


def test_langchain_prompt_template():
    """Teste com PromptTemplate do LangChain"""
    print("\n🧪 Teste 2: LangChain PromptTemplate")
    print("=" * 60)
    
    llm = TessLLM(temperature=0.8, max_tokens=150)
    
    template = PromptTemplate(
        input_variables=["nome", "tom"],
        template="Escreva uma mensagem de NPS com tom {tom} para {nome}."
    )
    
    chain = LLMChain(llm=llm, prompt=template)
    
    result = chain.run(nome="Maria", tom="empático")
    
    assert isinstance(result, str), "Resultado deve ser string"
    assert len(result) > 0, "Resultado não pode ser vazio"
    
    print(f"✅ Template: {template.template}")
    print(f"✅ Variáveis: nome=Maria, tom=empático")
    print(f"✅ Resultado: {result}")
    print("=" * 60)


def test_langchain_chain_multiple_vars():
    """Teste com múltiplas variáveis"""
    print("\n🧪 Teste 3: Chain com Múltiplas Variáveis")
    print("=" * 60)
    
    llm = TessLLM(temperature=0.7, max_tokens=200)
    
    template = PromptTemplate(
        input_variables=["cliente", "score", "categoria"],
        template="""Analise esta avaliação NPS:
Cliente: {cliente}
Score: {score}/10
Categoria: {categoria}

Crie um resumo executivo em 1 linha."""
    )
    
    chain = LLMChain(llm=llm, prompt=template)
    
    result = chain.run(
        cliente="João Silva",
        score=9,
        categoria="PROMOTOR"
    )
    
    assert isinstance(result, str), "Resultado deve ser string"
    assert len(result) > 0, "Resultado não pode ser vazio"
    
    print(f"✅ Resultado: {result}")
    print("=" * 60)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Testando TessLLM Wrapper com LangChain")
    print("=" * 60)
    
    try:
        test_tess_llm_basic()
        test_langchain_prompt_template()
        test_langchain_chain_multiple_vars()
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
