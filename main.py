import totvs
import random
import pandas as pd
from flask import Flask, jsonify, make_response
from time import sleep
from datetime import datetime
from dateutil.relativedelta import relativedelta

data_atual = datetime.now()

app = Flask(__name__)

@app.route("/belotos/<coligada>")
def hello_world(coligada):
    code = 200
    resposta = ""
    mes_send = 0
    mes_not_send = 0
    # Busca usuários para os boletos
    usuarios = totvs.GetContatoBoleto()
    # Busca os boletos na TOTVS
    data_atual = data_atual + relativedelta(months=1)
    mesref = "{}/{}".format(data_atual.month, data_atual.year)
    boletos = totvs.GetBoletos(data_atual=data_atual, coligada=coligada)
    if boletos==False or usuarios==False:
        code = 400
    else:
        usuarios = pd.DataFrame.from_records(usuarios)
        boletos = pd.DataFrame.from_records(boletos)
        users = pd.merge(usuarios, boletos, how="inner", left_on="CODCFO", right_on="SACADO")
        users = users.rename(columns={"CODIGOBARRA":"boleto"}).drop_duplicates()
        usuarios = users[["telefone","nome","primeiro_nome","ultimo_nome","boleto"]]
        users = usuarios.to_dict('records')
        # Envia os boletos para o Bot - WH = WebHook - configurado na plataforma do próprio Botconversa
        for user in users:
            res = bot.SendBoletosWH(user, mesref)
            random_num = random.randrange(5, 10)
            sleep(float(random_num))
            if res:
                mes_send+=1
            else:
                mes_not_send+=1
        resposta = {"mensagens_a_enviar":len(users),"mensagens_enviadas":mes_send,"mensagens_n_enviadas":mes_not_send}
    return make_response(code, jsonify({"resposta": resposta}))