#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Clona canal 7 \ 8 Updates e ksplice kernel DEVGRP.
Cadastra sistemas no clone.
Remove clones anteriores.

Paulo Ferraz - matricula
paulo_ferraz@example.com

Uso:
python ./clonechannel.py
	Informar a versão
	numérica do canal.
	Padrão 7

Histórico:

v1.0 - Tue Apr 25 16:57:09 -03 2023
Versão final que cria novos clones nos padrões:
	Ksplice (kernel)-DEVGRP_KSP_${data atual}
	Updates - x86_64-DEVGRP_UP_${data atual}
A partir de então, todos os sistemas são
migrados para estes novos clones automaticamente,
mantendo assim a uniformização do ambiente.

v1.1 - Tue Sep  5 09:28:14 -03 2023
Adaptação das funções para lidar com mudanças de
release menor.

Adição de funções separadas para clonar canais
release maior 8 e 9.

Função main() ajustada para chamar as necessárias
conforme a release maior clonada.

COPYRIGHT: Este programa é GPL.
"""

from authenticate import authenticate
import re
import time
import xmlrpclib

# Constantes globais Release Menor
CURRENTREL7 = 9
CURRENTREL8 = 8
CURRENTREL9 = 2


def cloneChannelUp(release=7):
    """
    Autentica no Spacewalk.
    Define clone canal 7/8/9 Updates.
    """

    # Incrementar a cada nova versão
    # Constante Release Menor Oracle 7
    currentRel7 = CURRENTREL7
    # Constante Release Menor Oracle 8
    currentRel8 = CURRENTREL8
    # Constante Release Menor Oracle 9
    currentRel9 = CURRENTREL9

    # Autenticação
    login = authenticate()
    client = login["cliente"]
    session = login["sessao"]

    # Variáveis
    ret = {}
    channels = client.channel.listSoftwareChannels(session)
    if release == 7:
        ref = client.channel.software.getDetails(
            session, "oraclelinux_r7_u" + str(currentRel7) + "-updates-x86_64"
        )
        pattern = "oraclelinux_r7_u" + str(currentRel7) + "-updates-x86_64_devgrp_up"
    elif release == 8:
        ref = client.channel.software.getDetails(
            session, "oraclelinux_r8_u" + str(currentRel8) + "-updates-x86_64"
        )
        pattern = "oraclelinux_r8_u"
    elif release == 9:
        ref = client.channel.software.getDetails(
            session, "oraclelinux_r9_u" + str(currentRel9) + "-updates-x86_64"
        )
        pattern = "oraclelinux_r9_u"

    refLabel = ref["label"]
    refSummary = ref["summary"]
    parent = ref["parent_channel_label"]
    today = time.strftime("%Y%m%d")
    entry = [
        item
        for item in channels
        if re.search(pattern + "[0-9]+-updates-x86_64_devgrp_up", str(item))
    ]

    # Lógica principal
    try:
        if entry[0].values():
            cloneOld = [
                item for item in entry[0].values() if re.search(pattern, str(item))
            ]
            cloneOldInfo = client.channel.software.getDetails(session, cloneOld[0])
            cloneNew = "clone-" + refLabel + "_devgrp_up_" + today
            cloneNewInfo = "Clone " + refSummary + "-DEVGRP_UP_" + today
            cloneRefLabel = cloneOldInfo["clone_original"]
    except IndexError:
        print("Atenção: Não há Clone de canal DEVGRP Updates!!!")

    ret = {
        "retCloneOldLabel": cloneRefLabel,
        "retClonOld": cloneOld,
        "retClonOldInfo": cloneOldInfo,
        "retClonNew": cloneNew,
        "retClonNewInfo": cloneNewInfo,
        "retCloneParent": parent,
    }

    # Encerra sessão
    client.auth.logout(session)

    # Retorna nome e descrição clone novo; nome, info, origem clone anterior; nome pai
    return ret


def cloneChannelKplc(release=7):
    """
    Autentica no Spacewalk.
    Define clone canal 7 ksplice.
    """

    # Autenticação
    login = authenticate()
    client = login["cliente"]
    session = login["sessao"]

    # Variáveis
    ret = {}
    channels = client.channel.listSoftwareChannels(session)
    if release == 7:
        ref = client.channel.software.getDetails(
            session, "oraclelinux_r7_ksplice_kernel"
        )
        pattern = "oraclelinux_r7_ksplice_kernel" + "_devgrp_ksp"

    refLabel = ref["label"]
    refSummary = ref["summary"]
    parent = ref["parent_channel_label"]
    today = time.strftime("%Y%m%d")
    entry = [item for item in channels if re.search(pattern, str(item))]

    # Lógica principal
    try:
        if entry[0].values():
            cloneOld = [
                item for item in entry[0].values() if re.search(pattern, str(item))
            ]
            cloneOldInfo = client.channel.software.getDetails(session, cloneOld[0])
            cloneNew = "clone-" + refLabel + "_devgrp_ksp_" + today
            cloneNewInfo = "Clone " + refSummary + "-DEVGRP_KSP_" + today
            cloneRefLabel = cloneOldInfo["clone_original"]
    except IndexError:
        print("Atenção: Não há Clone de canal DEVGRP Ksplice!!!")

    ret = {
        "retCloneOldLabel": cloneRefLabel,
        "retClonOld": cloneOld,
        "retClonOldInfo": cloneOldInfo,
        "retClonNew": cloneNew,
        "retClonNewInfo": cloneNewInfo,
        "retCloneParent": parent,
    }

    # Encerra sessão
    client.auth.logout(session)

    # Retorna nome e descrição clone novo; nome, info, origem clone anterior; nome pai
    return ret


def cloneChannelLate(release=8):
    """
    Autentica no Spacewalk.
    Define clone canal 8/9 Latest.
    """

    # Incrementar a cada nova versão
    # Constante Release Menor Oracle 8
    currentRel8 = CURRENTREL8
    # Constante Release Menor Oracle 9
    currentRel9 = CURRENTREL9

    # Autenticação
    login = authenticate()
    client = login["cliente"]
    session = login["sessao"]

    # Variáveis
    ret = {}
    channels = client.channel.listSoftwareChannels(session)

    if release == 8:
        ref = client.channel.software.getDetails(
            session, "oraclelinux_r8_latest-x86_64"
        )
        pattern = "oraclelinux_r8_latest-x86_64_devgrp_late_"
    elif release == 9:
        ref = client.channel.software.getDetails(
            session, "oraclelinux_r9_latest-x86_64"
        )
        pattern = "oraclelinux_r9_latest-x86_64_devgrp_late_"

    refLabel = ref["label"]
    refSummary = ref["summary"]
    parent = ref["parent_channel_label"]
    today = time.strftime("%Y%m%d")
    entry = [item for item in channels if re.search(pattern, str(item))]

    # Lógica principal
    try:
        if entry[0].values():
            cloneOld = [
                item for item in entry[0].values() if re.search(pattern, str(item))
            ]
            cloneOldInfo = client.channel.software.getDetails(session, cloneOld[0])
            cloneNew = "clone-" + refLabel + "_devgrp_late_" + today
            cloneNewInfo = "Clone " + refSummary + "-DEVGRP_LATE_" + today
            cloneRefLabel = cloneOldInfo["clone_original"]
    except IndexError:
        print("Atenção: Não há Clone de canal DEVGRP Latest!!!")

    ret = {
        "retCloneOldLabel": cloneRefLabel,
        "retClonOld": cloneOld,
        "retClonOldInfo": cloneOldInfo,
        "retClonNew": cloneNew,
        "retClonNewInfo": cloneNewInfo,
        "retCloneParent": parent,
    }

    # Encerra sessão
    client.auth.logout(session)

    # Retorna nome e descrição clone novo; nome, info, origem clone anterior; nome pai
    return ret


def systemSubscribClone(
    cloneUpOld, cloneUpNew, Release, cloneAuxOld=None, cloneAuxNew=None
):
    """
    Autentica no Spacewalk.
    Inscreve sistemas no canal clone.

    Uso: systemSubscribClone(ret["retClonOld"], ret["retClonNew"], Release)
    """

    # TODO
    # Implementar a função cloneChannelApp()
    # para cadastrar hosts 8 & 9 a fim de 
    # evitar quebra de dependências com
    # os outros clones

    # Incrementar a cada nova versão
    # Constante Release Menor Oracle 8
    currentRel8 = CURRENTREL8
    # Constante Release Menor Oracle 9
    currentRel9 = CURRENTREL9

    # Autenticação
    login = authenticate()
    client = login["cliente"]
    session = login["sessao"]

    # Variáveis  & constantes
    ORADEHO = "DBGRP_Oracle_Dev_e_Hom"
    ORAPROD = "DBGRP_Oracle_Producao"
    ora_hosts = []
    hosts = []
    ret = 0

    # Sistemas no canal antigo
    if Release == 7:
        inventary = client.channel.software.listSubscribedSystems(
            session, "".join(cloneUpOld)
        )
        # Cadastra sistemas no canal clone
        for ic in inventary:
            try:
                dic = []
                chan = []
                dic = client.channel.software.listSystemChannels(session, ic["id"])
                ch = {}
                for ch in dic:
                    # nao cadastra nos clones Updates e Ksplice anterirores
                    if not (ch["label"] == cloneUpOld or ch["label"] == cloneAuxOld):
                        # cadastra nos demais canais anteriormente cadastrados
                        chan.append(ch["label"])
                # cadastra nos novos clones Updates e Ksplice
                chan.append(cloneUpNew)
                chan.append(cloneAuxNew)
                client.system.setChildChannels(session, ic["id"], chan)
            except xmlrpclib.Fault as (errno, strerror):
                print("ERROR: {}".format(strerror))
                ret = errno
        # Apaga clone latest Ksplice e Updates se retorno Ok
        if ret == 0:
            removeOldClone(cloneAuxOld)
            removeOldClone(cloneUpOld)
    elif Release == 8:
        # Info do Base 8 mais recente
        pattern = "oraclelinux_r8_u"
        base = client.channel.software.getDetails(
            session, str(pattern) + str(currentRel8) + "-base-x86_64"
        )
    elif Release == 9:
        # Info do Base 9 mais recente
        pattern = "oraclelinux_r9_u"
        base = client.channel.software.getDetails(
            session, str(pattern) + str(currentRel9) + "-base-x86_64"
        )

    if Release == 8 or Release == 9:
        # Exclusões DB Oracle dispensadas da atualização
        oracle = client.systemgroup.listSystemsMinimal(session, ORADEHO)
        oracle += client.systemgroup.listSystemsMinimal(session, ORAPROD)
        for system in oracle:
            ora_hosts.append(system["name"].lower())

        # Relaçao de todos canais disponiveis
        channels = client.channel.listSoftwareChannels(session)

        # BASE + ATUAL:
        mostCurrentBase = base["label"]

        # Array com todos release menor deste base maior
        major = [
            item for item in channels if re.search(pattern + "[0-9]+-base", str(item))
        ]
        # Para cada release menor agrupa os sistemas cadastrados
        for minor in major:
            dic = []
            dic.append(
                client.channel.software.listSubscribedSystems(session, minor["label"])
            )
            # BASE ORIGINAL:
            primaryBase = minor["label"]
            # UPDATES ORIGINAL:
            primaryUpdate = minor["label"].replace("-base-x86_64", "-updates-x86_64")
            # LATEST ORIGINAL:
            primaryLatest = re.sub(
                r"_u\d+-base-x86_64", r"_latest-x86_64", minor["label"]
            )
            hosts = [leaf for sub in dic for leaf in sub]
            # Remoção da relação final de hosts
            # pertencentes aos grupos Oracle
            for h in ora_hosts:
                for i in hosts:
                    if i["name"] == h:
                        print("Host Oracle sendo removido: " + i["name"])
                        hosts.remove(i)

            for item in hosts:
                # Novos canais a se cadastrar os hosts
                newch = []
                newch.append(mostCurrentBase)
                newch.append(cloneUpNew)
                newch.append(cloneAuxNew)
                # Canais excluidos do novo cadastro
                if primaryBase != mostCurrentBase:
                    oldch = [
                        primaryBase,
                        primaryUpdate,
                        primaryLatest,
                        "".join(cloneUpOld),
                        "".join(cloneAuxOld),
                    ]
                else:
                    oldch = [
                        primaryUpdate,
                        primaryLatest,
                        "".join(cloneUpOld),
                        "".join(cloneAuxOld),
                    ]
                # remove dos canais clone antigos, caso estiver cadastrado
                try:
                    chan = client.system.listSubscribedChildChannels(
                        session, item["id"]
                    )
                    for (index, ch) in enumerate(chan):
                        if ch["label"] not in oldch:
                            newch.append(ch["label"])
                    # Para remover do canal base e updates antigos
                    # é só deixar eles fora do novo cadastramento.

                    # Cadastra no base mais atual, além do novo clone e
                    # outros canais anteriores que não o base e updates.
                    client.system.setChildChannels(session, item["id"], newch)
                except xmlrpclib.Fault as (errno, strerror):
                    print("ERROR: {}".format(strerror))
                    ret = errno
            # Apaga clone Updates release menor antigo se retorno Ok
            if ret == 0:
                removeOldClone(cloneUpOld)
        # Apaga clone latest antigo se retorno Ok
        if ret == 0:
            removeOldClone(cloneAuxOld)

    # Encerra sessão
    client.auth.logout(session)

    # Retorna eventual codigo exceção ou 0, se Ok
    return ret


def removeOldClone(ClonOld):
    """
    Remove clone anterior, se não houver inscritos nele.

    Uso: removeOldClone(ret["retClonOld"])
    """

    # Autenticação
    login = authenticate()
    client = login["cliente"]
    session = login["sessao"]

    # Remove canal clone anterior
    if not client.channel.software.listSubscribedSystems(session, "".join(ClonOld)):
        client.channel.software.delete(session, "".join(ClonOld))
    else:
        print(
            "Canal "
            + "".join(ClonOld)
            + " nao removido, pois contem sistemas inscritos!!!"
        )

    # Encerra sessão
    client.auth.logout(session)


def main():
    """
    Função principal que chama as auxiliares
    """

    # Autenticação
    login = authenticate()
    client = login["cliente"]
    session = login["sessao"]

    # Variáveis / constantes
    DEBUG = False
    default = 7
    release = int(raw_input("Informe a release Oracle Linux (7): ") or default)
    if release == 7:
        ksplice = cloneChannelKplc(release)
    elif release == 8 or release == 9:
        latest = cloneChannelLate(release)
    updates = cloneChannelUp(release)
    original_state = False

    # Clona canal Updates
    original_label = updates["retCloneOldLabel"]
    channel_details = {
        "name": updates["retClonNewInfo"],
        "label": updates["retClonNew"],
        "summary": updates["retClonNewInfo"],
        "parent_label": updates["retCloneParent"],
        "checksum": "sha256",
    }

    # Clona canal e retorna seu ID
    if not DEBUG:
        cloneUpNew = client.channel.software.clone(
            session, original_label, channel_details, original_state
        )
        print(
            "Detalhes clone updates = "
            + str(client.channel.software.getDetails(session, cloneUpNew))
        )

    # Clona canal ksplice caso release maior for 7
    if release == 7:
        original_label = ksplice["retCloneOldLabel"]
        channel_details = {
            "name": ksplice["retClonNewInfo"],
            "label": ksplice["retClonNew"],
            "summary": ksplice["retClonNewInfo"],
            "parent_label": ksplice["retCloneParent"],
            "checksum": "sha256",
        }
        # Clona canal e retorna seu ID
        if not DEBUG:
            cloneKplcNew = client.channel.software.clone(
                session, original_label, channel_details, original_state
            )
            print(
                "Detalhes clone ksplice = "
                + str(client.channel.software.getDetails(session, cloneKplcNew))
            )

    # Clona canal latest caso release maior for 8 ou 9
    if release == 8 or release == 9:
        original_label = latest["retCloneOldLabel"]
        channel_details = {
            "name": latest["retClonNewInfo"],
            "label": latest["retClonNew"],
            "summary": latest["retClonNewInfo"],
            "parent_label": latest["retCloneParent"],
            "checksum": "sha256",
        }
        # Clona canal e retorna seu ID
        if not DEBUG:
            cloneLateNew = client.channel.software.clone(
                session, original_label, channel_details, original_state
            )
            print(
                "Detalhes clone latest = "
                + str(client.channel.software.getDetails(session, cloneLateNew))
            )

    if release == 7 and not DEBUG:
        # Clone Updates novo e anterior
        regClonNewUp = client.channel.software.getDetails(session, cloneUpNew)["label"]
        regClonOldUp = updates["retClonOldInfo"]["label"]
        # Clone ksplice novo e anterior
        regClonNewKp = client.channel.software.getDetails(session, cloneKplcNew)[
            "label"
        ]
        regClonOldKp = ksplice["retClonOldInfo"]["label"]
        # Cadastra sistemas em clones updates e ksplice, além de apagar canais antigos, se retorno Ok
        status = systemSubscribClone(
            regClonOldUp, regClonNewUp, release, regClonOldKp, regClonNewKp
        )

    elif release == 8 or release == 9 and not DEBUG:
        # Clone Updates novo e anterior
        regClonNewUp = client.channel.software.getDetails(session, cloneUpNew)["label"]
        regClonOldUp = updates["retClonOldInfo"]["label"]
        # Clone Latest novo e anterior
        regClonNewLate = client.channel.software.getDetails(session, cloneLateNew)[
            "label"
        ]
        regClonOldLate = latest["retClonOldInfo"]["label"]
        # Cadastra sistemas em clones updates e latest, além de apagar canais antigos, se retorno Ok
        status = systemSubscribClone(
            regClonOldUp, regClonNewUp, release, regClonOldLate
        )

    # Encerra sessão
    client.auth.logout(session)


if __name__ == "__main__":
    main()
