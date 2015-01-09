# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import os
import json
import itertools

DIR = './json/'

def dominio():
    anos = [str(i) for i in range(2008,2014)]
    meses = ['%02d'%i for i in range(1,13)]
    result = list(itertools.product(anos,meses))
    dominio = [x+'-'+y for x,y in result]
    return dominio


def dataset(estado, cidade, bairro, num_quartos):
    fname = DIR+''+estado+'/'+cidade+'/'+bairro+'/%d_indices.json' % (num_quartos)
    f = open(fname,'r')
    ind = json.load(f)
    #ind = pd.io.json.read_json(fname)     
    f.close()
    return ind
    
def indices(estado=None, cidade=None, bairro=None, num_quartos=0):
    ds =  dataset(estado, cidade, bairro, num_quartos)
    lista  = [Indice(x) for x in ds]
    for ano_mes in dominio():
        tem = False
        for ind in lista:
            if ind.ano_mes == ano_mes:
                tem = True
                break
        if not tem:
            vazio = Indice()
            vazio.ano = int(ano_mes[:4])
            vazio.mes = int(ano_mes[-2:])
            lista.append(vazio)
    return sorted(lista, key=lambda indice: indice.ano_mes)[:(2013-2008+1)*12]

def lista_estados():
    return os.listdir(DIR)

def lista_cidades(estado=None):
    return os.listdir(DIR+'/'+estado)

def lista_bairros(estado,cidade):
    return os.listdir(DIR+'/'+estado+'/'+cidade)

class Zap(object):
    def __init__(self):
        pass
    
class Bairro(Zap):
    def __init__(self,estado,cidade,bairro):
        self.nome = bairro
        self.cidade = cidade
        self.estado = estado
        self.indices = [indices(estado,cidade,bairro,i) for i in range(4)]
        self.mes = dominio()
    
    def qt1(self):
        return self.qt(1)
    
    def qt2(self):
        return  self.qt(2)
    
    def qt3(self):
        return self.qt(3)
    
    def qt0(self):
        return self.qt(0)
    
    def qt(self,num_quartos):
        return [i.valor for i in self.indices[num_quartos]]
        
    def max_variacao(self, num_quartos=0):
        valores = [x for x in self.qt(num_quartos) if x != None]
        if len(valores) == 0:
            return 0
        min_ = min(valores)
        max_ = max(valores)
        return max_ - min_
        
    def __repr__(self):
        return self.nome
    
class Cidade(Zap):
    def __init__(self, estado, cidade):
        self.nome = cidade
        self.estado = estado
        self.bairros = {}
    
    def lista_bairros(self):
        return lista_bairros(self.estado,self.nome)
    
    def bairro(self,nome_bairro):
        return self.bairros.get(nome_bairro,Bairro(self.estado,self.nome,nome_bairro))

class Indice(object):
    def __init__(self,json=None):
        if json != None:
            self.ano = json['Ano']
            self._valor = json['Valor']
            self.mes = json['Mes']
            self.var = json['Variacao']
            self.var_m = json['VariacaoMensal']
            self.amostras = json['Amostra']
        else:
            self.ano = None
            self._valor = None
            self.mes = None
            self.var = None
            self.var_m = None
            self.amostras = 0
            
    @property
    def ano_mes(self):
        return '%d-%02d'%(self.ano, self.mes)
    
    def __repr__(self):
        return '%s: %s'%(self.ano_mes,self.valor)
    
    @property 
    def valor(self):
        if self._valor == 0: return None
        return self._valor
 
# <codecell>


# <codecell>


# <codecell>


# <codecell>


# <codecell>


