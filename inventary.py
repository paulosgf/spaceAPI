#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Retorna o levantamento dos hosts cadastrados 
no Spaccewalk, na forma de tupla:
'host': 'Oracle Linux Server release x.xx'

Paulo Ferraz - matricula
paulo_ferraz@example.com

Uso:
python ./inventary.py Ambiente
['Desenvolvimento', 'Homologacao', 'Producao']

Histórico:

v1.0 - Tue Apr 25 16:57:09 -03 2023
Versão final que retorna uma tupla
podendo ser convertida para string e
importada no DB LSUS, a fim de manter 
a sincronia entre os 2 ambientes.

COPYRIGHT: Este programa é GPL.
"""

from authenticate import authenticate
import xmlrpclib


def enum_srv(group):
    """
    Inventário periódico de servidores cadastrados
    no Spacewalk, relacionados por ambiente.
    """

    # Autenticação
    login = authenticate()
    client = login["cliente"]
    session = login["sessao"]

    # Variáveis
    lista = client.systemgroup.listSystems(session, group)
    array = {}

    if len(lista) != 0:
        for system in lista:
            array[
                str(system["hostname"]).lower()
            ] = "Oracle Linux Server release " + str(
                system["release"].replace("6Server", "6.10")
            )

    client.auth.logout(session)
    return array


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Faltou ambiente: 'Desenvolvimento', 'Homologacao', 'Producao'")
        sys.exit(1)
    else:
        print(enum_srv(sys.argv[1]))
