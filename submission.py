from collections import defaultdict
from pprint import pprint
import matplotlib.pyplot as plt # For visualising graph
import sys 

'''
    Inputs:
        path: Path to file containg sets and the formula
    Outputs:
        file_dict: Dictionary containing all input sets and the formula
'''
# TODO: Allow splitting by other whitespace types. For now space is fine
# TODO: Allow splitting when no whitespace is present (eg. X\land\neg Y)
# TODO: Split connectives into unary and binary
def read_file(path):
    REQUIRED_FIELDS = set(["variables", "constants", "predicates", "equality", "connectives", "quantifiers", "formula"])
    seen_fields = []
    file_dict = defaultdict(list)

    f = open(path, mode='r')
    f_lines = f.readlines()

    c_field = None
    for l in f_lines:
        colon_split = l.split(':')
        if len(colon_split) > 1:
            c_field = colon_split[0]
            seen_fields.append(c_field)
            colon_split = colon_split[1:]

        space_split = colon_split[0].split(' ')
        space_split = [x.replace('\n', '') for x in space_split if not x == '']
   
        # If a predicate, split into symbol-arity pair
        if c_field == 'predicates':
            file_dict[c_field] = file_dict[c_field] + [(x[:x.find("[")], int(x[x.find("[") + 1:x.find("]")])) for x in space_split]
            continue

        file_dict[c_field] = file_dict[c_field] + space_split

    f.close()
    
    if not set(seen_fields) == REQUIRED_FIELDS:
        print("File did not contain all fields. Terminating..")
        exit()
    return file_dict

class Node:
    def __init__(self, name):
        self.productions = []
        self.name = name
    def add_production(self, production):
        self.productions.append(production)
    def __str__(self):
        return self.name

def fo_to_nodes(fo_dict):
    nodes = {}
    # Connectives
    nodes['conn1'] = Node('conn1')
    nodes['conn2'] = Node('conn2')
    for conn in fo_dict['connectives']:
        if conn == "\\neg":
            nodes['conn1'].add_production(['\\neg'])
            continue
        nodes['conn2'].add_production([conn])

    # Constants
    nodes['const'] = Node('const')
    for const in fo_dict['constants']:
        nodes['const'].add_production([const])
    
    # Equality
    nodes['eq'] = Node('eq')
    for eq in fo_dict['equality']:
        nodes['eq'].add_production([eq])

    # Variables
    nodes['var'] = Node('var')
    for var in fo_dict['variables']:
        nodes['var'].add_production([var])

    # Quantifiers
    nodes['quan'] = Node('quan')
    for quan in fo_dict['quantifiers']:
        nodes['quan'].add_production([quan])

    # Predicates
    nodes['pred'] = Node('pred')
    for pred in fo_dict['predicates']:
        nodes['pred'].add_production([pred[0], '('] + ([nodes['var'], ',']*pred[1])[:-1] + [')'])

    # Formula
    nodes['form'] = Node('form')
    nodes['form'].add_production([nodes['form'], nodes['conn2'], nodes['form']])
    nodes['form'].add_production([nodes['conn1'], nodes['form']])
    nodes['form'].add_production([nodes['quan'], nodes['var'], nodes['form']])
    nodes['form'].add_production([nodes['const'], nodes['eq'], nodes['const']])
    nodes['form'].add_production([nodes['const'], nodes['eq'], nodes['var']])
    nodes['form'].add_production([nodes['var'], nodes['eq'], nodes['const']])
    nodes['form'].add_production([nodes['var'], nodes['eq'], nodes['var']])
    nodes['form'].add_production([nodes['pred']])
    nodes['form'].add_production([])

    for prod in nodes['form'].productions:
        print(' '.join(str(x) for x in prod))

# TODO: Convert some symbols to escaped versions
def print_grammar(fo_dict):
    productions = []
    non_terminals = []
    terminals = []

    non_terminals.append("form") # Starting symbol
    terminals += [',', '(', ')', '\\e'] # Terminals that are always present (Add \\ ?)

    # TODO: Check for empty fo_dict fields
    # First, generate rules for variables
    productions.append(
                f"var -> {' | '.join(fo_dict['variables'])}"
            )
    non_terminals.append("var")
    terminals += fo_dict['variables']

    # Constants
    productions.append(
                f"const -> {' | '.join(fo_dict['constants'])}"
            )
    non_terminals.append("const")
    terminals += fo_dict['constants'] 

    # Predicates
    productions.append(
            "pred -> " + ' | '.join(x[0] + ' ( ' + ('var , '*int(x[1]))[:-2] + ')' for x in fo_dict['predicates'])
            )
    non_terminals.append("pred")
    terminals += [x[0] for x in fo_dict['predicates']]

    # Equality
    productions.append(
                f"eq -> {' | '.join(fo_dict['equality'])}"
            )
    non_terminals.append("eq")
    terminals += fo_dict['equality']

    # Connectives 
    if '\\neg' in fo_dict['connectives']:
        productions.append(
                f"conn1 -> \\neg"    
            )
        non_terminals.append("conn1")

    productions.append(
                "conn2 -> " + ' | '.join(x for x in fo_dict['connectives'] if not x == '\\neg')
            )
    non_terminals.append("conn2")
    terminals += fo_dict['connectives']

    # Quantifiers
    productions.append(
                f"quan -> {' | '.join(fo_dict['quantifiers'])}"
            )
    non_terminals.append("quan")
    terminals += fo_dict['quantifiers']

    # Now, add productions for formula (form)
    productions.append(
                (
                    "form -> form conn2 form "
                    "| conn1 form "
                    "| quan var form "
                    "| const eq const | const eq var "
                    "| var eq const | var eq var "
                    "| pred "
                    "| \\e"
                )
            )

    pprint(non_terminals)
    pprint(terminals)
    pprint(productions)

def parse():
    pass

if __name__ == "__main__":
    # TODO: Ask more details on this log file.
    LOG_PATH = "./log.txt"

    if not len(sys.argv) == 2:
        print("Invalid arguments!")
        print("python {sys.argv[0]} input_file")
        exit()

    file_path = sys.argv[1]
    fo_dict = read_file(file_path)
    fo_to_nodes(fo_dict)
