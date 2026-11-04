import ply.lex as lex

# ==========================================
# LISTA DE TOKENS
# ==========================================

reserved = {
    # Palavras-chave de estrutura
    'package': 'KW_PACKAGE',
    'import': 'KW_IMPORT',
    'enum': 'KW_ENUM',
    'datatype': 'KW_DATATYPE',
    'genset': 'KW_GENSET',
    'general': 'KW_GENERAL',
    'specifics': 'KW_SPECIFICS',
    'disjoint': 'KW_DISJOINT',
    'complete': 'KW_COMPLETE',
    'specializes': 'KW_SPECIALIZES',
    'relation': 'KW_RELATION',

    # Tipos nativos
    'number': 'TYPE_NUMBER',
    'string': 'TYPE_STRING',
    'boolean': 'TYPE_BOOLEAN',
    'date': 'TYPE_DATE',
    'time': 'TYPE_TIME',
    'datetime': 'TYPE_DATETIME',

    # Metadados
    'ordered': 'META_ORDERED',
    'const': 'META_CONST',
    'derived': 'META_DERIVED',
    'subsets': 'META_SUBSETS',
    'redefines': 'META_REDEFINES',

    # Estereótipos de Classe (OntoUML / TONTO)
    'event': 'ST_EVENT',
    'situation': 'ST_SITUATION',
    'process': 'ST_PROCESS',
    'category': 'ST_CATEGORY',
    'mixin': 'ST_MIXIN',
    'phaseMixin': 'ST_PHASE_MIXIN',
    'roleMixin': 'ST_ROLE_MIXIN',
    'historicalRoleMixin': 'ST_HISTORICAL_ROLE_MIXIN',
    'kind': 'ST_KIND',
    'relator': 'ST_RELATOR',
    'collective': 'ST_COLLECTIVE',
    'quantity': 'ST_QUANTITY',
    'quality': 'ST_QUALITY',
    'mode': 'ST_MODE',
    'intrinsicMode': 'ST_INTRINSIC_MODE',
    'extrinsicMode': 'ST_EXTRINSIC_MODE',
    'subkind': 'ST_SUBKIND',
    'phase': 'ST_PHASE',
    'role': 'ST_ROLE',
    'historicalRole': 'ST_HISTORICAL_ROLE',

    # Estereótipos de Relação
    'componentOf': 'ST_COMPONENT_OF',
    'mediation': 'ST_MEDIATION',
    'material': 'ST_MATERIAL',
    'derivation': 'ST_DERIVATION',
    'characterization': 'ST_CHARACTERIZATION',
    'comparative': 'ST_COMPARATIVE',
    'externalDependence': 'ST_EXTERNAL_DEPENDENCE',
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
    'constitution': 'ST_CONSTITUTION',
}

tokens = [
    'CLASS_NAME',
    'RELATION_NAME',
    'DASH_IDENTIFIER',
    'NUMBER',
    'LBRACE',
    'RBRACE',
    'LBRACKET',
    'RBRACKET',
    'COLON',
    'COMMA',
    'AT',
    'RANGE',
    'STAR',
    'COMP_LEFT',
    'COMP_RIGHT',
    'DASH'
] + list(set(reserved.values()))

# ==========================================
# REGRAS SIMPLES DE TOKENS (EXPRESSÕES REGULARES)
# ==========================================

t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COLON = r':'
t_COMMA = r','
t_AT = r'@'
t_RANGE = r'\.\.'
t_STAR = r'\*'
t_COMP_LEFT = r'<>--'
t_COMP_RIGHT = r'--<>'
t_DASH = r'--'

# Ignorar espaços em branco e tabulações
t_ignore = ' \t\r'

# ==========================================
# REGRAS COMPLEXAS DE TOKENS
# ==========================================

# Identificadores com hífen (ex: functional-complexes, intrinsic-modes)
def t_DASH_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*-[a-zA-Z0-9_\-]*'
    return t

# Nomes iniciados com letra maiúscula (Classes, Gensets, Datatypes)
def t_CLASS_NAME(t):
    r'[A-Z][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'CLASS_NAME')
    return t

# Nomes iniciados com letra minúscula (Atributos, Relações, Palavras-chave)
def t_RELATION_NAME(t):
    r'[a-z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'RELATION_NAME')
    return t

# Números inteiros
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Ignorar comentários (linha única iniciada por //)
def t_COMMENT(t):
    r'//.*'
    pass

# Contagem de linhas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Tratamento de erros léxicos
def t_error(t):
    coluna = find_column(t.lexer.lexdata, t)
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lineno}, coluna {coluna}")
    t.lexer.skip(1)

# ==========================================
# FUNÇÕES AUXILIARES E CONSTRUÇÃO DO LEXER
# ==========================================

def find_column(input_text, token):
    line_start = input_text.rfind('\n', 0, token.lexpos)
    if line_start < 0:
        line_start = 0
    else:
        line_start += 1
    return (token.lexpos - line_start) + 1

def build_lexer():
    return lex.lex()

if __name__ == '__main__':
    # Teste rápido do Lexer via terminal
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            data = f.read()
        lexer = build_lexer()
        lexer.input(data)
        for tok in lexer:
            print(tok)