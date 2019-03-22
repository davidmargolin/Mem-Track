import json
from compiler import *
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
    num_parens = 0
    num_bracks = 0
    for line in source:
        for char in line: # match parentheses and brackets
            if char == '(':   num_parens += 1
            elif char == ')': num_parens -= 1
            elif char == '{': num_bracks += 1
            elif char == '}': num_bracks -= 1
    if num_parens != 0 or num_bracks != 0:
        raise Exception('mismatched parentheses or brackets')

    compiler = Compiler()

    try:
        head = compiler.read_head(source[0])
        returnType = head[0]
        functionName = head[1]
        parameter = {
            'type': head[2],
            'name': head[3],
            'address': -(compiler.declaration*4),
            'codeType': 'declaration'
        }
        instruction = compiler.read_instruction(1, source)['statement'] # ignore the first line

        functionClass = Function(returnType, functionName, parameter, instruction)
        obj = functionClass.get_object()
        assembly = MethodGenerator(obj).getObject()
        return jsonify(assembly)
    except Exception as e:
        return jsonify(str(e)), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)
