#!/usr/bin/env python3

import queue
import threading
import itertools
import operator
import concurrent.futures
import sys
import pygame

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
            print("STAP")
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
    # Initialize pygame
    pygame.init()
    
    #colors:
    # Define some colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    LILA = (255, 0, 255)
    # Set the HEIGHT and WIDTH of the screen

    WIDTH = 10
    HEIGHT = 10
    MARGIN = 2
    WINDOW_SIZE = [50*(WIDTH+MARGIN), 50*(HEIGHT+MARGIN)]
    screen = pygame.display.set_mode(WINDOW_SIZE)
     
    # Set title of screen
    pygame.display.set_caption("Array Backed Grid")
     
    # Loop until the user clicks the close button.
    done = False
     
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # font
    score_font = pygame.font.SysFont("Courier", 16)
     
    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # User clicks the mouse. Get the position
                pos = pygame.mouse.get_pos()
                # Change the x/y screen coordinates to grid coordinates
                column = pos[0] // (WIDTH + MARGIN)
                row = pos[1] // (HEIGHT + MARGIN)
                # Set that location to one
                print("Click ", pos, "Grid coordinates: ", row, column)
            elif event.type == pygame.KEYUP:
                key = event.dict["key"]
                if key == ord("q"):
                    done = True
                if key == 275:
                    print("right pressed")
                    outq.put(1)
                if key == 276:
                    print("left pressed")
                    outq.put(-1)
                if key == ord(" "):
                    outq.put(0)
        # Set the screen background
    
        screen.fill(BLACK)
        # tiles:
        """    0 is an empty tile. No game object appears in this tile.
            1 is a wall tile. Walls are indestructible barriers.
            2 is a block tile. Blocks can be broken by the ball.
            3 is a horizontal paddle tile. The paddle is indestructible.
            4 is a ball tile. The ball moves diagonally and bounces off objects.
        """
        if (-1,0) in grid.keys():
            score = grid[(-1,0)]
            score_text = score_font.render("Score: {0}".format(score), True, (255,255,255))
            # Copy the text surface to the main surface
            screen.blit(score_text, (35*(WIDTH+MARGIN), 46*(HEIGHT+MARGIN)))
        else:
            score = 0
        # Draw the grid
        for column in range(40):
            for row in range(40):
                color = WHITE
                if grid[(row, column)] == 1:
                    color = GREEN
                if grid[(row, column)] == 2:
                    color = RED
                if grid[(row, column)] == 3:
                    color = BLUE
                if grid[(row, column)] == 4:
                    color = LILA
                pygame.draw.rect(screen,
                                 color,
                                 [(MARGIN + WIDTH) * row + MARGIN,
                                  (MARGIN + HEIGHT) * column + MARGIN,
                                  WIDTH,
                                  HEIGHT])
     
        # Limit to 60 frames per second
        clock.tick(10)
     
        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()
     
    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()
    return score 
        
        # give out the color of the start coordinates
        # update 
        #outq.put(cur_color)

#

def update_grid(grid,inq, outq):
    ball_x = -1
    paddle_x = -1
    while True:
        x  = inq.get(block=True)
        y  = inq.get(block=True)
        id  = inq.get(block=True)
        # block while waiting 
        # draw current positon
        grid[(x,y)] = id
        # if ball or paddle moves:
        if id in (3,4):
            if id == 4:
                print("ball x:", x)
                ball_x = x
            if id == 3:
                print("padle x:", x)
                paddle_x = x
        # move paddle on ball updates: 
        if id == 4:
            if paddle_x < ball_x:
                print("move right")
                pass
                outq.put(1)
            elif paddle_x > ball_x:
                print("move left")
                outq.put(-1)
            else: 
                print("stay")
#
                outq.put(0)

        #print("new: (%s,%s): %s" %(x,y,id)) 

def calc_board(graphic_mode=False,start=None):
    """ start threads for the robot and the drawing function and return the drawed board coordinates"""
    instructions = []
    inqueue = queue.Queue()
    outqueue = queue.Queue()
    board_grid = {} # dict of painted coordinates, by default all are black -> 0   key is coords: (x,y), value is color (0,0):0
    for x in range(40):
        for y in range(40):
            board_grid[(x,y)]=0
    instructions = list(orig_instructions)
    additional_mem = [0] * 999
    instructions.extend(additional_mem)
    if start:
        instructions[0] = start
        print("patched")
    # lets start a worker for robot and the drawing grid, they will block when waiting for an input
    with concurrent.futures.ThreadPoolExecutor() as executor:
        robot = executor.submit(calculate_output, instructions, inqueue, outqueue)
        #
        #board = draw_board(board_grid, outqueue, inqueue)
        #update = update_grid(board_grid, outqueue)
        if graphic_mode:
            executor.submit(update_grid, board_grid, outqueue, inqueue)
            board = executor.submit(draw_board, board_grid, outqueue, inqueue)
    # lets wait till the robot finishes to get
        if robot.result():
            return outqueue
        if board.result():
            print(board.result())

def grouper(iterable, n, fillvalue=None):
    "grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)



print("Part 1")

grid = {}
for x,y,id in grouper(list(calc_board().queue), 3):
    grid[x,y] = id

# get all block tiles (id 2)

blocks = [key for (key, value) in grid.items() if value == 2]
print("Blocks: %s" % len(blocks))
print("Part 2")
print("Please read the score from the scoreboard")
calc_board(start=2, graphic_mode=True)
# input 2 to get the game started
# -1,0 is the score value
