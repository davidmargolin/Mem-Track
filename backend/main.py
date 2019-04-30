from compiler import *
from machineLib import *
from assemblyLib import *
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
def health_check():
    return "Application is running"

@app.route('/compile', methods = ['POST'])
@cross_origin()
def compile():
    source = request.json
    compiler = Compiler()
    function_indices = []
    for i, line in enumerate(source):
        if re.match(compiler.function_pattern, line):
            function_indices.append(i)

    functions = []
    for i, index in enumerate(function_indices):
        if i == len(function_indices)-1:
            functions.append(source[index:])
        else:
            functions.append(source[index:function_indices[i+1]])

    try:
        assembly = []
        function_names = []
        if not functions:
            raise Exception('no valid function(s) found')

        for function in functions:
            num_parens = 0
            num_bracks = 0
            for line in function:
                for char in line: # match parentheses and brackets
                    if char == '(':   num_parens += 1
                    elif char == ')': num_parens -= 1
                    elif char == '{': num_bracks += 1
                    elif char == '}': num_bracks -= 1
            if num_parens != 0 or num_bracks != 0:
                raise Exception('mismatched parentheses or brackets')

            head = compiler.read_head(function[0])
            returnType = head[0]
            functionName = head[1]
            if head[2] and head[3]:
                compiler.declaration += 1
                parameter = {
                    'type': head[2],
                    'name': head[3],
                    'address': -(compiler.declaration*4),
                    'codeType': 'declaration'
                }
                function_names.append((functionName, 'function', 1))
            else:
                parameter = {
                    'type': '',
                    'name': ''
                }
                function_names.append((functionName, 'function', 0))

            instruction = compiler.read_instruction(1, function)['statement'] # ignore the first line
            functionClass = Function(returnType, functionName, parameter, instruction)
            obj = functionClass.get_object()
            assembly += MethodGenerator(obj).getObject()
            compiler.identifiers = function_names # clear local variables, keep global variables (function names)

        machineCode = MachineCode(assembly, (compiler.declaration+1)*-4).getObject()
        return jsonify({'assembly': assembly, 'machineCode': machineCode})
    except Exception as e:
        return jsonify(str(e)), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)
