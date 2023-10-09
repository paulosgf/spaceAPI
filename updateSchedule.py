#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agenda atualizações dos 
clientes Spacewalk

Paulo Ferraz - matricula
paulo_ferraz@example.com

Uso:
python ./updateSchedule.py

Histórico:

v1.0 - Tue Apr 25 16:57:09 -03 2023
Versão final que faz agendamento de
atualizações seguidas de reboot 
conforme o ambiente:
- Dev \ Hom:
  Divide todo o ambiente pela 
  quantidade de ondas e escalona 
  o agendamento em datas sequenciais 
  a partir da definida. Remove grupos 
  de hosts restritos e divide os clusters
  entre sites automáticamente.
- Prod:
  Recebe um arquivo contendo os hosts
  a atualizar, um por linha e agenda em
  onda única na data definida.

COPYRIGHT: Este programa é GPL.
"""

import xmlrpclib
import math
import time
import datetime
from datetime import datetime, timedelta
from time import mktime
from authenticate import authenticate
from inventary import enum_srv
from pathlib import Path


def rebootUpdateActionChain(iso8601Time, hosts="", wave=1):
    """
    Na data agendada, cria corrente de ação
    envolvendo atualização seguida de reboot
    em qualquer ambiente.
    """

    # Variáveis
    packId = []
    retval = 1

    # Autenticação
    login = authenticate()
    client = login["cliente"]
    session = login["sessao"]

    # Agendamento
    for server in hosts:
        packId = []
        # identifica ID de cada host
        try:
            hostId = client.system.getId(session, server)[0]["id"]
        except IndexError:
            print(server + ": servidor não cadastrado!")
            continue
        # cria corrente de ação
        chainId = client.actionchain.createChain(session, "chain")
        # identifica pacotes a atualizar
        packs = client.system.listLatestUpgradablePackages(session, hostId)
        for p in range(len(packs)):
            packId.append(packs[p]["to_package_id"])
        # Se há pacotes, agenda atualização
        if packId:
            # adiciona os pacotes a corrente de ação
            client.actionchain.addPackageUpgrade(session, hostId, packId, "chain")
            # agenda reboot na sequencia de atualização
            client.actionchain.addSystemReboot(session, hostId, "chain")
            # define data e hora do agendamento no padrão ISO 8601
            retval = client.actionchain.scheduleChain(session, "chain", iso8601Time)
        else:
            print(server + ": Sem atualizações disponíveis!")
            client.actionchain.deleteChain(session, "chain")

    # Encerra sessão
    client.auth.logout(session)

    # Retorna 1 caso sucesso, exceção caso contrário.
    return retval


def schedPreProdUpdate(iso8601Time, envirom, amount):
    """
    Somente ambientes dev \ hom.
    Autentica no Spacewalk.
    Remove hosts DB Oracle da atualização.
    Escalona o ambiente.
    """

    # Variáveis & constantes
    DEBUG = False
    GROUP = "DBGRP_Oracle_Dev_e_Hom"
    oracle = {}
    ora_hosts = []
    dc1 = []
    dc2 = []
    dcGroup = []
    count = 0
    seq = 1
    grp = 0
    # Data inicial do agendamento sequencial
    incSched = iso8601Time.strftime("%Y-%m-%d %H:%M")

    # Autenticação
    login = authenticate()
    client = login["cliente"]
    session = login["sessao"]

    # Exclusões DB Oracle dispensadas da atualização
    oracle = client.systemgroup.listSystemsMinimal(session, GROUP)
    for system in oracle:
        ora_hosts.append(system["name"].lower())

    # hosts do ambiente
    hosts = enum_srv(envirom).keys()

    # Levantamento dos hosts em cluster
    for server in hosts:
        hostId = client.system.getId(session, server)[0]["id"]
        dc = client.system.getCustomValues(session, hostId)
        if ("DC" in dc) and (dc["DC"] == "1"):
            try:
                dc1.append(server)
            except KeyError:
                continue
        if ("DC" in dc) and (dc["DC"] == "2"):
            try:
                dc2.append(server)
            except KeyError:
                continue

    # Remoção da relação final de hosts
    # pertencentes aos clusters e ao grupo Oracle
    for h in ora_hosts:
        if h in hosts:
            hosts.remove(h)
        if h in dc1:
            dc1.remove(h)
        if h in dc2:
            dc2.remove(h)
    # Relação de todos os hosts em cluster
    # para remoção temporária do ambiente
    cluster = dc1 + dc2
    for h in cluster:
        hosts.remove(h)

    # Separação dos hosts nos 2 sites
    step = int(math.ceil(float(len(dc1)) / float((amount / 2))))
    for server in range(0, len(dc1), step):
        dcGroup.append(dc1[server : server + step])
    step = int(math.ceil(float(len(dc2)) / float((amount / 2))))
    for server in range(0, len(dc2), step):
        dcGroup.append(dc2[server : server + step])

    # Escalonamento de ondas do ambiente
    leng = len(hosts)
    while seq <= amount:
        wave = []
        rangelen = (leng / amount) * seq
        for h in range(count, rangelen):
            wave.append(hosts[h])
            count += 1
            if count == rangelen:
                seq += 1
                if (leng % amount) != 0:
                    if (seq - 1) == amount:
                        wave.extend(hosts[count : len(hosts) + 1])
                # Distribuição dos clusters entre ondas
                # adicionando novamente os hosts em cluster
                if grp < len(dcGroup):
                    wave += dcGroup[grp]
                    grp += 1
                print("ONDA {0}:".format(seq - 1))
                print(iso8601Time.strftime("%Y-%m-%d %H:%M"))
                print(" ".join(wave))
                # Caso o depuramento esteja desativado, realiza o agendamento
                if not DEBUG:
                    # Args data / hora ISO 8601 + onda
                    rebootUpdateActionChain(iso8601Time, wave)
                    iso8601Time = datetime.strptime(
                        incSched, "%Y-%m-%d %H:%M"
                    ) - timedelta(days=-1)
                    incSched = iso8601Time.strftime("%Y-%m-%d %H:%M")
                break

    # Encerra sessão
    client.auth.logout(session)

    # Retorna os hosts do ciclo completo
    return hosts


def schedProdUpdate(iso8601Time, hostsfile):
    """
    Somente ambiente produção.
    Autentica no Spacewalk.
    Remove eventiuais hosts DB Oracle da atualização.
    """

    # Variáveis & constantes
    DEBUG = False
    GROUP = "DBGRP_Oracle_Producao"
    hosts = []
    oracle = {}
    ora_hosts = []

    # Autenticação
    login = authenticate()
    client = login["cliente"]
    session = login["sessao"]

    # Exclusões DB Oracle dispensadas da atualização
    oracle = client.systemgroup.listSystemsMinimal(session, GROUP)
    for system in oracle:
        ora_hosts.append(system["name"].lower())

    # hosts do ambiente em onda única
    with open("./" + str(hostsfile), "r") as f:
        for line in f.readlines():
            cleanline = line.strip("\n")
            hosts.append(cleanline.lower())

    # Relação final de hosts
    for h in ora_hosts:
        if h in hosts:
            hosts.remove(h)
    print("ONDA UNICA:")
    print(" ".join(hosts))

    # Caso o depuramento esteja desativado, realiza o agendamento
    if not DEBUG:
        # Args data / hora ISO 8601 + onda
        rebootUpdateActionChain(iso8601Time, hosts)

    # Encerra sessão
    client.auth.logout(session)

    # Retorna todos os hosts desta onda
    return hosts


def main():
    while True:
        sched = raw_input("Data & Hora do agendamento 'YYYY-MM-DD HH:MM': ")
        try:
            timesched = time.strptime(sched, "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        if type(timesched) == time.struct_time:
            # Converte Datetime para ISO 8601
            iso8601Time = datetime.fromtimestamp(mktime(timesched))
            break

    while True:
        envirom = raw_input(
            "Informe o ambiente: 'Desenvolvimento', 'Homologacao', 'Producao': "
        )
        if (
            envirom == "Desenvolvimento"
            or envirom == "Homologacao"
            or envirom == "Producao"
        ):
            break
    if envirom == "Desenvolvimento" or envirom == "Homologacao":
        while True:
            amount = input("Informe a quantidade de ondas deste ciclo: ")
            if type(amount) == int:
                break
        # Arg: data \ hora, ambiente, qte ondas
        schedPreProdUpdate(iso8601Time, envirom, int(amount))
    elif envirom == "Producao":
        while True:
            hostsfile = raw_input("Informe o arquivo com os hosts, um por linha: ")
            path = Path("./" + hostsfile)
            if path:
                break
        # Arg: data \ hora, arquivo hosts
        schedProdUpdate(iso8601Time, path)


if __name__ == "__main__":
    main()
