import sys
import ply.yacc as yacc
from lexer import tokens, build_lexer, find_column

start = 'document'
codigo_fonte = ''

def p_document(p):
    'document : imports KW_PACKAGE package_name declarations'
    p[0] = {
        'pacote': p[3],
        'imports': p[1],
        'declaracoes': p[4]
    }

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

def p_declarations(p):
    '''declarations : declarations declaration
                    | empty'''
    p[0] = p[1] + [p[2]] if len(p) == 3 else []

def p_declaration(p):
    '''declaration : class_decl
                   | enum_decl
                   | datatype_decl
                   | external_relation
                   | genset_decl'''
    p[0] = p[1]

# ==========================================
# CLASSES
# ==========================================
def p_class_decl(p):
    'class_decl : class_stereotype CLASS_NAME superclass_opt class_body_opt'
    p[0] = {
        'tipo_declaracao': 'classe',
        'nome': p[2],
        'estereotipo': p[1],
        'superclasse': p[3],
        'atributos': p[4],
        'linha': p.lineno(1)
    }

# ==========================================
# ENUMS (Atualizado para aceitar qualquer nome)
# ==========================================
def p_enum_decl(p):
    'enum_decl : KW_ENUM CLASS_NAME LBRACE enum_values_opt RBRACE'
    p[0] = {
        'tipo_declaracao': 'enum',
        'nome': p[2],
        'valores': p[4],
        'linha': p.lineno(1)
    }

def p_enum_values_opt(p):
    '''enum_values_opt : enum_values
                       | empty'''
    p[0] = p[1] if p[1] else []

def p_enum_values(p):
    '''enum_values : enum_values COMMA enum_val
                   | enum_val'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]

def p_enum_val(p):
    '''enum_val : CLASS_NAME
                | RELATION_NAME'''
    p[0] = p[1]

# ==========================================
# DATATYPES
# ==========================================
def p_datatype_decl(p):
    'datatype_decl : KW_DATATYPE CLASS_NAME LBRACE attributes_opt RBRACE'
    p[0] = {
        'tipo_declaracao': 'datatype',
        'nome': p[2],
        'atributos': p[4],
        'linha': p.lineno(1)
    }

# ==========================================
# CONJUNTOS DE GENERALIZAÇÃO (Gensets)
# ==========================================
def p_genset_decl_2_mods(p):
    '''genset_decl : KW_DISJOINT KW_COMPLETE KW_GENSET CLASS_NAME LBRACE KW_GENERAL CLASS_NAME KW_SPECIFICS class_list RBRACE
                   | KW_COMPLETE KW_DISJOINT KW_GENSET CLASS_NAME LBRACE KW_GENERAL CLASS_NAME KW_SPECIFICS class_list RBRACE'''
    p[0] = {
        'tipo_declaracao': 'genset',
        'nome': p[4],
        'modificadores': [p[1], p[2]],
        'geral': p[7],
        'especificas': p[9],
        'linha': p.lineno(3)
    }

def p_genset_decl_1_mod(p):
    '''genset_decl : KW_DISJOINT KW_GENSET CLASS_NAME LBRACE KW_GENERAL CLASS_NAME KW_SPECIFICS class_list RBRACE
                   | KW_COMPLETE KW_GENSET CLASS_NAME LBRACE KW_GENERAL CLASS_NAME KW_SPECIFICS class_list RBRACE'''
    p[0] = {
        'tipo_declaracao': 'genset',
        'nome': p[3],
        'modificadores': [p[1]],
        'geral': p[6],
        'especificas': p[8],
        'linha': p.lineno(2)
    }

def p_genset_decl_0_mod(p):
    '''genset_decl : KW_GENSET CLASS_NAME LBRACE KW_GENERAL CLASS_NAME KW_SPECIFICS class_list RBRACE'''
    p[0] = {
        'tipo_declaracao': 'genset',
        'nome': p[2],
        'modificadores': [],
        'geral': p[5],
        'especificas': p[7],
        'linha': p.lineno(1)
    }

def p_class_list(p):
    '''class_list : class_list COMMA CLASS_NAME
                  | CLASS_NAME'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]

# ==========================================
# ESTEREÓTIPOS E HERANÇA
# ==========================================
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

def p_superclass_opt(p):
    '''superclass_opt : KW_SPECIALIZES CLASS_NAME
                      | empty'''
    p[0] = p[2] if len(p) == 3 else None

def p_class_body_opt(p):
    '''class_body_opt : LBRACE attributes_opt RBRACE
                      | empty'''
    p[0] = p[2] if len(p) == 4 else []

def p_attributes_opt(p):
    '''attributes_opt : attributes
                      | empty'''
    p[0] = p[1] if p[1] else [] 
    
def p_attributes(p):
    '''attributes : attributes class_item
                  | class_item'''     
    p[0] = p[1] + [p[2]] if len(p) == 3 else [p[1]]

def p_class_item(p):
    '''class_item : attribute
                  | internal_relation'''
    p[0] = p[1]

def p_attribute(p):
    'attribute : RELATION_NAME COLON data_type meta_opt'
    p[0] = { 
        'nome': p[1],
        'tipo_dado': p[3],
        'meta': p[4]
    }

# ==========================================
# RELAÇÕES E CARDINALIDADES
# ==========================================
def p_internal_relation(p):
    'internal_relation : AT relation_stereotype cardinality relation_sym cardinality CLASS_NAME'
    p[0] = { 
        'tipo_item': 'relacao_interna',
        'estereotipo': p[2],
        'cardinalidade_origem': p[3],
        'simbolo': p[4],
        'cardinalidade_destino': p[5],
        'destino': p[6]
    }

def p_external_relation(p):
    'external_relation : AT relation_stereotype KW_RELATION CLASS_NAME cardinality relation_sym RELATION_NAME relation_sym cardinality CLASS_NAME'
    p[0] = {
        'tipo_declaracao': 'relacao_externa',
        'estereotipo': p[2],
        'dominio': p[4],
        'cardinalidade_dominio': p[5],
        'nome_relacao': p[7],
        'cardinalidade_imagem': p[9],
        'imagem': p[10],
        'linha': p.lineno(1)
    }

def p_cardinality(p):
    '''cardinality : LBRACKET NUMBER RBRACKET
                   | LBRACKET NUMBER RANGE NUMBER RBRACKET
                   | LBRACKET NUMBER RANGE STAR RBRACKET
                   | LBRACKET STAR RBRACKET'''
    if len(p) == 4:
        p[0] = str(p[2])
    else:
        p[0] = f"{p[2]}..{p[4]}"

def p_relation_sym(p):
    '''relation_sym : COMP_LEFT
                    | COMP_RIGHT
                    | DASH'''
    p[0] = p[1]

def p_relation_stereotype(p):
    '''relation_stereotype : ST_COMPONENT_OF
                           | ST_MEDIATION
                           | ST_MATERIAL
                           | ST_DERIVATION
                           | ST_CHARACTERIZATION
                           | ST_COMPARATIVE
                           | ST_EXTERNAL_DEPENDENCE
                           | ST_MEMBER_OF
                           | ST_SUB_COLLECTION_OF
                           | ST_SUB_QUALITY_OF
                           | ST_INSTANTIATION
                           | ST_TERMINATION
                           | ST_PARTICIPATIONAL
                           | ST_PARTICIPATION
                           | ST_HISTORICAL_DEPENDENCE
                           | ST_CREATION
                           | ST_MANIFESTATION
                           | ST_BRINGS_ABOUT
                           | ST_TRIGGERS
                           | ST_COMPOSITION
                           | ST_AGGREGATION
                           | ST_INHERENCE
                           | ST_VALUE
                           | ST_FORMAL
                           | ST_CONSTITUTION'''
    p[0] = p[1]

# ==========================================
# TIPOS E METADADOS
# ==========================================
def p_data_type(p):
    '''data_type : TYPE_NUMBER
                 | TYPE_STRING
                 | TYPE_BOOLEAN
                 | TYPE_DATE
                 | TYPE_TIME
                 | TYPE_DATETIME
                 | CLASS_NAME'''  
    p[0] = p[1]  

def p_meta_opt(p):
    '''meta_opt : LBRACE meta_list RBRACE
                | empty'''
    p[0] = p[2] if len(p) == 4 else []

def p_meta_list(p):
    '''meta_list : meta_list COMMA meta_attr
                 | meta_attr'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]

def p_meta_attr(p):
    '''meta_attr : META_ORDERED
                 | META_CONST
                 | META_DERIVED
                 | META_SUBSETS
                 | META_REDEFINES'''
    p[0] = p[1]

def p_empty(p):
    'empty :'
    p[0] = None

# ==========================================
# TRATAMENTO DE ERROS E EXECUÇÃO
# ==========================================
class ErroSintatico(Exception):
    pass

def p_error(p):
    if p is None:
        print('Erro sintatico: fim inesperado do arquivo.')
    else:
        coluna = find_column(codigo_fonte, p)
        print(f"Erro sintatico na linha {p.lineno}, coluna {coluna}: token '{p.value}' inesperado.")
    raise ErroSintatico()

# Setup usando tabmodule exclusivo para evitar o cache!
parser = yacc.yacc(debug=False, write_tables=False, tabmodule="tonto_parser_tab", errorlog=yacc.NullLogger())

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
    print(f"Importacoes reconhecidas: {', '.join(resultado['imports']) or 'nenhuma'}")
    print(f"Declaracoes reconhecidas: {len(resultado['declaracoes'])}")

    for decl in resultado['declaracoes']:
        if decl['tipo_declaracao'] == 'classe':
            superclasse = f" specializes {decl['superclasse']}" if decl['superclasse'] else ''
            print(f"  [Classe] {decl['estereotipo']} {decl['nome']}{superclasse} (linha {decl['linha']})")
            
        elif decl['tipo_declaracao'] == 'enum':
            print(f"  [Enum] {decl['nome']} com {len(decl['valores'])} valores (linha {decl['linha']})")
            
        elif decl['tipo_declaracao'] == 'datatype':
            print(f"  [DataType] {decl['nome']} com {len(decl['atributos'])} atributos (linha {decl['linha']})")
            
        elif decl['tipo_declaracao'] == 'relacao_externa':
            print(f"  [Relação Externa] @{decl['estereotipo']} {decl['dominio']} {decl['cardinalidade_dominio']} -- {decl['nome_relacao']} -- {decl['cardinalidade_imagem']} {decl['imagem']} (linha {decl['linha']})")
            
        elif decl['tipo_declaracao'] == 'genset':
            mods = " ".join(decl['modificadores'])
            if mods:
                print(f"  [Genset] {mods} genset {decl['nome']} (Geral: {decl['geral']}, Específicas: {', '.join(decl['especificas'])}) (linha {decl['linha']})")
            else:
                print(f"  [Genset] genset {decl['nome']} (Geral: {decl['geral']}, Específicas: {', '.join(decl['especificas'])}) (linha {decl['linha']})")

    print('\nAnalise sintatica concluida com sucesso.')