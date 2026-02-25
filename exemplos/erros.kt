/*
 * Arquivo: erros.kt
 * Teste de recuperação de erros (Modo Pânico)
 */

fun testeErros() {
    val a = 10;
    
    // ERRO 1: Caractere inválido (^)
    val potencia = a ^ 2;

    // ERRO 2: Caractere inválido (~) e (@ solto)
    val teste = ~a;
    val email = usuario @ dominio;

    // ERRO 3: String não fechada na mesma linha (se for string simples)
    val texto = "String quebrada
    na linha de baixo";

    // ERRO 4: Char literal inválido (vazio ou com mais de 1 char)
    val c1 = '';
    val c2 = 'ab';

    println("Se você viu os erros acima e chegou aqui, o Modo Pânico funcionou!");
}
