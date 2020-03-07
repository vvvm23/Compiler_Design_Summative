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

BASE_COMBINE = BASE_VAR + BASE_CONST  + BASE_EQ + BASE_CONN + BASE_QUAN

BASE_FORMULA = [
    ["(", "(", "VAR1", "EQ", "VAR2", ")", "AND", "NEG", "FORALL", "VAR3", "PRED2", "(", "VAR1", ",", "VAR2", ")", ")"]
]

def gen_sub(sub=True):
    sub_dict = {'(': '(', ')': ')', ',': ','}
    if not sub:
        for arity, pred in enumerate(BASE_PRED):
            sub_dict[pred] = (pred, f"{pred}[{arity+1}]")
        for symbol in BASE_COMBINE:
            sub_dict[symbol] = symbol
        return sub_dict

    # Replace with a random id
    ALLOWED_CHARS = string.ascii_letters + string.digits + ''.join(list(set(string.punctuation) - set(",():[]|")))
    for arity, pred in enumerate(BASE_PRED):
        ran_id = ''.join(random.choices(ALLOWED_CHARS, 10))
        sub_dict[pred] = (ran_id, f"{ran_id}[{arity+1}]")
    for symbol in BASE_COMBINE:
        ran_id = ''.join(random.choices(ALLOWED_CHARS, 10))
        sub_dict[symbol] = ran_id

    return sub_dict

def write_to_file(formula, sub_dict, ran_order=False):
    FIELDS = [("variables", BASE_VAR), ("constants", BASE_CONST), ("predicates", BASE_PRED), ("equality", BASE_EQ), ("connectives", BASE_CONN), ("quantifiers", BASE_QUAN), ("formula", formula)]
    f = open("test.txt", mode='w')
    if ran_order: random.shuffle(FIELDS)
    
    for field in FIELDS:
        print(field)
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

def main():
    # Stage 1 - Just try the base
    sub_dict = gen_sub(sub=False)
    for formula in BASE_FORMULA:
        write_to_file(formula, sub_dict)
        call_program(sys.argv[1])


if __name__ == '__main__':
    main()
