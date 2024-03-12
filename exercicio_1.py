import random

import pandas as pd
import numpy as np
import pulp


if __name__ == '__main__':
    #Criação das estâncias
    random.seed(1000)

    numero_atividades = 15
    hora_inicio = 1

    setup_max = 2.2
    tempo_processo_max = 15
    atividades = [at for at in range(numero_atividades)]
    Upper = 1000
    Lower = 1
    #liberacao da data em horas!
    tempo_processo = [round(tempo_processo_max * random.random(), 2) for _ in range(numero_atividades)]
    tempo_setup = [round(setup_max * random.random(), 2) for _ in range(numero_atividades)]
    tempo_atv = [round(tempo_processo[i] + tempo_setup[i],2) for i in range(len(tempo_setup))]

    #hora fim precisa ser maior que a tempo máximo de processo e tempo_setup
    hora_fim = np.ceil(sum(tempo_processo)) + np.ceil(sum(tempo_setup)) + 10

    #Tomar cuidado para não gerar modelo infeasbile
    data_liberacao = [min(tempo_processo) + round(setup_max) + random.randint(hora_inicio + 20, hora_fim) for _ in range(numero_atividades)]

    #Criação do problema:
    problema_scheduling = pulp.LpProblem('Problema_Scheduling', pulp.LpMinimize)

    #Variaveis de Decisão:
    #Horário que a atividade N vai terminar:
    variaveis_x = np.array([pulp.LpVariable("x" + str(i), lowBound=0) for i in atividades])

    #se a tarefa I precede a tarefa J
    #mudar para matriz!!!
    variaveis_bin_sequenciamento = list()
    list_aux = list()
    list_aux_z= list()
    variaveis_para_linearidade = list()
    for i in range(len(variaveis_x)):
        for j in range(len(variaveis_x)):  # TODO: Aprender como usar a matriz do pulp!!
            if i == j:
                continue
            var = pulp.LpVariable("y" + str(i) + "_" + str(j), lowBound=0, upBound=1, cat=pulp.const.LpBinary)
            var_linear = pulp.LpVariable("z" + str(i) + "_" + str(j),0)
            list_aux.append(var)
            list_aux_z.append(var_linear)

        variaveis_bin_sequenciamento.append(list_aux[:])
        variaveis_para_linearidade.append(list_aux_z[:])
        list_aux.clear()
        list_aux_z.clear()


    var_makespan = pulp.LpVariable("makespan", lowBound=0)

    #Função Objetivo:
    #Minimizar o makespan!!!
    problema_scheduling += var_makespan

    #é necessário criar cada restrição com FOR?
    #TODO: se for a melhor forma de criar as restrições, usar apenas 1 for!

    #Restrições:
    # 1: definição do makespan
    # restricao_makespan = pulp.lpSum([x for x in variaveis_x] <= )
    # problema_scheduling += restricao_makespan
    for x in range(len(variaveis_x)):
        problema_scheduling += (var_makespan >= variaveis_x[x], f'Definição do Makespan  {variaveis_x[x]}')


    # 2: atividades não podem terminar antes do seu tempo de inicio (primeira atividade)
    # restricao_primeiro_inicio = pulp.lpSum([x for x in variaveis_x] >= [t for t in tempo_atv])
    # problema_scheduling += restricao_primeiro_inicio
    for x in range(len(variaveis_x)):
       problema_scheduling += (variaveis_x[x] >= tempo_atv[x], f'Tempo atividade tarefa {variaveis_x[x]}')

    # 3: Atividades não podem terminar após a data Liberacao
    # restricao_data_liberacao = pulp.lpSum([x for x in variaveis_x] >= [t for t in data_liberacao])
    # problema_scheduling += restricao_data_liberacao

    for x in range(len(variaveis_x)):
        problema_scheduling += (variaveis_x[x] <= data_liberacao[x], f'Restricao de cumprimento de prazo da tarefa {x}')


    #Definição do sequenciamento das tarefas!!
    #Restrição 4: #garante que a atividade n+1 só começar depois que a n terminar
    #Tarefa 5 será predecessora da tarefa 8. Logo: x8 >= x5 * variaveis_bin_sequenciamento[5,8] + tempo_atv[x8]. Ponto é: Preciso da binária de sucesão?


    for i in range(len(variaveis_x) -1):
        for j in range(len(variaveis_x)-1):

            problema_scheduling += (variaveis_para_linearidade[i][j] <= variaveis_bin_sequenciamento[i][j] * Upper,
                                    f'Linearidade superior de {variaveis_bin_sequenciamento[i][j]}')
            problema_scheduling += (variaveis_para_linearidade[i][j] >= variaveis_bin_sequenciamento[i][j] * Lower,
                                    f'Linearidade inferior de {variaveis_bin_sequenciamento[i][j]}')
            problema_scheduling += (variaveis_para_linearidade[i][j] <= variaveis_x[i] - Lower * (1 - variaveis_bin_sequenciamento[i][j]),
                                    f'Linearidade superior 2 de {variaveis_bin_sequenciamento[i][j]}')
            problema_scheduling += (variaveis_para_linearidade[i][j] >= variaveis_x[i] - Upper * (1 - variaveis_bin_sequenciamento[i][j]),
                                                                                                f'Linearidade inferior 2 de: {variaveis_bin_sequenciamento[i][j]}')

            problema_scheduling += (variaveis_x[i] >= variaveis_para_linearidade[i][j] + tempo_atv[i],
                     f'Garantia de continuidade de {variaveis_bin_sequenciamento[i][j]}') #Tentar somar o makerspan ??

    #escolher uma tarefa para ser realizada. Exceto a ultima, que talvez aponte para a primeira. Confirmar!!
    for i in range(len(variaveis_x)):
        problema_scheduling += (pulp.lpSum([j for j in variaveis_bin_sequenciamento[i]]) - 1 == 0, f'forçando sequencia da var {i}')

    #Cada ordem só pode ser executada uma vez
    for i in range(len(variaveis_x) - 1):
        problema_scheduling += (pulp.lpSum([j for j in variaveis_bin_sequenciamento[i]]) - 1 == 0, f'Cada ordem só pode ser executada uma vez {i}')




    problema_scheduling.solve()
    print("Status:", pulp.LpStatus[problema_scheduling.status])
    var = problema_scheduling.variables()
    for v in problema_scheduling.variables():
        if v.varValue == 0.0:
            continue
        print(v.name, "=", v.varValue)
    b=0
