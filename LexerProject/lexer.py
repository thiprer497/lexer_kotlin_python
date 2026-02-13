from .tokens import Token
from .constantes import OPERADORES, SIMBOLOS, KEYWORDS
from .utils import eh_hex, eh_bin, eh_sufixo_inteiro, eh_sufixo_float, eh_separador

class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.linha = 1
        self.coluna = 1
        self.erros = [] 

    # ==================================================
    # AUXILIARES BÁSICOS
    # ==================================================
    def ch_atual(self):
        if self.pos < len(self.source):
            return self.source[self.pos]
        return '\0'

    def ch_proximo(self):
        if self.pos + 1 < len(self.source):
            return self.source[self.pos + 1]
        return '\0'
    
    def ch_proximo_n(self, n=1):
        if self.pos + n < len(self.source):
            return self.source[self.pos + n]
        return '\0'

    def avancar(self):
        ch = self.ch_atual()
        self.pos += 1
        if ch == '\n':
            self.linha += 1
            self.coluna = 1
        else:
            self.coluna += 1
        return ch

    # ==================================================
    # MODO PÂNICO
    # ==================================================
    def erro_lexico(self, mensagem):
        erro = f"Erro léxico na linha {self.linha}, coluna {self.coluna}: {mensagem}"
        print(erro)
        self.erros.append(erro)
        self.avancar()
        return None

    # ==================================================
    # IGNORAR ESPAÇOS E COMENTÁRIOS
    # ==================================================
    def pular_espaco(self):
        while self.ch_atual() in [' ', '\t', '\r', '\n']:
            self.avancar()

    def pular_comentario_linha(self):
        while self.ch_atual() != '\n' and self.ch_atual() != '\0':
            self.avancar()

    def pular_comentario_blocos(self):
        profundidade = 1
        self.avancar(); self.avancar() # /*
        while profundidade > 0:
            if self.ch_atual() == '\0':
                return self.erro_lexico("Comentário de bloco não fechado")
            
            if self.ch_atual() == '/' and self.ch_proximo() == '*':
                profundidade += 1
                self.avancar(); self.avancar()
            elif self.ch_atual() == '*' and self.ch_proximo() == '/':
                profundidade -= 1
                self.avancar(); self.avancar()
            else:
                self.avancar()

    # ==================================================
    # LITERAIS NUMÉRICOS
    # ==================================================
    def reconhece_literais_numericos(self):
        inicio = self.pos
        linha, coluna = self.linha, self.coluna
        tipo = "INT_LITERAL"
        base = 10 
        
        # Hexadecimal (0x) ou Binário (0b)
        if self.ch_atual() == '0':
            if self.ch_proximo().lower() == 'x':
                base = 16
                self.avancar(); self.avancar()
                while self.eh_hex(self.ch_atual()) or self.eh_separador(self.ch_atual()):
                    self.avancar()
            elif self.ch_proximo().lower() == 'b':
                base = 2
                self.avancar(); self.avancar()
                while self.eh_bin(self.ch_atual()) or self.eh_separador(self.ch_atual()):
                    self.avancar()

        # Decimal ou Float
        if base == 10:
            while self.ch_atual().isdigit() or self.eh_separador(self.ch_atual()):
                self.avancar()
            
            if self.ch_atual() == '.' and self.ch_proximo() != '.': 
                tipo = "FLOAT_LITERAL"
                self.avancar()
                while self.ch_atual().isdigit() or self.eh_separador(self.ch_atual()):
                    self.avancar()
            
            if self.ch_atual().lower() == 'e':
                tipo = "FLOAT_LITERAL"
                self.avancar()
                if self.ch_atual() in ['+', '-']: 
                    self.avancar()
                while self.ch_atual().isdigit() or self.eh_separador(self.ch_atual()):
                    self.avancar()

        # Consome sufixos (L, u, f) do código fonte
        while self.ch_atual().lower() in ['u', 'l', 'f']:
            if self.ch_atual().lower() == 'f':
                tipo = "FLOAT_LITERAL"
            self.avancar()

        lexema = self.source[inicio:self.pos]
        
        # --- CÁLCULO DO VALOR ---
        valor_limpo = lexema.replace('_', '').lower()
        
        # CORREÇÃO: Se for HEX, 'f' é dígito, não sufixo float.
        # Apenas removemos sufixos se eles não fizerem parte da base numérica
        sufixos_validos = ['u', 'l']
        if base == 10: # Apenas decimal aceita 'f' como sufixo float
            sufixos_validos.append('f')

        # Remove sufixos do final da string para conversão
        while valor_limpo and valor_limpo[-1] in sufixos_validos:
            # Cuidado extra: no caso hex (0xFF), o último F é digito, não sufixo.
            # Kotlin usa 'L' ou 'u' para Hex. Não existe 'f' para Hex literal (float hex usa 'p')
            # Então se base=16, só removemos se for u ou l.
            if base == 16 and valor_limpo[-1] == 'f':
                break 
            valor_limpo = valor_limpo[:-1]
        
        valor = None
        try:
            if tipo == "INT_LITERAL":
                valor = int(valor_limpo, base)
            else:
                valor = float(valor_limpo)
        except:
            valor = None 

        return Token(tipo, lexema, valor, linha, coluna)

    # ==================================================
    # IDENTIFICADORES
    # ==================================================
    def reconhece_identificadores(self):
        inicio = self.pos
        linha, coluna = self.linha, self.coluna
        while self.ch_atual().isalnum() or self.ch_atual() == '_':  
            self.avancar()
        lexema = self.source[inicio:self.pos]
        
        tipo = KEYWORDS.get(lexema)
        valor = None
        if tipo == "KW_TRUE": valor = True
        elif tipo == "KW_FALSE": valor = False
        elif tipo == "KW_NULL": valor = None
        
        if tipo is not None:
            return Token(tipo, lexema, valor, linha, coluna)
        return Token("IDENTIFIER", lexema, None, linha, coluna)

    def reconhece_identificador_crase(self):
        linha, coluna = self.linha, self.coluna
        self.avancar()
        inicio = self.pos
        while self.ch_atual() != '`' and self.ch_atual() != '\0':
            self.avancar()
        
        if self.ch_atual() != '`':
            return self.erro_lexico("Identificador com crase não fechado")
            
        lexema_interno = self.source[inicio:self.pos]
        self.avancar()
        return Token("Quoted_identifier", lexema_interno, None, linha, coluna)

    # ==================================================
    # STRINGS E CHARS (COM SUPORTE A UNICODE)
    # ==================================================
    def processar_escape(self):
        self.avancar() # consome \
        char = self.ch_atual()
        
        # CORREÇÃO: Suporte a Unicode \uXXXX
        if char == 'u':
            self.avancar() # consome u
            hex_val = ""
            # Tenta ler 4 digitos hexadecimais
            for _ in range(4):
                if self.eh_hex(self.ch_atual()):
                    hex_val += self.avancar()
                else:
                    # Se falhar no meio (ex: \u00X), retorna o que leu pra não travar,
                    # mas vai dar erro de char inválido depois.
                    return '?' 
            try:
                return chr(int(hex_val, 16))
            except:
                return '?'

        escapes = {'n': '\n', 't': '\t', 'r': '\r', 'b': '\b', '"': '"', "'": "'", '\\': '\\', '$': '$'}
        self.avancar()
        return escapes.get(char, char)

    def reconhece_char_literal(self):
        linha, coluna = self.linha, self.coluna
        self.avancar() # '
        
        if self.ch_atual() == '\\':
            valor_char = self.processar_escape()
        else:
            valor_char = self.ch_atual()
            self.avancar()
            
        if self.ch_atual() != "'":
             return self.erro_lexico("Literal de caractere inválido ou não fechado")
        
        self.avancar() # fecha '
        return Token("CHAR_LITERAL", f"'{valor_char}'", valor_char, linha, coluna)

    def reconhece_string(self):
        linha, coluna = self.linha, self.coluna
        is_triple = False
        
        if self.ch_atual() == '"' and self.ch_proximo() == '"' and self.ch_proximo_n(2) == '"':
            is_triple = True
            self.avancar(); self.avancar(); self.avancar()
        else:
            self.avancar()

        tokens = []
        tokens.append(Token("STRING_START", '"""' if is_triple else '"', None, linha, coluna))

        buffer = ""
        while True:
            ch = self.ch_atual()
            
            if ch == '\0':
                return self.erro_lexico("String não fechada (EOF)")

            if is_triple:
                if ch == '"' and self.ch_proximo() == '"' and self.ch_proximo_n(2) == '"':
                    if buffer: tokens.append(Token("STRING_TEXT", buffer, buffer, linha, coluna))
                    tokens.append(Token("STRING_END", '"""', None, self.linha, self.coluna))
                    self.avancar(); self.avancar(); self.avancar()
                    break
            else:
                if ch == '"':
                    if buffer: tokens.append(Token("STRING_TEXT", buffer, buffer, linha, coluna))
                    tokens.append(Token("STRING_END", '"', None, self.linha, self.coluna))
                    self.avancar()
                    break
                if ch == '\n':
                     return self.erro_lexico("Quebra de linha em string simples")

            if ch == '$':
                if buffer:
                    tokens.append(Token("STRING_TEXT", buffer, buffer, linha, coluna))
                    buffer = ""
                
                self.avancar()
                if self.ch_atual() == '{':
                    tokens.append(Token("STRING_INTERP_START", "${", None, self.linha, self.coluna))
                    self.avancar()
                    expr_str = ""
                    while self.ch_atual() != '}' and self.ch_atual() != '\0':
                         expr_str += self.avancar()
                    tokens.append(Token("STRING_INTERP_EXPR", expr_str, None, self.linha, self.coluna))
                    tokens.append(Token("STRING_INTERP_END", "}", None, self.linha, self.coluna))
                    self.avancar()
                else:
                    inicio_id = self.pos
                    while self.ch_atual().isalnum() or self.ch_atual() == '_':
                        self.avancar()
                    nome_id = self.source[inicio_id:self.pos]
                    tokens.append(Token("STRING_INTERP_ID", nome_id, None, self.linha, self.coluna))
                continue

            if ch == '\\' and not is_triple:
                buffer += self.processar_escape()
            else:
                buffer += ch
                self.avancar()
        
        return tokens

    # ==================================================
    # OPERADORES
    # ==================================================
    def reconhece_operadores(self):
        linha, coluna = self.linha, self.coluna
        for tamanho in (3, 2, 1):
            if self.pos + tamanho <= len(self.source):
                lexema = self.source[self.pos : self.pos + tamanho]
                if lexema in OPERADORES:
                    for _ in range(tamanho): self.avancar()
                    return Token(OPERADORES[lexema], lexema, None, linha, coluna)
        return None

    # ==================================================
    # LOOP PRINCIPAL
    # ==================================================
    def proximo_token(self):
        if self.pos == 0 and self.ch_atual() == '#' and self.ch_proximo() == '!':
            self.pular_linha()
            return self.proximo_token()
        
        self.pular_espaco()

        if self.ch_atual() == '\0':
            return Token("EOF", "", None, self.linha, self.coluna)

        if self.ch_atual() == '/' and self.ch_proximo() == '/':
            self.pular_comentario_linha()
            return self.proximo_token()
        if self.ch_atual() == '/' and self.ch_proximo() == '*':
            erro = self.pular_comentario_blocos()
            if erro: return None 
            return self.proximo_token()

        if self.ch_atual().isalpha() or self.ch_atual() == '_':
            return self.reconhece_identificadores()
        
        if self.ch_atual().isdigit():
            return self.reconhece_literais_numericos()
        
        if self.ch_atual() == '"':
            return self.reconhece_string()

        if self.ch_atual() == "'":
            return self.reconhece_char_literal()
        
        if self.ch_atual() == '`':
            return self.reconhece_identificador_crase()

        token_op = self.reconhece_operadores()
        if token_op: return token_op
        
        if self.ch_atual() in SIMBOLOS:
            ch = self.avancar()
            return Token(SIMBOLOS[ch], ch, None, self.linha, self.coluna - 1)
        
        return self.erro_lexico(f"Caractere inesperado '{self.ch_atual()}'")

    def tokenize(self):
        tokens = []
        while True:
            try:
                result = self.proximo_token()
                if result is None: 
                    continue 
                
                if isinstance(result, list):
                    tokens.extend(result)
                    last_token = result[-1]
                else:
                    tokens.append(result)
                    last_token = result

                if last_token.tipo == "EOF":
                    break
            except Exception as e:
                print(f"Erro fatal não tratado: {e}")
                break
        return tokens

    def eh_hex(self, ch): return eh_hex(ch)
    def eh_bin(self, ch): return eh_bin(ch)
    def eh_separador(self, ch): return eh_separador(ch)