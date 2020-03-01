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

    def parse(self, string):
        self.string = string
        self.index = 0
        self.lookahead = string[0]
        code = self.formula()

    def match(self, c):
        if self.lookahead == c:
            self.index += 1
            self.lookahead = self.string[self.index]
            return 0
        return 1 

    def formulaR(self):
        if self.lookahead in self.symbols['connectives2']:
           code = self.connective2()
           code = code if code else self.formula() # If zero check formula, else just skip 
           return code
        else:
            # Not syntax, as can return nothing (e case)
            return 0

    def formula(self):
        if self.lookahead in [x[0] for x in self.symbols['predicates']]:
            code = self.predicates()
            code = code if code else self.formulaR()
        elif self.lookahead in self.symbols['quantifiers']:
            code = self.quantifier()
            code = code if code else self.variable()
            code = code if code else self.formula()
        elif self.lookahead in self.symbols['connectives1']:
            code = self.connective1()
            code = code if code else self.formula()
        elif self.lookahead == '(':
            # try all possibilities
            self.match('(')
            if not self.variable():
                pass
            elif not self.constant():
                pass
            elif not self.formula():
                # kill early
                code = self.match(')')
                code = self.formulaR()
            else:
                # Syntax
                pass

            code = self.equality()

            if not self.variable():
                pass
            elif not self.constant():
                pass
            else:
                # Syntax
                pass

            code = self.match(')')
            code = self.formulaR()

        else:
            # Syntax Error
            pass
        return code
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
            seen_fields.append(current_field)
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

    # Last connective is always negation
    parser.symbols['connectives2'] = parser.symbols['connectives'][:-1]
    parser.symbols['connectives1'] = parser.symbols['connectives'][-1]

    pprint(parser.symbols)
    f.close()
    if not set(seen_fields) == REQUIRED_FIELDS:
        print("ERROR: Input file was missing fields!")
        return "FAIL"
    return "OK"

if __name__ == '__main__':
    LOG_PATH = "./log.txt"

    if not len(sys.argv) == 2:
        print("Invalid arguments!")
        print("python {sys.argv[0]} input_file")
        exit()
    
    parser = PredictiveParser()
    file_path = sys.argv[1]
    if not parse_file(file_path, parser) == "OK":
        exit()
    parser.parse(parser.symbols['formula'])
