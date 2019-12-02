instructions = []

with open("input") as inputfile:
    instructions = [int(i) for i in inputfile.readline().strip().split(",")]

#restore previous state:

instructions[1] = 12
instructions[2] = 2

cur = 0

while instructions[cur] != 99:
    if instructions[cur] == 1:
        instructions[instructions[cur+3]] = instructions[instructions[cur+1]] + instructions[instructions[cur+2]]
    if instructions[cur] == 2:
        instructions[instructions[cur+3]] = instructions[instructions[cur+1]] * instructions[instructions[cur+2]]
        
    print(cur, instructions[cur])
    cur +=4

print(instructions)

