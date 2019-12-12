#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import requests
import random
from decimal import Decimal
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()
app = Flask(__name__)
contas = [{"numero": "1234", "saldo": "100,00"}, {"numero": "4345", "saldo": "50,00"},
          {"numero": "5678", "saldo": "250,00"}]
coordenador = False
seed = 0
reg = []
replicas = []
conta = []
op = []


# Metodo post para gravar a semente
@app.route('/seed', methods=['POST'])
def post_seed():
    global seed
    if not request.json or not 'seed' in request.json:
        abort(400)
    try:
        seed = request.json.get('seed')
        return make_response(jsonify({'seed': seed}), 201)
    except:
        pass


# Método post para adicionar replicas
@app.route('/replicas', methods=['POST'])
def post_replicas():
    global coordenador, replicas
    if coordenador == False:
        if not request.json or not 'replicas' in request.json:
            abort(400)
        try:
            replicas = request.json.get('replicas')
            coordenador = True
            return make_response(jsonify({'replicas': replicas}), 201)
        except:
            pass
    else:
        return make_response(jsonify({'NO': 'RÉPLICAS JA CADASTRADAS'}), 403)


# Método para retornar a lista de ações
@app.route('/acoes', methods=['GET'])
def get_acoes():
    return make_response(jsonify({'Ações:':op}), 200)


# Metodo para retornar lista de replicas
@app.route('/replicas', methods=['GET'])
def get_replicas():
    if (coordenador):
        return make_response(jsonify({'replicas': replicas}), 200)
    else :
        return make_response(jsonify({'ERROR': 'NOT FOUND'}), 404)


# Metodo post para remover lista de replicas
@app.route('/replicas', methods=['DELETE'])
def delete_replicas():
    global coordenador, replicas
    if coordenador == True:
        coordenador = False
        replicas = []
        return make_response(jsonify({'YES': 'RÉPLICAS REMOVIDAS'}), 200)
    else:
        return make_response(jsonify({'ERROR': 'NOT FOUND'}), 404)


# Metodo post para adicionar contas
@app.route('/contas', methods=['POST'])
def post_contas():
    global contas
    if not request.json or not 'contas' in request.json:
        abort(400)
    try:
        contas = request.json.get('contas')
    except:
        pass
    return make_response(jsonify({'contas': contas}), 201)


# Metodo para retornar lista de contas
@app.route('/contas', methods=['GET'])
def get_contas():
    return jsonify({'contas': contas})


# Método para executar a ação
@app.route('/acao', methods=['POST'])
def post_acao():
    global reg
    a = dict()
    if not request.json or not 'id' in request.json:
        abort(400)
    try:
        a['id'] = request.json.get('id')
        a['operacao'] = request.json.get('operacao')
        a['conta'] = request.json.get('conta')
        a['valor'] = request.json.get('valor')
    except:
        pass
    reg.append(a)
    if verifica_conta(a['conta']):
        if coordenador:
            if votacao(a):
                if decisao(a, "put"):
                    realiza_operacao(a)
                    return make_response(jsonify({'SUCCESS': 'CREATED'}), 201)
            else:
                if decisao(a, "delete"):
                    registra(a['id'], "fail")
                    return make_response(jsonify({'FAIL': '403 Forbidden'}), 403)
            return make_response(jsonify({'ERROR': 'ALGO INESPERADO OCORREU'}), 404)
        else:
            if realiza_sorteio():
                return make_response(jsonify({'YES':'ACESSO LIBERADO'}), 200)
            else:
                return make_response(jsonify({'NO':'ACESSO NEGADO'}), 403)
    else:
        reg.pop(len(reg)-1)
        return make_response(jsonify({'ERROR': 'NOT FOUND'}), 404)


# Método para executar a ação delete
@app.route('/acao', methods=['DELETE'])
def delete_acao():
    global reg
    id = request.json.get('id')
    if coordenador:
        return make_response(jsonify({'ERROR': 'BAD REQUEST'}), 400)
    else:
        r = localiza_id(id)
        if len(r) > 0:
            reg.remove(r)
            registra(id, "fail")
            return make_response(jsonify({'YES': 'AÇÃO CANCELADA'}), 200)
        else:
            return make_response(jsonify({'ERROR': 'NOT FOUND'}), 404)


# Método para executar a ação put
@app.route('/acao', methods=['PUT'])
def put_acao():
    global reg
    id = request.json.get('id')

    if coordenador:
        return make_response(jsonify({'ERROR': 'BAD REQUEST'}), 400)
    else:
        r = localiza_id(id)
        if len(r) > 0:
            reg.remove(r)
            realiza_operacao(r)
            return make_response(jsonify({'YES': 'AÇÃO REGISTRADA'}), 200)
        else:
            return make_response(jsonify({'ERROR': 'NOT FOUND'}), 404)


# Método para registrar operação
def registra(id, status):
    global op
    o = dict()
    o['id'] = id
    o['status'] = status
    op.append(o)


# Método de localização da id
def localiza_id(id):
    for r in reg:
        if r['id'] == id:
            return r


# Método para verificar existencia da conta
def verifica_conta(conta):
    for n in contas:
        if n['numero']==conta:
            return n


# Método para realizar a operação
def realiza_operacao(a):
    global conta
    conta = verifica_conta(a['conta'])
    if a['operacao'] == "debito":
        conta['saldo'] = str(Decimal(conta['saldo'].replace(",", ".")) - Decimal(a['valor'].replace(",", "."))).replace(".",",")
    elif a['operacao'] == "credito":
        conta['saldo'] = str(Decimal(conta['saldo'].replace(",", ".")) + Decimal(a['valor'].replace(",", "."))).replace(".",",")
    registra(a['id'], "success")


# Método para realizar o sorteio
def realiza_sorteio():
    rand = random.randint(1, 10)
    if rand > 7:
        return False
    else:
        return True


# Método para realizar a decisao
def decisao(dados, verbo):
    id = dict()
    id['id'] = dados['id']
    if verbo == "put":
        req1 = requests.put(replicas[0]['endpoint'] + "/acao", json=id)
        req2 = requests.put(replicas[1]['endpoint'] + "/acao", json=id)
    else:
        req1 = requests.delete(replicas[0]['endpoint'] + "/acao", json=id)
        req2 = requests.delete(replicas[1]['endpoint'] + "/acao", json=id)
    if req1.status_code == 200 and req2.status_code == 200:
        return True
    else:
        return False


# Método para analisar fase de votação
def votacao(dados):
    req1 = requests.post(replicas[0]['endpoint'] + "/acao", json=dados)
    req2 = requests.post(replicas[1]['endpoint'] + "/acao", json=dados)
    if req1.status_code == 200 and req2.status_code == 200:
        return True
    else:
        return False

if __name__ == "__main__":
    print("Servidor no ar!")
    porta = sys.argv[1]
    app.run(host='0.0.0.0', port=porta, debug=True)