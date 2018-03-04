
import collections
import io
import os
import random
import sys
import tempfile
import unittest
import fialka
#from argparse import ArgumentError

#args = None
root_rotor = 'ABCDEFGHJKLMNPRSTUVWXY1234567890'

def random_key(n=10):
    result = []
    for i in range(n):
        result.append(random.choice(root_rotor))
    return ''.join(result)

def char_freq(s):
    ctr = collections.Counter(s)
    mean = sum(ctr.values())/len(root_rotor)
    sigma2 = 0
    for c in root_rotor:
        if c not in ctr:
            cf = 0
        else:
            cf = ctr[c]
        dfms = (cf - mean)**2
        sigma2 += dfms
        #print(c, cf, mean, cf - mean, (cf - mean)**2, dfms)
    #print(len(s), len(root_rotor), len(ctr), mean, sigma2, sigma2**.5)
    return (sigma2**.5)/len(s)

class PlainText(unittest.TestCase):

    def setUp(self):
        self.context = fialka.application_context(['-e', 'ABCDEFGH1J', '1GN0REME'])

    def test_to_upper(self):
        self.assertEqual(fialka.plaintext('aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ1234567890#', self.context['root_rotor']),'AABBCCDDEEFFGGHH11JJKKLLMMNN00PPKKRRSSTTUUVVWWXXYY331234567890')

    def test_remove_punctuation(self):
        self.assertEqual(fialka.plaintext('a!~`@$%^&*()_-+=|\{}[];;<>,.?/#a', self.context['root_rotor']), 'AA')

class HelperFunctions(unittest.TestCase):
    def test_idx_add1(self):
        self.assertEqual(fialka.idx_add(13, 3), 16)
        self.assertEqual(fialka.idx_add(13, 21), 2)
        self.assertEqual(fialka.idx_add(13, -21), 24)
        self.assertEqual(fialka.idx_add(13, 11), 24)
        self.assertEqual(fialka.idx_add(11, 21), 0)
        self.assertEqual(fialka.idx_add(31, 1), 0)
        self.assertEqual(fialka.idx_add(0, -1), 31)
        self.assertEqual(fialka.idx_add(55, 682117), 28)
    def test_idx_add2(self):
        with self.assertRaises(TypeError):
            bogus = fialka.idx_add(31, 'A')
    def test_chunk_print(self):
        cleartext = '1TSABEAUT1FULDAY'
        captured = io.StringIO()
        sys.stdout = captured
        chunktext = fialka.chunk_print(cleartext)
        self.assertEqual(captured.getvalue(), '1TSAB EAUT1 FULDA Y\n')
    def test_comma_string_to_list1(self):
        self.assertEqual(fialka.comma_string_to_list('0,1,2,3,4,5,6,7,8,9'), [0,1,2,3,4,5,6,7,8,9])
        self.assertEqual(fialka.comma_string_to_list('9,7,3'), [9, 7, 3])
        self.assertEqual(fialka.comma_string_to_list('3,7,9'), [3, 7, 9])
        self.assertEqual(fialka.comma_string_to_list('0,1,0'), [0, 1, 0])
        with self.assertRaises(ValueError):
            bogus = fialka.comma_string_to_list('11,3,6')
        with self.assertRaises(ValueError):
            bogus = fialka.comma_string_to_list('0,1,A,2,3')
        with self.assertRaises(ValueError):
            bogus = fialka.comma_string_to_list('A0123')
    def test_get_cleartext1(self):
        ntf = tempfile.NamedTemporaryFile(delete=False)
        with open(ntf.name, 'w') as fp:
            fp.write('D0GG0NE')
        self.assertEqual(fialka.get_cleartext(None, ntf.name), 'D0GG0NE')
        os.remove(ntf.name)
        self.assertEqual(fialka.get_cleartext('HELL0G00DBYE', None), 'HELL0G00DBYE')
        with self.assertRaises(ValueError):
            fialka.get_cleartext(None, None)
        with self.assertRaises(ValueError):
            fialka.get_cleartext('123', 'ex_clear.txt')
    def test_str_find(self):
        self.assertEqual(fialka.str_find('ABCD', 'C'), 2)
        with self.assertRaises(IndexError):
            self.assertEqual(fialka.str_find('ABCD', 'c'), 2)

class ApplicationContext(unittest.TestCase):
    def test_sanity_check1(self):
        ctxt = fialka.application_context(['-e', 'ABCDEFGH1J', '1GN0REME'])
        ctxt['args'].key = 'LO0KIEHERE'
        with self.assertRaises(ValueError):
            fialka.sanity_check(ctxt)
    def test_sanity_check2(self):
        with self.assertRaises(ValueError):
            ctxt = fialka.application_context(['-e', 'ABCDEFGHIJ', 'FA1L'])
    def test_stop1(self):
        ctxt = fialka.application_context(['-e', 'ABCDEFGH1J', '1GN0REME'])
        self.assertEqual(fialka.stop(ctxt, 0), False) 
        ctxt['rotor'][0]['offset'] += 1
        self.assertEqual(fialka.stop(ctxt, 0), False) 
        ctxt['rotor'][0]['offset'] += 1
        self.assertEqual(fialka.stop(ctxt, 0), False) 
    def test_stop2(self): #Rotor 0: 01011010100
        ctxt = fialka.application_context(['-e', 'ABCDEFGH1J', '1GN0REME'])
        self.assertEqual(fialka.stop(ctxt, 1), False) 
        ctxt['rotor'][0]['offset'] += 1
        self.assertEqual(fialka.stop(ctxt, 1), True) 
        ctxt['rotor'][0]['offset'] += 1
        self.assertEqual(fialka.stop(ctxt, 1), False) 
        ctxt['rotor'][0]['offset'] += 1
        self.assertEqual(fialka.stop(ctxt, 1), True) 
        ctxt['rotor'][0]['offset'] += 1
        self.assertEqual(fialka.stop(ctxt, 1), True) 
        ctxt['rotor'][0]['offset'] += 1
        self.assertEqual(fialka.stop(ctxt, 1), False) 
        ctxt['rotor'][0]['offset'] += 1
        self.assertEqual(fialka.stop(ctxt, 1), True) 
        ctxt['rotor'][0]['offset'] += 1
        self.assertEqual(fialka.stop(ctxt, 1), False) 
        ctxt['rotor'][0]['offset'] += 1
        self.assertEqual(fialka.stop(ctxt, 1), True) 
        ctxt['rotor'][0]['offset'] += 1
        self.assertEqual(fialka.stop(ctxt, 1), False) 
        ctxt['rotor'][0]['offset'] += 1
        self.assertEqual(fialka.stop(ctxt, 1), False) 
    def test_application_context1(self):
        ctxt = fialka.application_context(['-e', '-w', '7,2,1', 'ABCDEFGH1J', 'TEST1NG123'])
        self.assertEqual(ctxt['args'].encrypt, True)
        self.assertEqual(ctxt['args'].decrypt, False)
        self.assertEqual(ctxt['args'].wheel_order, '7,2,1')
        self.assertEqual(ctxt['args'].key, 'ABCDEFGH1J')
        self.assertEqual(ctxt['args'].cleartext, 'TEST1NG123')
        self.assertEqual(ctxt['root_rotor'], 'ABCDEFGHJKLMNPRSTUVWXY1234567890')
        self.assertEqual(len(ctxt['rotor']), 3)
        self.assertEqual(ctxt['rotor'][0]['map'],'T78UALNCJPY6BMX039W4GRDFEH52KVS1')
        self.assertEqual(ctxt['rotor'][1]['map'],'LT2KDU7PN6FRSG4W38VX0HJA1Y9E5CBM')
        self.assertEqual(ctxt['rotor'][2]['map'],'CVF083DPT5LYE1JHM47KA9NWU2XB6RGS')
        self.assertEqual(ctxt['rotor'][0]['stop'],'01000011110100000001000110011011')
        self.assertEqual(ctxt['rotor'][1]['stop'],'00001001010001001010011101100010')
        self.assertEqual(ctxt['rotor'][2]['stop'],'10111101100111101111011111011001')
        self.assertEqual(ctxt['rotor'][0]['rule'], ctxt['rotor'][2]['rule'])
        self.assertNotEqual(ctxt['rotor'][0]['rule'], ctxt['rotor'][1]['rule'])
    def test_application_context2(self):
        ctxt = fialka.application_context(['-e', '-w', '7,2,1', '-s', '3,8,9', 'ABCDEFGH1J', 'TEST1NG123'])
        self.assertEqual(ctxt['args'].encrypt, True)
        self.assertEqual(ctxt['args'].decrypt, False)
        self.assertEqual(ctxt['args'].wheel_order, '7,2,1')
        self.assertEqual(ctxt['args'].wheel_stop_order, '3,8,9')
        self.assertEqual(ctxt['args'].key, 'ABCDEFGH1J')
        self.assertEqual(ctxt['args'].cleartext, 'TEST1NG123')
        self.assertEqual(ctxt['root_rotor'], 'ABCDEFGHJKLMNPRSTUVWXY1234567890')
        self.assertEqual(len(ctxt['rotor']), 3)
        self.assertEqual(ctxt['rotor'][0]['map'],'T78UALNCJPY6BMX039W4GRDFEH52KVS1')
        self.assertEqual(ctxt['rotor'][1]['map'],'LT2KDU7PN6FRSG4W38VX0HJA1Y9E5CBM')
        self.assertEqual(ctxt['rotor'][2]['map'],'CVF083DPT5LYE1JHM47KA9NWU2XB6RGS')
        self.assertEqual(ctxt['rotor'][0]['stop'],'01011110110111110100111000101101')
        self.assertEqual(ctxt['rotor'][1]['stop'],'01001000011010111001100101010100')
        self.assertEqual(ctxt['rotor'][2]['stop'],'00011010000101101000110101100011')
        self.assertEqual(ctxt['rotor'][0]['rule'], ctxt['rotor'][2]['rule'])
        self.assertNotEqual(ctxt['rotor'][0]['rule'], ctxt['rotor'][1]['rule'])
    @unittest.skip
    def test_application_context3(self):
        with self.assertRaises(ArgumentError):
            ctxt = fialka.application_context(['-e', '-d', '-z', 'ABCDEFGH1J', 'TEST1NG123'])
    @unittest.skip #TODO: how to catch this error from argparser? Override ap error handler?
    def test_application_context4(self):
        with self.assertRaises(ArgumentError):
            ctxt = fialka.application_context(['-e', '-d', '-w', '7,2,1', 'ABCDEFGH1J', 'TEST1NG123'])
    @unittest.skip
    def test_application_context5(self):
        with self.assertRaises(ArgumentError):
            ctxt = fialka.application_context(['ABCDEFGH1J', 'TEST1NG123'])

class WheelRotationRules(unittest.TestCase):
    def test_clockwise(self):
        self.assertEqual(fialka.clockwise(3, 2, 0), 4)
        self.assertEqual(fialka.clockwise(3, -7, 0), 4)
        self.assertEqual(fialka.clockwise(31, 721317, 0), 0)
        self.assertEqual(fialka.clockwise(31, 'A', 0), 0)
    def test_counter_clockwise(self):
        self.assertEqual(fialka.counter_clockwise(3, 2, 0), 2)
        self.assertEqual(fialka.counter_clockwise(3, -7, 0), 2)
        self.assertEqual(fialka.counter_clockwise(0, 721317, 0), 31)
        self.assertEqual(fialka.counter_clockwise(0, 'A', 0), 31)

class Reflect(unittest.TestCase):
    def test_reflect1(self):
        self.assertEqual(fialka.reflect(0, True), 9)
        self.assertEqual(fialka.reflect(0, False), 9)
        self.assertEqual(fialka.reflect(1, True), 23)
        self.assertEqual(fialka.reflect(1, False), 23)
        self.assertEqual(fialka.reflect(2, True), 6)
        self.assertEqual(fialka.reflect(2, False), 6)
        self.assertEqual(fialka.reflect(3, True), 20)
        self.assertEqual(fialka.reflect(3, False), 20)
        self.assertEqual(fialka.reflect(4, True), 28)
        self.assertEqual(fialka.reflect(4, False), 28)
        self.assertEqual(fialka.reflect(5, True), 14)
        self.assertEqual(fialka.reflect(5, False), 14)
        self.assertEqual(fialka.reflect(6, True), 2)
        self.assertEqual(fialka.reflect(6, False), 2)
        self.assertEqual(fialka.reflect(7, True), 12)
        self.assertEqual(fialka.reflect(7, False), 12)
        self.assertEqual(fialka.reflect(8, True), 17)
        self.assertEqual(fialka.reflect(8, False), 17)
        self.assertEqual(fialka.reflect(9, True), 0)
        self.assertEqual(fialka.reflect(9, False), 0)
        self.assertEqual(fialka.reflect(10, True), 11)
        self.assertEqual(fialka.reflect(10, False), 11)
        self.assertEqual(fialka.reflect(11, True), 10)
        self.assertEqual(fialka.reflect(11, False), 10)
        self.assertEqual(fialka.reflect(12, True), 7)
        self.assertEqual(fialka.reflect(12, False), 7)
        self.assertEqual(fialka.reflect(13, True), 13)  #
        self.assertEqual(fialka.reflect(13, False), 13) #
        self.assertEqual(fialka.reflect(14, True), 5)
        self.assertEqual(fialka.reflect(14, False), 5)
        self.assertEqual(fialka.reflect(15, True), 29)
        self.assertEqual(fialka.reflect(15, False), 29)
        self.assertEqual(fialka.reflect(16, True), 18) #
        self.assertEqual(fialka.reflect(16, False), 24) #
        self.assertEqual(fialka.reflect(17, True), 8)
        self.assertEqual(fialka.reflect(17, False), 8)
        self.assertEqual(fialka.reflect(18, True), 24) #
        self.assertEqual(fialka.reflect(18, False), 16) #
        self.assertEqual(fialka.reflect(19, True), 27)
        self.assertEqual(fialka.reflect(19, False), 27)
        self.assertEqual(fialka.reflect(20, True), 3)
        self.assertEqual(fialka.reflect(20, False), 3)
        self.assertEqual(fialka.reflect(21, True), 25)
        self.assertEqual(fialka.reflect(21, False), 25)
        self.assertEqual(fialka.reflect(22, True), 31)
        self.assertEqual(fialka.reflect(22, False), 31)
        self.assertEqual(fialka.reflect(23, True), 1)
        self.assertEqual(fialka.reflect(23, False), 1)
        self.assertEqual(fialka.reflect(24, True), 16) #
        self.assertEqual(fialka.reflect(24, False), 18) #
        self.assertEqual(fialka.reflect(25, True), 21)
        self.assertEqual(fialka.reflect(25, False), 21)
        self.assertEqual(fialka.reflect(26, True), 30)
        self.assertEqual(fialka.reflect(26, False), 30)
        self.assertEqual(fialka.reflect(27, True), 19)
        self.assertEqual(fialka.reflect(27, False), 19)
        self.assertEqual(fialka.reflect(28, True), 4)
        self.assertEqual(fialka.reflect(28, False), 4)
        self.assertEqual(fialka.reflect(29, True), 15)
        self.assertEqual(fialka.reflect(29, False), 15)
        self.assertEqual(fialka.reflect(30, True), 26)
        self.assertEqual(fialka.reflect(30, False), 26)
        self.assertEqual(fialka.reflect(31, True), 22)
        self.assertEqual(fialka.reflect(31, False), 22)
    @unittest.skip
    def test_reflect2(self):
        self.assertEqual(fialka.reflect(-1), 12)
        self.assertEqual(fialka.reflect(32), 12)

class EncryptDecrypt(unittest.TestCase):
    def setUp(self):
        self.context = fialka.application_context(['-e', 'ABCDEFGH1J', '1GN0REME'])

    def test_encode1(self):
        self.context['args'].encrypt = True
        self.context['args'].decrypt = False
        cleartext = 'C0MEHERE1SAY'
        encrypted = fialka.code(self.context, 'ABCDEFGH1J', cleartext)
        self.context['args'].encrypt = False
        self.context['args'].decrypt = True
        decrypted = fialka.code(self.context, 'ABCDEFGH1J', encrypted)
        self.assertNotEqual(decrypted, encrypted)
        self.assertEqual(decrypted, cleartext)

    def test_encode2(self):
        self.context['args'].encrypt = True
        self.context['args'].decrypt = False
        cleartext = 'ABCDEFGH1JKLMN0PKRSTUVWXY30123456789ABCDEFGH1JKLMN0PKRSTUVWXY30123456789'
        encrypted = fialka.code(self.context, 'ABCDEFGH1J', cleartext) 
        self.context['args'].encrypt = False
        self.context['args'].decrypt = True
        decrypted = fialka.code(self.context, 'ABCDEFGH1J', encrypted)
        self.assertNotEqual(decrypted, encrypted)
        self.assertEqual(decrypted, cleartext)

    def test_encode3(self):
        self.context['args'].encrypt = True
        self.context['args'].decrypt = False
        encrypted = fialka.code(self.context, 'A', 'A')
        self.context['args'].encrypt = False
        self.context['args'].decrypt = True
        decrypted = fialka.code(self.context, 'A', encrypted)
        self.assertNotEqual(decrypted, encrypted) #Rare but possible
        self.assertEqual(decrypted, 'A') 

    def test_encode4(self):
        self.context['args'].encrypt = True
        self.context['args'].decrypt = False
        encrypted = fialka.code(self.context, '0000000000', 'KAM9')
        self.assertEqual(self.context['rotor'][0]['offset'], 6+4) # r[0]['0']] == 6, 6+ len(cleartext) = 10
        self.assertEqual(self.context['rotor'][1]['offset'], 3-3) # r[1]['0']] == 3, 3 - sum(r[0][stop][7:11]) = 0
        self.assertEqual(self.context['rotor'][2]['offset'], 20+1) # r[1]['0']] == 3, 3 - sum(r[0][stop][7:11]) = 0
        self.assertEqual(self.context['rotor'][3]['offset'], 19-2) 
        self.assertEqual(self.context['rotor'][4]['offset'], 12+1) 
        self.assertEqual(self.context['rotor'][5]['offset'], 22-4) 
        self.assertEqual(self.context['rotor'][6]['offset'], 6+3) 
        self.context['args'].encrypt = False
        self.context['args'].decrypt = True
        decrypted = fialka.code(self.context, '0000000000', encrypted)
        self.assertNotEqual(decrypted, encrypted)
        self.assertEqual(decrypted, 'KAM9')

    def test_encode5(self):
        self.context['args'].encrypt = True
        self.context['args'].decrypt = False
        cleartext='Y0UMUSTREMEMBERTH1SAK1SS1SJUSTAK1SSAS1GH1SJUSTAS1GHTHEFUNDAMENTALTH1NGSAPPLYAST1MEG0ESBYANDWHENTW0L0VERSW00THEYST1LLSAY1L0VEY0U0NTHATY0UCANRELYN0MATTERWHATTHEFUTUREBR1NGSAST1MEG0ESBYM00L1GHTANDL0VES0NGSNEVER0UT0FDATEHEARTSFULL0FPASS10NJEAL0USYANDHATEW0MANNEEDSMANDANDMANMUSTHAVEH1SMATETHATN00NECANDENYU1TSST1LLTHESAME0LDST0RYAF1GHTF0RL0VEANDGL0RYACASE0FD00RD1ETHEW0RLDW1LLALWAYSWELC0MEL0VERSAST1MEG0ESBY'
        key = random_key()
        encrypted = fialka.code(self.context, key, cleartext) 
        sdratio = char_freq(encrypted)
        print(sdratio)
        self.assertTrue(sdratio < .07) #Should usually be true
        self.context['args'].encrypt = False
        self.context['args'].decrypt = True
        decrypted = fialka.code(self.context, key, encrypted)
        self.assertNotEqual(decrypted, encrypted)
        self.assertEqual(decrypted, cleartext)

    #Test to ensure changes haven't caused coding to devolve to simple
    #caesarian cipher.
    def test_encode6(self):
        self.context['args'].encrypt = True
        self.context['args'].decrypt = False
        encrypted = fialka.code(self.context, '0000000000', 'EEEEEE')
        self.context['args'].encrypt = False
        self.context['args'].decrypt = True
        decrypted = fialka.code(self.context, '0000000000', encrypted)
        self.assertNotEqual(decrypted, encrypted)
        self.assertNotEqual(encrypted[0:2], encrypted[2:4])
        self.assertNotEqual(encrypted[2:4], encrypted[4:6])
        self.assertNotEqual(encrypted[0:2], encrypted[4:6])
        self.assertNotEqual(encrypted[:3], encrypted[3:])
        self.assertEqual(decrypted, 'EEEEEE')

class EncryptOnly(unittest.TestCase):
    def test_encryptA(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'A'])
        self.assertEqual(len(context['rotor']), 1)
        encrypted = fialka.code(context, 'A', 'A')
        self.assertEqual(encrypted, '7')
    def test_encryptB(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'B'])
        encrypted = fialka.code(context, 'A', 'B')
        self.assertEqual(encrypted, 'T')
    def test_encryptC(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'C'])
        encrypted = fialka.code(context, 'A', 'C')
        self.assertEqual(encrypted, '1')
    def test_encryptD(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'D'])
        encrypted = fialka.code(context, 'A', 'D')
        self.assertEqual(encrypted, 'Y')
    def test_encryptE(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'E'])
        encrypted = fialka.code(context, 'A', 'E')
        self.assertEqual(encrypted, '6')
    def test_encryptF(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'F'])
        encrypted = fialka.code(context, 'A', 'F')
        self.assertEqual(encrypted, 'J')
    def test_encryptG(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'G'])
        encrypted = fialka.code(context, 'A', 'G')
        self.assertEqual(encrypted, '3')
    def test_encryptH(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'H'])
        encrypted = fialka.code(context, 'A', 'H')
        self.assertEqual(encrypted, 'P')
    def test_encryptJ(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'J'])
        encrypted = fialka.code(context, 'A', 'J')
        self.assertEqual(encrypted, 'F')
    def test_encryptK(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'K'])
        encrypted = fialka.code(context, 'A', 'K')
        self.assertEqual(encrypted, '8')
    def test_encryptL(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'L'])
        encrypted = fialka.code(context, 'A', 'L')
        self.assertEqual(encrypted, 'X')
    def test_encryptM(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'M'])
        encrypted = fialka.code(context, 'A', 'M')
        self.assertEqual(encrypted, '9')
    def test_encryptN(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'N'])
        encrypted = fialka.code(context, 'A', 'N')
        self.assertEqual(encrypted, 'U')
    def test_encryptN(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'N'])
        encrypted = fialka.code(context, 'A', 'N')
        self.assertEqual(encrypted, 'U')
    def test_encryptP(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'P'])
        encrypted = fialka.code(context, 'A', 'P')
        self.assertEqual(encrypted, '4')
    def test_encryptR(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'R'])
        encrypted = fialka.code(context, 'A', 'R')
        self.assertEqual(encrypted, 'R')
    def test_encryptS(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'S'])
        encrypted = fialka.code(context, 'A', 'S')
        self.assertEqual(encrypted, 'V')
    def test_encryptT(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'T'])
        encrypted = fialka.code(context, 'A', 'T')
        self.assertEqual(encrypted, 'B')
    def test_encryptU(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'U'])
        encrypted = fialka.code(context, 'A', 'U')
        self.assertEqual(encrypted, 'N')
    def test_encryptV(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'V'])
        encrypted = fialka.code(context, 'A', 'V')
        self.assertEqual(encrypted, 'S')
    def test_encryptW(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'W'])
        encrypted = fialka.code(context, 'A', 'W')
        self.assertEqual(encrypted, '0')
    def test_encryptX(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'X'])
        encrypted = fialka.code(context, 'A', 'X')
        self.assertEqual(encrypted, 'L')
    def test_encryptY(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', 'Y'])
        encrypted = fialka.code(context, 'A', 'Y')
        self.assertEqual(encrypted, 'D')
    def test_encrypt1(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', '1'])
        encrypted = fialka.code(context, 'A', '1')
        self.assertEqual(encrypted, 'C')
    def test_encrypt2(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', '2'])
        encrypted = fialka.code(context, 'A', '2')
        self.assertEqual(encrypted, '5')
    def test_encrypt3(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', '3'])
        encrypted = fialka.code(context, 'A', '3')
        self.assertEqual(encrypted, 'G')
    def test_encrypt4(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', '4'])
        encrypted = fialka.code(context, 'A', '4')
        self.assertEqual(encrypted, 'H')
    def test_encrypt5(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', '5'])
        encrypted = fialka.code(context, 'A', '5')
        self.assertEqual(encrypted, '2')
    def test_encrypt6(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', '6'])
        encrypted = fialka.code(context, 'A', '6')
        self.assertEqual(encrypted, 'E')
    def test_encrypt7(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', '7'])
        encrypted = fialka.code(context, 'A', '7')
        self.assertEqual(encrypted, 'A')
    def test_encrypt8(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', '8'])
        encrypted = fialka.code(context, 'A', '8')
        self.assertEqual(encrypted, 'K')
    def test_encrypt9(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', '9'])
        encrypted = fialka.code(context, 'A', '9')
        self.assertEqual(encrypted, 'M')
    def test_encrypt0(self):
        context = fialka.application_context(['-e', '-w', '0', 'A', '0'])
        encrypted = fialka.code(context, 'A', '0')
        self.assertEqual(encrypted, 'W')

#TODO: test that the rotors are all sane -- global data?
#TODO: rotor_position -- global data?
#TODO: code_char_wheel directly -- global data?
#TODO: reflection rule

if __name__ == '__main__':
    unittest.main()
