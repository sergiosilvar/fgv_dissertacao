# -*- coding: utf-8 -*-

import sys,os; 
import pandas as pd
import psycopg2
from mpltools import style
import unicodedata
import geopandas as gd
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

    
    return 'ERRO: ''unicode'', ''str'' ou ''list'' esperado. ' + str(type(str_or_list)) + ' encontrado.'