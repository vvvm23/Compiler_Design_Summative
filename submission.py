from pprint import pprint
from collections import defaultdict
import matplotlib.pyplot as plt # For visualising graph
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import sys 
import re

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

    form -> pred | ( var eq var ) | ( var eq const ) | ( const eq var ) | ( const eq const ) | ( form conn2 form ) | quan var form | conn1 form
'''

# Predictive Parser Class
class PredictiveParser:
    def __init__(self):
        self.lookahead = None
        self.string = None
        self.index = 0
        self.syntax_code = "OK" # Default syntax code is "OK"!
        self.error_list = []
        self.symbols = defaultdict(list) # Dictionary containing information on symbols
        # TODO: misleading name. <02-03-20, alex> #
        self.symbol_count = defaultdict(int) # Counts how many times a symbol appears in order to give unique label in graph
        self.G = nx.DiGraph() # Parse tree for displaying later

    # Simply updates the syntax error code
    def throw_syntax_error(self, code):
        if self.syntax_code == "OK":
            self.syntax_code = code

    # Prints the parse tree using networkx and matplotlib
    def print_graph(self):
        pos=graphviz_layout(self.G, prog='dot') # defined position of nodes in G
        # Draw the graph with transparent nodes and reduced font size
        plt.figure(1, figsize=(12,12))
        plt.title(' '.join(self.symbols['formula'])) # Display the input formula
        nx.draw(self.G, pos, with_labels=True, arrows=False, node_color=[[0.0,0.0,0.0,0.0]], font_size=8)
        plt.savefig("tree.png")
        # plt.show(block=1)

    # start function to begin parsing token stream from
    def parse(self, string):
        self.string = string 
        self.index = 0 
        self.lookahead = string[0] # Set the initial lookahead
        code = self.formula(None)
        if not self.index == len(self.string) - 1:
            code = 1
            self.throw_syntax_error("EX_END")
        return code

    # Match c with the current lookahead
    def match(self, c):
        if self.lookahead == c:
            self.index += 1
            if self.index < len(self.string): # Get next lookahead if available
                self.lookahead = self.string[self.index]
            else:
                # TODO: is this correct? <03-03-20, alex> #
                self.lookahead = "" 
                self.string.append("")
            return 0
        return 1 

    # function to resolve form production rule.
    # also the start symbol
    # form -> many
    def formula(self, parent):
        # Create formula node in graph
        self.symbol_count['form']+=1
        node_id = f"form_{self.symbol_count['form']}"
        self.G.add_node(node_id)
        if parent: # If it has a parent add an edge to it
            self.G.add_edge(parent, node_id)
        parent = node_id
        
        # Check if lookahead is a recognised symbol
        if not self.lookahead in self.symbols['all']:
            self.throw_syntax_error("UNKNOWN_SYMBOL")
            code = 1
        # Check if lookahead is a predicate
        elif self.lookahead in [x[0] for x in self.symbols['predicates']]:
            # form -> pred
            code = self.predicates(parent)
        # Check if lookahead is a quantifier
        elif self.lookahead in self.symbols['quantifiers']:
            # form -> quan var form
            code = self.quantifier(parent)
            code = code if code else self.variable(parent)
            if code: self.throw_syntax_error("EX_VAR")
            code = code if code else self.formula(parent)
        # Check if lookahead is in connectives with arity 1
        elif self.lookahead in self.symbols['connectives1']:
            # form -> conn1 form
            code = self.connective1(parent)
            code = code if code else self.formula(parent)
        # Check if lookahead opens a bracketed statement
        elif self.lookahead == '(':
            # try all possibilities
            # not expensive to do as only formula recurses
            code = self.match('(')
            
            # Add a bracket node to the graph
            self.symbol_count['(']+=1
            node_id = f"(_{self.symbol_count['(']}"
            self.G.add_node(node_id)
            self.G.add_edge(parent, node_id)
            
            # Check if lookahead is either variable, constant (continue) or formula (kill early)
            if not self.variable(parent):
                pass
            elif not self.constant(parent):
                pass
            # form -> ( form conn2 form )
            elif not self.formula(parent):
                code = code if code else self.connective2(parent)
                if code: self.throw_syntax_error("EX_CONN2")
                code = code if code else self.formula(parent)
                code = code if code else self.match(')')
                if code: self.throw_syntax_error("EX_BRACKET")
                self.symbol_count[')'] += 1
                node_id = f")_{self.symbol_count[')']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                return code
            else:
                # Syntax Error
                code = 1
                self.throw_syntax_error("UNEX_SYMBOL")

            code = code if code else self.equality(parent)
            if code: self.throw_syntax_error("EX_EQ")

            # Check if either variable or constant 
            # form -> ( var|const eq var )
            if not self.variable(parent):
                pass
            # form -> ( var|cnst eq const )
            elif not self.constant(parent):
                pass
            else:
                # Syntax Error
                self.throw_syntax_error("UNEX_SYMBOL")
                code = 1

            code = code if code else self.match(')')
            if code: self.throw_syntax_error("EX_BRACKET")

            # Add closing bracket node
            self.symbol_count[')']+=1
            node_id = f")_{self.symbol_count[')']}"
            self.G.add_node(node_id)
            self.G.add_edge(parent, node_id)

        else:
            # Syntax Error
            self.throw_syntax_error("UNEX_SYMBOL")
            code = 1
        return code

    # var -> x_1 | ... | x_n
    def variable(self, parent):
        # Check if the lookahead symbol is known
        if not self.lookahead in self.symbols['all']:
            self.throw_syntax_error("UNKNOWN_SYMBOL")
            return 1
        variables = self.symbols['variables']
        # TODO: this and similar could probably be made without for loop <02-03-20, alex> #
        for v in variables:
            if self.lookahead == v:
                # If the lookahead matches a variable create variable node
                self.symbol_count['var']+=1
                node_id = f"var_{self.symbol_count['var']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                parent = node_id

                # Create terminal node
                self.symbol_count[v]+=1
                node_id = f"{v}_{self.symbol_count[v]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                self.match(v)
                return 0
        
        # syntax error
        return 1

    # const -> C_1 | ... | C_n
    def constant(self, parent):
        # Check if the lookahead symbol is known
        if not self.lookahead in self.symbols['all']:
            self.throw_syntax_error("UNKNOWN_SYMBOL")
            return 1
        constants = self.symbols['constants']
        for c in constants:
            if self.lookahead == c:
                # If the lookahead matches a constant create const node
                self.symbol_count['const']+=1
                node_id = f"const_{self.symbol_count['const']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                parent = node_id

                # Create terminal node
                self.symbol_count[c]+=1
                node_id = f"{c}_{self.symbol_count[c]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                self.match(c)
                return 0

        # syntax error
        return 1
    
    # eq (EG) -> =
    def equality(self, parent):
        # Check if the lookahead symbol is known
        if not self.lookahead in self.symbols['all']:
            self.throw_syntax_error("UNKNOWN_SYMBOL")
            return 1
        equality = self.symbols['equality']
        for e in equality:
            if self.lookahead == e:
                # If the lookahead matches an equality node create a eq node
                self.symbol_count['eq']+=1
                node_id = f"eq_{self.symbol_count['eq']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                parent = node_id

                # Create terminal node
                self.symbol_count[e]+=1
                node_id = f"{e}_{self.symbol_count[e]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                self.match(e)
                return 0
        # syntax error
        return 1

    # form (EG) -> OR | AND | ... 
    def connective2(self, parent):
        # Check if the lookahead symbol is known
        if not self.lookahead in self.symbols['all']:
            self.throw_syntax_error("UNKNOWN_SYMBOL")
            return 1
        connectives2 = self.symbols['connectives2']
        for c in connectives2:
            if self.lookahead == c:
                # If the lookahead matches a connective2 create conn2 node
                self.symbol_count['conn2']+=1
                node_id = f"conn2_{self.symbol_count['conn2']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                parent = node_id

                # Create a terminal node
                self.symbol_count[c]+=1
                node_id = f"{c}_{self.symbol_count[c]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                self.match(c)
                return 0
        # syntax error
        return 1
    
    # conn1 (EG) -> NEG
    def connective1(self, parent):
        # Check if the lookahead symbol is known
        if not self.lookahead in self.symbols['all']:
            self.throw_syntax_error("UNKNOWN_SYMBOL")
            return 1
        connectives1 = self.symbols['connectives1']
        for c in connectives1:
            if self.lookahead == c:
                # If the lookahead matches a connective1 create a conn1 node
                self.symbol_count['conn1']+=1
                node_id = f"conn1_{self.symbol_count['conn1']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                parent = node_id

                # Create terminal node
                self.symbol_count[c]+=1
                node_id = f"{c}_{self.symbol_count[c]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                self.match(c)
                return 0
        # syntax
        return 1

    # quan (EG) -> EXISTS | FORALL
    def quantifier(self, parent):
        # Check if the lookahead symbol is known
        if not self.lookahead in self.symbols['all']:
            self.throw_syntax_error("UNKNOWN_SYMBOL")
            return 1
        quantifiers = self.symbols['quantifiers']
        for q in quantifiers:
            if self.lookahead == q:
                # If the lookahead matches a quantifier create a quan node
                self.symbol_count['quan']+=1
                node_id = f"quan_{self.symbol_count['quan']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                parent = node_id

                # Create a terminal node
                self.symbol_count[q]+=1
                node_id = f"{q}_{self.symbol_count[q]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                self.match(q)
                return 0
        # syntax
        return 1

    # pred -> P ( var, ..., var ) | ...
    def predicates(self, parent):
        # Check if the lookahead symbol is known
        if not self.lookahead in self.symbols['all']:
            self.throw_syntax_error("UNKNOWN_SYMBOL")
            return 1
        predicates = self.symbols['predicates']
        for p in predicates:
            if self.lookahead == p[0]:
                # If the lookahead matches a predicate identifier create a pred node
                self.symbol_count['pred']+=1
                node_id = f"pred_{self.symbol_count['pred']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)
                parent = node_id

                # Add the pred identifier as a terminal node
                code = self.match(p[0])
                self.symbol_count[p[0]]+=1
                node_id = f"{p[0]}_{self.symbol_count[p[0]]}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)

                # If the next lookahead matches (, create a new node
                code = code if code else self.match('(')
                if code: self.throw_syntax_error("EX_BRACKET")
                self.symbol_count['(']+=1
                node_id = f"(_{self.symbol_count['(']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)

                # Check if the arity of the predicate is correct and contains only variables
                # Create new nodes as we go
                for i in range(p[1]-1):
                    code = code if code else self.variable(parent)
                    if code: self.throw_syntax_error("EX_VAR")
                    code = code if code else self.match(',')
                    if code: self.throw_syntax_error("EX_COMMA")
                    self.symbol_count[',']+=1
                    node_id = f",_{self.symbol_count[',']}"
                    self.G.add_node(node_id)
                    self.G.add_edge(parent, node_id)
                # Final variable
                code = code if code else self.variable(parent)
                if code: self.throw_syntax_error("EX_VAR")
                code = code if code else self.match(')')
                if code: self.throw_syntax_error("EX_BRACKET")
                self.symbol_count[')']+=1
                node_id = f")_{self.symbol_count[')']}"
                self.G.add_node(node_id)
                self.G.add_edge(parent, node_id)

                return code
        # syntax error
        return 1

# function to parse file and check if its contents are valid
def parse_file(path, parser):
    # ensure file contains all required fields
    REQUIRED_FIELDS = set(["variables", "constants", "predicates", "equality", "connectives", "quantifiers", "formula"])
    seen_fields = []

    # populate the symbols with some symbols that are always present
    parser.symbols['all'] = [',', '(', ')']
    FORBIDDEN_SUBSTRINGS = [',', '(', ')', ':']

    # Try to open the file
    try:
        f = open(path, mode='r')
    except Exception as e:
        print("ERROR: Failed to open file!")
        return "FAIL"
    file_lines = f.readlines()
    f.close()

    current_field = None
    for l in file_lines: # Iterate through the lines in the file
        # Get field name if possible
        z = re.match(r"(.*):", l)
        if z:
            current_field = z.groups()[0]
            values = l.split()[1:]
            seen_fields.append(current_field)
        else:
            values = l.split() # continuing from a previous line 

        # If the current field is a formula, deal with the special case
        if current_field == "formula":
            split_values = []
            for v in values:
                # Add to first [] to add additional 'inner word' characters
                # Second is special single characters
                # Third is groups of special characters
                split = [x for x in re.findall(r"[\w\\]+|[,()]|[=]*", v) if not x == ''] 
                split_values = split_values + split # rebuild values
            values = split_values

        if not current_field in ["formula", "predicates"] and True in [x in parser.symbols['all'] for x in values]:
            print("ERROR: Reserved keyword or conflicting token detected in input file!")
            return "FAIL"

        # if the current field is a predicate, deal with the special case
        if current_field == "predicates":
            predicate_pairs = []
            for p in values:
                # Build pairs of (id, arity)
                if p[0] in parser.symbols['all']:
                    print("ERROR: Reserved keyword or conflicting token detected in input file!")
                    return "FAIL"
                predicate_pairs.append((p[:p.find('[')], int(p[p.find('[') + 1:p.find(']')])))
            values = predicate_pairs
            for v in values:
                check = [fs in v[0] for fs in FORBIDDEN_SUBSTRINGS]
                if True in check:
                    print("ERROR: Forbidden substring was found in a value")
                    return "FAIL"
            if not len(values) == len(set(values)):
                print("ERROR: Duplicate values in same class.")
                return "FAIL"
            parser.symbols['all'] = parser.symbols['all'] + [x[0] for x in values]

        elif not current_field == "formula": # add symbols to all (except for formula)
            # Check if forbidden substrings are in values
            for v in values:
                check = [fs in v for fs in FORBIDDEN_SUBSTRINGS]
                if True in check:
                    print("ERROR: Forbidden substring was found in a value")
                    return "FAIL"
            if not len(values) == len(set(values)):
                print("ERROR: Duplicate values in same class.")
                return "FAIL"
            parser.symbols['all'] = parser.symbols['all'] + values

        # also add symbols to relevant field
        parser.symbols[current_field] = parser.symbols[current_field] + values

    # Last connective is always negation, so seperate connectives out
    parser.symbols['connectives2'] = parser.symbols['connectives'][:-1]
    parser.symbols['connectives1'] = [parser.symbols['connectives'][-1]]

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

# Function to print the production rules based on the seen symbols
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
    print("form -> pred | ( var eq var ) | ( var eq const ) | ( const eq var ) | ( const eq const ) | ( form conn2 form ) | quan var form | conn1 form2")

# Entry point to program
if __name__ == '__main__':
    # Print a helpful message!
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Invalid arguments!")
        print("python {sys.argv[0]} input_file [log_file]")
        exit()
    
    parser = PredictiveParser()
    file_path = sys.argv[1]
    log_path = "log.txt"
    # if log file path is specified, replace default
    if len(sys.argv) == 3:
        log_path = sys.argv[2]

    # Parse the specified file
    if not parse_file(file_path, parser) == "OK":
        exit()

    # Define mappings between error codes and error messages
    ERROR_DICT = defaultdict(lambda: "GENERIC - Generic Syntax Error.")
    ERROR_DICT['UNKNOWN_SYMBOL'] = "UNKNOWN_SYMBOL - Unknown reference to symbol."
    ERROR_DICT['EX_VAR'] = ("EX_VAR - Expected Variable at this Position\n"
                            f"SUGG:\tDid you mean {' or '.join(parser.symbols['variables'])}?")
    ERROR_DICT['EX_CONST'] = ("EX_CONST - Expected Constant at this Position\n"
                              f"SUGG:\tDid you mean {' or '.join(parser.symbols['constants'])}?")
    ERROR_DICT['EX_EQ'] = ("EQ_EQ - Expected Equality Symbol at this Position\n"
                           f"SUGG:\tDid you mean {' or '.join(parser.symbols['equality'])}?")
    ERROR_DICT['EX_CONN2'] = ("EX_CONN2 - Expected Connective with 2-arity at this Position.\n"
                              f"SUGG:\tDid you mean {' or '.join(parser.symbols['connectives2'])}?")
    ERROR_DICT['EX_CONN1'] = ("EX_CONN1 - Expected Connective with 1-arity at this Position\n"
                              f"SUGG:\tDid you mean {' or '.join(parser.symbols['connectives1'])}?")
    ERROR_DICT['EX_QUAN'] = ("EX_QUAN - Expected a Quantifier at this Position.\n"
                             f"SUGG:\tDid you mean {' or '.join(parser.symbols['quantifiers'])}?")
    ERROR_DICT['EX_PRED'] = ("EX_PRED - Expected a Predicate at this Position.\n"
                             f"SUGG:\tDid you mean {' or '.join(x[0] for x in parser.symbols['predicates'])}?")
    ERROR_DICT['EX_BRACKET'] = "EX_BRACKET - Expected a bracket at this Position."
    ERROR_DICT['EX_COMMA'] = "EX_COMMA - Expected a comma at this Position."
    ERROR_DICT['EX_END'] = "EX_END - Expected end of string, but encountered more tokens."
    ERROR_DICT['UNEX_BRACKET'] = "UNEX_BRACKET - Unexpected Bracket at this Position."
    ERROR_DICT['UNEX_COMMA'] = "UNEX_COMMA - Unexpected Comma at this Position."
    ERROR_DICT['UNEX_SYMBOL'] = "UNEX_SYMBOL - This symbol was unexpected at this Position."
    
    # Print the grammar productions
    print("~~ PRODUCTIONS ~~")
    print_productions(parser)
    print("~~~~~~~~~~~~~~~~~\n")

    f = open(log_path, mode='w')
    # Parse the formula
    if parser.parse(parser.symbols['formula']):
        # If a syntax error, provide informtion
        f.write(f"ERROR:\tSyntax Error! Position {parser.index}\n")
        f.write('\t' + ''.join(f">>> {x} <<< " if i == parser.index else f"{x} " for i, x in enumerate(parser.string)) + '\n')
        f.write(f"\t{ERROR_DICT[parser.syntax_code]}\n")
        print(f"ERROR:\tSyntax Error! Position {parser.index}")
        print('\t' + ''.join(f"\33[41m{x} \033[0m" if i == parser.index else f"{x} " for i, x in enumerate(parser.string)))
        print(f"\t{ERROR_DICT[parser.syntax_code]}")
    else:
        # If a valid formula, print out the graph
        print("INFO:\tValid input string. See tree.png for parse tree")
        f.write(f"INFO:\tValid Input String! See tree.png for parse tree\n")
        parser.print_graph()
    f.close()
