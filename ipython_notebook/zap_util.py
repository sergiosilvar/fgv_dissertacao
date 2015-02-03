# -*- coding: utf-8 -*-

import sys,os; 
import pandas as pd
import psycopg2
from mpltools import style
import unicodedata
import geopandas as gd
from scipy.stats import norm as gauss, probplot, cumfreq
from matplotlib import rcParams
from  matplotlib.pyplot import figure, xlim, ylim,pcolor, colorbar, xticks, \
    yticks
from numpy import linspace, arange


style.use('ggplot')



x = os.getcwd()
l = x.rfind('\\')
path = x[:l+1]+'capturar_zap'
sys.path.append(path)

import dataset as d

# Connect to an existing database
con = psycopg2.connect("dbname=zap user=postgres")

def exec_sql(sql, con=None):
    if con == None: con = d.conecta_db()
    return d.__executar(sql,con=con)
    
def get(sql,id_='id',con=None):
    if con == None: con = d.conecta_db()
    return pd.io.sql.read_sql(sql, con, index_col=id_)

def get_geo(sql, con=None):
    if con == None: con = d.conecta_db()
    return gd.GeoDataFrame.from_postgis(sql, con)
    
tam_fig_original = None
def tam_figura(largura=None, altura=None):
    if tam_fig_original == None:
        tam_fig_original = rcParams['figure.figsize']

    if largura == None and altura == None:
        rcParams['figure.figsize'] = tam_fig_original
    if largura != None and altura == None:
        rcParams['figure.figsize'] = [largura*i for i in tam_fig_original]
    if largura != None and altura == None:
        rcParams = [largura, altura]
    if largura == None and altura != None:
        raise Exception('Ou ambos as variáveis são nulas ou somente "largura" é definida.')
    
        
        
            
 
def remove_acento(str_or_list):
    troca = []
    troca.append( {'de':['á','â','ã','ä','à'], 'para':'a'})
    troca.append( {'de':['Á','Â','Ã','Ä','À'], 'para':'A'})
    troca.append( {'de':['é','ê','ë','è'], 'para':'e'})
    troca.append( {'de':['É','Ê','Ë','È'], 'para':'E'})
    troca.append( {'de':['í','î','ï','ì'], 'para':'i'})
    troca.append( {'de':['Í','Î','Ï','Ì'], 'para':'I'})
    troca.append( {'de':['ó','ô','ö','õ','ò'], 'para':'o'})
    troca.append( {'de':['Ó','Ô','Ö','Õ','Ò'], 'para':'O'})
    troca.append( {'de':['ú','û','ü','ù'], 'para':'u'})
    troca.append( {'de':['Ú','Û','Ü','Ù'], 'para':'U'})
    troca.append( {'de':['ç'], 'para':'c'})
    troca.append( {'de':['Ç'], 'para':'C'})
    troca.append( {'de':['(', ')','[',']'], 'para':'_'})

    if type(str_or_list) == str:
        str_sem = str_or_list
        for item in troca:
            for c in item['de']:
                str_sem = str_sem.replace(c,item['para'])    
        return str_sem

    if type(str_or_list) == list:
        return [remove_acento(item) for item in str_or_list]
        
    if type(str_or_list) == unicode:
        return unicodedata.normalize('NFKD', str_or_list).encode('ascii', 'ignore')

    
    msg =  'ERRO: ''unicode'', ''str'' ou ''list'' esperado. ' + str(type(str_or_list)) + ' encontrado.'
    raise Exception(msg)
    
def plot_residual(smres):
    
    resid_std = (smres.resid-smres.resid.mean())/smres.resid.std()
    fig = figure()
    w,h = rcParams['figure.figsize']
    fig.set_size_inches(w*2,h*2)
    ylim_ = (resid_std.min()*1.01,resid_std.max()*1.01)
    xlim_ = (smres.fittedvalues.min(),smres.fittedvalues.max())
    ax = fig.add_subplot(221)
    probplot(resid_std, plot=ax);
    ylim(ylim_);

    
    ax = fig.add_subplot(222)
    ax.scatter(smres.fittedvalues,resid_std);
    
    # TODO: Parou de funcionar, substituido pelo codigo logo a seguir.
    #ax.axhline(y=smres.resid.mean(),
    #           xmin=smres.fittedvalues.min(),
    #           xmax=smres.fittedvalues.max(),color='r');
    x = linspace(smres.fittedvalues.min(),smres.fittedvalues.max(),5)
    y = [smres.resid.mean() for i in range(len(x))]
    ax.plot(x,y, 'r-', linewidth=2)

    xlim(xlim_);
    ylim(ylim_);

    ax = fig.add_subplot(223)
    ax.hist(resid_std,50);

    from matplotlib.colors import LogNorm
    ax = fig.add_subplot(224)
    ax.hexbin(smres.fittedvalues,resid_std, norm=LogNorm());
    ax.axhline(y=smres.resid.mean(),xmin=smres.fittedvalues.min(),xmax=smres.fittedvalues.max(),color='r');
    xlim(xlim_);
    ylim(ylim_);

def prep_formula(dataframe, dataframe_name, var_dep='preco'):
    
        

    # Determinar colunas que são identificadoers para serem removidos.
    cols_ids = set([c for c in dataframe.columns if c.find('id_')>-1])

    # Identificar colunas que contém valores ausentes.
    s = dataframe.isnull().sum()
    cols_nulos = set(s[s>0].index.tolist())

    # Colunas que são variáveis dependentes.
    cols_dep = set(['m2','preco'])

    # Juntar todas as colunas a serem removidas do modelo.
    cols_excluded = cols_ids.union(cols_nulos).union(cols_dep)

    # Definir as variáveis para o modelo.
    cols = set(dataframe.columns) - cols_excluded

    # Construir a fórmula.
    formula = dataframe_name + '.' + var_dep + ' ~ ' +  \
        ' + '.join([dataframe_name + '.'+c for c in cols])
    
    return formula, cols, cols_excluded    
    
def plot_corrmatrix(matrix, figsize=(8*1.05, 6*1.05),**args):

    figure(figsize=figsize)
    pcolor(matrix,**args);
    colorbar();

    max_ = len(matrix);
    yticks(arange(0.5,max_+0.5), range(0,max_));
    xticks(arange(0.5,max_+0.5), range(0,max_));
    
    
def cols_autocorr(matrix, threshold = 0.69999):
    from numpy import tril
    matrix.loc[:,:] =  tril(matrix, k=-1) # borrowed from Karl D's answer

    already_in = set()
    result = {}
    for col in matrix:
        perfect_corr = matrix[col][abs(matrix[col]) > threshold].index.tolist()
        #if perfect_corr and col not in already_in:
        #    already_in.update(set(perfect_corr))
        #    perfect_corr.append(col)
        #    cols_autocorr.append(perfect_corr)
        if len(perfect_corr) > 0:
            result[col] = [i+'({:.2f})'.format(matrix[col][i]) for i in perfect_corr]

    return result             
    
def print_autocorr(dataframe,cols_excluded=[]):
    if type(cols_excluded) != set:
        cols_excluded = set(cols_excluded)
    # Selecionar as colunas do modelo.
    valid_cols  = set(dataframe.columns.tolist()) - cols_excluded
    valid_cols = list(valid_cols)


    matrix_corr = dataframe[valid_cols].corr()

    cols_autoc = cols_autocorr(matrix_corr)


    print 'Coluna'.ljust(20),'|', 'Autocorrelacionada com '.ljust(50)
    for k,c in cols_autoc.iteritems():
        print str(k).ljust(20),':', str(c).ljust(50)
    