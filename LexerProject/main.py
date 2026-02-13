import sys
import os
from .lexer import Lexer
from .token_stream import TokenStream

def analisar_codigo(nome_arquivo, source_text):
    print(f"\n{'='*60}")
    print(f"ARQUIVO: {nome_arquivo}")
    print(f"{'='*60}")
    
    lexer = Lexer(source_text)
    ts = TokenStream(lexer)
    
    while True:
        try:
            t = ts.next()
            print(t)
            if t.tipo == "EOF":
                break
        except Exception as e:
            # Captura erros não tratados pelo modo pânico do lexer
            print(f"ERRO FATAL NO SISTEMA: {e}")
            break
    print(f"{'-'*60}")

def carregar_e_processar(caminho):
    # Resolve o caminho para absoluto (funciona Linux, Mac, Windows)
    caminho_absoluto = os.path.abspath(caminho)
    
    if not os.path.exists(caminho_absoluto):
        print(f"\nERRO: O arquivo '{caminho}' não foi encontrado.")
        print(f"   Procurado em: {caminho_absoluto}")
        return

    try:
        with open(caminho_absoluto, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        analisar_codigo(caminho, codigo)
    except Exception as e:
        print(f"Erro ao ler o arquivo {caminho}: {e}")

def main():
    # sys.argv[0] é o nome do script. Os argumentos começam do [1:]
    arquivos = sys.argv[1:]

    # Cenário 1: Nenhum argumento passado
    if not arquivos:
        # Tenta achar o 'teste.kt' padrão na mesma pasta deste script (LexerProject)
        diretorio_script = os.path.dirname(os.path.abspath(__file__))
        arquivo_padrao = os.path.join(diretorio_script, "teste.kt")
        
        if os.path.exists(arquivo_padrao):
            print("Nenhum arquivo informado via linha de comando.")
            print(f"Executando arquivo de teste padrão: {arquivo_padrao}")
            carregar_e_processar(arquivo_padrao)
        else:
            print("Uso: python -m LexerProject.main <arquivo1.kt> [arquivo2.kt ...]")
            print("Exemplo: python -m LexerProject.main /home/user/meu_codigo.kt")
        return

    # Cenário 2: Argumentos passados (1 ou mais arquivos)
    for arquivo in arquivos:
        carregar_e_processar(arquivo)

if __name__ == "__main__":
    main()