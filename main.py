from flask import Flask, jsonify, make_response
import totvs
from datetime import datetime
from dateutil.relativedelta import relativedelta
data_atual = datetime.now()

app = Flask(__name__)

@app.route("/")
def hello_world():
    # Busca os boletos na TOTVS
    data_atual = data_atual + relativedelta(months=1)
    boletos = totvs.GetBoletos(data_atual=data_atual)
    # Envia os boletos para o Bot - WH = WebHook - configurado na plataforma do próprio Botconversa
    resposta = bot.SendBoletosWH()
    return make_response(200, jsonify({"resposta": resposta}))