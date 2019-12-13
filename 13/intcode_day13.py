#!/usr/bin/env python3

import queue
import threading
import itertools
import operator
import concurrent.futures
import sys

with open(sys.argv[1]) as inputfile:
    orig_instructions = [int(i) for i in inputfile.readline().strip().split(",")]


"""opcodes:

1: addition: 3 parameters, param 3 = 1+2
2: multiplication: 3 parameters, param 3 = 1*2
3: input: 1 param, saves input() to address param1
4: output: 1 param, outputs the value at param1

    """

OPCODES = {1: {'len': 3, 'in': 2, 'out': 1, 'func': lambda x,y: x+y},
           2: {'len': 3, 'in': 2, 'out': 1, 'func': lambda x,y: x*y},
           3: {'len': 1, 'in': 0, 'out': 1,}, 
           4: {'len': 1, 'in': 1, 'out': 0},
           5: {'len': 2, 'in': 2, 'out': 0, 'func': lambda x: True if x!=0 else False},
           6: {'len': 2, 'in': 2, 'out': 0, 'func': lambda x: True if x==0 else False},
           7: {'len': 3, 'in': 2, 'out': 1, 'func': lambda x,y: 1 if x<y else 0},
           8: {'len': 3, 'in': 2, 'out': 1, 'func': lambda x,y: 1 if x==y else 0},
           # reset relative base
           9: {'len': 1, 'in': 1, 'out': 0},
           99: {'len': 0, 'func': ''},
           }
   
def calculate_output(memory, inputqueue, outputqueue):
    # Instruction Pointer
    IP = 0
    # Relative Base Pointer
    BP = 0
   
    ins = 0
    lastprint = 0
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
            return lastprint
            break
        # IMPORTANT:
        #  Parameters that an instruction writes to will never be in immediate mode.


        # for the rest of the instructions, only check here for param 0 & 1:
            # if modes != 1, we have to load the value from the memory location params points to
            # the target address and its mode get handled seperately
        for j in range(OPCODES[ins]['in']):
            if modes[j] == 0:
                params[j] = memory[params[j]]
            if modes[j] == 2:
                # adjust relative instruction by the relative base pointer BP
                params[j] = memory[BP+params[j]]

        # writing is only possible to absolute or relative modes       
        if ins in (1,2,7,8):
            temp_BP = 0
            if modes[2] == 2:
                temp_BP = BP
            memory[params[2]+temp_BP] = OPCODES[ins]['func'](params[0], params[1])
        # input only has an parameter to write to, no checking necesarry:
        # optional:  enable an inputbuffer to get inputs from
        if ins == 3:
            inputchar = inputqueue.get(block=True)
            temp_BP = 0
            if modes[0] == 2:
                temp_BP = BP
            memory[params[0]+temp_BP] = int(inputchar)

        if ins == 4:
            # printout the value or add it to the output buffer
            outputqueue.put(params[0])
            lastprint = params[0]
        if ins == 9:
            # increase the relative base by the argument
            BP += params[0]
        
        NEW_IP = IP + OPCODES[ins]['len']+1
        
        if ins in (5,6):
            if OPCODES[ins]['func'](params[0]):
                NEW_IP = params[1]

        IP = NEW_IP

    #return output

def draw_board(grid, inq, outq):
    """draw on the board, track the coordinates of the robot and return new color of the next grid field"""
    coord = (0,0)
    cur_dir = 1 # start with abitrary definition of up :)
    dir = [(-1,0),(0,-1),(1,0),(0,1)]  # list of delta_x, delta_y per direction. Order: LEFT, UP, RIGHT, DOWN rotate by getting the next index left/right :)
    
    # give out the color of the start coordinates
    cur_color = grid[coord]
    outq.put(cur_color)
    
    while True:
        draw_command  = inq.get(block=True,timeout=2)
        # kill the job after 2 seconds without input
        move_command  = inq.get(block=True)
        # draw command: 0 means to paint the panel black, and 1 means to paint the panel white.
        # move command: 0 means it should turn left 90 degrees, and 1 means it should turn right 90 degrees.
        
        # draw current positon
        grid[coord] = draw_command

        # move to next field
        # turn left or right:
        if move_command == 0:
            cur_dir = (cur_dir - 1 ) % 4
        elif move_command == 1:
            cur_dir = (cur_dir + 1 ) % 4
        
        # move 1 "forward" in cur_dir
        coord = (coord[0]+dir[cur_dir][0], coord[1]+dir[cur_dir][1])
        cur_color = 0 # by default field is black
        
        if coord in grid.keys():
            cur_color = grid[coord]
        outq.put(cur_color)

#

def calc_board(start=None):
    """ start threads for the robot and the drawing function and return the drawed board coordinates"""
    instructions = []
    inqueue = queue.Queue()
    outqueue = queue.Queue()
    board_grid = {} # dict of painted coordinates, by default all are black -> 0   key is coords: (x,y), value is color (0,0):0
    inqueue.put(start)
    instructions = list(orig_instructions)
    additional_mem = [0] * 999
    instructions.extend(additional_mem)
    # lets start a worker for robot and the drawing grid, they will block when waiting for an input
    with concurrent.futures.ThreadPoolExecutor() as executor:
        robot = executor.submit(calculate_output, instructions, inqueue, outqueue)
        #
        board = executor.submit(draw_board, board_grid, outqueue, inqueue)
    # lets wait till the robot finishes to get
        if robot.result():
            return outqueue

def grouper(iterable, n, fillvalue=None):
    "grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)



print("Part 1")

grid = {}
for x,y,id in grouper(list(calc_board().queue), 3):
    grid[x,y] = id

print(grid.keys())
# get all block tiles (id 2)

blocks = [key for (key, value) in grid.items() if value == 2]
print("Blocks: %s" % len(blocks))
sys.exit()
print("Part 2")

# input 2 to get the game started
# -1,0 is the score value
