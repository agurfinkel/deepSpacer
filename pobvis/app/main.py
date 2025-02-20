from flask import Flask, send_from_directory, jsonify, request
import json
from z3 import *
open_log('/tmp/z3log')
import metaspacer as ms

CHC = None
QUERY = None

app = Flask(__name__)
folder = '../../benchmarks/chc-comp18-benchmarks/lia/'
@app.route("/home/")
def home():

    return send_from_directory('static', 'index.html')

@app.route('/static/<path:path>')
def send_json(path):
    return send_from_directory('static', path)

@app.route("/format_node/", methods = ["POST"])
def format_node():
    global CHC, Q
    pob = request.form["pob"]
    lem = request.form["lem"]
    return jsonify(pob = pob, lem = lem)

@app.route("/execute_file/", methods = ["POST"])
def execute_file():
    global CHC, Q
    print(request.form)
    filename = request.form["filename"]
    print(folder + filename)
    query = request.form["query_text"]
    show_formula = request.form["show_formula"]
    params = json.loads(request.form["params"])
    level = int(request.form["level"])
    interactive = request.form["interactive"]
    lemmas_file = request.form["lemmas_file"]
    time = "Now"
    params["spacer.print_json"] = "static/"+filename + "." + time + ".json"
    CHC = ms.CHCProblem(folder+filename)
    if interactive and lemmas_file!="":
        Q = ms.Query(CHC, lemmas_file = lemmas_file, params = params)
    else:
        Q = ms.Query(CHC, params = params)
    if query=="": query = CHC.queries[0]
    try:
        res, _ = Q.execute(query, level = level)
        json_filename = params["spacer.print_json"]
        status = "OK"
    except Exception as e:
        res = "error"
        json_filename = ""
        status = str(e)

    if interactive:
        #overwrite old lemmas_file
        prefix = "Now"
        lemmas_file = "%s_%s_%sto%s.json"%(prefix, filename, str(level), str(params["spacer.max_level"]))
        Q.dump_lemmas(lemmas_file)

    if show_formula:
        print(folder+filename)
        with open(folder + filename, "r") as f:
            formula = f.read()
        return jsonify(debug_mess = status, result = str(res), json_filename = json_filename, formula = formula, lemmas_file = lemmas_file, internal_lemmas = Q.lemmas)
    else:
        return jsonify(debug_mess = status, result = str(res), json_filename = json_filename, lemmas_file = lemmas_file, internal_lemmas = Q.lemmas)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug = False, port=8888)
