#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verifica se as atualizações 
agendadas previamente concluiram
com sucesso ou falha

Paulo Ferraz - matricula
paulo_ferraz@example.com

Uso:
	python ./updatesVerify.py arquivo_hosts

	onde arquivo_hosts contem um servidor por 
	linha a ser verificado.

Histórico:

v1.0 - Fri Jun 16 10:10:18 -03 2023

COPYRIGHT: Este programa é GPL.
"""

import xmlrpclib, sys
from authenticate import authenticate

# TODO
# Tratar exceção qdo host não existe:
# IndexError: list index out of range

if len(sys.argv) < 2:
    print("ERRO: Faltou arquivo de hosts!")
    sys.exit()

hostsfile = str(sys.argv[1])


def verifyUpdates(hostsfile):
    """
    Verifica se as atualizações
    agendadas previamente concluiram
    com sucesso ou falha
    """

    # Variáveis
    hosts = []
    events = []

    # Autenticação
    login = authenticate()
    client = login["cliente"]
    session = login["sessao"]

    # Array de hosts
    with open("./" + str(hostsfile), "r") as f:
        for line in f.readlines():
            cleanline = line.strip("\n")
            hosts.append(cleanline.lower())

    # Retorno de falha das atualizações por host,
    # senão não retorna nada.
    for server in hosts:
        hostId = client.system.getId(session, server)[0]["id"]
        events = client.system.listSystemEvents(session, hostId, "Package Install")
        if len(events) > 0:
            stat = events[-1]["failed_count"]
            if stat == 1:
                print(server + ":")
                print(events[-1]["result_msg"])
                print("")

    # Encerra sessão
    client.auth.logout(session)

    # Em caso de erro, retorna host 
    # com sua respectiva exceção.
    # Em caso de successo, não retroana nada

    return hosts


if __name__ == "__main__":
    verifyUpdates(hostsfile)
