#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Após importar novamente os clientes Spacewalk,
recadastra-os nos canais corretos
"""

from authenticate import authenticate
import xmlrpclib
import sys
import xml.etree.ElementTree as ET

# Variáveis
#file = sys.argv[1]


def reregisterChannels(file):
    """
    Para cada cliente, obtêm seus canais de backup XML
    e cadastra o cliente nestes canais.
    """
    # Variáveis
    array = []

    # Autenticação
    login = authenticate()
    client = login["cliente"]
    session = login["sessao"]

    # Analisa arquivo XML backup
    tree = ET.parse(file)
    root = tree.getroot()
    try:
        for host in range(0, len(root)):
            ic = root[host][0].tag
            print(ic)
            id = client.system.getId(session, ic)[0]["id"]
	    for chan in range(0, len(root[host][0])):
	        array.append(root[host][0][chan].text)
	    client.system.setChildChannels(session, id, array)
	    array = []
    except xmlrpclib.Fault as (errno, strerror):
        print("ERROR: {}".format(strerror))

    # Encerra sessão
    client.auth.logout(session)


if "__name__" == "__main__":
    reregisterChannels()
