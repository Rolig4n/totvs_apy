import os
import requests as re
import html
from base64 import b64encode
from bs4 import BeautifulSoup as BS

url = os.getenv("TOTVS_API_HOST") # Pega url do host da totvs - deve ser o mesmo
username = os.getenv("LOGIN_RM")
password = os.getenv("SENHA_RM")
basic_auth = b64encode("{}:{}".format(username,password).encode("utf-8")).decode("ascii")
header_soap = {
    "Content-Type": "text/xml; charset=utf-8",
    "Authorization": "Basic {}".format(basic_auth),
    "SOAPAction": "http://www.totvs.com/IwsConsultaSQL/RealizarConsultaSQL"
}

def GetBoletos(data_atual):
    coligada = os.getenv("COLIGADA")
    dia = 30
    if data_atual.month == 2:
        if data_atual.year%4 == 0 and (data_atual.year%100 != 0 or data_atual.year%400 == 0):
            dia = 29
        else:
            dia = 28
    data = data_atual.replace(day=dia).strftime("%Y-%m-%d 00:00:00")
    filtro = f"""FBOLETO.CODCOLIGADA={coligada} AND FBOLETO.VENCIMENTO='{data}' AND 
    FBOLETO.STATUS = 0 AND FBOLETO.CNABSTATUS in (2,5)""" # Tabela cnabstatus https://www.forumrm.com.br/topic/194-constantes-internas-dos-aplicativos-totvs-rm/#:~:text=Status%20CNAB%20(Tabela%20FLAN%20%2D%20Campo%20CNABSTATUS)%3A
    payload = f"""<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:tot=\"http://www.totvs.com/\">   
        <soapenv:Header/>
        <soapenv:Body>
            <tot:ReadView>
                <!--Optional:-->
                <tot:DataServerName>FinBoletoLanData</tot:DataServerName>
                <!--Optional:-->
                <tot:Filtro>{filtro}</tot:Filtro>
                <!--Optional:-->
                <tot:Contexto>codcoligada={coligada};codsistema=G;codusuario={username}</tot:Contexto>
            </tot:ReadView>
        </soapenv:Body>
    </soapenv:Envelope>"""
    
    try:
        header_soap["SOAPAction"] = "http://www.totvs.com/IwsDataServer/ReadView"
        response = re.post("{}/wsDataServer/IwsDataServer".format(url), headers=header_soap, data=payload)
        if response.status_code == 200:
            response_xml = response.text
            xml = to_xml(response_xml, "xml_boletos")
            new_dataset = xml.find("NewDataSet")
            if new_dataset:
                first_child = new_dataset.find(True)
                if first_child:
                    tag_name = first_child.name
                    elementos = new_dataset.find_all(tag_name)
                    boletos = []
                    boleto_null = []
                    for elemento in elementos:
                        codigo = elemento.find("IPTE")
                        if codigo != None:
                            boletos.append({
                                "IDBOLETO": elemento.find("IDBOLETO").text,
                                "SACADO": elemento.find("SACADO").text,
                                "CODIGOBARRA": codigo.text
                            })
                        else:
                            boleto_null.append({
                                "IDBOLETO": elemento.find("IDBOLETO").text,
                                "SACADO": elemento.find("SACADO").text,
                                "NOMECLIFOR": elemento.find("NOMECLIFOR").text
                            })
                    return boletos
            return False
        else:
            return f"Requisição para {response.url} retornou: {response.reason}"
    except re.exceptions.RequestException as e:
        return f"Requisição retornou erros: {e}"
    except Exception as e:
        return f"Arquivo com erros: {e}"

def to_xml(response, folder_name) -> BS:
    nome_arquivo = "{}.xml".format(folder_name)
    if not os.path.exists(nome_arquivo):
        with open(nome_arquivo, 'w') as arquivo:
            arquivo.write("")
        return False
    soup_xml = BS(response, "xml")
    pretty_xml_str = str(soup_xml)
    pretty_xml_str = html.unescape(pretty_xml_str) # Transforma os marcadores &lt; &gt; em < > respectivamente

    with open(nome_arquivo, "w", encoding="utf-8") as file:
        file.write(pretty_xml_str)
    with open(nome_arquivo, "r", encoding="utf-8") as file:
        new_xml = BS(file, "xml") # arquivo formatado identifica as tags corretamente
        faults = new_xml.find("s:Fault")
        if faults == None:
            return new_xml
        else:
            for child in faults.contents:
                if child.name == "faultstring":
                    raise Exception(str(child.string).strip())