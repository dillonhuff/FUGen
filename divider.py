from bit_vector import *

def tc_neg(a):
    return ~a + bv_from_int(a.width(), 1)

