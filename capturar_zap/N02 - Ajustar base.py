
# coding: utf-8

# FGV - Modelagem e Mineração de Dados
# 
# Trabalho 2: Heatmap de imóveis do ZAP
# 
# Sérgio da Silva Rodrigues
# 
# Obter detalhes dos apartamentos e ajustes no banco de dados.

# In[ ]:

import sqlite3 as sql
import urllib2
from bs4 import BeautifulSoup
import IPython


# In[ ]:

# Adicionar campos
'''
con.execute('alter table home add column street;') 
con.execute('alter table home add column lat;') 
con.execute('alter table home add column long;') 
con.execute('alter table home add column bedrooms;')
con.execute('alter table home add column description;')
con.execute('alter table home add column condo;')
con.commit()
'''


# In[ ]:

# Alguns ajustes no banco de dados.
def adjust_db():
    
    rows = con.execute('select id,  neigh, city, url from home where bedrooms is null').fetchall()
    IDX_ID = 0
    IDX_NEIGH = 1
    IDX_CITY = 2
    IDX_URL = 3
    text1 = u'Apartamento-Padrao-'
    len_text1 = len(text1)
    text2 = u'-venda-'
    len_text2 = len(text2)
    for row in rows:
        id_ = row[IDX_ID]
        url = row[IDX_URL]
        start = url.index(text1) + len_text
        try:
            end = url.index(text2)
        except Exception as e:
            print 'erro: {0} - ID {1} - {2}'.format(e,id_, text2)
            continue
        bedrooms =  url[start:end]
        neigh = '-'.join(row[IDX_NEIGH].replace(u'Ç',u'C').split(' '))
        try:
            start = url.index(neigh)+len(neigh) + 1
        except Exception as e:
            print 'erro: ' + neigh + ' - ID: '+id_ 
            continue
        street =  url[start:]
        end = street.index('/')
        street = street[:end].replace('-',' ')
        
        sql = 'UPDATE HOME SET bedrooms = \''+bedrooms+'\', street = \''+street+'\' where id = \''+id_+ '\';'
        con.execute(sql)
    con.commit()
    


# In[ ]:

# Recupearar detalhes de um apartamento.
def extract_details(doc):
    description,lat,long,condo = None, None, None, None
    
    img = doc.find('img', class_='fichaMapa')
    if img != None:
        url_geo = img['src']
        start = url_geo.rindex('/')+1
        end = url_geo.rindex('.png')
        try:
            lat,long = url_geo[start:end].split('_')
        except Exception as e:
            onclick = img['onclick']
            start = onclick.index(u'abreMapa(')+len(u'abreMapa(')
            end = start + 29
            lat, long = onclick[start:end].split(',')
        
    h3_desc = doc.find('h3', attrs={'itemprop':'description'})
    if h3_desc != None: 
        description = unicode(h3_desc.string)
    
    #div_details = [str(s) for s in doc.findAll('div', class_='fc-maisdetalhes')]
    #feature_home,feature_condo = div_details
        
    li = doc.find(id='ctl00_ContentPlaceHolder1_resumo_liCondominio')
    if li != None:
            condo = unicode(li.find('span', class_='featureValue').string).replace('R$','').strip()
            
    
    #description,lat,long,condo
    return description, lat,long,condo

# Obter detalhes de uma lista de apartamentos.
def process_rows(rows):
    count = con.execute('select count(id) from home where lat is null').fetchone()[0]*1.0
    total = con.execute('select count(id) from home ').fetchone()[0]*1.0
    
    for row in rows: 
        url=row[3]
        id_=row[0]
        try:
            if (count % 10) == 0:
                IPython.core.display.clear_output()
    
            print 'Processing: %s' %(url)
            response = urllib2.urlopen(url).read()
            if response != None:
                doc = BeautifulSoup(response)
                description, lat,long,condo = extract_details(doc)
                #sql = u'UPDATE HOME SET  description= \''+description+'\', lat=\''+lat + '\',long=\''+long+'\',condo=\''+condo+'\' where id = \''+id_+'\';'
                sql = u'UPDATE HOME SET description=?, lat=?, long=?, condo=? where id=?;'
                con.execute(sql, (description, lat, long, condo, id_))
                con.commit()
        except Exception as e:
            s = u'Error: %s - ID: %s - SQL: %s' % (e,id_,sql)
            print s
            #f = open('error.txt', 'a')
            #f.write(s)
            #f.close()
            continue
            
        print 'Progess: %.3f%% - ID: %s' % (count/total*100.0, id_)
        count += 1
            



# In[ ]:

# Exportar para arquivo.
def export_to_file():
    con = sql.connect('zap_old.db')
    rows = con.execute('select id,price from home ').fetchall()
    f = open('zap_old.csv','w')
    for r in rows:
        f.write(str(r[0])+';'+str(r[1])+'\n')
    f.close()
    con.close()


# In[ ]:

def copy_zap():
    #rows = con.execute('select id,price from home ').fetchall()
    f = open('zap_old.csv','r')
    lines = f.readlines()
    f.close()
    con = sql.connect('zap.db')
    for line in lines:
        id_,price = line.split(';')
        update = u'update home set price_old2 = \''+price+'\' where id_home = ' + str(id_)
        con.execute(update)
        con.commit()
    con.close()


# ### Identificar apartamentos que foram vendidos 
# Acessar novamente as pagínas e assumir que aquelas que foram desativadas como vendidas.
# 
# Exemplo de página de apartamento "vendido":  
# http://www.zap.com.br/imoveis/oferta/Apartamento-Padrao-2-quartos-venda-RIO-DE-JANEIRO-COPACABANA-/ID-1393817
# 
# Conteúdo:  
# `<div class="erro_tit">Essa oferta foi desativada pelo anunciante.</div>`
# 
# 

# In[ ]:

def add_column_sold():
    con = sql.connect('zap.db')
    con.execute('alter table home add column sold date')
    con.close()


# In[ ]:

def check_homes_sold():
    con = sql.connect('zap.db')
    def debug(s): 
        #print s
        pass
        
    #rows = con.execute('select id_home,  url from home where url is not null').fetchall()
    rows = con.execute('select id_home,  url from home where sold is null and visited is null').fetchall()
    text_to_find = 'Essa oferta foi desativada pelo anunciante'
    total = 46015
    count = 0
    cmd=''
    sold = 0
    not_sold = 1
    for row in rows: 
            id_home=row[0]
            url=row[1]
            try:
                debug(u'Processing: %s' %(url))
                response = urllib2.urlopen(url).read()
                if response != None:
                    if response.find(text_to_find)>0:
                        debug(u'Achei apartamento vendido: ' + str(id_home))
                        cmd = u'UPDATE HOME SET  sold= date(\'now\',\'localtime\'), visited = date(\'now\',\'localtime\') where id_home = '+str(id_home)+';'
                        sold += 1
                    else:
                        cmd = u'UPDATE HOME SET  visited= date(\'now\',\'localtime\') where id_home = '+str(id_home)+';'
                        not_sold += 1
                        debug('Não vendido')
                    
                con.execute(cmd)
                con.commit()
                debug('Commit')
                    
            except Exception as e:
                s = u'Error: %s - ID: %s' % (e,id_)
                print s
                f = open('error2.txt', 'a')
                f.write(s)
                f.close()
                continue
    
            count += 1
            if (count % 50) == 0:
                print u'Progess: %.3f%% - Sold: %d - Not Sold: %d' % (count*1.0/total*100.0, sold, not_sold)
    con.close()


# In[ ]:



