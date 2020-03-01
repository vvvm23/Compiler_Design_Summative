from pprint import pprint
from collections import defaultdict
import matplotlib.pyplot as plt # For visualising graph
import sys 
import re

# TODO: forbid ( form ) only as result (perform simple check at end) <01-03-20, alewx> #
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

    def formula(self):
        if self.lookahead == None:
            pass
        elif self.lookahead == None:
            pass
        elif self.lookahead == None:
            pass
        elif self.lookahead == None:
            pass
        elif self.lookahead == None:
            pass
        else:
            # Syntax Error
            pass
    def variable(self):
        variables = self.symbols['variables']
        for v in variables:
            if self.lookahead == v:
                code = self.match(v)
                break

    def constant(self):
        constants = self.symbols['constants']
        for c in constants:
            if self.lookahead == c:
                code = self.match(c)
                break
        
    def equality(self):
        equalities = self.symbols['equalities']
        for e in equalities:
            if self.lookahead == e:
                code = self.match(e)
                break

    def connective2(self):
        connectives2 = self.symbols['connectives2']
        for c in connectives2:
            if self.lookahead == c:
                code = self.match(c)
                break

    def connective1(self):
        connectives1 = self.symbols['connectives1']
        for c in connectives1:
            if self.lookahead == c:
                code = self.match(c)
                break

    def quantifier(self):
        quantifiers = self.symbols['quantifiers']
        for q in quantifiers:
            if self.lookahead == q:
                code = self.match(q)
                break

    def predicates(self):
        pass

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

        print(current_field)
        print(values)
        

        print()

    f.close()

if __name__ == '__main__':
    LOG_PATH = "./log.txt"

    if not len(sys.argv) == 2:
        print("Invalid arguments!")
        print("python {sys.argv[0]} input_file")
        exit()

    file_path = sys.argv[1]
    parse_file(file_path, None)
