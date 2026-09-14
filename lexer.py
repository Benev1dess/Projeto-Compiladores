import ply.lex as lex

reserved = {
    'genset': 'GENSET', 'disjoint': 'DISJOINT', 'complete': 'COMPLETE',
    'general': 'GENERAL', 'specifics': 'SPECIFICS', 'where': 'WHERE',
    'package': 'PACKAGE', 'import': 'IMPORT', 'functional-complexes': 'FUNCTIONAL_COMPLEXES',
    
    'event': 'EVENT', 'situation': 'SITUATION', 'process': 'PROCESS',
    'category': 'CATEGORY', 'mixin': 'MIXIN', 'phaseMixin': 'PHASE_MIXIN',
    'roleMixin': 'ROLE_MIXIN', 'historicalRoleMixin': 'HISTORICAL_ROLE_MIXIN',
    'kind': 'KIND', 'collective': 'COLLECTIVE', 'quantity': 'QUANTITY',
    'quality': 'QUALITY', 'mode': 'MODE', 'intrisicMode': 'INTRINSIC_MODE',
    'extrinsicMode': 'EXTRINSIC_MODE', 'subkind': 'SUBKIND', 'phase': 'PHASE',
    'role': 'ROLE', 'historicalRole': 'HISTORICAL_ROLE',

    'material': 'MATERIAL', 'derivation': 'DERIVATION', 'comparative': 'COMPARATIVE',
    'mediation': 'MEDIATION', 'characterization': 'CHARACTERIZATION',
    'externalDependence': 'EXTERNAL_DEPENDENCE', 'componentOf': 'COMPONENT_OF',
    'memberOf': 'MEMBER_OF', 'subCollectionOf': 'SUB_COLLECTION_OF',
    'subQualityOf': 'SUB_QUALITY_OF', 'instantiation': 'INSTANTIATION',
    'termination': 'TERMINATION', 'participational': 'PARTICIPATIONAL',
    'participation': 'PARTICIPATION', 'historicalDependence': 'HISTORICAL_DEPENDENCE',
    'creation': 'CREATION', 'manifestation': 'MANIFESTATION', 'bringsAbout': 'BRINGS_ABOUT',
    'triggers': 'TRIGGERS', 'composition': 'COMPOSITION', 'aggregation': 'AGGREGATION',
    'inherence': 'INHERENCE', 'value': 'VALUE', 'formal': 'FORMAL', 'constitution': 'CONSTITUTION'
}

tokens = [
    #categorias gerais
    'CLASS_NAME',
    'RELATION_NAME',
    'INSTANCE_NAME',

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


t_ignore = ' \t'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)