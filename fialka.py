import argparse
import re
import sys
import pdb

"""
    TODO: Rotor config file.
    TODO: Add an override mapping to mimic enigma patch panel or fialka card reader
"""

#TODO: if key is longer than number of rotors? Warning? Shorter?
#TODO: other sanity checks?
def sanity_check(context):
    '''runtime tests for valid configuration'''
    for c in context['args'].key:
        if c not in context['root_rotor']:
            raise ValueError('Invalid character in key: {}'.format(c))
    if context['args'].encrypt == context['args'].decrypt:
        raise RuntimeError('Context encrypt and decrypt cannot have same value')
    if context['args'].cleartext is not None and context['args'].clear_file is not None:
        raise RuntimeError('Both cleartext file and command line string are specified')
    if context['args'].cleartext is None and context['args'].clear_file is None:
        raise RuntimeError('Neither cleartext file nor command line string are specified')
        
    return context

def application_context(cl_options):
    '''Establish app context including global state'''
    args = configure_parser(cl_options)
    root_rotor = 'ABCDEFGHJKLMNPRSTUVWXY1234567890'
    rotor = initialize_rotor(comma_string_to_list(args.wheel_order), 
            comma_string_to_list(args.wheel_stop_order))
    return sanity_check({'args': args, 'root_rotor': root_rotor, 'rotor': rotor})


def comma_string_to_list(comma_str):
    '''Pre-context, convert command line input to wheel order'''
    if comma_str is None:
        return None

    result = []
    l = comma_str.split(',')
    for c in l:
        i = int(c)
        if i > -1 and i < 11:  #TODO: better way than hard coding these limits?
            result.append(i)
        else:
            raise ValueError('wheel index outside allowed range: {}'.format(c))
    return result 

def plaintext(clear_text, root_rotor):
    '''translate message into 32-space message'''
    result = clear_text.upper()
    result = re.sub('I', '1', result)
    result = re.sub('O', '0', result)
    result = re.sub('Q', 'K', result)
    result = re.sub('Z', '3', result)
    regex = re.compile('[^' + root_rotor + ']')
    result = regex.sub('', result)
    return result

def get_cleartext(command_line, file_name):
    '''Return either command line cleartext or cleartext from clear file'''
    if command_line is None and file_name is not None:
        if file_name == '-':
            cleartext = sys.stdin.read()
            return cleartext
        else:
            with open(file_name, 'r') as sf:
                cleartext = sf.read()
            return cleartext
    elif command_line is not None and file_name is None:
        return command_line
    else:
        raise ValueError('Only command line cleartext or file name option can be populated.')

#TODO: In an era of copy/paste makes the application harder not easier. Make this a command line option
def chunk_print(text):
    '''print in blocks of 5 characters'''
    for i, c in enumerate(text, start=1):
        print(c, end='')
        if i % 5 == 0:
            print(' ', end='')
        if i % 25 == 0:
            print(flush=True)
    print(flush=True)

def str_find(s, c):
    '''find first occurance of char c in string s raise exception otherwise'''
    x = s.find(c)
    if x == -1:
        raise IndexError('char {} not found in string {}'.format(c, s))
    return x

def idx_add(i, j):
    '''circular addition for 32 space'''
    return (i + j) % 32

def clockwise(rotor_idx, msg_idx, stop):
    '''rotate wheel clockwise one step'''
    if stop:
        return rotor_idx
    return idx_add(rotor_idx, 1)

def counter_clockwise(rotor_idx, msg_idx, stop):
    '''rotate wheel counter clockwise one step'''
    if stop:
        return rotor_idx
    return idx_add(rotor_idx, -1)

def initialize_rotor(wheel_order=None, wheel_stop_order=None):
    '''Initialize rotor stack based on command line'''
    if wheel_order is None:
        wheel_order=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    if wheel_stop_order is None:
        wheel_stop_order=wheel_order

    wheel = [
        'UAM94E0F8XLH2T3DKGSJCYRP6B157VNW',
        'CVF083DPT5LYE1JHM47KA9NWU2XB6RGS',
        'LT2KDU7PN6FRSG4W38VX0HJA1Y9E5CBM',
        'N9LGY43BU2TEHKWAJMR0XF7518VP6SCD',
        'HGB18KFXC9720TYUJWPVR4MANDS5L63E',
        '67EJLY9GXKWADNP5FS218B0RCVUH3T4M',
        '7PUHCW0V15YB2LAERGXT48DNMF3J69KS',
        'T78UALNCJPY6BMX039W4GRDFEH52KVS1',
        '7Y5EJ2D48H3FR1NM0L6B9VWKPAUSTGXC',
        '0U9FDLCH7J2R5EPY6T3KSGAM81VBX4WN'
    ]

    #Advance blocking pins
    stop = [
        '01011010100001011101011010111000',
        '10111101100111101111011111011001',
        '00001001010001001010011101100010',
        '01011110110111110100111000101101',
        '00110110001010000000100000000110',
        '11110000100010110000011011010011',
        '00000100010000000101000011001011',
        '01000011110100000001000110011011',
        '01001000011010111001100101010100',
        '00011010000101101000110101100011'
    ]

    rotor = []
    #pdb.set_trace()
    for i, w in enumerate(wheel_order):
        r = {'offset': 0, 
                'map': wheel[w], 
                'stop': stop[wheel_stop_order[i]],  #TODO: if len(wso) < len(wo)
                'rule': clockwise if i%2 == 0 else counter_clockwise}
        rotor.append(r)

    return rotor

def rotor_position(rotor, setting):
    '''reset the rotor wheel based on input key'''
    for i, r in enumerate(rotor):
        if i < len(setting):
            #r['offset'] = r['map'].find(setting[i])  #TODO: not found should fail
            r['offset'] = str_find(r['map'], setting[i])
        else:
            r['offset'] = 0

def reflect(i, encrypt):
    '''At the end of the line of rotors, the signal is reflected back.
       The trick is to allow an occaisional character to code to itself.
       We do that with pin 13 but that means that the other special logic
       is required for an odd number of contacts in order to support an
       even number. Real fialka had 30. I've added 2 to make it perfectly
       5 bits.'''

    #magic circuit
    if i == 13:
        return 13
    if encrypt:
        if i == 16:
            return 18
        if i == 18:
            return 24
        if i == 24:
            return 16
    else:
        if i == 24:
            return 18
        if i == 18:
            return 16
        if i == 16:
            return 24

    #hard wired mappings
    outcontact = [9, 23, 6, 20, 28, 14, 2, 12, 17, 0, 11, 10, 7, None, 5, 29, None, 8, None, 27, 3, 25, 31, 1, None, 21, 30, 19, 4, 15, 26, 22]
    j = outcontact.index(i)
    if j == -1 or j == None:
        raise IndexError('input contact: {} not mapped'.format(i))
    return j

def stop(context, d):
    '''Wheel rotation is governed by stop bool vector of the outward wheel. 
       Outermost wheel always rotates.'''
    if d == 0:
        return False
    else:
        r = context['rotor'][d - 1]
        return bool(int(r['stop'][r['offset']]))

def code_char_wheel(context, x, n, d): #signal_position, nth char in message, wheel depth
    '''If all rotors have been traversed, reflect back up through rotor stack.
       Otherwise (1) run the wheel rotatation rule, (2) account for total 
       offset, (3) account for wiring of the wheel, (4) call the next deeper 
       wheel, (5) reverse step #3, and (6) reverse of step #2.
    '''
    if d == len(context['rotor']):  #reflect
        back_pos = reflect(x, context['args'].encrypt)
        #print('reflect: ', d, x, back_pos)
    else:
        r = context['rotor'][d] #current rotor
        #rotate rule function 
        r['offset'] = r['rule'](r['offset'], n, stop(context, d))
        #account for wheel offset
        for_pos = idx_add(r['offset'], x)
        #wheel wiring
        for_pos2 = str_find(r['map'], context['root_rotor'][for_pos])
        #next wheel
        back_pos2 = code_char_wheel(context, for_pos2, n, d + 1)  
        back_pos = idx_add( -1 * r['offset'], str_find(context['root_rotor'], r['map'][back_pos2]))
        #print('wheel: ', d, x, for_pos, for_pos2, back_pos2, back_pos, rotor[d][0])
    return back_pos

#TODO: is this necessary? Could I make a call to the recursive stack w/o?
def code_char(context, c, n):
    '''begin recursive call stack to code_char_wheel'''
    #x = context['root_rotor'].find(c)
    x = str_find(context['root_rotor'], c)
    return context['root_rotor'][code_char_wheel(context, x, n, 0)]

def code(context, key, cleartext):
    '''
    Main entrypoint. Loop through message and encode each character.
    Return the encoded value.
    '''
    rotor_position(context['rotor'], key)
    result = []
    for i, c in enumerate(plaintext(cleartext, context['root_rotor'])):
        result.append(code_char(context, c, i))

    return ''.join(result)

def configure_parser(cl_args):
    '''set up the command line option parser'''
    man = '''
    SW representation of a Fialka-inspired electomechanical cipher machine.
    http://www.cryptomuseum.com/crypto/fialka/index.htm
    1. Similar to enigma with more rotors. Rotor position 0 is closest to 
       keyboard / display. Rotor 9 is closest to reflector. To encode a 
       character goes through each wheel of the rotor and translates to
       a new position based on the unique wiring of that wheel. From there
       it passes to the same position on the next deepest wheel until
       it gets to the reflector which passes is backwards through the 
       wheel stack.
    2. Possibility that a letter may be translated to itself. (Magic circuit)
       In the Enigma, the inability for a character to translate to itself
       made the code weaker.
    3. Rotor turning rules are more complicated than Enigma. Even wheels go 
       clockwise and odd wheels go counter clockwise. However, a particular 
       wheel will turn only if a setting in the next outer wheel has turning 
       enabled. These settings like the letter mappings are the key for the
       device.
    4. A-Z excepting I(1), O(0), Q(9), Z(3), as well as 0-9. 32 characters 5 bits.

    The object of this utility is not to accurately duplicate the Fialka. 
    Instead, to create a working decode and encode utility with similar 
    properties to the Fialka.
    '''
    parser = argparse.ArgumentParser(description='Fialka (Soviet Enigma machine) inspired encode/decode', epilog=man)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', '--encrypt', action='store_true')
    group.add_argument('-d', '--decrypt', action='store_true')
    parser.add_argument('-w', '--wheel-order')
    parser.add_argument('-s', '--wheel-stop-order')
    parser.add_argument('key', help='10 digit key')
    group2 = parser.add_mutually_exclusive_group(required=True)
    group2.add_argument('cleartext', nargs='?', help='message to be encoded or decoded')
    group2.add_argument('-f', '--clear-file', help='file containing message to be encoded or decoded')
    args = parser.parse_args(cl_args)
    return args

if __name__ == '__main__':
    #TODO: Better error handling
    context = application_context(sys.argv[1:])
    #print(context)
    print(code(context, context['args'].key, get_cleartext(context['args'].cleartext, context['args'].clear_file)))

