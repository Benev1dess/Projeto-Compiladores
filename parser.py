
import sys
import ply.yacc as yacc
from lexer import tokens, build_lexer, find_column

start = 'document'
codigo_fonte = ''


# Um documento possui importacoes, pacote e declaracoes de classes
def p_document(p):
    'document : imports KW_PACKAGE package_name classes'
    p[0] = {
        'pacote': p[3],
        'imports': p[1],
        'classes': p[4]
    }


# Lista opcional de importacoes
def p_imports(p):
    '''imports : imports import_decl
               | empty'''
    p[0] = p[1] + [p[2]] if len(p) == 3 else []


def p_import_decl(p):
    'import_decl : KW_IMPORT package_name'
    p[0] = p[2]


def p_package_name(p):
    '''package_name : CLASS_NAME
                    | RELATION_NAME'''
    p[0] = p[1]


# Permite varias declaracoes de classe no mesmo arquivo
def p_classes(p):
    '''classes : classes class_decl
               | empty'''
    p[0] = p[1] + [p[2]] if len(p) == 3 else []


# Cada classe possui estereotipo, nome e superclasse opcional
def p_class_decl(p):
    'class_decl : class_stereotype CLASS_NAME superclass_opt class_body_opt'

    p[0] = {
        'nome': p[2],
        'estereotipo': p[1],
        'superclasse': p[3],
        'linha': p.lineno(1)
    }


# Estereotipos aceitos nas declaracoes de classes
def p_class_stereotype(p):
    '''class_stereotype : ST_EVENT
                        | ST_SITUATION
                        | ST_PROCESS
                        | ST_CATEGORY
                        | ST_MIXIN
                        | ST_PHASE_MIXIN
                        | ST_ROLE_MIXIN
                        | ST_HISTORICAL_ROLE_MIXIN
                        | ST_KIND
                        | ST_RELATOR
                        | ST_COLLECTIVE
                        | ST_QUANTITY
                        | ST_QUALITY
                        | ST_MODE
                        | ST_INTRINSIC_MODE
                        | ST_EXTRINSIC_MODE
                        | ST_SUBKIND
                        | ST_PHASE
                        | ST_ROLE
                        | ST_HISTORICAL_ROLE'''
    p[0] = p[1]


# Reconhece a especializacao de uma classe
def p_superclass_opt(p):
    '''superclass_opt : KW_SPECIALIZES CLASS_NAME
                      | empty'''
    p[0] = p[2] if len(p) == 3 else None


# Permite classes sem corpo ou com chaves vazias
def p_class_body_opt(p):
    '''class_body_opt : LBRACE RBRACE
                      | empty'''
    p[0] = None


def p_empty(p):
    'empty :'
    p[0] = None


class ErroSintatico(Exception):
    pass


# Identifica o primeiro erro sintatico encontrado
def p_error(p):
    if p is None:
        print('Erro sintatico: fim inesperado do arquivo.')
    else:
        coluna = find_column(codigo_fonte, p)
        print(
            f"Erro sintatico na linha {p.lineno}, "
            f"coluna {coluna}: token '{p.value}' inesperado."
        )

    raise ErroSintatico()


# Constroi o analisador sintatico
parser = yacc.yacc(
    debug=False,
    write_tables=False,
    errorlog=yacc.NullLogger()
)


# Executa a analise utilizando os tokens do lexer
def analisar(texto):
    global codigo_fonte
    codigo_fonte = texto

    scanner = build_lexer()
    return parser.parse(texto, lexer=scanner, tracking=True)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Uso: python parser.py <arquivo.tonto>')
        sys.exit(1)

    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as arquivo:
            texto = arquivo.read()
    except OSError as erro:
        print(f'Erro ao abrir arquivo: {erro}')
        sys.exit(1)

    try:
        resultado = analisar(texto)
    except ErroSintatico:
        sys.exit(1)

    print(f"Pacote reconhecido: {resultado['pacote']}")
    print(
        f"Importacoes reconhecidas: "
        f"{', '.join(resultado['imports']) or 'nenhuma'}"
    )
    print(f"Classes reconhecidas: {len(resultado['classes'])}")

    for classe in resultado['classes']:
        superclasse = (
            f" specializes {classe['superclasse']}"
            if classe['superclasse'] else ''
        )

        print(
            f"  {classe['estereotipo']} "
            f"{classe['nome']}{superclasse} "
            f"(linha {classe['linha']})"
        )

    print('Analise sintatica concluida com sucesso.')
