#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import re
from sys import platform
import pickle
from unicodedata import normalize
from datetime import date


from viacep import ViaCEP

#Funcao para validar email
def validaEmail(email):
    #Expressao regular para padrao email
    padraoEmail = re.fullmatch(r'((\w+\@)(\w+\.\w+\.*\w*)[\s+\|*\/*.+]*)',email);

    if  padraoEmail != None:
        #Se estiver no padrao, devolve o e-mail
        return padraoEmail.group(2)+padraoEmail.group(3)
    else:
        return ""

def tell_me_about(s):
    print(type(s), s)

#funcao para remover os acentos
def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

#funcao que retorna o endereco dado o cep como parametro
def retorna_Endereco(cep):
    data = ViaCEP(cep)
    endereco = data.getDadosCEP()
    if endereco == 'CEP NÃO INFORMADO' or endereco == 'CEP NÃO ENCONTRADO':
        return None, None, None, None
    else:
        return endereco['logradouro'], endereco['bairro'], endereco['localidade'], endereco['uf']

#funcao para buscar CEP a partir do endereco.
def retorna_CEP(visitante, constantes):
    if not visitante[constantes['cidade']]:
        visitante[constantes['cidade']] = 'Rio de Janeiro'
    if not visitante[constantes['uf']]:
        visitante[constantes['uf']] = 'RJ'

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
                    return "Endereco nao encontrado","","",""
                else:
                    for endereco in enderecos:
                        if endereco['bairro'].upper() == visitante[constantes['bairro']].upper() or re.search(visitante[constantes['bairro']].upper(), endereco['bairro'].upper()) or not visitante[constantes['bairro']]:
                            if not endereco['complemento']:
                                return endereco['cep'], endereco['bairro'], endereco['localidade'], endereco['uf']
                            else:
                                if visitante[constantes['numero']].isnumeric():
                                    tipo = 'par' if int(visitante[constantes['numero']]) % 2 == 0 else 'ímpar'
                                    complemento = endereco['complemento'].split(" ")
                                    if complemento[0] == "até":
                                        if len(complemento) > 2 and complemento[-1] == tipo and int(complemento[1]) >= int(visitante[constantes['numero']]):
                                            return endereco['cep'], endereco['bairro'], endereco['localidade'], endereco['uf']
                                        elif len(complemento) == 2 and int(complemento[1].split("/")[1]) >= int(visitante[constantes['numero']]):
                                            return endereco['cep'], endereco['bairro'], endereco['localidade'], endereco['uf']
                                    elif complemento[0] == "de": #and int(complemento[1]) <= int(visitante[constantes['numero']]):
                                        if complemento[1].isdigit():
                                            if complemento[2] == "a" and complemento[-1] == tipo and int(complemento[1]) <= int(visitante[constantes['numero']]) and int(complemento[3]) >= int(visitante[constantes['numero']]):
                                                return endereco['cep'], endereco['bairro'], endereco['localidade'], endereco['uf']
                                            elif complemento[2] == "ao" and complemento[3] == "fim" and complemento[-1] == tipo and int(complemento[1]) <= int(visitante[constantes['numero']]):
                                                return endereco['cep'], endereco['bairro'], endereco['localidade'], endereco['uf']
                                        else:
                                            if complemento[2] == "a" and int(complemento[1].split("/")[0]) <= int(visitante[constantes['numero']]) and int(complemento[3].split("/")[1]) >= int(visitante[constantes['numero']]):
                                                return endereco['cep'], endereco['bairro'], endereco['localidade'], endereco['uf']
                                            elif complemento[2] == "ao" and complemento[3] == "fim" and int(complemento[1].split("/")[0]) <= int(visitante[constantes['numero']]):
                                                return endereco['cep'], endereco['bairro'], endereco['localidade'], endereco['uf']
                                    elif complemento[0] == visitante[constantes['numero']] and len(complemento) == 1:
                                        return endereco['cep']
                                    elif endereco['complemento'] == visitante[constantes['numero']]+" "+visitante[constantes['complemento']]:
                                        return endereco['cep'], endereco['bairro'], endereco['localidade'], endereco['uf']
                                    elif len(complemento) == 2 and complemento[0] == 'lado' and complemento[1] == tipo:
                                        return endereco['cep'], endereco['bairro'], endereco['localidade'], endereco['uf']
                                else:
                                    return endereco['cep'], endereco['bairro'], endereco['localidade'], endereco['uf']
                        else:
                            return "","","",""
            elif enderecos != "ENDERECO NAO INFORMADO":
                return enderecos[0]['cep'], enderecos[0]['bairro'], enderecos[0]['localidade'], enderecos[0]['uf']
            else:
                return "","","",""
        elif enderecos != "ENDERECO NAO INFORMADO":
            return enderecos[0]['cep'], enderecos[0]['bairro'], enderecos[0]['localidade'], enderecos[0]['uf']

        else:
            return "","","",""
    else:
        return "","","",""

#funcao para retirar abreviacao e colocar primeira letra maiuscula
def trataNome(nome):
    if len(nome) >= 2 and nome[1] != ".":
       return nome.capitalize()
    else:
        return ""

def atribui_voluntario(visitante, constantes, voluntarios):
    achou=False
    i=0

    if not visitante[constantes['acompanhamento']] or visitante[constantes['acompanhamento']] == "" or visitante[constantes['acompanhamento']] == "\n":
        while not achou and i < len(voluntarios):
            if visitante[constantes['sexo']] != voluntarios[i][2]:
                i += 1
            else:
                achou = True
    else:
        while not achou and i < len(voluntarios):
            if visitante[constantes['acompanhamento']] != voluntarios[i][3]:
                i += 1
            else:
                achou = True
    if not achou:
        print("Voluntario nao cadastrado ", visitante[constantes['acompanhamento']])
        i = -1
    return i

def retornaMediaPonderada(voluntario):
    return voluntario[0] + (voluntario[1]/3)


def retornaVoluntatios(unidade):
    # Abrindo arquivo com voluntarios de acompanhamento
    fhAcompanhamento = open(r'acompanhamento_'+unidade+'.txt', 'r')

    voluntarios = []
    for acompanhamento in fhAcompanhamento:
        voluntario = acompanhamento.split(";")
        voluntario[0] = int(voluntario[0])
        voluntario[1] = int(voluntario[1])
        voluntarios.append(voluntario)

    fhAcompanhamento.close()

    # ordenando por quantidade de acompanhamentos
    voluntarios.sort(key=retornaMediaPonderada)

    return voluntarios

def atualizaVoluntarios(unidade, voluntarios):
    # Abrindo arquivo com voluntarios de acompanhamento
    fhAcompanhamento = open(r'acompanhamento_'+unidade+'.txt', 'w')

    for voluntario in voluntarios:
        voluntario[0] = str(voluntario[0])
        voluntario[1] = str(voluntario[1])
        fhAcompanhamento.writelines(';'.join(voluntario))

    fhAcompanhamento.close()

def geraSaida(fhOut, fhTratados, voluntarios, visitante, constantes):
    fhOut.writelines(visitante[constantes['nome']] + ";" + visitante[constantes['email']].lower() + ";;;" +
                     visitante[constantes['sexo']].lower() + ";" + visitante[constantes['estado_civil']].lower() + ";" +
                     visitante[constantes['data_nascimento']] + ";;;;;BR;" + visitante[constantes['uf']] + ";" +
                     visitante[constantes['cidade']] + ";" + visitante[constantes['cep']] + ";" +
                     visitante[constantes['rua']] + ";" + visitante[constantes['numero']] + ";" +
                     visitante[constantes['complemento']] + ";" + visitante[constantes['bairro']] + ";" + telefone +
                     ";nao_membro;17;;;;;;;;;;;;;;" + visitante[constantes['qual']] + ";;;" +
                     visitante[constantes['data_atendimento']] + ";;;;;;\n")


    visitante[constantes['observacao']] += ' Atendente Somar: ' + visitante[constantes['voluntario']]
    voluntario = atribui_voluntario(visitante, constantes, voluntarios)
    if voluntario != -1:
        if visitante[constantes['status']] == 'Sem interesse':
            voluntarios[voluntario][1] += 1
        elif visitante[constantes['status']] == 'Evangélico com interesse pela AFCC':
            voluntarios[voluntario][1] += 2
        else:
            voluntarios[voluntario][0] += 1

        fhTratados.writelines(';'.join(visitante[0:3]) + ';' + ';'.join(visitante[4:-2]) + ';' +
                              visitante[constantes['data_atendimento']] + ';' + voluntarios[voluntario][3])
    else:
        fhTratados.writelines(';'.join(visitante[0:3]) + ';' + ';'.join(visitante[4:-2]) + ';' +
                              visitante[constantes['data_atendimento']] + ';' + visitante[constantes['acompanhamento']])
    voluntarios.sort(key=retornaMediaPonderada)


#Codigo principal

if platform == 'linux':
    file = r'/home/pi/Downloads/Cadastro Visitantes - Cadastro Visitantes.tsv'
else:
    file = r'C:\Users\f8084698\Downloads\Cadastro Visitantes - Cadastro Visitantes.tsv'


#Abrindo arquivo com dados dos Visitantes
fh = open(file,'r+',encoding = 'utf8')

#Pegando o Header do Arquivo para identificar os campos
campos = fh.readline().upper().split("\t")

#inicializando indices a partir do Header do arquivo
constantes = {
    'unidade':campos.index('VISITANTE_DA'),
    'nome':campos.index('NOME_COMPLETO'),
    'cep':campos.index('CEP'),
    'rua': campos.index('ENDERECO'),
    'rua_manual': campos.index('RUA_MANUAL'),
    'numero':campos.index('NUMERO'),
    'complemento':campos.index('COMPLEMENTO'),
    'bairro':campos.index('BAIRRO'),
    'cidade':campos.index('CIDADE'),
    'uf':campos.index('UF'),
    'email':campos.index('EMAIL'),
    'autoria_email':campos.index('AUTORIZA_EMAIL'),
    'telefone':campos.index('TELEFONE'),
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
    'data_atendimento':campos.index('DATA_ATENDIMENTO'),
    'acompanhamento':campos.index('ACOMPANHAMENTO (OPCIONAL)\n')
}

fhTratados = open(r'tratados.csv','w',encoding = 'utf8')

#Abrindo Arquivo de Tratamento Manual
fhTratarManual = open(r'TratamentoManual.csv','w',encoding = 'utf8')

#inserindo Headers
fhTratarManual.writelines(";".join(campos))

erro = False
visitanteTijuca = False
visitanteCaxias = False
dup_email = {}

today = date.today()
ano = today.strftime("%Y")

#Para cada linha no arquivo de entrada
for cadastro in fh:
    cadastro = cadastro.replace(";",".")
    visitante = cadastro.split("\t")
    print(visitante)
    if visitante[constantes['rua']] == 'CEP NAO ENCONTRADO':
        visitante[constantes['rua']] = visitante[constantes['rua_manual']]
        visitante[constantes['cep']] = ''
    elif not visitante[constantes['rua']]:
        visitante[constantes['rua']] = visitante[constantes['rua_manual']]

    temp = visitante[constantes['cep']].replace("-","")
    if not temp.isnumeric():
        visitante[constantes['cep']] = None

    if not visitante[constantes['cep']] or visitante[constantes['cep']] == "#ERROR!":
        #Se visitante nao possui CEP, Busca CEP pelo endereco
        visitante[constantes['cep']], visitante[constantes['bairro']], visitante[constantes['cidade']], visitante[constantes['uf']] = retorna_CEP(visitante, constantes)
    elif not visitante[constantes['rua']] or visitante[constantes['rua']] == "#ERROR!":
        if not visitante[constantes['cep']] or visitante[constantes['cep']] == "#ERROR!":
            visitante[constantes['cep']] = ""
            visitante[constantes['rua']] = ""
            visitante[constantes['bairro']] = ""
            visitante[constantes['cidade']] = ""
            visitante[constantes['uf']] = ""
        else:
            rua, bairro, cidade, uf = retorna_Endereco(visitante[constantes['cep']])
            if rua == None:
                visitante[constantes['cep']] = ""
                visitante[constantes['rua']] = ""
                visitante[constantes['bairro']] = ""
                visitante[constantes['cidade']] = ""
                visitante[constantes['uf']] = ""
            else:
                visitante[constantes['rua']], visitante[constantes['bairro']], visitante[constantes['cidade']], visitante[constantes['uf']] = rua, bairro, cidade, uf
    elif visitante[constantes['rua']] == "#MANUAL!":
        visitante[constantes['rua']] = visitante[constantes['rua_manual']]
        visitante[constantes['cep']] = ''

    # remove acentuacao
    visitante[constantes['rua']] = remover_acentos(visitante[constantes['rua']])
    visitante[constantes['bairro']] = remover_acentos(visitante[constantes['bairro']])
    visitante[constantes['cidade']] = remover_acentos(visitante[constantes['cidade']])

    #Trata campo Nome para retirar abreviacao e Colocar primeira letra maiuscula e as outras minusculas.
    visitante[constantes['nome']]="|".join(map(trataNome, visitante[constantes['nome']].split(" ")))
    visitante[constantes['nome']] = re.sub(r'(\|+)', r' ', visitante[constantes['nome']])
    visitante[constantes['nome']] =  visitante[constantes['nome']].strip()
    #remove acentuacao
    visitante[constantes['nome']]=remover_acentos(visitante[constantes['nome']])

    # remove acentuacao
    visitante[constantes['voluntario']]=remover_acentos(visitante[constantes['voluntario']])


    visitante[constantes['telefone']] = re.sub(r'(\D*)', r'', visitante[constantes['telefone']])

    if visitante[constantes['telefone']]:
        if (len(visitante[constantes['telefone']]) == 11 and visitante[constantes['telefone']][2] == '9') or (len(visitante[constantes['telefone']]) == 9 and visitante[constantes['telefone']][0] == '9'):
            if(len(visitante[constantes['telefone']]) == 11):
                telefone =';;'+visitante[constantes['telefone']][0:2]+';'+visitante[constantes['telefone']][2:]+';;'
            else:
                telefone = ';;21;' + visitante[constantes['telefone']] + ';;'
        elif (len(visitante[constantes['telefone']]) == 10 and visitante[constantes['telefone']][2] != '9') or (len(visitante[constantes['telefone']]) == 8 and visitante[constantes['telefone']][0] != '9'):
            if (len(visitante[constantes['telefone']]) == 10):
                telefone = visitante[constantes['telefone']][0:2]+';'+ visitante[constantes['telefone']][2:]+';;;;'
            else:
                telefone = '21;'+ visitante[constantes['telefone']] +';;;;'
        else:
            telefone = ';;' + visitante[constantes['telefone']][0:2] + ';' + visitante[constantes['telefone']][2:] + ';;'
            #erro = True
            #fhTratarManual.writelines(";".join(visitante))
            #continue
    else:
        telefone = ';;;;;'

    if visitante[constantes['estado_civil']]:
        if visitante[constantes['estado_civil']][-1] == ")":
            visitante[constantes['estado_civil']] = visitante[constantes['estado_civil']][0:-3]
            visitante[constantes['estado_civil']] = remover_acentos("_".join(visitante[constantes['estado_civil']].split(" ")).lower())
        else:
            visitante[constantes['estado_civil']] = remover_acentos("_".join(visitante[constantes['estado_civil']].split(" ")).lower())
    else:
        visitante[constantes['estado_civil']]='nao_informado'

    visitante[constantes['qual']] = remover_acentos(visitante[constantes['qual']])
    visitante[constantes['email']] = remover_acentos(visitante[constantes['email']])
    visitante[constantes['email']] = validaEmail(visitante[constantes['email']])
    if visitante[constantes['email']] in dup_email:
        print(visitante[constantes['email']])
        visitante[constantes['email']] = ""
    else:
        dup_email[visitante[constantes['email']]] = 1

    visitante[constantes['data_nascimento']] = visitante[constantes['data_nascimento']].replace(ano, '1900')

    if visitante[constantes['cep']] == 'Endereco nao encontrado':
        #Se nao encontrou CEP, jogar para tratamento manual
        visitante[constantes['cep']] = ""
        visitante[constantes['rua']] = ""
        visitante[constantes['bairro']] = ""
        visitante[constantes['cidade']] = ""
        visitante[constantes['uf']] = ""

    unidade = visitante[constantes['unidade']].split("_")[1].upper()
    if unidade == "TIJUCA":
        if not visitanteTijuca:
            # Abrindo Arquivo de saida OK
            fhOutTijuca = open(r'cadastro_'+unidade+'.csv', 'w', encoding='utf8')

            #Gerando Header
            fhOutTijuca.writelines('nome_completo;email;tipo_documento;numero_documento;sexo;estado_civil;'
                                   'data_nascimento;apelido;login_skype;trabalho;cargo;pais;estado;cidade;cep;'
                                   'logradouro;numero_logradouro;complemento_logradouro;bairro;ddd_telefone_fixo;'
                                   'numero_telefone_fixo;ddd_telefone_celular;numero_telefone_celular;'
                                   'ddd_telefone_outro;numero_telefone_outro;tipo_vinculo;status;imagem_perfil;'
                                   'id_sistema_legado;Filhos;data_de_casamento;data_de_entrada;data_de_saida;'
                                   'facebook;grau_de_escolaridade;quantidade_de_filhos  ;nome_pai;nome_mae;'
                                   'nome_conjuge;consagracao;ultima_igreja_que_frequentou;data_de_batismo;'
                                   'voluntariado;data_filiacao;informacoes_extras_membro;nome_da_celula;batizado;'
                                   'curso_biblico;tamanho_blusa;confirmacao\n')

            #Pegando Voluntarios da Tijuca
            voluntarios_tijuca = retornaVoluntatios(unidade)
            visitanteTijuca = True

        # Gerando saida
        geraSaida(fhOutTijuca, fhTratados, voluntarios_tijuca, visitante, constantes)
    elif unidade == "CAXIAS":
        if not visitanteCaxias:

            # Abrindo Arquivo de saida OK
            fhOutCaxias = open(r'cadastro_' + unidade + '.csv', 'w', encoding='utf8')

            #Gerando Header
            fhOutCaxias.writelines('nome_completo;email;tipo_documento;numero_documento;sexo;estado_civil;'
                                   'data_nascimento;apelido;login_skype;trabalho;cargo;pais;estado;cidade;cep;'
                                   'logradouro;numero_logradouro;complemento_logradouro;bairro;ddd_telefone_fixo;'
                                   'numero_telefone_fixo;ddd_telefone_celular;numero_telefone_celular;'
                                   'ddd_telefone_outro;numero_telefone_outro;tipo_vinculo;status;imagem_perfil;'
                                   'id_sistema_legado;Filhos;data_de_casamento;data_de_entrada;data_de_saida;'
                                   'facebook;grau_de_escolaridade;quantidade_de_filhos  ;nome_pai;nome_mae;'
                                   'nome_conjuge;consagracao;ultima_igreja_que_frequentou;data_de_batismo;'
                                   'voluntariado;data_filiacao;informacoes_extras_membro;nome_da_celula;batizado;'
                                   'curso_biblico;tamanho_blusa;confirmacao\n')

            # Pegando Voluntarios da Caxias
            voluntarios_caxias = retornaVoluntatios(unidade)
            visitanteCaxias = True
        # Gerando saida
        geraSaida(fhOutCaxias, fhTratados, voluntarios_caxias, visitante, constantes)
    else:
        print("ERRO: Unidade nao tratada")
        exit(12)



#Fecha arquivos do processamento
fh.close()
fhTratados.close()
fhTratarManual.close()

if visitanteTijuca:
    atualizaVoluntarios("TIJUCA", voluntarios_tijuca)
    fhOutTijuca.close()

if visitanteCaxias:
    atualizaVoluntarios("CAXIAS", voluntarios_caxias)
    fhOutCaxias.close()

#Se nao teve erro. Remove arquivo.
if not erro:
    os.unlink(fhTratarManual.name)
