#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Remove todas tarefas penduradas
em action chains, que impedem
a criação de novas tarefas agendadas

Paulo Ferraz - matricula
paulo_ferraz@example.com

Uso:
	python ./emptyActionChain.py

Histórico:

v1.0 - Mon Jun 12 15:51:47 -03 2023

COPYRIGHT: Este programa é GPL.
"""

import xmlrpclib, sys
from authenticate import authenticate


def emptyActionChain():
    """
    Retorna nome action chain removida
    ou aviso de que não existem.
    """

    # Autenticação
    login = authenticate()
    client = login["cliente"]
    session = login["sessao"]

    # ID da chain
    chainId = client.actionchain.listChains(session)
    try:
        chainName = chainId[0]["label"]
    except IndexError:
        print("ERRO: Não há action chains!")
        sys.exit()
    if chainName:
        client.actionchain.deleteChain(session, chainName)

    # Encerra sessão
    client.auth.logout(session)

    return chainName


if __name__ == "__main__":
    print(emptyActionChain())
