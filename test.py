import sys
import subprocess
import random
from collections import defaultdict
import string

BASE_VAR = ["VAR1", "VAR2", "VAR3", "VAR4", "VAR5"]
BASE_CONST = ["CONST1", "CONST2", "CONST3", "CONST4", "CONST5"]
BASE_PRED = ["PRED1", "PRED2", "PRED3", "PRED4"]
BASE_EQ = ["EQ"]
BASE_CONN = ["AND", "OR", "IMPLIES", "IFF", "NEG"]
BASE_QUAN = ["EXISTS", "FORALL"]

BASE_FORMULA = [
    ["(", "(", "VAR1", "EQ", "VAR2", ")", "AND", "NEG", "FORALL", "VAR3", "PRED2", "(", "VAR1", ",", "VAR2", ")", ")"],
    "( ( ( ( PRED1 ( VAR1 ) AND PRED1 ( VAR2 ) ) OR PRED2 ( VAR1 , VAR2 ) ) IMPLIES PRED3 ( VAR1 , VAR2 , VAR3 ) ) IFF PRED4 ( VAR1 , VAR2 , VAR3 , VAR4 ) )".split(),

    "EXISTS VAR1 FORALL VAR2 EXISTS VAR3 FORALL VAR4 EXISTS VAR5 ( PRED4 ( VAR1 , VAR2 , VAR3 , VAR4 ) IMPLIES ( CONST1 EQ CONST2 ) )".split(),
    "( ( ( CONST1 EQ CONST2 ) AND ( CONST1 EQ VAR1 ) ) IFF ( ( VAR1 EQ CONST1 ) AND ( VAR1 EQ VAR2 ) ) )".split()
]

def gen_sub(sub=True):
    sub_dict = {'(': '(', ')': ')', ',': ',',
                ' ': ' ', '\t':'\t', '\n':'\n'}
    if not sub:
        for arity, pred in enumerate(BASE_PRED):
            sub_dict[pred] = (pred, f"{pred}[{arity+1}]")
        for symbol in BASE_VAR + BASE_CONST + BASE_EQ + BASE_CONN + BASE_QUAN:
            sub_dict[symbol] = symbol
        return sub_dict

    # Replace with a random id
    ALLOWED_CHARS = string.ascii_letters + string.digits + '_'
    for arity, pred in enumerate(BASE_PRED):
        ran_id = ''.join(random.choices(ALLOWED_CHARS, k=10))
        sub_dict[pred] = (ran_id, f"{ran_id}[{arity+1}]")

    for symbol in BASE_CONN + BASE_QUAN:
        ran_id = ''.join(random.choices(ALLOWED_CHARS+'\\', k=10))
        sub_dict[symbol] = ran_id

    for symbol in BASE_EQ:
        ran_id = ''.join(random.choices(ALLOWED_CHARS+'=', k=10))
        sub_dict[symbol] = ran_id

    for symbol in BASE_VAR + BASE_CONST:
        ran_id = ''.join(random.choices(ALLOWED_CHARS, k=10))
        sub_dict[symbol] = ran_id

    return sub_dict

def write_to_file(formula, sub_dict, ran_order=False, fields=None):
    FIELDS = [("variables", BASE_VAR), ("constants", BASE_CONST), ("predicates", BASE_PRED), ("equality", BASE_EQ), ("connectives", BASE_CONN), ("quantifiers", BASE_QUAN), ("formula", formula)]
    
    if fields:
        FIELDS = [x if x[0] not in fields else (fields[x[0]], x[1]) for x in FIELDS]

    f = open("test.txt", mode='w')
    if ran_order: random.shuffle(FIELDS)
    
    for field in FIELDS:
        if field[0] == "predicates" or (fields and "predicates" in fields and field[0] == fields["predicates"]):
            f.write(f"{field[0]}: {' '.join(sub_dict[x][1] for x in field[1])}\n")
            continue
        if field[0] == "formula" or (fields and "formula" in fields and field[0] == fields["formula"]):
            write_string = f"{field[0]}: "
            for x in field[1]:
                sub = sub_dict[x]
                if type(sub) == tuple:
                    write_string = write_string + sub[0] + ' '
                else:
                    write_string = write_string + sub + ' '
            f.write(write_string + '\n')
            continue
        f.write(f"{field[0]}: {' '.join(sub_dict[x] for x in field[1])}\n")

    f.close()

def call_program(py_path, ex_pass=True):
    print(f"This program should {'PASS' if ex_pass else 'FAIL'}")
    subprocess.run(["python", py_path, "test.txt"])
    print("\n")

def main():
    # Stage 1 - Just try the base
    print("-- STAGE 1: Basic Input --")
    sub_dict = gen_sub(sub=False)
    for formula in BASE_FORMULA:
        write_to_file(formula, sub_dict)
        call_program(sys.argv[1])
    print("\n\n")

    # Stage 2 - Random IDs
    print("-- STAGE 2: Random Symbol Names --")
    STAGE2_IT = 3
    for _ in range(STAGE2_IT):
        sub_dict = gen_sub(sub=True)
        for formula in BASE_FORMULA:
            write_to_file(formula, sub_dict, ran_order=True)
            call_program(sys.argv[1])
    print("\n\n")

    # Stage 3 - Add extra whitespace
    print("-- STAGE 3: Extra Whitespace --")
    STAGE3_IT = 3
    NB_INSERTIONS = 10
    WHITESPACE = [' ', '\t', '\n']
    for _ in range(STAGE3_IT):
        sub_dict = gen_sub(sub=True)
        for formula in BASE_FORMULA:
            n = len(formula)
            insert = random.sample(range(n), NB_INSERTIONS)
            insert_char = [(x, WHITESPACE[random.randint(0, 2)]) for x in insert]

            for i, ic in enumerate(insert_char):
                formula = formula[:ic[0]+i] + [ic[1]] + formula[ic[0]+i:]

            write_to_file(formula, sub_dict, ran_order=True)
            call_program(sys.argv[1])
    print("\n\n")

    # Stage 4 - Remove random parts of the formula 
    # All of these should fail
    print("-- STAGE 4: Randomly remove parts of formula --")
    STAGE4_IT = 5
    NB_DELETIONS = 1
    for _ in range(STAGE4_IT):
        sub_dict = gen_sub(sub=False)
        for formula in BASE_FORMULA:
            n = len(formula)
            delete = random.sample(range(n), NB_DELETIONS)
            delete.sort()

            for i, d in enumerate(delete):
                formula = formula[:d-i] + formula[d-i+1:]

            write_to_file(formula, sub_dict, ran_order=True)
            call_program(sys.argv[1], ex_pass=False)
    print("\n\n")

    # Stage 5 - Add random valid symbols
    print("-- STAGE 5: Add random valid symbols --")
    STAGE5_IT = 5
    NB_INSERTIONS = 1
    # TODO: predicates <07-03-20> #
    INSERTION = BASE_VAR + BASE_CONST + BASE_EQ + BASE_CONN + BASE_QUAN + list('()')
    for _ in range(STAGE5_IT):
        sub_dict = gen_sub(sub=False)
        for formula in BASE_FORMULA:
            n = len(formula)
            insert = random.sample(range(n), NB_INSERTIONS)
            
            insert_char = [(x, INSERTION[random.randint(0, len(INSERTION)-1)]) for x in insert]

            for i, ic in enumerate(insert_char):
                formula = formula[:ic[0]+i] + [ic[1]] + formula[ic[0]+i:]

            write_to_file(formula, sub_dict, ran_order=True)
            call_program(sys.argv[1], ex_pass=False)
    print("\n\n")

    # Stage 6 - Break Grammar Rules
    # invalid field names
    # duplicate field names
    # invalid characters in strings (eg, \ in variables)
    print("-- STAGE 6: Break grammar rules --")
    for formula in BASE_FORMULA:
        FIELD_SUB = [
            {"formula": "form"},
            {"equality": "eq"},
            {"constants": "const"},
            {"quantifiers": "equality"},
            {"predicates": "variables"}
        ]

        print("- Trying Invalid Field Names -")
        for field in FIELD_SUB:
            sub_dict = gen_sub(sub=True)
            write_to_file(formula, sub_dict, fields=field, ran_order=True)
            call_program(sys.argv[1], ex_pass=False)

        print("- Trying Duplicate Field Names -")
        sub_dict = gen_sub(sub=True)
        write_to_file(formula, sub_dict, ran_order=False)
        f = open("test.txt", mode='a')
        f.write("variables: VAR0\n")
        f.close()
        call_program(sys.argv[1], ex_pass=False)

        print("- Trying invalid characters in strings -")
        sub_dict = gen_sub(sub=False)
        sub_dict['VAR1'] = f"\\{sub_dict['VAR1']}"
        write_to_file(formula, sub_dict, ran_order=False)
        call_program(sys.argv[1], ex_pass=False)

        sub_dict = gen_sub(sub=False)
        sub_dict['CONST1'] = f"={sub_dict['CONST1']}"
        write_to_file(formula, sub_dict, ran_order=False)
        call_program(sys.argv[1], ex_pass=False)

        sub_dict = gen_sub(sub=False)
        sub_dict['EXISTS'] = f"={sub_dict['EXISTS']}"
        write_to_file(formula, sub_dict, ran_order=False)
        call_program(sys.argv[1], ex_pass=False)

        sub_dict = gen_sub(sub=False)
        sub_dict['EQ'] = f"\\{sub_dict['EQ']}"
        write_to_file(formula, sub_dict, ran_order=False)
        call_program(sys.argv[1], ex_pass=False)
    print("\n\n")

    # Stage 7 - Targetted Formula Cases
    targetted_formulas = [
        ("VAR1 EQ VAR2".split(), False, "Must be surrounded by brackets"),
        ("NEG ( PRED1 ( VAR1 ) )".split(), False, "Unnessecary Brackets"),
        ("( PRED1 ( VAR1 ) )".split(), False, "Unnessecary Brackets"),
        ("PRED1 ( VAR1 ) AND PRED1 ( VAR2 )".split(), False, "Must be surrounded by brackets"),
        ("( PRED1 ( VAR1 ) AND PRED1 ( VAR2 ) AND PRED1 ( VAR3 ) )".split(), False, "Missing brackets"),
        ("FORALL VAR3 ( PRED2 ( VAR1 , VAR3 ) )".split(), False, "Unnessecary Brackets"),
        ("PRED2 ( CONST1 , CONST2 )".split(), False, "Constants cannot be arguments"),
        ("( VAR1 EQ VAR2 EQ VAR3 )".split(), False, "Missing brackets"),
        ("( ( ( ( ( ( ( ( ( ( CONST1 EQ CONST2 ) ) ) ) ) ) ) ) ) )".split(), False, "Unnessecary brackets")
    ]

    for formula in targetted_formulas:
        sub_dict = gen_sub(sub=False)
        write_to_file(formula[0], sub_dict, ran_order=True)
        call_program(sys.argv[1], ex_pass=formula[1])
        print(f"This test has the following message attached to it:\n{formula[2]}\n")

if __name__ == '__main__':
    main()
