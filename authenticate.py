#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Função auxiliar para autenticação na 
API Spacewalk por estes scripts.

Paulo Ferraz - matricula
paulo_ferraz@example.com

Uso:
login = authenticate()    
login = authenticate(SATELLITE_URL, SATELLITE_LOGIN, SATELLITE_SENHA)
login['cliente'].auth.logout(login['sessao'])

Histórico:

v1.0 - Tue Apr 25 16:57:09 -03 2023
Versão única que faz uso do usuário de sistema
"inscription", criado no Spacewalk especificamente
para este fim.

COPYRIGHT: Este programa é GPL.
'"""

import xmlrpclib

# Constantes
SATELLITE_URL = "http://server.example.com/rpc/api"
SATELLITE_LOGIN = "inscription"
SATELLITE_SENHA = "segredo"


def authenticate(url=SATELLITE_URL, login=SATELLITE_LOGIN, senha=SATELLITE_SENHA):
    """
    Cria Obj retornando dados de
    autenticação no Spacewalk
    """

    obj = {}
    cliente = xmlrpclib.Server(url, verbose=0)
    sessao = cliente.auth.login(login, senha)

    obj["cliente"] = cliente
    obj["sessao"] = sessao

    return obj


if __name__ == "__main__":
    authenticate()
