import mdl
from display import *
from matrix import *
from draw import *
import sys

set_basename = False
basename = 'anim'
set_frames = False
frames = None

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """
def first_pass(basename, frames, commands ):
    vary = False
    for command in commands:
        if command[0] == 'basename':
            basename = command[1]
        elif command[0] == 'frames':
            frames = command[1]
        elif command[0] == 'vary':
            vary = True
    if basename == -1:
        print 'basename set to default'
        basename = 'default'
    if frames == -1 and vary:
        print 'no frames'
        sys.exit()
    return basename, frames


"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropriate value. 
  ===================="""

def second_pass( commands,  frames ):
    table = []
    i = 0
    while i < frames:
        table.append({})
        i+=1
        
    i = 0
    for command in commands:
        if command[0] == "vary":
            if command[2] <= command[3] and command[4]>=0 and command[5] < frames:                
                i=0
                while i <= command[3]-command[2]:
                    val = command[4]+i/float(command[3]-command[2])*(command[5]-command[4])
                    d=table[i+command[2]]
                    d[command[1]] = val
                    i+=1
            else:
                print "error: \n"+str(command)
                sys.exit()
    return table


def run(filename):
    """
    This function runs an mdl script
    """
    basename = -1
    frames = -1
    color = [255, 255, 255]
    tmp = new_matrix()
    ident( tmp )

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    ident(tmp)
    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    tmp = []
    step = 0.1
    rets = first_pass(basename, frames, commands);
    basename = rets[0]
    frames = rets[1]
    d = second_pass(commands,frames)
    i = 0
    while i <frames:
        for command in commands:
            c = command[0]
            args = command[1:]
            if c == 'box':
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'move':
                if(len(args)>3) and args[3]!=None:
                    knob = d[i][args[3]]
                else:
                    knob = 1
                tmp = make_translate(args[0]*knob, args[1]*knob, args[2]*knob)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                if(len(args)>3):
                    knob = d[i][args[3]]
                else:
                    knob = 1
                print knob
                tmp = make_scale(knob*(args[0]-1)+1, knob*(args[1]-1)+1, knob*(args[2]-1)+1)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                if(len(args)>2):
                    knob = d[i][args[2]]
                else:
                    knob = 1
                theta = (args[1] * (math.pi/180))*knob
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
        fname = "anim/"+basename+"%03d"%i+".png"
        save_extension(screen, fname)
        tmp = new_matrix()
        ident(tmp)
        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        i+=1
