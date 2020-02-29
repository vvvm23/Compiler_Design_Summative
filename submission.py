from pprint import pprint
from collections import defaultdict
import matplotlib.pyplot as plt # For visualising graph
import sys 
import re

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

if __name__ == '__main__':
    LOG_PATH = "./log.txt"

    if not len(sys.argv) == 2:
        print("Invalid arguments!")
        print("python {sys.argv[0]} input_file")
        exit()

    file_path = sys.argv[1]
