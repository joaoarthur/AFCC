#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import requests
from sys import exit

__version__ = '1.3.1'


class ViaCEP:

    def __init__(self, cep=None, uf=None, cidade=None, rua=None):
        self.__cep = cep
        self.__uf = uf
        self.__cidade = cidade
        self.__rua = rua

    def getDadosCEP(self):
        if self.__cep:
            url_api = ('http://www.viacep.com.br/ws/%s/json' % self.__cep)
            req = requests.get(url_api)
            if req.status_code == 200:
                dados_json = json.loads(req.text)
                return dados_json
        else:
            return 'CEP NÃO INFORMADO'

    def getDadosEndereco(self):
        if self.__rua:
            if self.__cidade:
                cidade_temp = self.__cidade.split(" ")
                self.__cidade = "%20".join(cidade_temp)
            else:
                self.__cidade = "rio%20de%20janeiro"
            if not self.__uf:
                self.__uf = "RJ"
            rua_temp = self.__rua.split(" ")
            self.__rua = "%20".join(rua_temp)
            url_api = ('http://viacep.com.br/ws/' + self.__uf + '/' + self.__cidade + '/' + self.__rua + '/json/')
            req = requests.get(url_api)
            if req.status_code == 200:
                dados_json = json.loads(req.text)
                if not dados_json[0]['logradouro'] and not dados_json[0]['bairro']:
                    return None
                else:
                    return dados_json
            else:
                return None
        else:
            return 'ENDERECO NAO INFORMADO'
