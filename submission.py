from pprint import pprint
from collections import defaultdict
import matplotlib.pyplot as plt # For visualising graph
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import sys 
import re

# TODO: forbid ( form ) only as result (perform simple check at end) <01-03-20, alewx> #
# TODO: stretch, fuzzy finder to recommend suggestions  <01-03-20, alex> #
'''
Production Rules:
    var     -> x_1 | ... | x_n

    const   -> c_1 | ... | c_n

    pred    -> P_1 (\\var , ... , \\var ) | ...

    eq      -> =

    conn1   -> \\neg

    conn2   -> \\land | \\lor | \\implies | \\iff

    quan    -> \\exists | \\forall

    form    -> \\pred \\formR | ( \\var == \\var ) \\formR | ( \\var == \\const ) \\formR
            |  ( \\const == \\var ) \\formR | ( \\const == \\const ) \\formR |
            |  \\quan \\var \\form | \\conn1 \\form
            |  ( \\form ) \\formR

    formR   -> \\conn2 \\form || e
'''

class PredictiveParser:
    def __init__(self):
        self.lookahead = None
        self.string = None
        self.index = 0
        self.syntax_code = "OK"
        self.symbols = defaultdict(list)
        self.terminal_count = defaultdict(int)
        self.G = nx.DiGraph()

    def throw_syntax_error(self, code):
        # Change only to first error found
        # if self.syntax_code == "OK":
        self.syntax_code = code

    def print_graph(self):
        plt.title(' '.join(self.symbols['formula']))
        pos=graphviz_layout(self.G, prog='dot')
        nx.draw(self.G, pos, with_labels=True, arrows=False, node_color=[[0.0,0.0,0.0,0.0]], font_size=8)
        plt.show()

    # code 0: match
    # code 1: syntax error
    def parse(self, string):
        self.string = string
        self.index = 0
        self.lookahead = string[0]
        return self.formula(None)

    def match(self, c):
        if self.lookahead == c:
            self.index += 1
            if self.index < len(self.string):
                self.lookahead = self.string[self.index]
            return 0
        return 1 

    def formulaR(self, parent):
        self.terminal_count['formR']+=1
        node_id = f"formR_{self.terminal_count['formR']}"
        self.G.add_node(node_id)
        self.G.add_edge(parent, node_id)
        if self.lookahead in self.symbols['connectives2']:
           code = self.connective2(node_id)
           code = code if code else self.formula(node_id) # If zero check formula, else just skip 
           return code
        else:
            # Not syntax, as can return nothing (e case)
            self.terminal_count['none']+=1
            self.G.add_node(f"none_{self.terminal_count['none']}")
            self.G.add_edge(node_id, f"none_{self.terminal_count['none']}")
            return 0

    def formula(self, parent):
        self.terminal_count['form']+=1
        node_id = f"form_{self.terminal_count['form']}"
        self.G.add_node(node_id)
        if parent:
            self.G.add_edge(parent, node_id)
        parent = node_id
        
        if not self.lookahead in self.symbols['all']:
            code = 1
            self.throw_syntax_error("UNKNOWN_SYMBOL")
        elif self.lookahead in [x[0] for x in self.symbols['predicates']]:
            code = self.predicates(parent)
            code = code if code else self.formulaR(parent)
        elif self.lookahead in self.symbols['quantifiers']:
            code = self.quantifier(parent)
            code = code if code else self.variable(parent)
            code = code if code else self.formula(parent)
        elif self.lookahead in self.symbols['connectives1']:
            code = self.connective1(parent)
            code = code if code else self.formula(parent)
        elif self.lookahead == '(':
            # try all possibilities
            code = self.match('(')
            self.terminal_count['(']+=1
            node_id = f"(_{self.terminal_count['(']}"
            self.G.add_node(node_id)
            self.G.add_edge(parent, node_id)
            if not self.variable(parent):
                pass
            elif not self.constant(parent):
                pass
            elif not self.formula(parent):
                # kill early
                code = code if code else self.match(')')
                self.terminal_count[')']+=1
                node_id = f")_{self.terminal_count[')']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                code = code if code else self.formulaR(parent)
                return code
            else:
                # Syntax
                if self.lookahead in ['(', ')']:
                    self.throw_syntax_error("UNEX_BRACKET")
                elif self.lookahead in [',']:
                    self.throw_syntax_error("UNEX_COMMA")
                else:
                    self.throw_syntax_error("UNEX_SYMBOL")
                code = 1

            code = code if code else self.equality(parent)

            if not self.variable(parent):
                pass
            elif not self.constant(parent):
                pass
            else:
                # Syntax
                if self.lookahead in ['(', ')']:
                    self.throw_syntax_error("UNEX_BRACKET")
                elif self.lookahead in [',']:
                    self.throw_syntax_error("UNEX_COMMA")
                else:
                    self.throw_syntax_error("UNEX_SYMBOL")
                code = 1

            code = code if code else self.match(')')
            self.terminal_count[')']+=1
            node_id = f")_{self.terminal_count[')']}"
            self.G.add_node(node_id)
            self.G.add_edge(parent, node_id)
            code = code if code else self.formulaR(parent)
        else:
            # Syntax Error
            if self.lookahead in ['(', ')']:
                self.throw_syntax_error("UNEX_BRACKET")
            elif self.lookahead in [',']:
                self.throw_syntax_error("UNEX_COMMA")
            else:
                self.throw_syntax_error("UNEX_SYMBOL")
            code = 1
        return code
    def variable(self, parent):
        if not self.lookahead in self.symbols['all']:
            self.throw_syntax_error("UNKNOWN_SYMBOL")
            return 1
        variables = self.symbols['variables']
        for v in variables:
            if self.lookahead == v:
                self.terminal_count['var']+=1
                node_id = f"var_{self.terminal_count['var']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                parent = node_id

                self.terminal_count[v]+=1
                node_id = f"{v}_{self.terminal_count[v]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                self.match(v)
                return 0
        
        # syntax
        self.throw_syntax_error("EX_VAR")
        return 1

    def constant(self, parent):
        if not self.lookahead in self.symbols['all']:
            self.throw_syntax_error("UNKNOWN_SYMBOL")
            return 1
        constants = self.symbols['constants']
        for c in constants:
            if self.lookahead == c:
                self.terminal_count['const']+=1
                node_id = f"const_{self.terminal_count['const']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                parent = node_id

                self.terminal_count[c]+=1
                node_id = f"{c}_{self.terminal_count[c]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                self.match(c)
                return 0

        # syntax
        self.throw_syntax_error("EX_CONST")
        return 1
        
    def equality(self, parent):
        if not self.lookahead in self.symbols['all']:
            self.throw_syntax_error("UNKNOWN_SYMBOL")
            return 1
        equality = self.symbols['equality']
        for e in equality:
            if self.lookahead == e:
                self.terminal_count['eq']+=1
                node_id = f"eq_{self.terminal_count['eq']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                parent = node_id

                self.terminal_count[e]+=1
                node_id = f"{e}_{self.terminal_count[e]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                self.match(e)
                return 0
        # syntax
        self.throw_syntax_error("EX_EQ")
        return 1

    def connective2(self, parent):
        if not self.lookahead in self.symbols['all']:
            self.throw_syntax_error("UNKNOWN_SYMBOL")
            return 1
        connectives2 = self.symbols['connectives2']
        for c in connectives2:
            if self.lookahead == c:
                self.terminal_count['conn2']+=1
                node_id = f"conn2_{self.terminal_count['conn2']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                parent = node_id

                self.terminal_count[c]+=1
                node_id = f"{c}_{self.terminal_count[c]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                self.match(c)
                return 0
        # syntax
        self.throw_syntax_error("EX_CONN2")
        return 1

    def connective1(self, parent):
        if not self.lookahead in self.symbols['all']:
            self.throw_syntax_error("UNKNOWN_SYMBOL")
            return 1
        connectives1 = self.symbols['connectives1']
        for c in connectives1:
            if self.lookahead == c:
                self.terminal_count['conn1']+=1
                node_id = f"conn1_{self.terminal_count['conn1']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                parent = node_id

                self.terminal_count[c]+=1
                node_id = f"{c}_{self.terminal_count[c]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                self.match(c)
                return 0
        # syntax
        self.throw_syntax_error("EX_CONN1")
        return 1

    def quantifier(self, parent):
        if not self.lookahead in self.symbols['all']:
            self.throw_syntax_error("UNKNOWN_SYMBOL")
            return 1
        quantifiers = self.symbols['quantifiers']
        for q in quantifiers:
            if self.lookahead == q:
                self.terminal_count['quan']+=1
                node_id = f"quan_{self.terminal_count['quan']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                parent = node_id

                self.terminal_count[q]+=1
                node_id = f"{q}_{self.terminal_count[q]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                self.match(q)
                return 0
        # syntax
        self.throw_syntax_error("EX_QUAN")
        return 1

    def predicates(self, parent):
        if not self.lookahead in self.symbols['all']:
            self.throw_syntax_error("UNKNOWN_SYMBOL")
            return 1
        predicates = self.symbols['predicates']
        for p in predicates:
            if self.lookahead == p[0]:
                self.terminal_count['pred']+=1
                node_id = f"pred_{self.terminal_count['pred']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                parent = node_id

                code = self.match(p[0])
                self.terminal_count[p[0]]+=1
                node_id = f"{p[0]}_{self.terminal_count[p[0]]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)

                code = code if code else self.match('(')
                self.terminal_count['(']+=1
                node_id = f"(_{self.terminal_count['(']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)

                for i in range(p[1]-1):
                    code = code if code else self.variable(parent)
                    code = code if code else self.match(',')
                    self.terminal_count[',']+=1
                    node_id = f",_{self.terminal_count[',']}"
                    self.G.add_node(node_id)
                    self.G.add_edge(parent, node_id) # hmm
                code = code if code else self.variable(parent)
                code = code if code else self.match(')')
                self.terminal_count[')']+=1
                node_id = f")_{self.terminal_count[')']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                return code
        # syntax
        self.throw_syntax_error("EX_PRED")
        return 1

# TODO: reserved words <02-03-20, alex> #
def parse_file(path, parser):
    REQUIRED_FIELDS = set(["variables", "constants", "predicates", "equality", "connectives", "quantifiers", "formula"])
    seen_fields = []

    parser.symbols['all'] = [',', '(', ')']
    try:
        f = open(path, mode='r')
    except Exception as e:
        print("ERROR: Failed to open file!")
        return "FAIL"
    file_lines = f.readlines()

    current_field = None
    for l in file_lines:
        # Get field name if possible
        z = re.match(r"(.*):", l)
        if z:
            current_field = z.groups()[0]
            values = l.split()[1:]
            seen_fields.append(current_field)
        else:
            values = l.split()

        if current_field == "formula":
            split_values = []
            for v in values:
                # Add to first [] to add additional 'inner word' characters
                # TODO: does this generalise? <02-03-20,alex> #
                split = [x for x in re.findall(r"[\w\\]+|[,()]|[=]*", v) if not x == ''] 
                split_values = split_values + split
            values = split_values

        if current_field == "predicates":
            predicate_pairs = []
            for p in values:
                predicate_pairs.append((p[:p.find('[')], int(p[p.find('[') + 1:p.find(']')])))
            values = predicate_pairs
        if current_field == "predicates":
            parser.symbols['all'] = parser.symbols['all'] + [x[0] for x in values]

        elif not current_field == "formula":
            parser.symbols['all'] = parser.symbols['all'] + values
        parser.symbols[current_field] = parser.symbols[current_field] + values

    # Last connective is always negation
    parser.symbols['connectives2'] = parser.symbols['connectives'][:-1]
    parser.symbols['connectives1'] = [parser.symbols['connectives'][-1]]

    f.close()
    if not set(seen_fields) == REQUIRED_FIELDS:
        print("ERROR: Input file was missing fields!")
        return "FAIL"
    if not len(parser.symbols['connectives']) == 5:
        print("ERROR: Input file was missing some connectives")
        return "FAIL"
    if not len(parser.symbols['quantifiers']) == 2:
        print("ERROR: Input file was missing some quantifiers")
        return "FAIL"
    if not len(parser.symbols['equality']) == 1:
        print("ERROR: Input file was missing some equalities")
        return "FAIL"
    return "OK"

def print_productions(parser):
    print("var -> " + ' | '.join(parser.symbols['variables']))
    print("const -> " + ' | '.join(parser.symbols['constants']))
    print("eq -> " + ' | '.join(parser.symbols['equality']))
    print("conn1 -> " + ' | '.join(parser.symbols['connectives1']))
    print("conn2 -> " + ' | '.join(parser.symbols['connectives2']))
    print("quan -> " + ' | '.join(parser.symbols['quantifiers']))
    print("pred -> " + ' | '.join(
        x[0] + ' ( ' + 'var , ' * (x[1]-1) + 'var )'
        for x in parser.symbols['predicates']
    ))
    print("formR -> conn2 form | e")
    print("form -> pred formR | ( var eq var ) formR | ( var eq const ) formR | ( const eq var ) formR | ( const eq const ) formR | quan var form | conn1 form | ( form ) formR ")

if __name__ == '__main__':
    if not len(sys.argv) == 2 and not len(sys.argv) == 3:
        print("Invalid arguments!")
        print("python {sys.argv[0]} input_file")
        exit()
    
    parser = PredictiveParser()
    file_path = sys.argv[1]
    if len(sys.argv) == 3:
        import pdb; pdb.set_trace()

    ERROR_DICT = defaultdict(lambda: "GENERIC - Generic Syntax Error.")
    ERROR_DICT['UNKNOWN_SYMBOL'] = "UNKNOWN_SYMBOL - Unknown reference to symbol."
    ERROR_DICT['EX_VAR'] = "EX_VAR - Expected Variable at this Position"
    ERROR_DICT['EX_CONST'] = "EX_CONST - Expected Constant at this Position"
    ERROR_DICT['EX_EQ'] = "EQ_EQ - Expected Equality Symbol at this Position"
    ERROR_DICT['EX_CONN2'] = "EX_CONN2 - Expected Connective with 2-arity at this Position."
    ERROR_DICT['EX_CONN1'] = "EX_CONN1 - Expected Connective with 1-arity at this Position"
    ERROR_DICT['EX_QUAN'] = "EX_QUAN - Expected a Quantifier at this Position."
    ERROR_DICT['EX_PRED'] = "EX_PRED - Expected a Predicate at this Position."
    ERROR_DICT['UNEX_BRACKET'] = "UNEX_BRACKET - Unexpected Bracket at this Position."
    ERROR_DICT['UNEX_COMMA'] = "UNEX_COMMA - Unexpected Comma at this Position."
    ERROR_DICT['UNEX_SYMBOL'] = "UNEX_SYMBOL - This symbol was unexpected at this Position."

    if not parse_file(file_path, parser) == "OK":
        exit()
    print("~~ PRODUCTIONS ~~")
    print_productions(parser)
    print("~~~~~~~~~~~~~~~~~\n")

    if parser.parse(parser.symbols['formula']):
        print(f"ERROR:\tSyntax Error! Position {parser.index}")
        print('\t' + ''.join(f"\33[41m{x} \033[0m" if i == parser.index else f"{x} " for i, x in enumerate(parser.string)))
        print(f"\t{ERROR_DICT[parser.syntax_code]}")

    else:
        print("Valid input string")
        parser.print_graph()
