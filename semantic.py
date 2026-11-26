import sys
from collections import defaultdict


GENSET_RULES = {
    'subkind':   {'disjoint': 'obrigatorio', 'complete': 'opcional'},
    'role':      {'disjoint': 'proibido',    'complete': 'opcional'},
    'phase':     {'disjoint': 'obrigatorio', 'complete': 'opcional'},
    'rolemixin': {'disjoint': 'obrigatorio', 'complete': 'obrigatorio'},
}
ROTULO = {
    'subkind': 'Subkind Pattern', 'role': 'Role Pattern',
    'phase': 'Phase Pattern', 'rolemixin': 'RoleMixin Pattern',
}
NOME_CURTO = {'subkind': 'Subkind', 'role': 'Role', 'phase': 'Phase',
              'rolemixin': 'RoleMixin'}

NATIVOS = {'number', 'string', 'boolean', 'date', 'time', 'datetime'}
RIGIDOS = {'kind', 'subkind', 'collective', 'quantity', 'relator', 'mode',
           'quality', 'category', 'intrinsicMode', 'extrinsicMode'}
ANTI_RIGIDOS = {'role', 'phase', 'roleMixin', 'phaseMixin',
                'historicalRole', 'historicalRoleMixin'}
SORTAIS_DEPENDENTES = {'subkind', 'role', 'phase'}


def limite_inferior(card):
    """'1..*' -> 1 ; '*' -> 0 ; '0..1' -> 0 ; None -> None"""
    if card is None:
        return None
    base = str(card).split('..')[0]
    return 0 if base == '*' else int(base)


class Achado:
    def __init__(self, linhas, titulo, detalhe='', sugestao='', sev=''):
        self.linhas = sorted({l for l in linhas if l})
        self.titulo = titulo
        self.detalhe = detalhe
        self.sugestao = sugestao
        self.sev = sev

    @property
    def ordem(self):
        return self.linhas[0] if self.linhas else 0

    def rotulo_linhas(self):
        return 'L' + ','.join(map(str, self.linhas)) if self.linhas else 'L?'

class Modelo:
    def __init__(self, ast):
        self.pacote = ast['pacote']
        self.imports = ast['imports']
        self.classes = {}          # nome -> declaração
        self.duplicadas = []
        self.enums, self.datatypes = {}, {}
        self.gensets, self.relacoes_externas = [], []

        for d in ast['declaracoes']:
            t = d['tipo_declaracao']
            if t == 'classe':
                if d['nome'] in self.classes:
                    self.duplicadas.append(d)
                else:
                    self.classes[d['nome']] = d
            elif t == 'enum':
                self.enums[d['nome']] = d
            elif t == 'datatype':
                self.datatypes[d['nome']] = d
            elif t == 'genset':
                self.gensets.append(d)
            elif t == 'relacao_externa':
                self.relacoes_externas.append(d)

        # genset também declara generalização
        self.pais_genset = defaultdict(list)
        for g in self.gensets:
            for e in g['especificas']:
                self.pais_genset[e].append(g['geral'])

    def est(self, nome):
        c = self.classes.get(nome)
        return c['estereotipo'] if c else None

    def linha(self, nome):
        c = self.classes.get(nome)
        return c['linha'] if c else 0

    def pais(self, nome):
        """Pais efetivos = 'specializes' declarado + gensets em que é específica."""
        c = self.classes.get(nome)
        declarados = c['superclasse'] if c else []
        return list(dict.fromkeys(declarados + self.pais_genset.get(nome, [])))

    def filhos_de(self, pai, estereotipo):
        return [n for n, c in self.classes.items()
                if c['estereotipo'] == estereotipo and pai in self.pais(n)]

    def com_estereotipo(self, estereotipo):
        return [n for n, c in self.classes.items()
                if c['estereotipo'] == estereotipo]

    @staticmethod
    def relacoes(classe, estereotipo=None):
        return [a for a in classe['atributos']
                if a.get('tipo_item') == 'relacao_interna'
                and (estereotipo is None or a.get('estereotipo') == estereotipo)]


class Analisador:
    def __init__(self, ast):
        self.m = Modelo(ast)
        self.padroes, self.erros, self.incompletos = [], [], []
        self.erros_por_genset = defaultdict(int)

    def _erro(self, linhas, titulo, sugestao='', sev='ERRO', genset=None):
        self.erros.append(Achado(linhas, titulo, sugestao=sugestao, sev=sev))
        if genset is not None and sev == 'ERRO':
            self.erros_por_genset[id(genset)] += 1

    def _incompleto(self, linhas, titulo, sugestao=''):
        self.incompletos.append(Achado(linhas, titulo, sugestao=sugestao))

    def _padrao(self, linhas, titulo, detalhe=''):
        self.padroes.append(Achado(linhas, titulo, detalhe=detalhe))

    def _indefinido(self, nome, linha, contexto):
        tem_imp = bool(self.m.imports)
        self._erro([linha],
                   f"'{nome}' ({contexto}) não foi declarado"
                   + (" neste pacote (pode vir de um import)" if tem_imp else ""),
                   "declare a classe neste pacote ou importe o pacote que a define",
                   'AVISO' if tem_imp else 'ERRO')

    def executar(self):
        self.verificar_declaracoes()
        for g in self.m.gensets:
            self.verificar_genset(g)
        self.padroes_sortais()
        self.padrao_rolemixin()
        self.padrao_relator()
        self.padrao_mode()
        for lista in (self.padroes, self.erros, self.incompletos):
            lista.sort(key=lambda a: a.ordem)
        return self

    def verificar_declaracoes(self):
        m = self.m

        for d in m.duplicadas:
            self._erro([d['linha'], m.linha(d['nome'])],
                       f"Classe '{d['nome']}' declarada mais de uma vez",
                       "renomeie ou remova uma das declarações")

        vistos = {}
        for g in m.gensets:
            if g['nome'] in vistos:
                self._erro([g['linha'], vistos[g['nome']]],
                           f"Genset '{g['nome']}' declarado mais de uma vez",
                           "use nomes distintos para cada genset")
            vistos[g['nome']] = g['linha']

        for nome, c in m.classes.items():
            est = c['estereotipo']

            for sup in c['superclasse']:
                if sup not in m.classes:
                    self._indefinido(sup, c['linha'], f"superclasse de '{nome}'")
                elif est in RIGIDOS and m.est(sup) in ANTI_RIGIDOS:
                    self._erro([c['linha']],
                               f"'{nome}' ({est}, rígido) especializa '{sup}' "
                               f"({m.est(sup)}, anti-rígido)",
                               "um tipo rígido não pode especializar um anti-rígido; "
                               "inverta a especialização ou ajuste o estereótipo")

            if est in SORTAIS_DEPENDENTES and not m.pais(nome):
                kinds = m.com_estereotipo('kind')
                if len(kinds) == 1:
                    sug = f"adicione 'specializes {kinds[0]}' (único kind do pacote)"
                elif kinds:
                    sug = f"adicione 'specializes <um de: {', '.join(kinds)}>'"
                else:
                    sug = "declare um kind e faça a classe especializá-lo"
                self._erro([c['linha']],
                           f"'{nome}' ({est}) não especializa nenhuma classe", sug)

            for a in c['atributos']:
                if a.get('tipo_item') == 'relacao_interna':
                    if a['destino'] not in m.classes:
                        self._indefinido(a['destino'], a.get('linha', c['linha']),
                                         f"destino de relação em '{nome}'")
                else:
                    self._verificar_tipo_atributo(a, nome, c['linha'])

        for nome, d in m.datatypes.items():
            for a in d['atributos']:
                if a.get('tipo_item') != 'relacao_interna':
                    self._verificar_tipo_atributo(a, nome, d['linha'])

        for r in m.relacoes_externas:
            for lado in ('dominio', 'imagem'):
                if r[lado] not in m.classes:
                    self._indefinido(r[lado], r['linha'], f"{lado} de @{r['estereotipo']}")

    def _verificar_tipo_atributo(self, attr, dono, linha):
        t = attr['tipo_dado']
        if t in NATIVOS or t in self.m.enums or t in self.m.datatypes:
            return
        self._indefinido(t, attr.get('linha', linha),
                         f"tipo do atributo '{attr['nome']}' em '{dono}'")


    def classificar(self, g):
        """Qual ODP baseado em genset este genset instancia (ou None)."""
        m = self.m
        estg = m.est(g['geral'])
        sp = {m.est(s) for s in g['especificas']}
        if not sp or None in sp:
            return None
        if estg == 'kind' and len(sp) == 1:
            x = next(iter(sp))
            if x in ('subkind', 'role', 'phase'):
                return x
        if estg == 'roleMixin' and sp == {'role'}:
            return 'rolemixin'
        return None

    def verificar_genset(self, g):
        m = self.m
        nome, geral, specs = g['nome'], g['geral'], g['especificas']
        mods = set(g['modificadores'])
        ln = g['linha']

        if geral not in m.classes:
            self._indefinido(geral, ln, f"general do genset '{nome}'")
        for s in specs:
            if s not in m.classes:
                self._indefinido(s, ln, f"specific do genset '{nome}'")
        if len(set(specs)) != len(specs):
            self._erro([ln], f"Genset '{nome}' repete classes em 'specifics'",
                       "liste cada classe específica uma única vez", genset=g)
        if geral in specs:
            self._erro([ln], f"Genset '{nome}': '{geral}' é general e specific ao mesmo tempo",
                       "remova a classe de 'specifics'", genset=g)

        padrao = self.classificar(g)

        if padrao is None:
            estg = m.est(geral)
            sp = {m.est(s) for s in specs if m.est(s)}
            if estg in ('kind', 'roleMixin') and sp:
                permitido = {'kind': {'subkind', 'role', 'phase'},
                             'roleMixin': {'role'}}[estg]
                if estg == 'kind' and len(sp) > 1 and sp <= permitido:
                    self._erro([ln], f"Genset '{nome}' mistura estereótipos "
                                     f"({', '.join(sorted(sp))}) sob o kind '{geral}'",
                               "separe em um genset por padrão (um para subkinds, "
                               "outro para roles, outro para phases)", genset=g)
                elif sp - permitido:
                    ruins = [s for s in specs if m.est(s) in (sp - permitido)]
                    self._erro([ln], f"Genset '{nome}': {', '.join(ruins)} não pode(m) "
                                     f"especializar {estg} '{geral}' por este genset",
                               f"specifics válidos para {estg}: {', '.join(sorted(permitido))}",
                               genset=g)
            return

        regras = GENSET_RULES[padrao]
        for mod in ('disjoint', 'complete'):
            tem = mod in mods
            if regras[mod] == 'obrigatorio' and not tem:
                self._erro([ln], f"{ROTULO[padrao]}: genset '{nome}' sem '{mod}' "
                                 f"({mod} é obrigatório neste padrão)",
                           f"escreva '{mod} genset {nome} {{ ... }}'", genset=g)
            if regras[mod] == 'proibido' and tem:
                self._erro([ln], f"{ROTULO[padrao]}: genset '{nome}' usa '{mod}', "
                                 f"que não se aplica a este padrão",
                           f"remova '{mod}' do genset '{nome}'", genset=g)

        if len(specs) < 2:
            self._erro([ln], f"Genset '{nome}' tem só 1 classe específica; "
                             f"um genset particiona em ao menos 2",
                       "acrescente outra classe em 'specifics'", 'AVISO')

        if padrao != 'rolemixin':     # no rolemixin, o genset é quem declara a generalização
            for s in specs:
                c = m.classes.get(s)
                if c and c['superclasse'] and geral not in c['superclasse']:
                    self._erro([ln, c['linha']],
                               f"'{s}' declara 'specializes {', '.join(c['superclasse'])}' "
                               f"mas o genset '{nome}' o coloca sob '{geral}'",
                               f"troque para 'specializes {geral}'", genset=g)


    def padroes_sortais(self):
        m = self.m
        for kind in m.com_estereotipo('kind'):
            for tipo in ('subkind', 'role', 'phase'):
                membros = m.filhos_de(kind, tipo)
                if not membros:
                    continue
                gs = [g for g in m.gensets
                      if g['geral'] == kind and self.classificar(g) == tipo]

                if gs:
                    for g in gs:
                        cobertos = set(g['especificas'])
                        linhas = [m.linha(kind), g['linha']] + \
                                 [m.linha(s) for s in g['especificas']]
                        viol = self.erros_por_genset.get(id(g), 0)
                        self._padrao(
                            linhas, ROTULO[tipo] + (f" (com {viol} violação(ões))" if viol else ""),
                            f"kind {kind}; {tipo}s: {', '.join(g['especificas'])}; "
                            f"genset {g['nome']} [{' '.join(g['modificadores']) or 'sem modificadores'}]")
                        faltantes = [x for x in membros if x not in cobertos]
                        if faltantes:
                            if 'complete' in g['modificadores']:
                                self._erro([g['linha']] + [m.linha(x) for x in faltantes],
                                           f"Genset '{g['nome']}' é complete, mas não lista "
                                           f"{tipo}(s) de '{kind}': {', '.join(faltantes)}",
                                           f"inclua {', '.join(faltantes)} em 'specifics'",
                                           genset=g)
                            else:
                                self._incompleto([g['linha']] + [m.linha(x) for x in faltantes],
                                                 f"{ROTULO[tipo]} parcial: {', '.join(faltantes)} "
                                                 f"especializa(m) '{kind}' fora do genset '{g['nome']}'",
                                                 f"dedução: acrescentar {', '.join(faltantes)} em 'specifics'")
                    continue

                # sem genset: sobrecarga por evidência parcial 
                linhas = [m.linha(kind)] + [m.linha(x) for x in membros]
                if len(membros) >= 2:
                    self._incompleto(
                        linhas,
                        f"{ROTULO[tipo]} incompleto: kind '{kind}' com {len(membros)} {tipo}s "
                        f"({', '.join(membros)}) e nenhum genset",
                        "dedução: " + self._tpl_genset(tipo, kind, membros))
                elif tipo in ('subkind', 'phase'):
                    self._incompleto(
                        linhas,
                        f"{ROTULO[tipo]} incompleto: só existe {tipo} '{membros[0]}' "
                        f"sob '{kind}' (o padrão particiona em ao menos 2)",
                        f"dedução: declare ao menos mais um {tipo} sob '{kind}' e o genset "
                        + self._tpl_genset(tipo, kind, [membros[0], f"Outro_{NOME_CURTO[tipo]}"]))

    @staticmethod
    def _tpl_genset(tipo, geral, specs):
        regras = GENSET_RULES[tipo]
        mods = [x for x in ('disjoint', 'complete') if regras[x] != 'proibido']
        nome = f"{geral}_{NOME_CURTO[tipo]}_Genset"
        return (f"{' '.join(mods)} genset {nome} "
                f"{{ general {geral} specifics {', '.join(specs)} }}")

    # RoleMixin
    def padrao_rolemixin(self):
        m = self.m
        for nome in m.com_estereotipo('roleMixin'):
            c = m.classes[nome]
            gs = [g for g in m.gensets
                  if g['geral'] == nome and self.classificar(g) == 'rolemixin']
            candidatos = [r for r in m.com_estereotipo('role')
                          if nome in m.classes[r]['superclasse']]

            if gs:
                for g in gs:
                    specs = g['especificas']
                    viol = self.erros_por_genset.get(id(g), 0)
                    linhas = [c['linha'], g['linha']] + [m.linha(s) for s in specs]
                    self._padrao(
                        linhas, ROTULO['rolemixin'] + (f" (com {viol} violação(ões))" if viol else ""),
                        f"roleMixin {nome}; roles: {', '.join(specs)}; genset {g['nome']} "
                        f"[{' '.join(g['modificadores']) or 'sem modificadores'}]")
                    bases = [tuple(sorted(p for p in m.pais(s) if m.est(p) == 'kind'))
                             for s in specs]
                    if len(specs) >= 2 and len(set(bases)) == 1 and bases[0]:
                        self._erro([g['linha']] + [m.linha(s) for s in specs],
                                   f"Todos os roles de '{nome}' especializam o mesmo kind "
                                   f"({', '.join(bases[0])}); isso é o Role Pattern, "
                                   f"não o RoleMixin Pattern",
                                   "use roles de kinds diferentes ou troque o roleMixin por um genset de roles",
                                   'AVISO')
                    faltantes = [r for r in candidatos if r not in specs]
                    if faltantes:
                        self._incompleto([g['linha']] + [m.linha(x) for x in faltantes],
                                         f"RoleMixin Pattern parcial: {', '.join(faltantes)} "
                                         f"especializa(m) '{nome}' fora do genset '{g['nome']}'",
                                         f"dedução: acrescentar {', '.join(faltantes)} em 'specifics'")
                continue

            if len(candidatos) >= 2:
                self._incompleto([c['linha']] + [m.linha(x) for x in candidatos],
                                 f"RoleMixin Pattern incompleto: '{nome}' tem roles "
                                 f"({', '.join(candidatos)}) mas nenhum genset",
                                 "dedução: " + self._tpl_genset('rolemixin', nome, candidatos))
            else:
                roles = m.com_estereotipo('role')
                self._incompleto([c['linha']],
                                 f"RoleMixin Pattern incompleto: '{nome}' não agrupa roles "
                                 f"(o padrão exige ao menos 2 roles de kinds distintos)",
                                 "dedução: " + self._tpl_genset('rolemixin', nome,
                                                                 roles[:2] or ['Role_A', 'Role_B']))

    # Relator
    def padrao_relator(self):
        m = self.m
        mediados = {}
        for nome, c in m.classes.items():
            if c['estereotipo'] != 'relator':
                continue
            meds = m.relacoes(c, 'mediation')
            alvos = [r['destino'] for r in meds]
            unicos = list(dict.fromkeys(alvos))
            mediados[nome] = unicos
            linhas_med = [r.get('linha', c['linha']) for r in meds]

            if len(unicos) < len(alvos):
                self._erro([c['linha']] + linhas_med,
                           f"Relator '{nome}' tem mais de uma mediation para a mesma classe",
                           "mantenha uma única mediation por entidade mediada")

            if len(unicos) < 2:
                livres = [n for n in m.com_estereotipo('role') if n not in unicos]
                sug = ["@mediation [1..*] -- [1..*] " + (unicos[0] if unicos else "<Role_A>"),
                       "@mediation [1..*] -- [1..*] " + (livres[0] if livres else "<Role_B>")]
                self._incompleto([c['linha']] + linhas_med,
                                 f"Relator Pattern incompleto: '{nome}' medeia {len(unicos)} "
                                 f"entidade(s); o padrão exige ao menos 2 roles",
                                 "dedução: " + " / ".join(sug))
                continue

            for r in meds:
                d, ln = r['destino'], r.get('linha', c['linha'])
                if d in m.classes and m.est(d) != 'role':
                    roles = m.filhos_de(d, 'role')
                    dica = (f"mediar o role que especializa '{d}'"
                            + (f" (ex.: {', '.join(roles)})" if roles
                               else " (declare um role que o especialize)"))
                    self._erro([ln], f"mediation de '{nome}' aponta para '{d}' "
                                     f"({m.est(d)}); o Relator Pattern usa roles", dica, 'AVISO')
                for lado, card in (('do relator', r.get('cardinalidade_origem')),
                                   ('de '+d, r.get('cardinalidade_destino'))):
                    lo = limite_inferior(card)
                    if lo is not None and lo < 1:
                        self._erro([ln], f"mediation em '{nome}': cardinalidade {lado} "
                                         f"[{card}] permite 0; mediation exige dependência existencial",
                                   "use [1..*] (ou [1]) nesse lado")

            completo, linhas_pad, materiais = True, [c['linha']] + linhas_med + [m.linha(x) for x in unicos], []
            for i in range(len(unicos)):
                for j in range(i + 1, len(unicos)):
                    a, b = unicos[i], unicos[j]
                    rels = [x for x in m.relacoes_externas
                            if {x['dominio'], x['imagem']} == {a, b}]
                    mat = [x for x in rels if x['estereotipo'] == 'material']
                    if mat:
                        for x in mat:
                            linhas_pad.append(x['linha'])
                            materiais.append(f"{x['dominio']} -- {x['nome_relacao']} -- {x['imagem']}")
                        continue
                    completo = False
                    for x in rels:
                        self._erro([x['linha']],
                                   f"Relação entre '{a}' e '{b}' (mediados por '{nome}') "
                                   f"usa @{x['estereotipo']}; o padrão exige @material",
                                   f"troque '@{x['estereotipo']}' por '@material'")
                    if not rels:
                        self._incompleto(
                            [c['linha']] + linhas_med,
                            f"Relator Pattern incompleto: '{nome}' medeia '{a}' e '{b}' "
                            f"mas falta a relação material entre eles",
                            f"dedução: @material relation {a} [1..*] -- relationName -- [1..*] {b}")
            if completo:
                self._padrao(linhas_pad, "Relator Pattern",
                             f"relator {nome} medeia {', '.join(unicos)}; "
                             f"relação material: {'; '.join(materiais)}")

        for x in m.relacoes_externas:
            if x['estereotipo'] != 'material':
                continue
            d, i = x['dominio'], x['imagem']
            for lado in (d, i):
                if lado in m.classes and m.est(lado) != 'role':
                    self._erro([x['linha']], f"@material liga '{lado}' ({m.est(lado)}); "
                                             f"o Relator Pattern liga roles",
                               f"use o role que especializa '{lado}'", 'AVISO')
            if not any(d in al and i in al for al in mediados.values()):
                self._incompleto(
                    [x['linha']],
                    f"Relator Pattern incompleto: relação @material entre '{d}' e '{i}' "
                    f"sem relator que medeie ambos",
                    f"dedução: relator {d}_{i}_Relator {{ @mediation [1..*] -- [1..*] {d} ; "
                    f"@mediation [1..*] -- [1..*] {i} }}")
    def padrao_mode(self):
        m = self.m
        kinds = m.com_estereotipo('kind')
        dica_alvo = ' | '.join(kinds) if kinds else '<Classe>'
        for nome in m.com_estereotipo('mode'):
            c = m.classes[nome]
            ch = m.relacoes(c, 'characterization')
            ex = m.relacoes(c, 'externalDependence')
            l_ch = [r.get('linha', c['linha']) for r in ch]
            l_ex = [r.get('linha', c['linha']) for r in ex]

            if len(ch) > 1:
                self._erro([c['linha']] + l_ch,
                           f"Mode '{nome}' tem {len(ch)} characterization; "
                           f"um mode inere em exatamente um portador",
                           "mantenha uma única @characterization")

            for r in ch + ex:
                lo_dest = r.get('cardinalidade_destino')
                if lo_dest is not None and str(lo_dest) != '1':
                    self._erro([r.get('linha', c['linha'])],
                               f"@{r['estereotipo']} em '{nome}': cardinalidade [{lo_dest}] "
                               f"no lado de '{r['destino']}'; o padrão usa [1]",
                               "troque a cardinalidade por [1]")

            if ch and ex:
                if {r['destino'] for r in ch} & {r['destino'] for r in ex}:
                    comum = ({r['destino'] for r in ch} & {r['destino'] for r in ex}).pop()
                    self._erro([c['linha']] + l_ch + l_ex,
                               f"Mode '{nome}': portador e dependência externa são a mesma "
                               f"classe ('{comum}')",
                               "externalDependence deve apontar para uma classe diferente do portador")
                self._padrao([c['linha']] + l_ch + l_ex, "Mode Pattern",
                             f"mode {nome}; characterization -> {ch[0]['destino']}; "
                             f"externalDependence -> {', '.join(r['destino'] for r in ex)}")
            elif ch:
                self._incompleto([c['linha']] + l_ch,
                                 f"Mode Pattern incompleto: '{nome}' só tem @characterization "
                                 f"(portador '{ch[0]['destino']}')",
                                 f"dedução: @externalDependence [1..*] -- [1] {dica_alvo}  "
                                 f"(se não há dependência externa, é um intrinsicMode)")
            elif ex:
                self._erro([c['linha']] + l_ex,
                           f"Mode '{nome}' tem @externalDependence mas nenhuma @characterization; "
                           f"todo mode inere em um portador",
                           f"acrescente: @characterization [1..*] -- [1] {dica_alvo}")
            else:
                self._incompleto([c['linha']],
                                 f"Mode Pattern incompleto: '{nome}' não tem relações",
                                 f"dedução: @characterization [1..*] -- [1] {dica_alvo} ; "
                                 f"@externalDependence [1..*] -- [1] {dica_alvo}")
    def imprimir(self, arquivo):
        barra = '=' * 72
        print(barra)
        print(f"ANÁLISE SEMÂNTICA: {arquivo}  (package {self.m.pacote})")
        print(barra)

        print("\n[1] PADRÕES ENCONTRADOS")
        if not self.padroes:
            print("   (nenhum padrão completo reconhecido)")
        for a in self.padroes:
            print(f"   [{a.rotulo_linhas()}] ✔ {a.titulo}")
            print(f"        {a.detalhe}")

        print("\n[2] ERROS E COERÇÃO (correção sugerida)")
        if not self.erros:
            print("   (nenhum erro)")
        for a in self.erros:
            print(f"   [{a.rotulo_linhas()}] {a.sev}: {a.titulo}")
            if a.sugestao:
                print(f"        ↳ coerção: {a.sugestao}")

        print("\n[3] PADRÕES INCOMPLETOS (dedução)")
        if not self.incompletos:
            print("   (nenhum)")
        for a in self.incompletos:
            print(f"   [{a.rotulo_linhas()}] ~ {a.titulo}")
            if a.sugestao:
                print(f"        ↳ {a.sugestao}")

        n_err = sum(1 for a in self.erros if a.sev == 'ERRO')
        n_av = len(self.erros) - n_err
        print(f"\nRESUMO: {len(self.padroes)} padrão(ões) · {n_err} erro(s) · "
              f"{n_av} aviso(s) · {len(self.incompletos)} incompleto(s)\n")
        return n_err


def analisar_semantica(ast):
    return Analisador(ast).executar()


def main(argv):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    if len(argv) < 2:
        print('Uso: python3 semantic.py <arquivo.tonto> [outros.tonto ...]')
        return 1

    from parser import analisar, ErroSintatico   # import tardio: núcleo testável sem PLY

    total_erros = 0
    for caminho in argv[1:]:
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                texto = f.read()
        except OSError as e:
            print(f'Erro ao abrir {caminho}: {e}')
            total_erros += 1
            continue
        try:
            ast = analisar(texto)
        except ErroSintatico:
            print(f'>> {caminho}: erro sintático; análise semântica não executada.\n')
            total_erros += 1
            continue
        total_erros += analisar_semantica(ast).imprimir(caminho)
    return 1 if total_erros else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))


