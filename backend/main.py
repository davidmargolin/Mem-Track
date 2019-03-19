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
    compiler = Compiler()
    head = compiler.read_head(source[0])
    returnType = head[0]
    functionName = head[1]
    parameter = {
        'type': head[2],
        'name': head[3],
        'address': -(compiler.declaration*4),
        'codeType': 'declaration'
    }
    instruction = compiler.read_instruction(1, source)['statement']   # ignore the first line

    functionClass = Function(returnType, functionName, parameter, instruction)
    obj = functionClass.get_object()
    assembly = MethodGenerator(obj).getObject()
    return jsonify(assembly)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
