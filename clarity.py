from pypeg2 import *

import re

class Type(Keyword):
    grammar = Enum(
        K("void"),
        K("boolean"),
        K("char"),
        K("byte"), K("int"), K("long"),
        K("int8"), K("int16"), K("int32"), K("int64"),
        K("uint8"), K("uint16"), K("uint32"), K("uint64"),
        K("float"), K("double"),
        K("string"),
        K("tuple"),
        K("array"),
        K("dict"),
        K("set"),
        K("binary"),
        K("object"),
        )

class Constants(str):
    grammar = [
        re.compile(r"0[xX][0-9a-fA-F]+"),  # HEX-значения
        re.compile(r"\d+\.\d*f"),          # float значения
        re.compile(r"\d+\.\d+"),           # double значения
        re.compile(r"\d+l"),               # long значения
        re.compile(r"\d+i8"),              # int8
        re.compile(r"\d+i16"),             # int16
        re.compile(r"\d+i32"),             # int32
        re.compile(r"\d+i64"),             # int64
        re.compile(r"\d+u8"),              # uint8
        re.compile(r"\d+u16"),             # uint16
        re.compile(r"\d+u32"),             # uint32
        re.compile(r"\d+u64"),             # uint64
        re.compile(r"\d+"),                # целые числа без суффиксов
        re.compile(r"'[^']'"),             # char
        "true", "false", "null",           # логические и null значения
        '""',                              # пустая строка
        "{}",                              # пустой словарь
        "[]",                              # пустой список
        "()",                              # пустой кортеж
        re.compile(r'"[^"]*"'),            # строки (не пустые)
        re.compile(r"\[.*?\]"),            # списки
        re.compile(r"\(.*?\)"),            # кортежи
        re.compile(r"{.*?}"),              # словари
    ]

class Identifier(str):
    grammar = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")

class FunctionCallArgument(Plain):
    grammar = attr("argument_name", Identifier), "=", attr("argument_value", Identifier)

class FunctionCallArguments(List):
    grammar = optional(csl(FunctionCallArgument))

class FunctionCall(Namespace):
    grammar = attr("function_name", Identifier), "(", attr("function_arguments", FunctionCallArguments), ")"

class Operator(str):
    grammar = re.compile(r"\+|\-|\*|\/|\=\=")

class UnaryExpression(Plain):
    grammar = optional("-"), [Constants, Identifier, FunctionCall]

class GroupExpression(Plain):
    grammar = "(", attr("expression", "Expression"), ")"

class Expression(List):
    grammar = UnaryExpression, maybe_some(Operator, [UnaryExpression, GroupExpression])

class AssignmentStatement(Namespace):
    grammar = attr("variable_name", Identifier), "=", attr("variable_expression", Expression), ";"

class ReturnStatement(Namespace):
    grammar = "return", csl(Expression), ";"

class CodeBlock(List):
    grammar = maybe_some([AssignmentStatement, ReturnStatement])

class FunctionReturn(Plain):
    grammar = attr("return_type", Type)

class FunctionReturns(List):
    grammar = csl(FunctionReturn)

class FunctionParameter(Plain):
    grammar = attr("parameter_type", Type), attr("parameter_name", Identifier)

class FunctionParameters(List):
    grammar = optional(csl(FunctionParameter))

class Function(Namespace):
    grammar = (
        attr("function_returns", FunctionReturns),
        attr("function_name", Identifier),
        "(", attr("function_params", FunctionParameters), ")",
        "{", attr( "function_code", CodeBlock), "}"
    )

class Program(List):
    grammar = maybe_some([Function])

source_code = """
int32, float foo(int32 x, float y) {
    x = -x + 2 * (y + z(1,2)) / x;
}
"""

parsed_program = None

try:
    print("run")
    parsed_program = parse(source_code, Program)
    print("finish")
except GrammarTypeError as e:
    print("parse error:", e)

for function in parsed_program:
    print(function.function_returns)
    for ret in function.function_returns:
        print(ret.return_type)
    print(function.function_name)
    for par in function.function_params:
        print(par.parameter_type, par.parameter_name)

    for code in function.function_code:
        if isinstance(code, AssignmentStatement):
            print("variable_name", code.variable_name)
            print("variable_expression", code.variable_expression)
            for index, expr in enumerate(code.variable_expression):
                print(index, expr)
        if isinstance(code, ReturnStatement):
            print("return")

print(parsed_program)

"""


void main() {
    a = 1;
    b = true;
    c = null;
    d = "test";
    e = {};
    f = [1,2,3];
    g = (1,2,3.0);
    d = {"a":1, "b":true, "c":null, "d":"test", "e":{}, "f":[1,2,3], "g":(1,2,3.0)};

    x, y = foo(x = a, y = 1.f);
}
"""