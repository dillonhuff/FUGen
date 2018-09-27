from parser import *
import language as l
import ast
from rtl import *
from scheduling import *
from utils import *

def test_repeated_assignment():
    code_gen = codegen_for_module('many_assigns')    
    f_spec = specialize_types(code_gen, 'many_assigns', [l.ArrayType(32)])

    constraints = ScheduleConstraints()
    sched = schedule(code_gen, f_spec, constraints)

    print(sched.to_string())

    mod = generate_rtl(f_spec, sched)

    assert(mod.name == f_spec.name)

    generate_verilog(mod)

    print('Function before verilog tb run')
    print(f_spec.to_string())

    res = run_iverilog_test(mod.name)
    print('res =', res)
    assert(res == 'passed\n')

def test_non_inlined_functions():
    code_gen = codegen_for_module('non_inlined_function')    
    f_spec = specialize_types(code_gen, 'non_inlined', [l.ArrayType(32)])

    constraints = ScheduleConstraints()
    constraints.no_inline('plus_nums')
    constraints.set_resource_count('plus_nums_32', 1)
    sched = schedule(code_gen, f_spec, constraints)

    assert(sched.get_subschedule("plus_nums_32").num_cycles() == 0)

    print(sched.to_string())

    mod = generate_rtl(f_spec, sched)

    assert(mod.name == f_spec.name)

    generate_verilog(mod)

    print('Function before verilog tb run')
    print(f_spec.to_string())

    res = run_iverilog_test(mod.name)
    print('res =', res)
    assert(res == 'passed\n')
    

def test_tc_neg_parse():
    code_gen = codegen_for_module('tc_neg')
    print(code_gen.get_function("tc_neg").to_string())

    constraints = ScheduleConstraints()
    f_spec = specialize_types(code_gen, "tc_neg", [l.ArrayType(16)])

    print('')
    print(f_spec.to_string())

    assert(f_spec.symbol_type('a') == l.ArrayType(16))
    
    sched = schedule(code_gen, f_spec, constraints)

    assert(sched.num_states() == 1)

    # One add, one invert, one constant
    assert(sched.num_functional_units() == 3)

    #assert(has_prefix(sched.get_binding(f_spec.instructions[0]), "invert_16"))

    print(sched.to_string())
    mod = generate_rtl(f_spec, sched)

    assert(mod.name == f_spec.name)

    generate_verilog(mod)

    res = run_iverilog_test(mod.name)

    assert(res == 'passed\n')
    
def test_tc_abs_parse():
    # code_str = open('tc_abs.py').read()
    # code = ast.parse(code_str)

    # code_gen = LowCodeGenerator()
    # code_gen.visit(code)

    code_gen = codegen_for_module('tc_abs')
    print(code_gen.get_function("tc_abs").to_string())

    constraints = ScheduleConstraints()
    f_spec = specialize_types(code_gen, "tc_abs", [l.ArrayType(16)])

    print('')
    print(f_spec.to_string())

    assert(f_spec.symbol_type('a') == l.ArrayType(16))
    
    sched = schedule(code_gen, f_spec, constraints)

    print(sched.to_string())

    mod = generate_rtl(f_spec, sched)

    assert(mod.name == f_spec.name)

    generate_verilog(mod)

    res = run_iverilog_test(mod.name)
    assert(res == 'passed\n')

def test_instr_replacemant():
    call = CallInstr('res', 'func', ['hello', 'no'])
    call.replace_values(lambda name: 'a' if name == 'hello' else name)
    assert(call.args[0] == 'a')
    
def test_approximate_reciprocal_parse():
    # code_str = open('divider.py').read()
    # code = ast.parse(code_str)

    # code_gen = LowCodeGenerator()
    # code_gen.visit(code)

    code_gen = codegen_for_module('divider')
    print(code_gen.get_function("approximate_reciprocal").to_string())

    constraints = ScheduleConstraints()
    f_spec = specialize_types(code_gen, "approximate_reciprocal", [l.ArrayType(16)])

    assert(f_spec.symbol_type('one_ext') == l.ArrayType(32))

def parse_file(file_name):
    code_str = open(file_name).read()
    code = ast.parse(code_str)

    code_gen = LowCodeGenerator()
    code_gen.visit(code)

    return code_gen

def test_approximate_divider_parse():
    #code_gen = parse_file("divider")

    code_gen = codegen_for_module('divider')
    print(code_gen.get_function("newton_raphson_divide").to_string())

    constraints = ScheduleConstraints()
    f_spec = specialize_types(code_gen, "newton_raphson_divide", [l.ArrayType(8), l.ArrayType(8)])

    print('')
    print(f_spec.to_string())

    assert(f_spec.symbol_type('n') == l.ArrayType(8))
    assert(f_spec.symbol_type('d') == l.ArrayType(8))    
    sched = schedule(code_gen, f_spec, constraints)

    print(sched.to_string())

    mod = generate_rtl(f_spec, sched)

    assert(mod.name == f_spec.name)

    generate_verilog(mod)

    res = run_iverilog_test(mod.name)
    assert(res == 'passed\n')

def test_huang_reciprocal():

    code_gen = codegen_for_module('huang_divider')    
    # code_gen = parse_file("huang_divider.py")

    # code_gen = parse_file("divider")    
    constraints = ScheduleConstraints()
    f_spec = specialize_types(code_gen, 'huang_square_reciprocal', [l.ArrayType(8)]) #, l.ArrayType(16)])

    print(f_spec.to_string())

def test_huang_divider():

    code_gen = codegen_for_module('huang_divider')    
    f_spec = specialize_types(code_gen, 'huang_divide', [l.ArrayType(16), l.ArrayType(16)])

    constraints = ScheduleConstraints()
    sched = schedule(code_gen, f_spec, constraints)

    print(sched.to_string())

    mod = generate_rtl(f_spec, sched)

    assert(mod.name == f_spec.name)

    generate_verilog(mod)

    res = run_iverilog_test(mod.name)
    assert(res == 'passed\n')

def test_make_const():

    code_gen = codegen_for_module('make_const')    
    f_spec = specialize_types(code_gen, 'make_const', [l.ArrayType(16), 27])

    constraints = ScheduleConstraints()
    sched = schedule(code_gen, f_spec, constraints)

    print(sched.to_string())

    mod = generate_rtl(f_spec, sched)

    assert(mod.name == f_spec.name)

    generate_verilog(mod)

    res = run_iverilog_test(mod.name)
    assert(res == 'passed\n')
    
