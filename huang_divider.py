from bit_vector import *

def tc_neg(a):
    return ~a + bv_from_int(a.width(), 1)

def sign_bit(v):
    return v[v.width() - 1:v.width() - 1]

def tc_is_neg(a):
    return a[a.width() - 1:a.width() - 1] == bv_from_int(1, 1)

def tc_abs(a):
    return tc_neg(a) if tc_is_neg(a) else a

def normalize_left(a):
    return a << leading_zero_count(a)

def build_one_fp(width, dist):
    return bv_from_int(width, 1) << bv_from_int(width, dist)

def compute_reciprocal(b):
    width = b.width()
    normed = normalize_left(b)

    top_8 = normed

    assert(top_8.width() == width)

    one_ext = build_one_fp(2*width, 2*width - 1)
    top_8_ext = zero_extend(2*width, top_8)
    quote = one_ext / top_8_ext

    print('Quote =', quote)

    sliced_quote = (normalize_left(quote))[quote.width() - width:quote.width() - 1]

    return sliced_quote
    
def approximate_reciprocal(b):
    width = b.width()
    approximation_width = 10
    normed = normalize_left(b)

    top_8 = zero_extend(width, normed[width - approximation_width : width - 1])

    assert(top_8.width() == width)

    one_ext = build_one_fp(2*width, 2*width - 1) #bv_from_int(2*width, 1 << (2*width - 1))
    top_8_ext = zero_extend(2*width, top_8)
    quote = one_ext / top_8_ext

    print('Quote =', quote)

    sliced_quote = (normalize_left(quote))[quote.width() - width:quote.width() - 1]
    print('Sliced quote =', sliced_quote)

    return sliced_quote

def mul_fp(a, b, decimal_place):
    assert(a.width() == b.width());
    
    width = a.width()
    a_ext = zero_extend(2*width, a)
    b_ext = zero_extend(2*width, b)
    prod = a_ext * b_ext

    return (prod >> bv_from_int(width, decimal_place))[0:width - 1]

def huang_divide(n_in, d_in):
    assert(n_in.width() == d_in.width())
    assert(n_in.width() % 2 == 0)

    width = n_in.width()
    m = width // 2
    
    n_abs = tc_abs(n_in)
    d_abs = tc_abs(d_in)

    d_norm = normalize_left(d_abs)
    n_norm = normalize_left(n_abs)

    y_l = d_norm[0 : m - 2]
    y_h = d_norm[width - m - 1 : width - 1]

    print('y_h =', y_h)
    print('y_l =', y_l)

    assert(y_l.width() == m - 1)
    assert(y_h.width() == m + 1)

    print('y_h float   =', fixed_point_to_float(y_h, m))
    print('y_h_2 comp  =', fixed_point_to_float(y_h, m) * fixed_point_to_float(y_h, m))

    y_h_2 = mul_fp(y_h, y_h, m)

    print('y_h_2 float =', fixed_point_to_float(y_h_2, m))
    
    y_h_2_r = compute_reciprocal(y_h_2)

    print('y_h_2_r       =', y_h_2_r)
    print('y_h_2_r float =', fixed_point_to_float(y_h_2_r, m))
    print('y_h_2_r comp  =', 1 / (fixed_point_to_float(y_h, m) * fixed_point_to_float(y_h, m)))

    n_sign = sign_bit(n_in)
    d_sign = sign_bit(d_in)

    return n_abs
    
def newton_raphson_divide(ne, de):
    assert(ne.width() == de.width())

    width = ne.width()
    
    n = tc_abs(ne)
    d = tc_abs(de)

    n_sign = sign_bit(ne)
    d_sign = sign_bit(de)

    one = build_one_fp(width, width - 1) #bv_from_int(width, 1 << (width - 1))
    lzc = leading_zero_count(d)
    normed_d = d << (lzc - bv_from_int(width, 1))

    print('Normalized d =', normed_d)

    n_ext = zero_extend(2*width, n)

    X0 = approximate_reciprocal(normed_d)

    print('X0 =', X0)

    X = X0 + mul_fp(X0, one - mul_fp(X0, normed_d, width - 1), width - 1)

    print('X1 =', X)
    
    print('X    =', fixed_point_to_float(X, width - 1))
    print('1 / D =', 1.0 / fixed_point_to_float(normed_d, width - 1))

    long_prod = n_ext * zero_extend(2*width, X)

    print('n_ext =', n_ext)
    print('n_ext*d =', long_prod)

    widthBV = bv_from_int(width, width)
    res_shift = widthBV + widthBV - (lzc - bv_from_int(width, 1)) - bv_from_int(width, 2)
    print('res_shift =', res_shift)
    shifted_prod = (long_prod >> res_shift)[0:width - 1]
    print('shifted_prod =', shifted_prod)

    q = shifted_prod if normed_d != build_one_fp(width, width - 2) else n >> (widthBV - lzc - bv_from_int(width, 1))

    print('d_sign = ', d_sign)
    print('n_sign = ', n_sign)    

    out = q if d_sign == n_sign else tc_neg(q)

    return out
