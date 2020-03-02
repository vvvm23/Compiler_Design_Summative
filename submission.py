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

    # code 0: match
    # code 1: syntax error
    def parse(self, string):
        self.string = string
        self.index = 0
        self.lookahead = string[0]
        return self.formula()

    def match(self, c):
        if self.lookahead == c:
            self.index += 1
            if self.index < len(self.string):
                self.lookahead = self.string[self.index]
            return 0
        print(f"Failed at {self.index} {self.lookahead}")
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
            code = self.match('(')
            if not self.variable():
                pass
            elif not self.constant():
                pass
            elif not self.formula():
                # kill early
                code = code if code else self.match(')')
                code = code if code else self.formulaR()
                return code
            else:
                # Syntax
                code = 1

            code = code if code else self.equality()

            if not self.variable():
                pass
            elif not self.constant():
                pass
            else:
                # Syntax
                code = 1

            code = code if code else self.match(')')
            code = code if code else self.formulaR()

        else:
            # Syntax Error
            code = 1
        return code
    def variable(self):
        variables = self.symbols['variables']
        for v in variables:
            if self.lookahead == v:
                self.match(v)
                return 0
        
        # syntax
        return 1

    def constant(self):
        constants = self.symbols['constants']
        for c in constants:
            if self.lookahead == c:
                self.match(c)
                return 0

        # syntax
        return 1
        
    def equality(self):
        equality = self.symbols['equality']
        for e in equality:
            if self.lookahead == e:
                self.match(e)
                return 0
        # syntax
        return 1

    def connective2(self):
        connectives2 = self.symbols['connectives2']
        for c in connectives2:
            if self.lookahead == c:
                self.match(c)
                return 0
        # syntax
        return 1

    def connective1(self):
        connectives1 = self.symbols['connectives1']
        for c in connectives1:
            if self.lookahead == c:
                self.match(c)
                return 0
        # syntax
        return 1

    def quantifier(self):
        quantifiers = self.symbols['quantifiers']
        for q in quantifiers:
            if self.lookahead == q:
                self.match(q)
                return 0
        # syntax
        return 1

    def predicates(self):
        predicates = self.symbols['predicates']
        for p in predicates:
            if self.lookahead == p[0]:
                code = self.match(p[0])
                code = code if code else self.match('(')
                for i in range(p[1]-1):
                    code = code if code else self.variable()
                    code = code if code else self.match(',')
                code = code if code else self.variable()
                code = code if code else self.match(')')
                return code
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
                # Add to first [] to add additional 'inner word' characters
                split = [x for x in re.findall(r"[\w\\]+|[,()=]", v) if not x == ''] 
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
    LOG_PATH = "./log.txt"

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
    print(parser.symbols['formula'][40:46])
    if parser.parse(parser.symbols['formula']):
        print("ERROR: Syntax Error")
    else:
        print("Valid input string")
