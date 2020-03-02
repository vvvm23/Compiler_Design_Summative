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
        self.symbols = defaultdict(list)
        self.terminal_count = defaultdict(int)
        self.G = nx.DiGraph()

    def print_graph(self):
        plt.title("Parse Tree")
        pos=graphviz_layout(self.G, prog='dot')
        nx.draw(self.G, pos, with_labels=True, arrows=False)
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
        self.terminal_count['formulaR']+=1
        node_id = f"formulaR_{self.terminal_count['formulaR']}"
        self.G.add_node(node_id)
        self.G.add_edge(parent, node_id)
        if self.lookahead in self.symbols['connectives2']:
           code = self.connective2(node_id)
           code = code if code else self.formula(node_id) # If zero check formula, else just skip 
           return code
        else:
            # Not syntax, as can return nothing (e case)
            return 0

    def formula(self, parent):
        self.terminal_count['formula']+=1
        node_id = f"formula_{self.terminal_count['formula']}"
        self.G.add_node(node_id)
        if parent:
            self.G.add_edge(parent, node_id)
        parent = node_id

        if self.lookahead in [x[0] for x in self.symbols['predicates']]:
            node_id = f"predicate_{self.index}"
            self.G.add_node(node_id)
            self.G.add_edge(parent, node_id)
            code = self.predicates(node_id)
            code = code if code else self.formulaR(node_id)
        elif self.lookahead in self.symbols['quantifiers']:
            node_id = f"quantifier_{self.index}"
            self.G.add_node(node_id)
            self.G.add_edge(parent, node_id)
            code = self.quantifier(node_id)
            code = code if code else self.variable(node_id)
            code = code if code else self.formula(node_id)
        elif self.lookahead in self.symbols['connectives1']:
            node_id = f"conn1_{self.index}"
            self.G.add_node(node_id)
            self.G.add_edge(parent, node_id)
            code = self.connective1(node_id)
            code = code if code else self.formula(node_id)
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
                code = 1

            code = code if code else self.equality(parent)

            if not self.variable(parent):
                pass
            elif not self.constant(parent):
                pass
            else:
                # Syntax
                code = 1

            code = code if code else self.match(')')
            self.terminal_count[')']+=1
            node_id = f")_{self.terminal_count[')']}"
            self.G.add_node(node_id)
            self.G.add_edge(parent, node_id)
            code = code if code else self.formulaR(parent)
        else:
            # Syntax Error
            code = 1
        return code
    def variable(self, parent):
        variables = self.symbols['variables']
        for v in variables:
            if self.lookahead == v:
                self.terminal_count[v]+=1
                node_id = f"{v}_{self.terminal_count[v]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                self.match(v)
                return 0
        
        # syntax
        return 1

    def constant(self, parent):
        constants = self.symbols['constants']
        for c in constants:
            if self.lookahead == c:
                self.terminal_count[c]+=1
                node_id = f"{c}_{self.terminal_count[c]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                self.match(c)
                return 0

        # syntax
        return 1
        
    def equality(self, parent):
        equality = self.symbols['equality']
        for e in equality:
            if self.lookahead == e:
                self.terminal_count[e]+=1
                node_id = f"{e}_{self.terminal_count[e]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                self.match(e)
                return 0
        # syntax
        return 1

    def connective2(self, parent):
        connectives2 = self.symbols['connectives2']
        for c in connectives2:
            if self.lookahead == c:
                self.terminal_count[c]+=1
                node_id = f"{c}_{self.terminal_count[c]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                self.match(c)
                return 0
        # syntax
        return 1

    def connective1(self, parent):
        connectives1 = self.symbols['connectives1']
        for c in connectives1:
            if self.lookahead == c:
                self.terminal_count[c]+=1
                node_id = f"{c}_{self.terminal_count[c]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                self.match(c)
                return 0
        # syntax
        return 1

    def quantifier(self, parent):
        quantifiers = self.symbols['quantifiers']
        for q in quantifiers:
            if self.lookahead == q:
                self.terminal_count[q]+=1
                node_id = f"{q}_{self.terminal_count[q]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                self.match(q)
                return 0
        # syntax
        return 1

    def predicates(self, parent):
        predicates = self.symbols['predicates']
        for p in predicates:
            if self.lookahead == p[0]:
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
        return 1

# TODO: reserved words <02-03-20, alex> #
def parse_file(path, parser):
    REQUIRED_FIELDS = set(["variables", "constants", "predicates", "equality", "connectives", "quantifiers", "formula"])
    seen_fields = []

    f = open(path, mode='r')
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

        parser.symbols[current_field] = parser.symbols[current_field] + values

    # Last connective is always negation
    parser.symbols['connectives2'] = parser.symbols['connectives'][:-1]
    parser.symbols['connectives1'] = [parser.symbols['connectives'][-1]]

    pprint(parser.symbols)
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

if __name__ == '__main__':
    # LOG_PATH = "./log.txt"

    if not len(sys.argv) == 2 and not len(sys.argv) == 3:
        print("Invalid arguments!")
        print("python {sys.argv[0]} input_file")
        exit()
    
    parser = PredictiveParser()
    file_path = sys.argv[1]
    if len(sys.argv) == 3:
        import pdb; pdb.set_trace()

    if not parse_file(file_path, parser) == "OK":
        exit()
    print(parser.symbols['formula'])
    if parser.parse(parser.symbols['formula']):
        print("ERROR: Syntax Error")
    else:
        print("Valid input string")
        parser.print_graph()
