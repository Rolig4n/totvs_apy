import requests as re

url_webhook = "https://backend.botconversa.com.br/api/v1/webhooks-automation/catch/135369"
header = {
    "Content-Type": "application/json",
    "X-Frame-Options" : "DENY",
    "X-Frame-Options": "SAMEORIGIN",
    "Connection": "keep-alive"
}

def webhook(data, mesref):
    body = {
        "telefone": data["telefone"],
        "mensagem": """Prezado {}, para sua comodidade segue o seu boleto referente parcela do mês de {}.\n\nsegue código de barras para facilitar seu pagamento:\n*{}*\n\nBoleto também está disponível no Portal do Aluno para pagamento.\n*Lembramos ainda que o prazo para pagamento com os descontos de antecipação e bolsas encerra-se todo dia 05 de cada mês.*\nQualquer dificuldade no acesso ao boleto, entre em contato com nosso atendimento financeiro: Telefone e WhatsApp: (34) 3411-9700\nPortal do Aluno: http://facfama.eunanuvem.com.br/FrameHTML/web/app/edu/PortalEducacional/login/\n*Obs.: Caso o boleto tenha sido quitado, desconsiderar esse aviso.*
        """.format(data["nome"], mesref, data["boleto"])
    }
    
    try:
        response = re.post("{}/{}/".format(url_webhook, "v2Du8J72hoVk"), headers=header, json=body)
        if response.status_code == 200:
            return True
        else:
            return False
    except re.exceptions.RequestException as e:
        return False
