import random

import pandas as pd
import numpy as np
import pulp as p


"""
Modelo matematico pergunta 2:

Parâmetros:
Volume_t = Volume de cada tubo
Peso_t = Peso de cada tubo
Volume_Final = Volume total esperado
Peso_Final = Peso total esperado
C_final = Total de containers esperado
Ordens = SO-1 e SO-2
BigM = 50

Váriaveis:
C = Binária representando cada container (A, B, C, D,E, etc)
T = Binária representando cada tubo. Ex: (A-S0_1-1)

F.O.:
Max Somatório de Tubos = sum(Ti)


Restrições:
1 - Restrição do total de containers:
    sum(Ci) = C_final 
    
2 - Peso Total:
    sum(Ti * Peso_t(i)) = Peso_Final

3 - Volume Total:
    sum(Ti * Volume_t(i)) = Volume_Final

4 - Garantia de 1 tubo por container e Ordem:

    sum(Ti) = 1  para todo Contaner e Ordem
    
5 - BigM para ativação do tubo:

    sum(Tubos) >= Ti  para todo container e ordem
    sum(Tubos) <= Ti * BigM
"""


def cria_nome_var(container, os_, pipe):
    return container + "_" + os_ + "_" + str(pipe)

def formata_dado_container(container):
    if len(container) == 1: #Se for somente uma letra, adicionar um - na frente para diferenciar!
        return "_" + container
    else:
        return container

def formata_dado_tubo(tubo):
    if len(str(tubo)) == 1:
        return "0" + str(tubo)
    else:
        return str(tubo)


if __name__ == '__main__':
    #Leitura de dados
    path = "data.xlsx"
    df_dados = pd.read_excel(path)

    #formatação de dados para tentar trabalhar com uma variável apenas!!
    df_dados['Container'] = df_dados.apply(lambda x: formata_dado_container(x['Container']), axis=1)
    df_dados['Steel Pipe'] = df_dados.apply(lambda x: formata_dado_tubo(x['Steel Pipe']), axis=1)
    df_dados['var'] = df_dados.apply(lambda x: cria_nome_var(x['Container'],x['Sales Order'],x['Steel Pipe']), axis=1)

    #constantes
    n_containers = 35
    volume_total = 5163.69
    peso_total = 18884
    BigM = 30

    #Criação dos indices!
    containers = list(pd.unique(df_dados['Container']))
    ord_s = list(pd.unique(df_dados['Sales Order']))
    tubos = [str(t) for t in pd.unique(df_dados['Steel Pipe'])]
    var_aux = list(df_dados['var'])

    #Criação dos parâmetros
    par_vol = {list(df_dados['var'])[i]: list(df_dados['Steel Pipe volume (m³)'])[i] for i in range(len(var_aux))}
    par_peso = {list(df_dados['var'])[i]: list(df_dados['Steel Pipe weight (kg)'])[i] for i in range(len(var_aux))}


    #Criação das variaveis
    var = p.LpVariable.dict("decisoes", var_aux, lowBound=0, upBound=1, cat=p.LpInteger)
    var_containers = p.LpVariable.dict("container", containers, lowBound=0, upBound=1, cat=p.LpInteger)
    #var_ord = p.LpVariable.dict("ordem", ord_s, lowBound=0, upBound=1, cat=p.LpInteger)
    # = p.LpVariable.dict("tubo", tubos, lowBound=0, upBound=1, cat=p.LpInteger)



    #Funcao Objetivo: Minimizar quantidade de containers!
    # Criação do problema no pulp
    prob = p.LpProblem("Decisao_Containers", p.LpMinimize)
    prob += (p.lpSum([var_containers[i] for i in containers]), 'Minimizar o total de containers')

    #Funcao Objetivo 2: Maximizar quantidade de tubos!
    #prob = p.LpProblem("Decisao_Containers", p.LpMaximize)
    #prob += (p.lpSum([var[i] for i in var]), 'Maximizar o total de tubos')

    #Restrições
    #Escolha de 35 containers:
    prob += (p.lpSum([var_containers[i] for i in containers]) == n_containers, 'Garante escolha dos 35 containers')

    #Restrição que garante o volume total
    prob += (p.lpSum([var[tb] * par_vol[tb] for tb in var]) == volume_total, 'Restrição que garante o volume total')

    #Restrição que garante o peso total
    prob += (p.lpSum([var[tb] * par_peso[tb] for tb in var]) == peso_total, 'Restrição que garante o peso total')

    #Garantir 1 tubo por ordem por container
    for cont in containers:
        #ordens_do_container cont
        ordens = list(pd.unique(df_dados.loc[df_dados.Container == cont]['Sales Order']))
        for os in ordens:
            tubos_ordem = list(df_dados.loc[((df_dados.Container == cont) & (df_dados['Sales Order'] == os))]['Steel Pipe'])
            prob += (p.lpSum([var[cria_nome_var(cont, os, tb)] for tb in tubos_ordem]) <= 1,
                     f'Garante que 1 tubo do container {cont} e os {os} sera escolhido')

    #Ativação do container !!!!
    for cont in containers:
        ordens_cont = list(pd.unique(df_dados.loc[df_dados.Container == cont]['Sales Order']))
        list_tubos = list()
        for os in ordens_cont:
            tubos_ordem = list(df_dados.loc[((df_dados.Container == cont) & (df_dados['Sales Order'] == os))]['Steel Pipe'])
            for tb in tubos_ordem: #Ver Itertools!!!
                list_tubos.append(var[cria_nome_var(cont, os, tb)]) #estou fazendo a mesma coisa várias vezes. criar estrutura uma vez só!!

        prob += (p.lpSum([p for p in list_tubos]) >= var_containers[cont], f'BigM ativacação inf cont {cont}')
        prob += (p.lpSum([p for p in list_tubos]) <= var_containers[cont] * BigM , f'BigM ativacação sup cont {cont}')

    #Chamada do solver
    prob.solve()

    #Pos otimização
    tubos_final = [v for v in prob.variables() if "decisoes" in v.name and v.varValue > 0.0]
    containers_final = [v for v in prob.variables() if "container" in v.name and v.varValue > 0.0]

    #conferencia quantidades
    print(f'Total de containers: {len(containers_final)}')
    print(f' Total de tubos: {len(tubos_final)}')

    #Conferencia peso e volume
    print(f'Volume total: {sum(par_vol[v.name[9:]] for v in tubos_final)}')
    print(f'Peso total: {sum(par_peso[v.name[9:]] for v in tubos_final)}')

    for v in prob.variables():
        if v.varValue == 0.0:
            continue
        print(v.name, "=", v.varValue)


    """
    Resposta questão 1:
    Solução encontrada de acordo como o print da linha 116
    
    
    Resposta questão 2:
    
    Existe mais de uma solução otima e que pode ser encontrada, por exemplo, ao alterarmos a função objetivo.
    Por exemplo, pode-se colocar a função objetivo como sendo minimizar o total de containers, ou então minimizar ou até
    maximizar (conforme testado descomentando as linhas 64 e 65) a quantidade de tubos selecionados. 
    
    Na opção de minimizar os containers a solução retorna 44 tubos, enquanto na opção de maximização a quantidade 
    de tubos é 54.
    
    """