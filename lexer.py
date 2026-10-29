
import sys
import ply.lex as lex

# Estereotipos utilizados nas declaracoes de classes
CLASS_STEREOTYPES = {
    'event': 'ST_EVENT',
    'situation': 'ST_SITUATION',
    'process': 'ST_PROCESS',
    'category': 'ST_CATEGORY',
    'mixin': 'ST_MIXIN',
    'phaseMixin': 'ST_PHASE_MIXIN',
    'roleMixin': 'ST_ROLE_MIXIN',
    'historicalRoleMixin': 'ST_HISTORICAL_ROLE_MIXIN',
    'kind': 'ST_KIND',
    'collective': 'ST_COLLECTIVE',
    'quantity': 'ST_QUANTITY',
    'quality': 'ST_QUALITY',
    'mode': 'ST_MODE',
    'intrisicMode': 'ST_INTRINSIC_MODE',
    'intrinsicMode': 'ST_INTRINSIC_MODE',
    'extrinsicMode': 'ST_EXTRINSIC_MODE',
    'subkind': 'ST_SUBKIND',
    'phase': 'ST_PHASE',
    'role': 'ST_ROLE',
    'relator': 'ST_RELATOR',
    'historicalRole': 'ST_HISTORICAL_ROLE'
}

# Estereotipos utilizados nas relacoes
RELATION_STEREOTYPES = {
    'material': 'ST_MATERIAL',
    'derivation': 'ST_DERIVATION',
    'comparative': 'ST_COMPARATIVE',
    'mediation': 'ST_MEDIATION',
    'characterization': 'ST_CHARACTERIZATION',
    'externalDependence': 'ST_EXTERNAL_DEPENDENCE',
    'componentOf': 'ST_COMPONENT_OF',
    'memberOf': 'ST_MEMBER_OF',
    'subCollectionOf': 'ST_SUB_COLLECTION_OF',
    'subQualityOf': 'ST_SUB_QUALITY_OF',
    'instantiation': 'ST_INSTANTIATION',
    'termination': 'ST_TERMINATION',
    'participational': 'ST_PARTICIPATIONAL',
    'participation': 'ST_PARTICIPATION',
    'historicalDependence': 'ST_HISTORICAL_DEPENDENCE',
    'creation': 'ST_CREATION',
    'manifestation': 'ST_MANIFESTATION',
    'bringsAbout': 'ST_BRINGS_ABOUT',
    'triggers': 'ST_TRIGGERS',
    'composition': 'ST_COMPOSITION',
    'aggregation': 'ST_AGGREGATION',
    'inherence': 'ST_INHERENCE',
    'value': 'ST_VALUE',
    'formal': 'ST_FORMAL',
    'constitution': 'ST_CONSTITUTION'
}

KEYWORDS = {
    'genset': 'KW_GENSET',
    'disjoint': 'KW_DISJOINT',
    'complete': 'KW_COMPLETE',
    'general': 'KW_GENERAL',
    'specifics': 'KW_SPECIFICS',
    'where': 'KW_WHERE',
    'package': 'KW_PACKAGE',
    'import': 'KW_IMPORT',
    'functional-complexes': 'KW_FUNCTIONAL_COMPLEXES',
    'specializes': 'KW_SPECIALIZES',
    'enum': 'KW_ENUM',
    'datatype': 'KW_DATATYPE',
    'relation': 'KW_RELATION',
    'overlapping': 'KW_OVERLAPPING',
    'incomplete': 'KW_INCOMPLETE'
}

NATIVE_TYPES = {
    'number': 'TYPE_NUMBER',
    'string': 'TYPE_STRING',
    'boolean': 'TYPE_BOOLEAN',
    'date': 'TYPE_DATE',
    'time': 'TYPE_TIME',
    'datetime': 'TYPE_DATETIME'
}

META_ATTRIBUTES = {
    'ordered': 'META_ORDERED',
    'const': 'META_CONST',
    'derived': 'META_DERIVED',
    'subsets': 'META_SUBSETS',
    'redefines': 'META_REDEFINES'
}

reserved = {}
reserved.update(CLASS_STEREOTYPES)
reserved.update(RELATION_STEREOTYPES)
reserved.update(KEYWORDS)
reserved.update(NATIVE_TYPES)
reserved.update(META_ATTRIBUTES)

tokens = list(dict.fromkeys([
    'CLASS_NAME',
    'RELATION_NAME',
    'INSTANCE_NAME',
    'CUSTOM_DATATYPE',
    'ERROR_IDENTIFIER',
    'NUMBER',
    'STRING_LITERAL',
    'LBRACE',
    'RBRACE',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'RANGE',
    'COMP_LEFT',
    'COMP_RIGHT',
    'DASH',
    'STAR',
    'AT',
    'DOT',
    'COLON',
    'COMMA'
] + list(reserved.values())))

# Simbolos utilizados nas declaracoes e cardinalidades
t_RANGE = r'\.\.'
t_COMP_LEFT = r'<>--'
t_COMP_RIGHT = r'--<>'
t_DASH = r'--'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_STAR = r'\*'
t_AT = r'@'
t_DOT = r'\.'
t_COLON = r':'
t_COMMA = r','

t_ignore = ' \t\r'


def t_COMMENT(t):
    r'//[^\n]*|/\*[\s\S]*?\*/'
    t.lexer.lineno += t.value.count('\n')


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_NUMBER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t


def t_STRING_LITERAL(t):
    r'"([^"\\\n]|\\.)*"'
    return t


# Classifica identificadores de acordo com as convencoes da linguagem
def t_IDENTIFIER(t):
    r'functional-complexes|[a-zA-Z_][a-zA-Z0-9_]*'

    val = t.value

    if val in reserved:
        t.type = reserved[val]
        return t

    has_digits = any(c.isdigit() for c in val)
    has_underscore = '_' in val

    if (val.endswith('DataType') and val[0].isalpha()
            and not has_digits and not has_underscore):
        t.type = 'CUSTOM_DATATYPE'

    elif (val[0].isalpha() and val[-1].isdigit()
          and not any(c.isdigit() for c in val.rstrip('0123456789'))):
        t.type = 'INSTANCE_NAME'

    elif val[0].isupper() and not has_digits:
        t.type = 'CLASS_NAME'

    elif val[0].islower() and not has_digits:
        t.type = 'RELATION_NAME'

    else:
        t.type = 'ERROR_IDENTIFIER'

    return t


def find_column(input_text, token):
    line_start = input_text.rfind('\n', 0, token.lexpos) + 1
    return token.lexpos - line_start + 1


def diagnose_identifier(val):
    if val.startswith('_'):
        return 'Identificadores nao devem iniciar com sublinhado.'

    if val.endswith('DataType'):
        if '_' in val:
            return 'Tipos DataType nao podem conter sublinhado.'
        if any(c.isdigit() for c in val):
            return 'Tipos DataType nao podem conter numeros.'

    if any(c.isdigit() for c in val):
        return 'Numeros sao permitidos apenas no final de nomes de instancias.'

    return 'Identificador incompativel com as regras de nomenclatura.'


def t_error(t):
    col = find_column(t.lexer.lexdata, t)

    t.lexer.errors.append({
        'fase': 'LEXICA',
        'linha': t.lineno,
        'coluna': col,
        'mensagem': f"Caractere nao reconhecido: {t.value[0]!r}.",
        'sugestao': 'Remova o caractere ou verifique a pontuacao.'
    })

    t.lexer.skip(1)


# Cria uma instancia independente do analisador lexico
def build_lexer():
    scanner = lex.lex(module=sys.modules[__name__])
    scanner.lineno = 1
    scanner.errors = []
    return scanner


lexer = build_lexer()


# Retorna os tokens com suas posicoes e os erros encontrados
def tokenize(codigo_fonte):
    scanner = build_lexer()
    scanner.input(codigo_fonte)

    resultado = []

    for tok in scanner:
        coluna = find_column(codigo_fonte, tok)

        resultado.append({
            'tipo': tok.type,
            'valor': tok.value,
            'linha': tok.lineno,
            'coluna': coluna
        })

        if tok.type == 'ERROR_IDENTIFIER':
            scanner.errors.append({
                'fase': 'LEXICA',
                'linha': tok.lineno,
                'coluna': coluna,
                'mensagem': f"Lexema {tok.value!r} invalido.",
                'sugestao': diagnose_identifier(tok.value)
            })

    erros = sorted(
        scanner.errors,
        key=lambda e: (e['linha'], e['coluna'])
    )

    return resultado, erros


def print_tokens(resultado):
    print(f"{'LINHA':<6} | {'COLUNA':<6} | {'TIPO (TOKEN)':<25} | LEXEMA")
    print('-' * 65)

    for tok in resultado:
        if tok['tipo'] == 'ERROR_IDENTIFIER':
            continue

        print(
            f"{tok['linha']:<6} | "
            f"{tok['coluna']:<6} | "
            f"{tok['tipo']:<25} | "
            f"{tok['valor']}"
        )


# Contabiliza as ocorrencias por categoria de token
def print_lexical_summary(resultado, errors):
    category_counts = {
        'Classes': 0,
        'Relações': 0,
        'Estereótipos (Classe/Relação)': 0,
        'Indivíduos (Instâncias)': 0,
        'Palavras Reservadas': 0,
        'Tipos de Dados Nativos': 0,
        'Tipos Customizados (DataType)': 0,
        'Meta-Atributos': 0,
        'Símbolos Especiais': 0,
        'Erros Encontrados': len(errors)
    }

    for tok in resultado:
        tipo = tok['tipo']

        if tipo == 'ERROR_IDENTIFIER':
            continue

        if tipo == 'CLASS_NAME':
            category_counts['Classes'] += 1

        elif tipo == 'RELATION_NAME':
            category_counts['Relações'] += 1

        elif tipo == 'INSTANCE_NAME':
            category_counts['Indivíduos (Instâncias)'] += 1

        elif tipo == 'CUSTOM_DATATYPE':
            category_counts['Tipos Customizados (DataType)'] += 1

        elif tipo.startswith('ST_'):
            category_counts['Estereótipos (Classe/Relação)'] += 1

        elif tipo.startswith('KW_'):
            category_counts['Palavras Reservadas'] += 1

        elif tipo.startswith('TYPE_'):
            category_counts['Tipos de Dados Nativos'] += 1

        elif tipo.startswith('META_'):
            category_counts['Meta-Atributos'] += 1

        else:
            category_counts['Símbolos Especiais'] += 1

    print('\n' + '=' * 65)
    print('TABELA DE SÍNTESE (RESUMO DE OCORRÊNCIAS)')
    print('=' * 65)
    print(f"{'CATEGORIA':<35} | QUANTIDADE")
    print('-' * 50)

    for cat, qtd in category_counts.items():
        print(f'{cat:<35} | {qtd} ocorrência(s)')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Uso correto: python lexer.py <arquivo.tonto>')
        sys.exit(1)

    nome_arquivo = sys.argv[1]

    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as arq:
            codigo_fonte = arq.read()

    except OSError as erro:
        print(f'Erro ao abrir o arquivo: {erro}')
        sys.exit(1)

    resultado, erros = tokenize(codigo_fonte)

    print(f'\nAnalisando arquivo: {nome_arquivo}')
    print_tokens(resultado)

    for erro in erros:
        print(
            f"[ERRO LÉXICO] Linha {erro['linha']}, "
            f"Coluna {erro['coluna']}: "
            f"{erro['mensagem']} "
            f"Sugestão: {erro['sugestao']}"
        )


    print_lexical_summary(resultado, erros)
