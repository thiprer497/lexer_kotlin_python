from dataclasses import dataclass
from typing import Any

@dataclass
class Token:
    tipo: str
    lexema: str
    valor: Any # esse valor foi adicionado pra ficar igual o exemplo do professor
    linha: int
    coluna: int

    def __repr__(self):
        # Exibe o valor apenas se não for None, para ficar limpo no terminal
        val_str = f", valor={self.valor}" if self.valor is not None else ", valor=null"
        return f"Token({self.tipo}, '{self.lexema}'{val_str}, linha={self.linha}, coluna={self.coluna})"