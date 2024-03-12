import random

import pandas as pd
import numpy as np

#proposta: Usar o simulated annealing para resolver o problema

from random import *
import numpy as np
from dataclasses import dataclass
import copy
import random
import math


class SimulatedAnnealing():


    def __init__(self, T, alfa, max_times, max_lado, veiculos, comprimento, coef):
        self.T: float = T
        self.alfa: float = alfa
        self.max_lado = max_lado
        self.max_times: int = max_times
        self.veiculos = veiculos
        self.comprimento = comprimento
        self.coef = coef


    def randon_change(self, vetor):
        #TODO: Use 2-opt to create new vector? PLEASE USE NUMPY TO IMPROVE THIS!!!!
        pos_change_1 = (randrange(0, len(vetor)))
        node1 = vetor[pos_change_1]
        pos_change_2 = (randrange(0, len(vetor)))
        node2 = vetor[pos_change_2]
        vetor[pos_change_1] = node2
        vetor[pos_change_2] = node1


        return vetor

    def energy_calculate(self, new_vetor, initial=False):
        new_vetor = new_vetor if initial else self.commons.change_two_opt(new_vetor)
        separte_routes = self.commons.define_routes(new_vetor, self.demands, self.vehicle_capacity)
        dist_total = self.commons.dist_calculate(separte_routes, self.matrix)

        return new_vetor, dist_total

    def reduct_t_geometric(self, T):
        return T * self.alfa

    def gera_solucao_inicial(self, vetor):

        """
        Método para calcular a solução inicial. A principio essa solução será uma que escolherá aleatoriamente
        veículos para cada um dos lados.A principio poderá ter quantos carros em cada lado quiser e aalteração
        será na perturbação

        :param vetor:
        :return: lista de lista contendo os veículos no lado 0 e veículo no lado 1

        """
        lado_0 = list()
        lado_1 = list()
        for carro in vetor:
            if random.random() <= self.coef:
                lado_0.append(carro)
            else:
                lado_1.append(carro)

        return [lado_0, lado_1]


    def perturba_solucao(self, vetor_p):
        """
        Método para pertubar a solução.
        Escolhe 1 veículo do lado A aleatório e decide se troca outro com o do lado B ou só troca o veículo de lado.

        :param vetor:
        :return: vetor perturbado e energia dessa nova solução
        """
        #TODO: mesma operação 2 vezes. Transformar num método
        v = copy.deepcopy(vetor_p)
        veiculo_1_ladoA = None
        veiculo_2_lado_B = None
        if len(v[0]):
            p1 = random.randint(0, len(v[0])-1)
            veiculo_1_ladoA = v[0][p1]
            if random.random() <= self.coef and len(v[1]): #envia carro do segundo vetor para o primeiro
                p2 = random.randint(0, len(v[1])-1)
                veiculo_2_lado_B = v[1][p2]
                v[1].remove(veiculo_2_lado_B)
                v[0].append(veiculo_2_lado_B)

            v[0].remove(veiculo_1_ladoA)
            v[1].append(veiculo_1_ladoA)

        if len(v[1]) -1:
            p_1 = random.randint(0, len(v[1])-1)
            veiculo_1_LadoB = v[1][p_1] if v[1][p_1] != veiculo_1_ladoA else v[1][p_1-1]
            if random.random() <= self.coef and len(v[0]) -1:
                p_2 = random.randint(0, len(v[0]) -1)
                veiculo_2_lado_A = v[0][p_2] if v[0][p_2] != veiculo_2_lado_B else v[0][p_2-1]
                v[0].remove(veiculo_2_lado_A)
                v[1].append(veiculo_2_lado_A)

            v[1].remove(veiculo_1_LadoB)
            v[0].append(veiculo_1_LadoB)

        new_vetor = copy.deepcopy([v[0],v[1]])

        energia_nova = self.calcula_energia(new_vetor)
        return new_vetor, energia_nova

    def calcula_energia(self, vector_ce):
        energia_A = sum(self.comprimento[v] for v in vector_ce[0])
        energia_B = sum(self.comprimento[v] for v in vector_ce[1])
        #return max(energia_A, energia_B) #Comprimento da rua, logo seria o comprimento do maior lado?
        return max(energia_A , energia_B) - min(energia_A, energia_B)

    def simulated_annealing(self, initial_solution=None):
        if initial_solution is not None:
            vetor = copy.deepcopy(initial_solution)
        else:
            vetor = self.gera_solucao_inicial(vetor=self.veiculos)

        e_base = self.calcula_energia(vetor)
        times = 0
        T = self.T
        vector = copy.deepcopy(vetor)
        while times < self.max_times:
            vector_change, e_2 = self.perturba_solucao(vetor_p=vector)
            delta = e_2 - e_base
            if delta < 0:
                vector = vector_change[:]
                e_base = e_2
            else:
                x = random.random()
                if x < (math.exp(-delta / T)):
                    vector = vector_change[:]
                    e_base = e_2
            times += 1
            T = self.reduct_t_geometric(T)

        print(f'Lado 0 com {sum(self.comprimento[v] for v in vector[0])} e veiculos {vector[0]}')
        print(f'Lado 1 com {sum(self.comprimento[v] for v in vector[1])} e veiculos {vector[1]}')

        return e_base


    def multiple_executions(self, number_executions=500, initial_solution=None):
        cont = 0
        list_result = list()
        while cont <= number_executions:
            _, result = self.simulated_annealing(initial_solution)
            cont += 1
            list_result.append(result)

        return list_result, min(list_result) #TODO: return the best rote


if __name__ == '__main__':
    seed(1000)
    n_veiculos = 15
    veiculos = np.array([i for i in range(n_veiculos)])
    comprimento = np.array([4, 4.5, 5, 4.1, 2.4, 5.2, 3.7, 3.5, 3.2, 4.5, 2.3, 3.3, 3.8, 4.6, 3])
    T = 10000
    alfa = 0.9
    max_times = 10000
    teste_max_em_1_lado = 9 #Teste para perturbação da solução
    coef = 0.5


    SA = SimulatedAnnealing(T=T,
                            alfa=alfa,
                            max_times=max_times,
                            max_lado=teste_max_em_1_lado,
                            veiculos=veiculos,
                            comprimento=comprimento,
                            coef=coef)

    SA.simulated_annealing()

    """
    Segunda questão: O que é necessário mudar se um dos lados dispõe de 15 metros para ser ocupados: 
    Será necessário alterar a função de geração da solução inicial, perturbação e cálculo da energia, sendo:
    - Geração da solução inicial: 
        A solução nesse segundo exemplo devem ser quais carros guardar nos 15m disponíveis. 
        Então é necessário escolher aleatoriamente veiculos até que a soma dos comprimentos seja menor ou igual a 15, 
        para encontrarmos um conjunto de veículos alocados para ser umasolução viável.
    
    - Perturbação: 
        Escolher um veículo aleatório para sair e outro para entrar aleatoriamente, atendendo a viabilidade da solução
        
    - Cálculo da energia:
        Deverá ser 15 (ou valor máximo permitido) subtraido do total ocupado pelos veículos daquela solução para 
        que a metaheurística encontre a solução que deixe o menor espaço faltando no lado restrito. 
        Dessa forma a melhor solução consiste em encontrar a combinação de veículos que melhor aproveite o espaço dis-
        ponível.
    
    Como caracteristica das metaheurísticas os demais procedimentos permanecem os mesmos.
    """