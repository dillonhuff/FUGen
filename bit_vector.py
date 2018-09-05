import re

X = 2
Z = 3

class QuadValueBit():
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if (not isinstance(other, QuadValueBit)):
            return False
        return self.value == other.value

    def __ne__(self, other):
        if (not isinstance(other, QuadValueBit)):
            return True
        return not (self == other)

    def is_binary(self):
        return self.value == 0 or self.value == 1

    def binary_value(self):
        assert(self.is_binary())
        return self.value
    
    def invert(self):
        if (self.value == 0):
            return QuadValueBit(1)
        elif self.value == 1:
            return QuadValueBit(0)
        elif self.value == X:
            return QuadValueBit(X)
        else:
            return QuadValueBit(Z)

    def to_string(self):
        if (self.value == 0):
            return '0'
        elif self.value == 1:
            return '1'
        elif self.value == X:
            return 'x'
        else:
            return 'z'
        
    def __repr__(self):
        return self.to_string()

QVB = QuadValueBit

def to_qb(binary_string):
    if (binary_string == '1'):
        return QVB(1)
    elif (binary_string == '0'):
        return QVB(0)
    elif (binary_string == 'x'):
        return QVB(X)
    elif (binary_string == 'X'):
        return QVB(X)
    elif (binary_string == 'z'):
        return QVB(Z)
    elif (binary_string == 'Z'):
        return QVB(Z)
    else:
        print('Error: Unsupported digit =', binary_string)
        assert(False)

class QuadValueBitVector():
    def __init__(self, bits):
        self.bits = bits;
        #print('First bits       = ', self.bits)
        #self.bits.reverse()

        #print('Initialized bits = ', self.bits)

    def to_string(self):
        strn = ''
        for i in range(len(self.bits) - 1, -1, -1):
            b = self.bits[i]
            strn += b.to_string()
        # for b in self.bits:
        #     strn += b.to_string()

        return strn

    def __eq__(self, other):
        if (not isinstance(other, QuadValueBitVector)):
            return False
        
        if (len(other.bits) != len(self.bits)):
            return False

        for i in range(0, len(self.bits)):
            if (other.bits[i] != self.bits[i]):
                return False
        return True

    def get(self, ind):
        return self.bits[ind]

    def set(self, ind, val):
        assert(isinstance(val, QuadValueBit))
        
        self.bits[ind] = val

    def width(self):
        return len(self.bits)

    def __str__(self):
        return self.to_string()

    def slice_bits(self, end, start):
        assert(end >= start)
        
        res_bits = []
        for i in range(start, end + 1):
            res_bits.append(self.bits[i])

        assert(len(res_bits) == (end - start + 1))
        res =  BV(res_bits)
        print('result of slicing', self, '[', str(end), ':', str(start), '] =',res)
        return res

    def __add__(self, other):
        assert(isinstance(other, QuadValueBitVector))
        assert(self.width() == other.width())

        print('self  =', self)
        print('other = ', other)
        
        resBits = []
        carry = 0
        for i in range(0, len(other.bits)):
            ab = self.get(i)
            bb = other.get(i)
            if (not ab.is_binary() or not bb.is_binary()):
                return unknown_bv(self.width())

            # print('ab = ', ab)
            # print('bb = ', bb)
            val = ab.binary_value() + bb.binary_value() + carry
            # print('val = ', val)
            if (val >= 2):
                carry = 1

            if (val == 1 or val == 3):
                resBits.append(QVB(val % 2))
            else:
                resBits.append(QVB(0))

        return BV(resBits)

    def zero_extend(self, width):
        assert(width >= self.width())
        
        resBits = []
        for bit in self.bits:
            resBits.append(bit)
        for i in range(0, width - self.width()):
            resBits.append(QVB(0))

        assert(len(resBits) == width)
        
        return BV(resBits)
        
    def __repr__(self):
        return self.to_string()
    
BV = QuadValueBitVector

def bv(binary_string):
    rmatch = re.match(r'((\d)*)\'b((\d)*)', binary_string)
    if not rmatch:
        assert(False)

    width = int(rmatch.group(1))
    value = rmatch.group(3)

    print( 'width = ', width )
    print( 'value = ', value )
    bits = []

    for digit in value:
        bits.append(to_qb(digit))

    bits.reverse()

    assert(len(bits) == width)

    return BV(bits)

def twos_complement_absolute_value(bv):
    return plus(invert(bv), BV(bv.length(), 1))

def invert(bv):
    bits = []
    for bit in bv.bits:
        bits.append(bit.invert())

    return BV(bits)

def bv_from_list(lst):
    vec = BV(lst)
    vec.bits.reverse()
    return vec

def bv_from_int(width, val):
    assert(isinstance(val, int))
    #assert(val >= 0)

    bits = list('{0:0b}'.format(val))
    bits.reverse()

    bitList = []
    for b in bits:
        bitList.append(to_qb(b))
    print('Bits =', bitList)

    assert(len(bitList) <= width)
    return BV(bitList).zero_extend(width)
