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

if __name__ == "__main__":
    # TODO: Ask more details on this log file.
    LOG_PATH = "./log.txt"

    if not len(sys.argv) == 2:
        print("Invalid arguments!")
        print("python {sys.argv[0]} input_file")
        exit()

    file_path = sys.argv[1]
    fo_dict = read_file(file_path)

    pprint(fo_dict)
    print_grammar(fo_dict)
