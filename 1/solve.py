def calc_module(weight):
    return int(weight/3)-2

def part_1(input):
    sum = 0
    for line in input:
        # here might be a good spot for the 3.8 walrus operator :)
        if len(line.strip())>0:
            #print(line)
            sum += calc_module(int(line.strip()))
    return sum




if __name__ == "__main__":
    with open("input_1") as inputfile:
        input_1 = inputfile.readlines()
    print("part 1")
    print(part_1(input_1))
