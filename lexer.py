import ply.lex as lex

# Dicionário de palavras reservadas e estereótipos
reserved = {
    'package': 'KW_PACKAGE',
    'import': 'KW_IMPORT',
    'enum': 'KW_ENUM',
    'datatype': 'KW_DATATYPE',
    'specializes': 'KW_SPECIALIZES',
    'relation': 'KW_RELATION',
    'genset': 'KW_GENSET',
    'disjoint': 'KW_DISJOINT',
    'complete': 'KW_COMPLETE',
    'general': 'KW_GENERAL',
    'specifics': 'KW_SPECIFICS',
    
    # Estereótipos de Classes
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

    # Estereótipos de Relações
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

    # Tipos Primitivos
    'string': 'TYPE_STRING',
    'number': 'TYPE_NUMBER',
    'boolean': 'TYPE_BOOLEAN',
    'date': 'TYPE_DATE',
    'time': 'TYPE_TIME',
    'datetime': 'TYPE_DATETIME',
    
    # Metadados
    'ordered': 'META_ORDERED',
    'const': 'META_CONST',
    'derived': 'META_DERIVED',
    'subsets': 'META_SUBSETS',
    'redefines': 'META_REDEFINES'
}

# Lista principal de tokens (Tem que bater com o que o parser.py usa)
tokens = [
    'CLASS_NAME', 'RELATION_NAME',
    'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET', 'COLON', 'COMMA',
    'AT', 'DASH', 'COMP_LEFT', 'COMP_RIGHT', 'RANGE', 'STAR', 'NUMBER'
] + list(reserved.values())

# Expressões regulares simples
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COLON = r':'
t_COMMA = r','
t_AT = r'@'
t_DASH = r'-{1,2}'
t_COMP_LEFT = r'<'
t_COMP_RIGHT = r'>'
t_RANGE = r'\.\.'
t_STAR = r'\*'

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Ignorar comentários (começando com //)
def t_COMMENT(t):
    r'//.*'
    pass

# Identificadores (Nomes de Classes e Relações)
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9\-]*'
    # Verifica se a palavra capturada é uma palavra reservada (ex: role, genset, string)
    if t.value in reserved:
        t.type = reserved[t.value]
    # Se a primeira letra for maiúscula, classifica como classe/enum (ex: Clinico_Geral01)
    elif t.value[0].isupper():
        t.type = 'CLASS_NAME'
    # Se for minúscula, classifica como nome de relação
    else:
        t.type = 'RELATION_NAME'
    return t

# Ignorar espaços em branco e tabulações
t_ignore = ' \t\r'

# Contar quebras de linha para mensagens de erro precisas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Tratamento de erro léxico
def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lineno}")
    t.lexer.skip(1)

# Construtor do Lexer
def build_lexer():
    return lex.lex()

# Função auxiliar para calcular a coluna
def find_column(input_str, token):
    last_cr = input_str.rfind('\n', 0, token.lexpos)
    if last_cr < 0:
        last_cr = 0
    column = (token.lexpos - last_cr) + 1
    return column