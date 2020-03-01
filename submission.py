from pprint import pprint
from collections import defaultdict
import matplotlib.pyplot as plt # For visualising graph
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

    def match(self, c):
        if self.lookahead == c:
            self.index += 1
            self.lookahead = self.string[self.index]
            return "OK"
        return "SYNTAX_ERROR"

    def formulaR(self):
        if self.lookahead in self.symbols['connectives']:
           code = self.connective2()
           code = self.formula()
        else:
            # Not syntax, as can return nothing (e case)
            pass

    def formula(self):
        if self.lookahead in [x[0] for x in self.symbols['predicates']]:
            code = self.predicates()
        elif self.lookahead in self.symbols['quantifiers']:
            code = self.quantifier()
        elif self.lookahead in self.symbols['conn1']:
            code = self.connective1()
        elif self.lookahead == '(':
            # try all possibilities
            self.match('(')
            if self.variable():
                pass
            elif self.constant():
                pass
            elif self.formula():
                # kill early
                code = self.match(')')
                code = self.formulaR()
            else:
                # Syntax
                pass

            code = self.equality()

            if self.variable():
                pass
            elif self.constant():
                pass
            else:
                # Syntax
                pass

            code = self.match(')')
            code = self.formulaR()

        else:
            # Syntax Error
            pass
    def variable(self):
        variables = self.symbols['variables']
        for v in variables:
            if self.lookahead == v:
                code = self.match(v)
                return 0
        
        # syntax
        return 1

    def constant(self):
        constants = self.symbols['constants']
        for c in constants:
            if self.lookahead == c:
                code = self.match(c)
                return 0

        # syntax
        return 1
        
    def equality(self):
        equalities = self.symbols['equalities']
        for e in equalities:
            if self.lookahead == e:
                code = self.match(e)
                return 0
        # syntax
        return 1

    def connective2(self):
        connectives2 = self.symbols['connectives2']
        for c in connectives2:
            if self.lookahead == c:
                code = self.match(c)
                return 0
        # syntax
        return 1

    def connective1(self):
        connectives1 = self.symbols['connectives1']
        for c in connectives1:
            if self.lookahead == c:
                code = self.match(c)
                return 0
        # syntax
        return 1

    def quantifier(self):
        quantifiers = self.symbols['quantifiers']
        for q in quantifiers:
            if self.lookahead == q:
                code = self.match(q)
                return 0
        # syntax
        return 1

    def predicates(self):
        predicates = self.symbols['predicates']
        for p in predicates:
            if self.lookahead == p[0]:
                code = self.match(p[0])
                code = self.match('(')
                for i in range(p[1]-1):
                    code = self.variable()
                    code = self.match(',')
                code = self.variable()
                code = self.match(')')
                return 0
        # syntax
        return 1


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
        else:
            values = l.split()

        if current_field == "formula":
            split_values = []
            for v in values:
                split = [x for x in re.split(r"(\W)", v) if not x == ''] 
                split_values = split_values + split
            values = split_values

        if current_field == "predicates":
            predicate_pairs = []
            for p in values:
                predicate_pairs.append((p[:p.find('[')], int(p[p.find('[') + 1:p.find(']')])))
            values = predicate_pairs

        parser.symbols[current_field] = parser.symbols[current_field] + values

    pprint(parser.symbols)
    f.close()

if __name__ == '__main__':
    LOG_PATH = "./log.txt"

    if not len(sys.argv) == 2:
        print("Invalid arguments!")
        print("python {sys.argv[0]} input_file")
        exit()
    
    parser = PredictiveParser()
    file_path = sys.argv[1]
    parse_file(file_path, parser)
