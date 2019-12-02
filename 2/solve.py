
with open("input") as inputfile:
    orig_instructions = [int(i) for i in inputfile.readline().strip().split(",")]




def calculate_output(memory):
    IP = 0
    

    while memory[IP] != 99:
        if memory[IP] == 1:
            memory[memory[IP+3]] = memory[memory[IP+1]] + memory[memory[IP+2]]
        if memory[IP] == 2:
            memory[memory[IP+3]] = memory[memory[IP+1]] * memory[memory[IP+2]]
        # print(cur, instructions[cur])
        IP +=4

    #print("Value at adress 0 after running: %s" % instructions[0])
    return memory[0]

def fuzz_inputs(target):
    # run calculate_output until target is reached
    
    for noun in range(99):
        for verb in range(99):
            instructions = list(orig_instructions)
            # patching:
            instructions[1] = noun
            instructions[2] = verb
            value = calculate_output(instructions)
            if value == target:
                return noun*100+verb
# part1

#restore previous state:

instructions = list(orig_instructions)
instructions[1] = 12
instructions[2] = 2

print("Value at adress 0 after running: %s" % calculate_output(instructions))

# part2
print("%s is the final state" % fuzz_inputs(19690720))

