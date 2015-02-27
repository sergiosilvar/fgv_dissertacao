# -*- coding: latin-1 -*-

import sys,os; 
import pandas as pd
import psycopg2
from mpltools import style
import unicodedata
import geopandas as gd
from scipy.stats import norm as gauss, probplot, cumfreq
from matplotlib import rcParams
from  matplotlib.pyplot import figure, xlim, ylim,pcolor, colorbar, xticks, \
    yticks, subplots
from numpy import linspace, arange,std, polyfit, polyval,sqrt





x = os.getcwd()
l = x.rfind('\\')
path = x[:l+1]+'capturar_zap'
sys.path.append(path)

import dataset as d

# Connect to an existing database
con = psycopg2.connect("dbname=zap user=postgres")

def set_style(sty='ggplot'):
    style.use(sty)


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
        raise Exception('Ou ambos as variaveis sao nulas ou somente "largura" eh definida.')
    
        
        
            
 
def remove_acento(str_or_list):
    troca = []
    troca.append( {'de':['á','à','ã','ä','â'], 'para':'a'})
    troca.append( {'de':['Á','À','Ã','Ä','Â'], 'para':'A'})
    troca.append( {'de':['é','è','ë','ê'], 'para':'e'})
    troca.append( {'de':['É','È','Ë','Ê'], 'para':'E'})
    troca.append( {'de':['í','ì','ï','î'], 'para':'i'})
    troca.append( {'de':['Í','Ì','Ï','Î'], 'para':'I'})
    troca.append( {'de':['ó','ò','ö','õ','ô'], 'para':'o'})
    troca.append( {'de':['Ó','Ò','Ö','Õ','Ô'], 'para':'O'})
    troca.append( {'de':['ú','ù','ü','û'], 'para':'u'})
    troca.append( {'de':['Ú','Ù','Ü','Û'], 'para':'U'})
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

def prep_formula(dataframe, dataframe_name, var_dep='preco', func=None):
    
        

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
    if func != None: 
        yname = '{}({}.{}) '.format(func, dataframe_name, var_dep)   
    else:
        yname = '{}.{} '.format(dataframe_name, var_dep)
    formula = yname + ' ~ ' +  \
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

    if len(cols_autoc) == 0:
        print 'NÃ£o hÃ¡ colunas autocorrelacionadas.'
    else:
        print 'Coluna'.ljust(20),'|', 'Autocorrelacionada com '.ljust(50)
        for k,c in cols_autoc.iteritems():
            print str(k).ljust(20),':', str(c).ljust(50)
    
def scatter_distancia(dfx,suptitle=None):
    # Colunas que representam distâncias.
    dist_columns = sorted([c for c in dfx.columns if c.find('dist_') > -1])

   
    # Definir tamanho do gráfico.
    w,h = rcParams['figure.figsize']
    f,a = subplots(len(dist_columns), 2)
    f.set_size_inches(w*2, h*len(dist_columns))
    
    
    # Título central da figura.
    if suptitle != None:
        f.suptitle(suptitle)
    
    # Plotar gráficos.
    for i in range(len(dist_columns)):
        col_name = dist_columns[i]
        x = dfx[col_name]
        fx = linspace(x.min(),x.max(),50)
        
        a[i, 0].scatter(x, dfx.preco)
        p = polyfit(x,dfx.preco,1)
        a[i, 0].plot(fx, polyval(p,fx), linewidth=2)
        a[i, 0].set_title(col_name + u' x preÃ§o')
        
        a[i, 1].scatter(x,dfx.m2)
        p = polyfit(x,dfx.m2,1)
        a[i, 1].plot(fx, polyval(p,fx), linewidth=2)
        a[i, 1].set_title(col_name + u' x $R\$/m^2$')

        
def plot_boxhist(x,titulo=None,xlabel=None):
    f,a = subplots(2,1)
    a0,a1 = a.ravel()
    bp = a0.boxplot(x,vert=False);
    a0.text(max(x)*0.8,1.2, 
        s='$3\sigma$={:.2f}'.format(3*std(x)), 
        bbox={'facecolor':'w', 'pad':10, 'alpha':0.5},
        style='italic',fontsize=15)
    
    a1.hist(x,bins=30);
    
    if titulo != None: 
        a0.set_title(titulo);
    if xlabel != None:
        a1.set_xlabel(xlabel);
        
        
def rmse(resid):
    return sqrt((resid**2/len(resid)).sum())
        