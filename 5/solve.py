#!/usr/bin/env python3

with open("input") as inputfile:
    orig_instructions = [int(i) for i in inputfile.readline().strip().split(",")]


"""opcodes:

1: addition: 3 parameters, param 3 = 1+2
2: multiplication: 3 parameters, param 3 = 1*2
3: input: 1 param, saves input() to address param1
4: output: 1 param, outputs the value at param1

    """

    # TODO add input/output counters?
OPCODES = {1: {'len': 3, 'in': 2, 'out': 1, 'func': lambda x,y : x+y},
        2: {'len': 3, 'in': 2, 'out': 1, 'func': lambda x,y : x*y},
        3: {'len': 1, 'in': 0, 'out': 1, 'func': input},
        4: {'len': 1, 'in': 1, 'out': 0, 'func': lambda x: print("print",x)},
        5: {'len': 2, 'in': 2, 'out': 0, 'func': lambda x: True if x!=0 else False},
        6: {'len': 2, 'in': 2, 'out': 0, 'func': lambda x: True if x==0 else False},
        7: {'len': 3, 'in': 2, 'out': 1, 'func': lambda x,y: 1 if x<y else 0},
        8: {'len': 3, 'in': 2, 'out': 1, 'func': lambda x,y: 1 if x==y else 0},
        99: {'len': 0, 'func': ''},
        }

def calculate_output(memory):
    IP = 0
   
    ins = 0
    while IP <= len(memory):

        # last two segments are the instructions
        ins = int(str(memory[IP])[-2:])
        # check if we actually have a proper opcode
        assert ins in OPCODES.keys()

        # depending on the number of parameters, the segments in front are for parameter handling (direct/indirect mode)
        params = [] 
        modes = []
        for i in range(1,OPCODES[ins]['len']+1):
            # i starts with 1 to get a proper offset to IP when accessing the next memory block
            params.append(memory[IP+i])
            if i <= len(str(memory[IP])[:-2]):
                # the parsing of the mode integers happens backwards:  CBAOP, with A for param 0, B for param 1 and C for param 2
                modes.append(int(str(memory[IP])[:-2][::-1][i-1]))
            else:
                modes.append(0)
        if ins == 99:
            # ALL MACHINES STOP
            break

        # IMPORTANT:
        #  Parameters that an instruction writes to will never be in immediate mode.


        # input only has an parameter to write to, no checking necesarry:
        if ins == 3:
            memory[params[0]] = int(OPCODES[ins]['func']())
        
        # for the rest of the instructions, only check here for param 0 & 1:
            # if modes != 1, we have to load the value from the memory location params points to
        for j in range(OPCODES[ins]['in']):
            if not modes[j]:
                params[j] = memory[params[j]]


        if ins in (1,2,7,8):
            memory[params[2]] = OPCODES[ins]['func'](params[0], params[1])
        if ins == 4:
            OPCODES[ins]['func'](params[0])
        
        NEW_IP = IP + OPCODES[ins]['len']+1
        
        if ins in (5,6):
            if OPCODES[ins]['func'](params[0]):
                NEW_IP = params[1]


        IP = NEW_IP

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

print("Value at adress 0 after running: %s" % calculate_output(instructions))


