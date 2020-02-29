from pprint import pprint
import matplotlib.pyplot as plt # For visualising graph
import sys 
import re

class PredictiveParser:
    def __init__(self):
        self.lookahead = None

    def formula(self):
        pass
    
    def variable(self):
        pass

    def constant(self):
        pass

    def equality(self):
        pass

    def connective2(self):
        pass

    def connective1(self):
        pass

    def quantifier(self):
        pass

    def predicates(self):
        pass

if __name__ == '__main__':
    LOG_PATH = "./log.txt"

    if not len(sys.argv) == 2:
        print("Invalid arguments!")
        print("python {sys.argv[0]} input_file")
        exit()

    file_path = sys.argv[1]
