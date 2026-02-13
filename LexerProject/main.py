import os
from .lexer import Lexer
from .token_stream import TokenStream

def carregar_codigo(arquivo):
    # Obtém o caminho absoluto do diretório onde este script (main.py) está
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_arquivo = os.path.join(diretorio_atual, arquivo)
    
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo '{arquivo}' não foi encontrado em {diretorio_atual}")
        return None

def demo(source_text: str):
    print(":: INICIANDO ANALISE LEXICA ::")
    lexer = Lexer(source_text)
    ts = TokenStream(lexer)
    
    while True:
        try:
            t = ts.next()
            print(t)
            if t.tipo == "EOF":
                break
        except Exception as e:
            # Captura erros léxicos e continua (Modo Pânico simplificado)
            print(f"ERRO FATAL NO LEXER: {e}")
            break

if __name__ == "__main__":
    # Nome do arquivo Kotlin que está na mesma pasta
    NOME_ARQUIVO = "teste.kt"
    
    codigo_fonte = carregar_codigo(NOME_ARQUIVO)
    
    if codigo_fonte:
        demo(codigo_fonte)