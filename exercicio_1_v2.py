import random

import pandas as pd
import numpy as np
import pulp as p


if __name__ == '__main__':
    #Criação das estâncias
    random.seed(1000)

    numero_atividades = 10
    hora_inicio = 1

    setup_max = 2.2
    tempo_processo_max = 15
    atividades = [at for at in range(numero_atividades)]
    predecessor_atv = [(t,j) for t in atividades for j in atividades]
    var_linear = [(t,j) for t in atividades for j in atividades]



    #liberacao da data em horas!
    tempo_processo = [round(tempo_processo_max * random.random(), 2) for _ in range(numero_atividades)]
    tempo_setup = [round(setup_max * random.random(), 2) for _ in range(numero_atividades)]
    #tempo_atv = [round(tempo_processo[i] + tempo_setup[i],2) for i in range(len(tempo_setup))]
    tempo_atv = [11.75, 12.19, 2.56, 6.31, 8.59, 8.93, 16.62, 2.0, 11.9, 6.49, 9.12] #, 5.13, 12.15, 3.8, 8.41]
    tempo_atv = {i: tempo_atv[i] for i in atividades}
    Upper = sum(tempo_atv) + 1
    Lower = 1
    #hora fim precisa ser maior que a tempo máximo de processo e tempo_setup
    hora_fim = np.ceil(sum(tempo_atv[t] for t in tempo_atv.keys())) + 10

    #Tomar cuidado para não gerar modelo infeasbile
    #data_liberacao = [min(tempo_processo) + round(setup_max) + random.randint(hora_inicio + 20, hora_fim) for _ in range(numero_atividades)]
    data_liberacao = [39.49, 58.49, 83.49, 106.49, 90.49, 67.49, 68.49, 100.49, 133.49, 39.49, 84.49] #, 105.49, 126.49, 102.49, 133.49]
    data_liberacao = {i: data_liberacao[i] for i in atividades}

    #Criação do problema:
    prob = p.LpProblem('Problema_Scheduling', p.LpMinimize)

    #Variaveis:
    makespan = p.LpVariable.dicts("makespan", [0] ,lowBound=0,  cat=p.LpContinuous)

    #Fim do processamento da atividade I
    fim_atividade = p.LpVariable.dicts("fim atividade", atividades, cat=p.LpContinuous)

    #Atividade i é produzido antes da atividade j
    var_seq = p.LpVariable.dicts("sequenciamento", (atividades, atividades), cat=p.LpBinary)

    #Var Linearidade
    var_lin = p.LpVariable.dicts("linearidade", (atividades, atividades), cat=p.LpContinuous)

    #Função objetivo: Minimizar o makespan
    prob += (makespan[0], f'Função objetivo de minimizar o makespan')

    #Restrições
    #Definição do inicio do processamento da atividade I+i
    for i in fim_atividade:
        for j in atividades:
            if i == j:
                continue
                #Atividade j vem depois da atividade i!!!
            prob += (var_lin[i][j] <= Upper * var_seq[i][j])
            prob += (var_lin[i][j] >= Lower * var_seq[i][j])
            prob += (var_lin[i][j] <= fim_atividade[j] - Lower * (1 - var_seq[i][j]))
            prob += (var_lin[i][j] >= fim_atividade[j] - Upper * (1 - var_seq[i][j]))

            #Definição do horário fim da atividade
            prob += (fim_atividade[j] >= var_lin[i][j] + tempo_atv[j])

            #definição da variavel de sequencia!
            prob += (fim_atividade[i] - fim_atividade[j] + (Upper * var_seq[i][j]) >= tempo_atv[j])
            prob += (fim_atividade[j] - fim_atividade[i] + Upper * (1 - var_seq[i][j]) >= tempo_atv[j])


    for atv in fim_atividade:
        prob += (makespan >= fim_atividade[atv])
        prob += (fim_atividade[atv] <= data_liberacao[atv])


            #TESTE INICIAL SEM A RESTRIÇÃO DE PRAZO!!
    solver_pulp = p.getSolver('PULP_CBC_CMD', timeLimit=360)
    prob.solve(solver_pulp)

    for v in prob.variables():
        if v.varValue == 0.0:
            continue
        print(v.name, "=", v.varValue)
    b=0



    #Cada atividade só pode ter ser predecessora de uma atividade!