# -*- coding: utf-8 -*-

'''
Created on 05/05/2014

@author: sergio
'''
import sqlite3 as sqlite
import datetime
from zap_logging import log
import re
import pandas as pd
import psycopg2
from psycopg2.extras import DictCursor
from sqlalchemy import create_engine, MetaData
import sqlalchemy

#DATABASE_NAME = '..\spatialite\zap_dataset.sqlite'



def dia_hoje():
    return datetime.datetime.now().strftime("%d/%m/%Y")

def conecta_db():
    '''
    Retorna conexãoo ao dataset.
    '''
    #return sqlite.connect(DATABASE_NAME)
    return psycopg2.connect("dbname=zap user=sergio")



def planta_semente(url=None):
    insere_paginas([{'url':'http://www.zap.com.br/imoveis/rio-de-janeiro+rio-de-janeiro/imovel-padrao/venda/'}])
     
def paginas_nao_visitadas():
    return __select('select url from pagina where dt_visita is null where id not in (select id from erro)')

def paginas():
    cmd = 'select url from pagina '
    r = __select(cmd)
    
    lista = [x['url']  for x in  r.fetchall()]
    return lista

def registra_visita_pagina(url):
    
    cmd = 'update pagina set dt_visita = \''+dia_hoje()+ '\' where url = \''+ \
        url+'\'' 
    __executar(cmd)
    
def remove_imovel(ap):
    cmd = "delete from imovel where id = '{}'".format(ap['id'])
    __executar(cmd)
    
def existe_imovel(ap):
    r = __select("select id from imovel where id = '{}'".format(ap['id']))
    return len(r)>0
    
    
def mudou_preco(apt):
    
    
    cmd = "select * from vw_preco " \
        "where id ='{}' and preco = '{}' and dt_publicacao = '{}'" \
        .format(apt['id'],apt['preco'], apt['dt_publicacao'])
    r = __select(cmd)
    return (len(r) == 0)


def insere_novo_preco(apt):
    cmd = "insert into preco (id, dt_criacao, dt_publicacao, preco ) values " +\
        " ('{}','{}','{}','{}')".format(apt['id'], dia_hoje(), 
                                        apt['dt_publicacao'],apt['preco'])
    __executar(cmd)
    


def insere_imoveis(imoveis):
    log.debug('Inserindo {} imoveis.'.format(len(imoveis)))
    for apt in imoveis:
        if not existe_imovel(apt):
            apt[u'dt_criacao'] = dia_hoje()
            keys = sorted(apt.keys())     
            campos = ','.join(keys)
            valores = ','.join(["'"+apt[k]+"'" for k in keys if apt[k] != None])
            cmd = 'insert into imovel ('+campos+')'+' values ('+ valores+')'
            try:
                __executar(cmd)
                log.debug('imovel id={} inserido.'.format(apt['id']))
            except psycopg2.IntegrityError as e:
                log.warn(e)
        elif mudou_preco(apt):
            log.debug("imovel id = '{}' mudou preço.".format(apt['id']))
            insere_novo_preco(apt)

def __executar(cmd,params=None,con=None):
    cur = None
    try:
        if con == None: 
            con = d.conecta_db()
        
        cur = con.cursor()
        cur.execute(cmd,params)
        con.commit()
        cur.close()
        con.close()
    except Exception as e:
        if cur:
            cur.close()
        if con:
            con.close()
        raise e
    
def insere_paginas(paginas):
    
    log.debug('Inserindo {} paginas.'.format(len(paginas)))
    for pag in paginas:
        pag[u'dt_criacao'] = dia_hoje()
        keys = sorted(pag.keys())     
        campos = ','.join(keys)
        valores = ','.join(["'"+pag[k]+"'" for k in keys])
        cmd = 'insert into pagina ('+campos+')'+' values ('+ valores+')'
        try:
            __executar(cmd)
            log.debug('Pagina url={} inserida.'.format(pag['url']))
        except psycopg2.IntegrityError as e:
            log.error(e)
    

def imoveis_para_geolocalizar():
    '''
    Retorna ids dos imoveis sem geolocalização Google.
    '''
    return __select('select id,rua,bairro,cidade from vw_imovel where '+
                    ' glat is null '+
                    ' and rua is not null '+
                    ' and bairro is not null ' +
                    ' and cidade is not null ')


def define_rua_imoveis():
    '''
    Atualizar as ruas dos imoveis com base na URL para aqueles que não
    tem rua definida.
    '''
    
    apts = __select('select id, bairro, url from imovel where rua is null')
    while len(apts) > 0:
        for ap in apts:
            id_ = ap['id']
            url = ap['url']
            bairro = ap['bairro'].replace(u'Ç','C')
    
            # Rua ex:'http://www.zap.com.br/imoveis/SuperDestaque/imovel-Padrao
            # -4-quartos-venda-RIO-DE-JANEIRO-BOTAFOGO-RUA-DONA-MARIANA/ID-5462410'
            match =re.match(r'.*'+bairro.replace(' ','-')+'-(.*)/ID.*', url)
            if match:
                rua = match.groups()[0]
                rua = rua.replace('-',' ')
                atualiza_imoveis([{'id':id_, 'rua':rua}])
                log.debug(u'Rua {0} do imovel {1} atualizado.'.format(rua,id_))
        apts = __select('select id, bairro, url from imovel where rua is null')
    
def atualiza_imoveis(imoveis):
    def __atualiza_apt(unid,id):
            valores = u', '.join([u"{0} = '{1}'".format(k,unid[k]) for k in keys 
                        if unid[k] != None])
            cmd = u"update imovel set {0} where id = '{1}'".format(
                    valores, id)
            __executar(cmd)

    log.debug('Atualizando {} imoveis.'.format(len(imoveis)))

    for apt in imoveis:
        apt['dt_atualizacao'] = datetime.datetime.now().strftime("%d/%m/%y")
        keys = apt.keys()
        keys.remove('id')
        tentar_sem_descricao = False     
        try:
            __atualiza_apt(apt, apt['id'])
            log.debug(u'imovel id={} atualizado.'.format(apt['id']))
        except Exception as e:
            tentar_sem_descricao = True

        if tentar_sem_descricao: 
            try:
                if apt.has_key('descricao'):
                    apt.pop('descricao', None)
                    keys.remove('descricao')
                __atualiza_apt(apt, apt['id'])
            except Exception as e:
                log.error(u'Erro apt ID={}:{}'.format(apt['id'],e))
                insere_erro(apt['id'], e)
                continue

    
def __select(cmd):
   
    # POSTGRES 
    con = conecta_db()
    dict_cur = con.cursor(cursor_factory=DictCursor)
    dict_cur.execute(cmd)
    rows = dict_cur.fetchall()
    lista = [dict(r) for r in rows]
    dict_cur.close()
    con.close()
    return lista
    
    
        
def testa_log():
    log.debug('Testando log em dataset.py via captura.py')
        
    


def ruas_para_geolocalizar():
    '''
    Retorna ruas dos imoveis sem geolocalização Google.
    '''
    return __select('select distinct rua,bairro,cidade from vw_imovel where '+
                    ' glat is null '+
                    ' and rua is not null '+
                    ' and rua <> \'\' '+
                    ' and bairro is not null ' +
                    ' and cidade is not null ')
    


def atualiza_geolocalizacao_ruas(ruas):
    log.debug('Atualizando geolocalizacao de {} ruas.'.format(len(ruas)))

    for r in ruas:
        r['dt_atualizacao'] = datetime.datetime.now().strftime("%d/%m/%y")
        keys = r.keys()
        keys.remove('rua')
        keys.remove('bairro')
        keys.remove('cidade')
        try:
            valores = u', '.join(["{0} = '{1}'".format(k,r[k]) for k in keys 
                        if r[k] != None])
            cmd = u"update imovel set {} where rua = '{}' and bairro = '{}' and cidade = '{}'".format(valores, r['rua'], r['bairro'], r['cidade'])
            __executar(cmd)
            log.debug(u'imoveis da rua {} - bairro {} atualizados.'.format(r['rua'],r['bairro']))
        except psycopg2.IntegrityError as e:
            log.error(e)
            
            
        except UnicodeEncodeError as e:
            log.error(u'Erro de unicode na rua {}-{}'.format(r['rua'],r['bairro']))
            continue
        
        except psycopg2.OperationalError as e:
            # Database is locked.
            log.error(e)
            continue
    
    
def imoveis_nao_visitados():
    #return __select('select id,url from imovel where det_imovel is  null and carac_imovel is  null and carac_condo is  null')
    return __select('select id,url from imovel where dt_visita is  null')

# FIXME: Remover apt duplicados.
def remove_duplicados():
    dup = __select('select * from imovel group by id having count(id) > 1')
    for d in dup:
        #remove_imovel(d)
        insere_imoveis([d])

def remove_preco_duplicado():
    dup = __select('select id,dt_publicacao,preco from preco group by  ' +
        ' id,dt_criacao,dt_publicacao,preco having count(* ) > 1 order by 1')
    for d in dup:
        #remove_imovel(d)
        insere_imoveis([d])
        
        
def insere_erro(id,msg=None):
    cmd = "insert into erro (id) values ('{}')".format(id,msg)
    __executar(cmd)

def exporta_csv(arquivo='imoveis.csv'):
    con = conecta_db()
    cmd = 'select id, lat,lng, preco/area as m2, url from vw_imovel'
    df = pd.io.sql.read_frame(cmd,con)
    df.to_csv(arquivo, index=False, encoding='utf-8')
    log.debug('Arquivo de exportacao ''{}'' criado.'.format(arquivo))
    con.close()
    
def imoveis():
    return __select('select id,area, preco,m2,condominio,garagem, quartos, ' +
        'suites, dt_criacao, dt_publicacao, dt_visita, dt_atualizacao, lat, '+
        'lng,url,distancia  from vw_imovel ')

    

def salva_dataframe(df,tabela,*args,**kwargs):
    engine = create_engine(r'postgresql://sergio:@localhost/zap')
    meta = sqlalchemy.MetaData(engine, schema='public')
    meta.reflect(engine, schema='public')
    pdsql = pd.io.sql.SQLDatabase(engine, meta=meta)
    if not kwargs.has_key('if_exists'):
        kwargs['if_exists'] = 'replace'
    if not kwargs.has_key('index'):
        kwargs['index'] = True
    #pdsql.to_sql(dfc, 'caracteristica',if_exists='replace',index=True)    
    pdsql.to_sql(df,tabela,*args,**kwargs)    
    
if __name__ == '__main__':
    pass
    #planta_semente()