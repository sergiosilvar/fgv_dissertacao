# -*- coding: iso-8859-1 -*-

import sys,os; 
import pandas as pd
import psycopg2
import unicodedata
from scipy.stats import norm as gauss, probplot, cumfreq
from matplotlib import rcParams
from  matplotlib.pyplot import figure, xlim, ylim,pcolor, colorbar, xticks, \
    yticks, subplots, subplot, style,xlabel,ylabel,setp
from numpy import linspace, arange,std, polyfit, polyval,sqrt,mean,NaN
from matplotlib.colors import LogNorm
from matplotlib.gridspec import GridSpec
import statsmodels.api as sm
import statsmodels.formula.api as smf


# Nomes das tabelas no banco de dados.
TBL_VAR_SOCIOAMB = '_var_socioambiental'
TBL_VAR_ESTRUTURAL = '_var_estrutural'
TBL_VWIMOVEL = 'vw_imovel'
VW_DISTANCIA = 'vw_distancia'

# Adiciona o diretório "capturar_zap" ao "path" do Python para poder acessar
# o módulo "dataset" nesse diretório.
x = os.getcwd()
l = x.rfind('/')
path = x[:l+1]+'capturar_zap'
sys.path.append(path)

import dataset as d

IMOVEIS_CSV = './imoveis_dataset.csv'
def get_imoveis_from_csv():
    return pd.read_csv(IMOVEIS_CSV,index_col='id')
    

def set_style(sty='ggplot'):
    '''
    Define estilo visual dos gráficos da biblioteca matplotlib.
    
    @param sty - nome do estilo dos gráficos a ser aplicado.
    '''
    style.use(sty)


def exec_sql(sql, con=None):
    '''
    Executa um SQL diretamente ao banco de dados e retorna seu resultado.
    
    @param sql - Código SQL a ser executado no banco de dados.
    @param con - Objeto de conexão ao banco de dados.
    '''
    if con == None: con = d.conecta_db()
    return d.__executar(sql,con=con)
    
    
def get(sql,id_='id',con=None):
    '''
    Executa um SQL do tipo SELECT no banco de dados e retorna seu resultado como
    um pandas.DataFrame.
    
    @param sql - Código SQL do tipo SELECT a ser executado.
    @param id_ - Nome do campo a ser tratado como "index" do objeto 
        pandas.DataFrame.
    @param con - Objeto de conexão ao banco de dados.
    '''
    if con == None: con = d.conecta_db()
    return pd.io.sql.read_sql(sql, con, index_col=id_)

# Variável global para armazenar tamanho original das figuras da biblioteca
# matplotlib.
tam_fig_original = None
def tam_figura(largura=None, altura=None):
    '''
    Define o tamanho das figuras dos gráficos da biblioteca matplotlib.
    Caso nenhum valor seja passado, a configuração do tamanho da figura é
    atribuído ao valor original.
    
    @param largura - Tamanho da largura da figura.
    @param altura - Tamanho da altura da figura.
    '''
    if tam_fig_original == None:
        tam_fig_original = rcParams['figure.figsize']

    if largura == None and altura == None:
        rcParams['figure.figsize'] = tam_fig_original
    if largura != None and altura == None:
        rcParams['figure.figsize'] = [largura*i for i in tam_fig_original]
    if largura != None and altura == None:
        rcParams = [largura, altura]
    if largura == None and altura != None:
        raise Exception('Defina apenas "lagura" ou nenhuma.')
        
 
def remove_acento(str_or_list, codec='utf-8'):
    '''
    Retorna uma string ou uma lista de texto com todos os caracteres acentuados
    substituídos pelos seus respectivos caracteres sem acento.
    
    @param str_or_list - String ou lista de strings.
    @param codec - Cócido CODEC da string ou lista de strings.
    '''
    if type(str_or_list) == str:
        s = str_or_list.decode(codec)
        return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
        
    if type(str_or_list) == list:
        return [remove_acento(item) for item in str_or_list]
        
    if type(str_or_list) == unicode:
        return unicodedata.normalize('NFKD', str_or_list).encode('ascii', 
            'ignore')
    
    
    msg =  'ERRO: ''unicode'', ''str'' ou ''list'' esperado. ' + \
        str(type(str_or_list)) + ' encontrado.'
    raise Exception(msg)
    
    
def prep_formula(dataframe,  var_dep='preco', func=None, cat=[],ignore=[]):
    '''
    Retorna uma tupla contendo a fórmula para uso de regressão linear da 
    biblioteca "statsmodels", uma lista de variáveis utilizadas na construção
    da fórmula e uma lista das variáveis rejeitadas para a utilizar na fórmula.
    
    As variáveis rejeitadas são aquelas que possuem valores nulos, junto com a
    lista de variáveis definidas no parâmetro "ignore".
    
    @param dataframe - Objeto pandas.Dataframe com o modelo para a regressão 
        linear. 
    @param var_dep - Nome da variável dependente da regressão linear.
    @param func - Função a ser aplicada na variável dependente.
    @param cat - Lista de variáveis independentes a serem tratadas como 
        categóricas.
    @param ignore - Lista de variáveis independentes a serem ignoradas na 
        construção da fórmula.
    '''
    cat=cat[:]
    ignore=ignore[:] 

    # Determinar colunas que são identificadoers para serem removidos.
    cols_ids = set([c for c in dataframe.columns if c.find('id_')>-1])

    # Identificar colunas que contém valores ausentes.
    s = dataframe.isnull().sum()
    cols_nulos = set(s[s>0].index.tolist())

    # Colunas que são variáveis dependentes.
    cols_dep = set(['m2','preco'])

    # Juntar todas as colunas a serem removidas do modelo.
    cols_excluded = cols_ids.union(cols_nulos).\
        union(cols_dep).union(set(ignore))

    # Definir as variáveis para o modelo.
    cols = list(set(dataframe.columns) - cols_excluded)

    # Construir a fórmula.
    if func != None: 
        yname = '{}({}) '.format(func, var_dep)   
    else:
        yname = '{} '.format(var_dep)
    formula = yname + ' ~ ' +  ' + '.join(cols)

    for c in cat:
        formula = formula.replace('{}'.format(c),
             'C({})'.format(c))
    
    return formula, cols, cols_excluded    
    
    
def plot_corrmatrix(matrix, figsize=(8*1.05, 6*1.05),**args):
    '''
    Plota uma matriz de correlação em conjunto com uma legenda de cores.
    
    @param matrix - Matriz com os valores a terem a correlação verificada.
    @param figsisze - Tamanho da figura a ser gerada.
    @param **args - Demais argumentos a serem passados para o método "pcolor".
    '''
    figure(figsize=figsize)
    pcolor(matrix,**args);
    colorbar();

    max_ = len(matrix);
    yticks(arange(0.5,max_+0.5), range(0,max_));
    xticks(arange(0.5,max_+0.5), range(0,max_));
    
    
def vars_corr(matrix, threshold = 0.69999):
    '''
    Retorna uma lista de variáveis correlacionadas entre si, onde o grau de 
    correlação é dado pelo parâmetro "threshold".
    
    @param matrix - Matriz de correlação obtida pelo método 
        pandas.DataFrame.corr().   
    @param threshold - Limite inferior de determinação de correlação entre duas
        variáveis.
        
    '''
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
    
def print_autocorr(dataframe,cols_excluded=[], threshold = 0.79999):
    '''
    Imprime na saída padrão um relatório exibindo as variáveis correlacionadas
    entre si.
    
    @param dataframe - Objeto pandas.DataFrame que contém as variáveis a serem 
        verificadas a correlação.
    @param cols_excluded - Lista de variáveis a serem excluídas da verificação
        de correlação.
    '''
    if type(cols_excluded) != set:
        cols_excluded = set(cols_excluded)
    # Selecionar as colunas do modelo.
    valid_cols  = set(dataframe.columns.tolist()) - cols_excluded
    valid_cols = list(valid_cols)


    matrix_corr = dataframe[valid_cols].corr()

    cols_autoc = vars_corr(matrix_corr, threshold)

    if len(cols_autoc) == 0:
        print(u'Nao ha colunas correlacionadas entre si.')
    else:
        print 'Coluna'.ljust(20),'|', 'Autocorrelacionada com '.ljust(50)
        for k,c in cols_autoc.items():
            print str(k).ljust(20),':', str(c).ljust(50)
    
def scatter_distancia(dfx,suptitle=None):
    '''
    Plota uma visualização customizada que exibe scatter plot para cada variável
    que representa uma distância no eixo X e o preço correspondente no eixo Y,
    ajusanto uma reta para verificação da tendência de Y ao longo de X.
    
    @param dfx - Objeto pandas.DataFrame com as variáveis de interesse.
    @param suptitle - Título superior do gráfico.
    '''
    
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
        a[i, 0].set_title(col_name + u' x preço')
        
        a[i, 1].scatter(x,dfx.m2)
        p = polyfit(x,dfx.m2,1)
        a[i, 1].plot(fx, polyval(p,fx), linewidth=2)
        a[i, 1].set_title(col_name + u' x $R\$/m^2$')

        
def plot_boxhist(x,titulo=None,xlabel=None):
    '''
    Plota uma visualização customizada que consiste em um boxplot acima de um
    histograma, para visualizar a distribuição de uma variável "x" entre esses
    dois tipos de gráficos.
    
    @param x - Variável de interesse de visualização.
    @param titulo - Título do gráfico.
    @param xlabel - Rótulo a ser exibido para o eixo X.
    '''
    
    #f,a = subplots(2,1)
    #a0,a1 = a.ravel()
    
    fig = figure()
    gs = GridSpec(3,1)
    a0 = subplot(gs[0,:])
    a1 = subplot(gs[1:,:], sharex=a0)
    
    bp = a0.boxplot(x,vert=False);
    a0.text(max(x)*0.8,1.2, 
        s='$3\sigma$={:.2f}'.format(3*std(x)), 
        bbox={'facecolor':'w', 'pad':10, 'alpha':0.5},
        style='italic',fontsize=13);
    setp(a0.get_xticklabels(), visible=False);
    
    a1.hist(x,bins=30);
    
    if titulo != None: 
        a0.set_title(titulo);
    if xlabel != None:
        a1.set_xlabel(xlabel);
    gs.tight_layout(fig)
        
        
def rmse(resid):
    '''
    Retonar o erro médio qudrático de uma lista de erros residuais de uma 
    regressão.
    
    @param resid - Lista de erros residuais de uma regressão linear.
    '''
    return sqrt((resid**2/len(resid)).sum())
    
    
def get_imoveis_dataframe(with_missing_data=True, bairro_g=None):
    '''
    Retorna um objeto pandas.DataFrame contendo todas as observações de imóveis
    com as variáveis de interesse do estudo.
    
    @param with_missing_data - Determina se o dataframe retornado trata as 
    variáveis com valores ausentes ou não.
    
    @param bairro_g - Filtra pelo nome do bairro.
    
    '''

    # Variáveis intrínsecas básicas.
    sql = 'select id,area,p.preco_ajustado as preco,condominio,garagem,'+\
        ' quartos,suites,lat,lng,bairro_g,p.m2_ajustado as m2, '+\
        'b.gid as id_bairro_g ' +\
        ' from {} i inner join preco_ajustado p '.format(TBL_VWIMOVEL) +\
        ' using(id) '+\
        ' inner join bairro b on b.nome = i.bairro_g'
    if bairro_g != None:
        sql += ' where bairro_g = \'{}\''.format(bairro_g) 
    df = get(sql,  None)
        
    df['bairro_g'] = df.bairro_g.apply(lambda x: remove_acento(x))

    # Variáveis sócio econômicas, por bairro.
    df_soc = get('select *  from {} '.format(TBL_VAR_SOCIOAMB), None)
    del df_soc['nome']

    # Unir imóveis com variáveis socioeconômicas por bairro.
    df = pd.merge(df,df_soc, left_on='id_bairro_g', right_on='gid', how='inner')
    del df_soc

    # Variáveis espaciais.
    df_dist = get('select id, dist_favela,dist_bombeiro,dist_centro,' + \
        'dist_centro_lng,dist_centro_lat,dist_delegacia,dist_lagoa,' + \
        'dist_logradouro,dist_metro,dist_praia,dist_saude_publica,' + \
        'dist_saude_privada,dist_trem from {}'.format(VW_DISTANCIA), None)

    # Demais variáveis intrínsecas dummies.
    #var_not_dummies = ['andar','elevadores','ano','unidades'] 
    df_int = get('select * from {}'.format(TBL_VAR_ESTRUTURAL), None)
        
    # Unir com variáveis espaciais e intrínsecas.
    df_int.index = df_int.id
    df_dist.index = df_dist.id
    df.index = df.id
    del df['id'], df_dist['id'], df_int['id']
    df = pd.concat([df,df_dist,df_int], axis=1, join='inner')
    del df['gid'], df['id_bairro_g'],df_dist, df_int
    
    if not with_missing_data:
        df.condominio.fillna(0, inplace=True)
        df.garagem.fillna(0, inplace=True)
        df.suites.fillna(0, inplace=True)
        del df['andares'],df['ano'],df['unidades_andar']    
        
        
    return df

def plot_residual(predicted,actual):
    '''
    Plota uma visualização customizada com gráficos exibindo informações dos 
    valores residuais de uma regressão linear.
    
    @param smres - Lista de valores residuais de uma regressão linear.
    '''
    
    delta = 100
    # Gráfico superior esquerdo.
    resid = predicted - actual
    resid_std = (resid-mean(resid))/std(resid)
    fig = figure()
    w,h = rcParams['figure.figsize']
    fig.set_size_inches(w*2,h*2)
    ax = fig.add_subplot(221)
    probplot(resid_std, plot=ax);
    xlim(-5,5)

    # Gráfico superior direito.
    ax = fig.add_subplot(222)
    ax.scatter(predicted,resid);
    ax.axhline(y=mean(resid),xmin=min(predicted),xmax=max(predicted),color='r');
    xlim(min(predicted)-delta,max(predicted)+delta)
    ylim(min(resid)-delta,max(resid)+delta)
    xlabel(u'Inferência')
    ylabel('Residual')

    # Gráfico inferior esquerdo.
    ax = fig.add_subplot(223)
    ax.hist(resid_std,100);
    xlim(-5,5)

    # Gráfico inferior direito.
    ax = fig.add_subplot(224)
    ax.hexbin(predicted,resid, norm=LogNorm());
    ax.axhline(y=mean(resid),xmin=min(predicted),xmax=max(predicted),color='r');
    xlim(min(predicted)-delta,max(predicted)+delta)
    ylim(min(resid)-delta,max(resid)+delta)



def ols(dataframe,cat=[], ignore=[], avoid_corr=False, avoid_plow=True,
        alpha=0.05,corr_limit=0.8, remove_plow_by_step=False):
    ignore = ignore[:]
    cat = cat[:]
    dataframe = dataframe.copy()
    lm = None
    c,e = None, None
    
    # Proteção contra loop infinito.
    MAX_LOOP = dataframe.shape[1] +1
    
    cols = list(set(dataframe.columns.tolist())-set(ignore))
        
    # Remover variáveis correlacionadas entre si.        
    if avoid_corr:
        while True: 
            cols_autocorr = vars_corr( dataframe[cols].corr(),corr_limit).keys()
            if len(cols_autocorr) > 0:
                ignore = list(set(ignore).union(set(cols_autocorr)))
                cols = list(set(dataframe.columns.tolist())-set(ignore))
            else:
                break
                              
    # Remover colunas estatísticamente insignificante.
    ignore_anterior = -1
    if avoid_plow:
        loop = 0
        while True:
            loop += 1

            # Evitar mais loops que variáveis.
            if loop > MAX_LOOP:
                raise Exception('Loop maior que variaveis!')

            f,c,e = prep_formula(dataframe,cat=cat,ignore=ignore)       
            lm = sm.formula.ols(f, dataframe).fit()
            plow = lm.pvalues[lm.pvalues > alpha]
            plow.sort(ascending=False, inplace=True)

            # Identifica variáveis de baixo pvalue
            cols_plow = [i for i in plow.index.tolist() 
                if i.find('Intercept')==-1]

            #print 'cols_plow: {}'.format(cols_plow)
            if len(cols_plow) > 0:
                if remove_plow_by_step:
                    ignore = list(set(ignore).union(set([cols_plow[0]])))
                else:
                    if len(ignore) == ignore_anterior:
                        raise Exception(u'Quantidade de variaveis a ignorar plow repetiu: {}'.\
                        format(len(ignore)))
                    ignore = list(set(ignore).union(set(cols_plow)))
                #print 'len ignore: {}'.format(ignore)
            else:
                e = ignore
                break
    else:
        f,c,e = prep_formula(dataframe,cat=cat,ignore=ignore)       
        lm = sm.formula.ols(f, dataframe).fit()

    del cat,ignore,dataframe
    vars_used = [i for i in lm.params.index.tolist() if i != 'Intercept']
    return lm, vars_used, e


def prep_statsmodels(dataframe,bairro_g=True,other_vars=True, unused_vars=False):
    '''
    Retorna dataframe preparado para ser executado no statsmodels.
    @param bairro_g - Determina se transforma bairros em dummies.
    @param demais - determina se transforma as variáveis quartos,suites e   
        garagens em dummies.
    @param unused_vars - Determina se retorna variáveis não usadas no modelo:
        lat,lng,condominio e m2.
    
    '''
    
    
    if other_vars:
        # Varáveis categóricas 
        for var_ in ['suites','quartos','garagem']:
            temp = pd.get_dummies(dataframe[var_])
            del temp[temp.columns.tolist()[0]]
            temp.columns = [var_+'_'+str(int(i)) for i 
                             in temp.columns.tolist()]
        
            dataframe = pd.concat([dataframe,temp], axis=1)
            # Eliminar dependência linear.
            del dataframe[var_]
        
    if bairro_g:
        # Variável bairro.
        # Alterar nome para compatibilidade com stasmodels.
        dataframe['bairro_g'] = dataframe.bairro_g.apply(
            lambda x : x.replace(' ', '_').replace('(','').replace(')',''))

        db = pd.get_dummies(dataframe.bairro_g)
        # Eliminar dependência linear.
        del db['Centro']
        dataframe = pd.concat([dataframe,db],axis=1)
        del dataframe['bairro_g']
        
    if not unused_vars:
        for i in ['lat','lng','condominio','m2','dist_centro_lat',\
            'dist_centro_lng','se_anos_estudo']:
            del dataframe[i]
        
    return dataframe
    
    
def run_model(dataframe, n_folds=5):
    '''
    Avalia a performance de X e retorna a média do RMSE de treino, teste e Rˆ2.
    
    @param dataframe - pandas.DataFrame com o conjunto de dados.

    @param n_folds - Número de folds para o K_Fold. Se n_folds = 1, executa uma
        única iteraçã com todo o comjunto de deados.
    '''
    
    from sklearn import cross_validation as cv
    rmse_train = [];
    rmse_test = [];
    r2 = [];

    if n_folds == 1:
        lm,_,_ = ols(dataframe)
        return rmse(lm.resid),NaN,lm.rsquared
    else:
        kfold = cv.KFold(len(dataframe),n_folds,shuffle=False);
    
        for train,test in kfold:
            df_test = dataframe.iloc[test];
            df_train = dataframe.iloc[train];
            lm,_,_ = ols(df_train);
            predict = lm.predict(df_test);
            resid = predict - df_test.preco;
            rmse_test.append(rmse(resid));
            r2.append(lm.rsquared)
            rmse_train.append(rmse(lm.resid));
    
    return mean(rmse_train),mean(rmse_test),mean(r2);

def res_coef(lm_result):
    '''
    Converte um statsmodels.ResultWraper em um pandas.DataFrame ordenado
    pelos coeficientes.
    
    @param lm_result: statsmodels.ResultWraper 
    '''
    
    tbl = lm_result.params.copy()
    tbl.sort(ascending=False)
    dfv = pd.DataFrame(tbl, columns=['Coef'])
    return dfv

def res_coef_bairros(lm_result):
    '''
    Converte um statsmodels.ResultWraper em um pandas.DataFrame com somente
    os coeficientes de bairros. 
    '''
    import re
    coef = lm_result.params.copy()
    coef.sort(ascending=False)
    vars_ = coef.index.tolist()
    import re
    p = re.compile(r'[A-Z].*')
    idx = [vars_[i] for i in range(len(vars_)) if p.search(vars_[i])]
    bairros = pd.DataFrame(coef.loc[idx], columns=['Coef'])
    bairros.drop('Intercept',inplace=True)
    return bairros
    
def res_coef_intr(lm_result):
    '''
    Converte um statsmodels.ResultWraper em um pandas.DataFrame com somente
    os coeficientes das variáveis intrínsecas. 
    '''
    
    import re
    coef = lm_result.params.copy()
    coef.sort(ascending=False)
    vars_ = coef.index.tolist()
    p = re.compile(r'[A-Z].*')
    idx_ = [vars_[i] for i in range(len(vars_)) if not p.search(vars_[i])]
    varint = pd.DataFrame(coef.loc[idx_], columns=['Coef'])
    return varint
    
def statsmodels_df(lm_):
    '''
    Converte a tabela de parâmtros de um  objeto 
    statsmodels.ResultWraper em um pandas.DataFrame ordenado 
    pelo valor do coeficiente.
    '''
    from collections import OrderedDict as OD
    dic = OD()
    dic['coef']=lm_.params
    dic['std err']=lm_.bse
    dic['t']=lm_.tvalues
    dic['P>|t|']=lm_.pvalues
    dic['[95% Conf. Int.]']=lm_.conf_int().apply(
        lambda x: '%1.3f'%x[0]+ ' '+'%1.3f'%x[1], axis=1)
    df = pd.DataFrame.from_dict(dic, )
    # Alteração do nome para manter o 'Intercept' no topo.
    df.index = [i.replace('Intercept','!Intercept') 
                for i in df.index.tolist()]   
    df.sort(inplace=True)
    # Alteração do nome para manter o 'Intercept' no topo.
    df.index = [i.replace('!Intercept','Intercept') 
                for i in df.index.tolist()]       
     #df.index.name = 'Variavel'    
    return df    
    
def getW():
    import pysal
    BASE_DIR = './spreg'
    K_NN = 100
    W_FILE = '{}/W_cidade_knn_{}.gal'.format(BASE_DIR,K_NN)
    f = pysal.open(W_FILE, 'r')
    w = f.read()
    f.close()
    w.transform = 'r'
    return w