
with open("input") as inputfile:
    instructions = [int(i) for i in inputfile.readline().strip().split(",")]

def calculate_output(memory):
    IP = 0
    instructions = memory

    while instructions[IP] != 99:
        if instructions[IP] == 1:
            instructions[instructions[IP+3]] = instructions[instructions[IP+1]] + instructions[instructions[IP+2]]
        if instructions[IP] == 2:
            instructions[instructions[IP+3]] = instructions[instructions[IP+1]] * instructions[instructions[IP+2]]
            
        # print(cur, instructions[cur])
        IP +=4

    #print("Value at adress 0 after running: %s" % instructions[0])
    return instructions[0]

# part1

#restore previous state:

instructions[1] = 12
instructions[2] = 2

print("Value at adress 0 after running: %s" % calculate_output(instructions))

