from collections import defaultdict
from pprint import pprint

// TODO: Allow splitting by other whitespace types. For now space is fine
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
       
        file_dict[c_field] = file_dict[c_field] + space_split

    f.close()
    
    if not set(seen_fields) == REQUIRED_FIELDS:
        print("File did not contain all fields. Terminating..")
        exit()
    return file_dict

if __name__ == "__main__":
    print(read_file("example.txt"))
