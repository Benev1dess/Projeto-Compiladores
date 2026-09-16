import sys
import ply.lex as lex

CLASS_STEREOTYPES = {
    'event': 'ST_EVENT', 'situation': 'ST_SITUATION', 'process': 'ST_PROCESS',
    'category': 'ST_CATEGORY', 'mixin': 'ST_MIXIN', 'phaseMixin': 'ST_PHASE_MIXIN',
    'roleMixin': 'ST_ROLE_MIXIN', 'historicalRoleMixin': 'ST_HISTORICAL_ROLE_MIXIN',
    'kind': 'ST_KIND', 'collective': 'ST_COLLECTIVE', 'quantity': 'ST_QUANTITY',
    'quality': 'ST_QUALITY', 'mode': 'ST_MODE', 'intrisicMode': 'ST_INTRINSIC_MODE',
    'extrinsicMode': 'ST_EXTRINSIC_MODE', 'subkind': 'ST_SUBKIND', 'phase': 'ST_PHASE',
    'role': 'ST_ROLE', 'historicalRole': 'ST_HISTORICAL_ROLE'
}

RELATION_STEREOTYPES = {
    'material': 'ST_MATERIAL', 'derivation': 'ST_DERIVATION', 'comparative': 'ST_COMPARATIVE',
    'mediation': 'ST_MEDIATION', 'characterization': 'ST_CHARACTERIZATION',
    'externalDependence': 'ST_EXTERNAL_DEPENDENCE', 'componentOf': 'ST_COMPONENT_OF',
    'memberOf': 'ST_MEMBER_OF', 'subCollectionOf': 'ST_SUB_COLLECTION_OF',
    'subQualityOf': 'ST_SUB_QUALITY_OF', 'instantiation': 'ST_INSTANTIATION',
    'termination': 'ST_TERMINATION', 'participational': 'ST_PARTICIPATIONAL',
    'participation': 'ST_PARTICIPATION', 'historicalDependence': 'ST_HISTORICAL_DEPENDENCE',
    'creation': 'ST_CREATION', 'manifestation': 'ST_MANIFESTATION', 'bringsAbout': 'ST_BRINGS_ABOUT',
    'triggers': 'ST_TRIGGERS', 'composition': 'ST_COMPOSITION', 'aggregation': 'ST_AGGREGATION',
    'inherence': 'ST_INHERENCE', 'value': 'ST_VALUE', 'formal': 'ST_FORMAL', 'constitution': 'ST_CONSTITUTION'
}

KEYWORDS = {
    'genset': 'KW_GENSET', 'disjoint': 'KW_DISJOINT', 'complete': 'KW_COMPLETE',
    'general': 'KW_GENERAL', 'specifics': 'KW_SPECIFICS', 'where': 'KW_WHERE',
    'package': 'KW_PACKAGE', 'import': 'KW_IMPORT', 'functional-complexes': 'KW_FUNCTIONAL_COMPLEXES',
    'specializes': 'KW_SPECIALIZES', 'enum': 'KW_ENUM'
}

NATIVE_TYPES = {
    'number': 'TYPE_NUMBER', 'string': 'TYPE_STRING', 'boolean': 'TYPE_BOOLEAN',
    'date': 'TYPE_DATE', 'time': 'TYPE_TIME', 'datetime': 'TYPE_DATETIME'
}

META_ATTRIBUTES = {
    'ordered': 'META_ORDERED', 'const': 'META_CONST', 'derived': 'META_DERIVED',
    'subsets': 'META_SUBSETS', 'redefines': 'META_REDEFINES'
}

reserved = {}
reserved.update(CLASS_STEREOTYPES)
reserved.update(RELATION_STEREOTYPES)
reserved.update(KEYWORDS)
reserved.update(NATIVE_TYPES)
reserved.update(META_ATTRIBUTES)

tokens = [
    #categorias gerais
    'CLASS_NAME',
    'RELATION_NAME',
    'INSTANCE_NAME',
    'CUSTOM_DATATYPE',
    'ERROR_IDENTIFIER',

    # simbolos
    'LBRACE',       # {
    'RBRACE',       # }
    'LPAREN',       # (
    'RPAREN',       # )
    'LBRACKET',     # [
    'RBRACKET',     # ]
    'RANGE',        # ..
    'COMP_LEFT',    # <>--
    'COMP_RIGHT',   # --<>
    'STAR',         # *
    'AT',           # @
    'DOT',          # .
    'COLON',        # :
    'COMMA',        # ,
] + list(reserved.values())

t_RANGE      = r'\.\.'
t_COMP_LEFT  = r'<>--'
t_COMP_RIGHT = r'--<>'
t_LBRACE     = r'\{'
t_RBRACE     = r'\}'
t_LPAREN     = r'\('
t_RPAREN     = r'\)'
t_LBRACKET   = r'\['
t_RBRACKET   = r'\]'
t_STAR       = r'\*'
t_AT         = r'@'
t_DOT        = r'\.'
t_COLON      = r':'
t_COMMA      = r','

t_ignore = ' \t'

def t_COMMENT(t):
    r'//.*'
    pass

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

#
def t_IDENTIFIER(t):
    #palavras comecadas com letra ou _
    r'[a-zA-Z_][a-zA-Z0-9_]*' 
    val = t.value
    
    if val in reserved:
        t.type = reserved[val]
        return t
        
    has_digits = any(c.isdigit() for c in val)
    has_underscore = '_' in val

    if val.endswith('DataType') and val[0].isalpha() and not has_digits and not has_underscore:
        t.type = 'CUSTOM_DATATYPE'
        return t

    if val[0].isalpha() and val[-1].isdigit():
        t.type = 'INSTANCE_NAME'
        return t

    if val[0].isupper() and not has_digits:
        t.type = 'CLASS_NAME'
        return t

    if val[0].islower() and not has_digits:
        t.type = 'RELATION_NAME'
        return t

    t.type = 'ERROR_IDENTIFIER'
    return t



def find_column(input_text, token):
    line_start = input_text.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1


def diagnose_identifier(val):
    if val.endswith('DataType'):
        if '_' in val:
            return "Tipos de dados customizados ('DataType') não podem conter sublinhado ('_')."
        if any(c.isdigit() for c in val):
            return "Tipos de dados customizados ('DataType') não podem conter números."
    if val[0].isupper() and any(c.isdigit() for c in val):
        return "Nomes de classe não podem conter números (para instâncias, o número deve ser o último caractere)."
    if val[0].islower() and any(c.isdigit() for c in val):
        return "Nomes de relação não podem conter números."
    if val.startswith('_'):
        return "Identificadores em TONTO não devem iniciar com sublinhado ('_')."
    return "Sintaxe de identificador incompatível com as convenções TONTO."


def t_error(t):
    col = find_column(t.lexer.lexdata, t)
    print(f"[ERRO LÉXICO] Linha {t.lineno}, Coluna {col}: Caractere não reconhecido '{t.value[0]}'. Sugestão: Remova o caractere ou verifique a pontuação.")
    t.lexer.skip(1)


lexer = lex.lex()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso correto: python lexer.py <arquivo.tonto>")
        sys.exit(1)
        
    nome_arquivo = sys.argv[1]
    
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as arq:
            codigo_fonte = arq.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
        sys.exit(1)
    
    lexer.input(codigo_fonte)
    
    print(f"\nAnalisando arquivo: {nome_arquivo}")
    print(f"{'LINHA':<6} | {'COLUNA':<6} | {'TIPO (TOKEN)':<25} | {'LEXEMA'}")
    print("-" * 65)
    
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
        'Erros Encontrados': 0
    }
    
    for tok in lexer:
        col = find_column(codigo_fonte, tok)
        
        if tok.type == 'ERROR_IDENTIFIER':
            category_counts['Erros Encontrados'] += 1
            sugestao = diagnose_identifier(tok.value)
            print(f"[ERRO NOMENCLATURA] Linha {tok.lineno}, Coluna {col}: Lexema '{tok.value}' inválido. Sugestão: {sugestao}")
            continue

        print(f"{tok.lineno:<6} | {col:<6} | {tok.type:<25} | {tok.value}")


        if tok.type == 'CLASS_NAME':
            category_counts['Classes'] += 1
        elif tok.type == 'RELATION_NAME':
            category_counts['Relações'] += 1
        elif tok.type == 'INSTANCE_NAME':
            category_counts['Indivíduos (Instâncias)'] += 1
        elif tok.type == 'CUSTOM_DATATYPE':
            category_counts['Tipos Customizados (DataType)'] += 1
        elif tok.type.startswith('ST_'):
            category_counts['Estereótipos (Classe/Relação)'] += 1
        elif tok.type.startswith('KW_'):
            category_counts['Palavras Reservadas'] += 1
        elif tok.type.startswith('TYPE_'):
            category_counts['Tipos de Dados Nativos'] += 1
        elif tok.type.startswith('META_'):
            category_counts['Meta-Atributos'] += 1
        else:
            category_counts['Símbolos Especiais'] += 1

    print("\n" + "=" * 65)
    print("TABELA DE SÍNTESE (RESUMO DE OCORRÊNCIAS)")
    print("=" * 65)
    print(f"{'CATEGORIA':<35} | {'QUANTIDADE'}")
    print("-" * 50)
    
    for cat, qtd in category_counts.items():
        print(f"{cat:<35} | {qtd} ocorrência(s)")