#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from viacep import ViaCEP

def retorna_Endereco(cep):
    print(cep)
    data = ViaCEP(cep)
    endereco = data.getDadosCEP()
    print(endereco)
    if endereco == 'CEP NÃO INFORMADO':
        return None, None, None, None
    else:
        return endereco['logradouro'], endereco['bairro'], endereco['localidade'], endereco['uf']

#funcao para buscar CEP a partir do endereco.
def retorna_CEP(visitante, constantes):
    if visitante[constantes['rua']]:
        data = ViaCEP(uf=visitante[constantes['uf']], rua=visitante[constantes['rua']]+" "+visitante[constantes['numero']]+" "+visitante[constantes['complemento']], cidade=visitante[constantes['cidade']])
        enderecos = data.getDadosEndereco()
        if not enderecos:
            data = ViaCEP(uf=visitante[constantes['uf']],
                          rua=visitante[constantes['rua']] + " " + visitante[constantes['numero']], cidade=visitante[constantes['cidade']])
            enderecos = data.getDadosEndereco()
            if not enderecos:
                data = ViaCEP(uf=visitante[constantes['uf']],
                              rua=visitante[constantes['rua']],
                              cidade=visitante[constantes['cidade']])
                enderecos = data.getDadosEndereco()
                if not enderecos:
                    return "Endereco nao encontrado"
                else:
                    for endereco in enderecos:
                        if endereco['bairro'].upper() == visitante[constantes['bairro']].upper() and endereco[
                            'localidade'].upper() == visitante[constantes['cidade']].upper() and endereco['uf'].upper() == \
                                visitante[constantes['uf']].upper():
                            if not endereco['complemento']:
                                return endereco['cep']
                            else:
                                tipo = 'par' if int(visitante[constantes['numero']]) % 2 == 0 else 'ímpar'
                                complemento = endereco['complemento'].split(" ")
                                if complemento[0] == "até":
                                    if len(complemento) > 2 and complemento[-1] == tipo and int(complemento[1]) >= int(visitante[constantes['numero']]):
                                        return endereco['cep']
                                    elif len(complemento) == 2 and int(complemento[1].split("/")[1]) >= int(visitante[constantes['numero']]):
                                        return endereco['cep']
                                elif complemento[0] == "de": #and int(complemento[1]) <= int(visitante[constantes['numero']]):
                                    if complemento[1].isdigit():
                                        if complemento[2] == "a" and complemento[-1] == tipo and int(complemento[1]) <= int(visitante[constantes['numero']]) and int(complemento[3]) >= int(visitante[constantes['numero']]):
                                            return endereco['cep']
                                        elif complemento[2] == "ao" and complemento[3] == "fim" and complemento[-1] == tipo and int(complemento[1]) <= int(visitante[constantes['numero']]):
                                            return endereco['cep']
                                    else:
                                        if complemento[2] == "a" and int(complemento[1].split("/")[0]) <= int(visitante[constantes['numero']]) and int(complemento[3].split("/")[1]) >= int(visitante[constantes['numero']]):
                                            return endereco['cep']
                                        elif complemento[2] == "ao" and complemento[3] == "fim" and int(complemento[1].split("/")[0]) <= int(visitante[constantes['numero']]):
                                            return endereco['cep']
                                elif complemento[0] == visitante[constantes['numero']] and len(complemento) == 1:
                                    print(endereco)
                                    return endereco['cep']
                                elif endereco['complemento'] == visitante[constantes['numero']]+" "+visitante[constantes['complemento']]:
                                    print(endereco)
                                    return  endereco['cep']
            elif enderecos != "ENDERECO NAO INFORMADO":
                return enderecos[0]['cep']
            else:
                return enderecos
        elif enderecos != "ENDERECO NAO INFORMADO":
            return enderecos[0]['cep']
        else:
            return enderecos
    else:
        return "ENDERECO NAO INFORMADO"

#funcao para retirar abreviacao e colocar primeira letra maiuscula
def trataNome(nome):
    if len(nome) >= 2 and nome[1] != ".":
       return nome.capitalize()
    else:
        return ""

#Codigo principal

#Abrindo arquivo com dados dos Visitantes
fh = open(r'C:\Users\oi273045\Downloads\Cadastro Visitantes - Cadastro Visitantes.tsv','r',encoding = 'utf8')

#Pegando o Header do Arquivo para identificar os campos
campos = fh.readline().upper().split("\t")

#inicializando indices a partir do Header do arquivo
constantes = {
    'nome':campos.index('NOME_COMPLETO'),
    'cep':campos.index('CEP'),
    'rua':campos.index('ENDERECO'),
    'numero':campos.index('NUMERO'),
    'complemento':campos.index('COMPLEMENTO'),
    'bairro':campos.index('BAIRRO'),
    'cidade':campos.index('CIDADE'),
    'uf':campos.index('UF'),
    'email':campos.index('EMAIL'),
    'autoria_email':campos.index('AUTORIZA_EMAIL'),
    'telfone':campos.index('TELEFONE'),
    'data_nascimento':campos.index('DATA_DE_NASCIMENTO'),
    'sexo':campos.index('SEXO'),
    'estado_civil':campos.index('ESTADO_CIVIL'),
    'culto':campos.index('VISITOU_NO_CULTO'),
    'como_conheceu':campos.index('COMO_NOS_CONHECEU'),
    'membro_de_igreja':campos.index('MEMBRO_DE_ALGUMA_IGREJA_EVANGELICA'),
    'qual':campos.index('QUAL'),
    'status':campos.index('STATUS'),
    'observacao':campos.index('OBSERVACAO'),
    'voluntario':campos.index('VOLUNTARIO'),
    'data_atendimento':campos.index('DATA_ATENDIMENTO\n')
}

#Abrindo Arquivo de saida OK
fhOut = open(r'cadastro.csv','w',encoding = 'utf8')

#Abrindo Arquivo de Tratamento Manual
fhTratarManual = open(r'TratamentoManual.csv','w',encoding = 'utf8')

#inserindo Headers
#fhOut.writelines(",".join(campos))
fhOut.writelines(campos[constantes['nome']]+","+campos[constantes['data_nascimento']]+","+campos[constantes['email']]+","+campos[constantes['sexo']]+","+campos[constantes['estado_civil']]+","+campos[constantes['telfone']]+","+campos[constantes['cep']]+","+campos[constantes['rua']]+","+campos[constantes['numero']]+","+campos[constantes['complemento']]+","+campos[constantes['bairro']]+","+campos[constantes['cidade']]+","+campos[constantes['uf']]+","+campos[constantes['culto']]+","+campos[constantes['como_conheceu']]+","+campos[constantes['membro_de_igreja']]+","+campos[constantes['qual']]+","+campos[constantes['status']]+","+campos[constantes['observacao']]+","+campos[constantes['voluntario']]+","+campos[constantes['data_atendimento']])
fhTratarManual.writelines(",".join(campos))

erro=False

#Para cada linha no arquivo de entrada
for cadastro in fh:
    visitante = cadastro.split("\t")

    if not visitante[constantes['cep']] or visitante[constantes['cep']] == "#ERROR!":
        #Se visitante nao possui CEP, Busca CEP pelo endereco
        visitante[constantes['cep']] = retorna_CEP(visitante, constantes)
    elif not visitante[constantes['rua']]:
        if not visitante[constantes['cep']] or visitante[constantes['cep']] == "#ERROR!":
            erro = True
            fhTratarManual.writelines(",".join(visitante))
        else:
            visitante[constantes['rua']], visitante[constantes['bairro']], visitante[constantes['cidade']], visitante[constantes['uf']] = retorna_Endereco(visitante[constantes['cep']])
    #Trata campo Nome para retirar abreviacao e Colocar primeira letra maiuscula e as outras minusculas.
    visitante[constantes['nome']]=" ".join(map(trataNome, visitante[constantes['nome']].split(" ")))
    visitante[constantes['voluntario']]=" ".join(map(trataNome, visitante[constantes['voluntario']].split(" ")))

    if visitante[constantes['cep']] == 'ENDERECO NAO INFORMADO':
        #Se nao encontrou CEP, jogar para tratamento manual
        erro=True
        fhTratarManual.writelines(",".join(visitante))
    else:
        #fhOut.writelines(",".join(visitante))
        fhOut.writelines(visitante[constantes['nome']]+","+visitante[constantes['data_nascimento']]+","+visitante[constantes['email']]+","+visitante[constantes['sexo']]+","+visitante[constantes['estado_civil']]+","+visitante[constantes['telfone']]+","+visitante[constantes['cep']]+","+visitante[constantes['rua']]+","+visitante[constantes['numero']]+","+visitante[constantes['complemento']]+","+visitante[constantes['bairro']]+","+visitante[constantes['cidade']]+","+visitante[constantes['uf']]+","+visitante[constantes['culto']]+","+visitante[constantes['como_conheceu']]+","+visitante[constantes['membro_de_igreja']]+","+visitante[constantes['qual']]+","+visitante[constantes['status']]+","+visitante[constantes['observacao']]+","+visitante[constantes['voluntario']]+","+visitante[constantes['data_atendimento']])

#Fecha arquivos do processamento
fh.close()
fhOut.close()
fhTratarManual.close()

#Se nao teve erro. Remove arquivo.
if not erro:
    os.unlink(fhTratarManual.name)