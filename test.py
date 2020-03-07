import sys
import subprocess
import random
from collections import defaultdict
import string

BASE_VAR = ["VAR1", "VAR2", "VAR3", "VAR4", "VAR5"]
BASE_CONST = ["CONST1", "CONST2", "CONST3", "CONST4", "CONST5"]
BASE_PRED = ["PRED1", "PRED2", "PRED3"]
BASE_EQ = ["EQ"]
BASE_CONN = ["AND", "OR", "IMPLIES", "IFF", "NEG"]
BASE_QUAN = ["EXISTS", "FORALL"]

BASE_FORMULA = [
    ["(", "(", "VAR1", "EQ", "VAR2", ")", "AND", "NEG", "FORALL", "VAR3", "PRED2", "(", "VAR1", ",", "VAR2", ")", ")"]
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

def write_to_file(formula, sub_dict, ran_order=False):
    FIELDS = [("variables", BASE_VAR), ("constants", BASE_CONST), ("predicates", BASE_PRED), ("equality", BASE_EQ), ("connectives", BASE_CONN), ("quantifiers", BASE_QUAN), ("formula", formula)]
    f = open("test.txt", mode='w')
    if ran_order: random.shuffle(FIELDS)
    
    for field in FIELDS:
        if field[0] == "predicates":
            f.write(f"{field[0]}: {' '.join(sub_dict[x][1] for x in field[1])}\n")
            continue
        if field[0] == "formula":
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
    print()

def main():
    # Stage 1 - Just try the base
    sub_dict = gen_sub(sub=False)
    for formula in BASE_FORMULA:
        write_to_file(formula, sub_dict)
        call_program(sys.argv[1])

    # Stage 2 - Random IDs
    STAGE2_IT = 5
    for _ in range(STAGE2_IT):
        sub_dict = gen_sub(sub=True)
        for formula in BASE_FORMULA:
            write_to_file(formula, sub_dict)
            call_program(sys.argv[1])

    # Stage 3 - Add extra whitespace
    STAGE3_IT = 10
    NB_INSERTIONS = 5
    WHITESPACE = [' ', '\t', '\n']
    for _ in range(STAGE3_IT):
        sub_dict = gen_sub(sub=True)
        for formula in BASE_FORMULA:
            n = len(formula)
            insert = random.sample(range(n), NB_INSERTIONS)
            insert_char = [(x, WHITESPACE[random.randint(0, 2)]) for x in insert]

            for i, ic in enumerate(insert_char):
                formula = formula[:ic[0]+i] + [ic[1]] + formula[ic[0]+i:]

            write_to_file(formula, sub_dict)
            call_program(sys.argv[1])



if __name__ == '__main__':
    main()
