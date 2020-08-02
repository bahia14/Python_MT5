import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn
import statsmodels.api as sm
from scipy.stats import zscore
from statsmodels import regression
from statsmodels.tsa.stattools import coint


class Pair_trading():
    def __init__(self, data_var, data_preco, par, valor_inicial):
        self.financeiro = valor_inicial
        self.posicionado = 0  # comeca sem nenhuma operação aberta
        self.lista_resultado_operacoes = []
        self.lista_evolucao_carteira = []
        self.lista_dias_carregando = []
        self.lista_rentabilidade_operacao = []
        self.contador_dias = 0
        # guarda tickers das acoes
        self.t1 = par[0]
        self.t2 = par[1]
        self.volume_operacao = 0

        self.dados_var = data_var
        self.dados_preco = data_preco

    def calcula_zscore_spread(self, stock1, stock2):
        stock1 = sm.add_constant(stock1)
        results = sm.OLS(stock2, stock1).fit()
        stock1 = stock1[self.t1]
        b = results.params[self.t1]
        spread = stock2 - (b*stock1)
        zs = zscore(spread)[-1]
        return zs

    def condicoes_operar(self, zs, gatilho_high, preco_s1, preco_s2, index):
        if zs >= gatilho_high and self.posicionado == 0:
            # parametros para iniciar operacao
            self.posicionado = 1  # entrou em uma operacao
            self.volume = (self.financeiro/2)//preco_s1
            self.razao = preco_s1/preco_s2
            self.contador_dias = index
            # guarda dados de quantas ações está comprado/vendido
            self.qtd_s1 = self.volume
            self.qtd_s2 = self.volume*self.razao
            # calcula valor total da compra e venda (idealmente devem ser iguais)
            # vende  s1 (credita caixa)
            valor_operado_s1 = preco_s1*self.qtd_s1
            valor_operado_s2 = -preco_s2 * \
                self.qtd_s2  # compra s2 (debita caixa)
#             print(f'v1  R${valor_operado_s1:.2f} | v2 R${valor_operado_s2:.2f}')
#             print(f'C1  R${preco_s1:.2f} | D2 R${(preco_s2*self.razao):.2f}')
            self.financeiro += valor_operado_s1 + valor_operado_s2

        elif zs <= 0.08 and self.posicionado == 1:
            # calcula preço das açoes que estão em carteira
            valor_operado_s1 = -self.qtd_s1 * \
                preco_s1  # compra s1 (debita  caixa)
            valor_operado_s2 = self.qtd_s2 * \
                preco_s2  # vende  s2 (credita caixa)
#             print(f'v1 R${valor_operado_s1:.2f} | v2  R${valor_operado_s2:.2f}')
#             print(f'D1  R${preco_s1:.2f} | C2 R${(preco_s2*self.razao):.2f}')
            resultado_trade = valor_operado_s1 + valor_operado_s2
#             print(f'resu: R${resultado_trade:.2f}\n')
            self.financeiro += resultado_trade
            # zera quantidades de ações sendo operadas
            self.qtd_s1 -= self.qtd_s1
            self.qtd_s2 -= self.qtd_s2
            # guarda dados para acompanhamento ao longo do tempo
            self.lista_rentabilidade_operacao.append(
                resultado_trade/(self.financeiro-resultado_trade)*100)
            self.lista_evolucao_carteira.append(self.financeiro)
            self.lista_dias_carregando.append(index-self.contador_dias)
            self.lista_resultado_operacoes.append(resultado_trade)
            # zera parametros para próximas operações
            self.posicionado = 0
            self.razao = 0
            self.volume = 0
            self.contador_dias = 0

    def opera(self):
        period = 45
        c = 0
        s1 = self.dados_var[self.t1]
        s2 = self.dados_var[self.t2]
        for index in range(period, len(self.dados_var)):
            # seleciona a acao 1 com uma janela com *period* dias
            j1 = (s1[c:index])
            j2 = (s2[c:index])

            preco_s1 = self.dados_preco[self.t1][self.dados_var.index ==
                                                 index].values[0]
            preco_s2 = self.dados_preco[self.t2][self.dados_var.index ==
                                                 index].values[0]

            zs = self.calcula_zscore_spread(stock1=j1, stock2=j2)
            self.condicoes_operar(
                zs=zs, gatilho_high=1.1, preco_s1=preco_s1, preco_s2=preco_s2, index=index)
            c += 1
