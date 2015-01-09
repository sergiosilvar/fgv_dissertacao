
# coding: utf-8

# FGV - Modelagem e Mineração de Dados
# 
# Trabalho 2: Heatmap de imóveis do ZAP
# 
# Sérgio da Silva Rodrigues
# 
# Capturar informações de imóveis do ZAP.

# In[1]:

from bs4 import BeautifulSoup 
import urllib2
import re
import os
import datetime as dt


# Escrever conteúdo em um arquivo.
def write_file(filename, content):
    WRITE_MODE = 'w'
    f = open(filename, WRITE_MODE)
    f.write(content)
    f.close()

# Ler todo o conteúdo de um arquivo.
def read_file(filename):
    READ_MODE = 'r'
    f = open(filename, READ_MODE)
    text = f.read()
    f.close()
    return text

# Helper para debug.
def debug(s):
    #print s
    pass


# In[2]:

# Estrutura para armazenar dados de um apartamento.
class Home:
    def __init__(self,
            area=None,
            bedrooms=None,
            city=None,
            created=None,
            garage=None,
            id=None,
            neigh=None,
            price=None,
            published=None,
            state=None,
            suites=None,
            visited=None,
            url=None,
            url_photo=None ):
        self.area=area
        self.bedrooms=bedrooms
        self.city=city
        self.created=created
        self.garage=garage
        self.id=id
        self.neigh=neigh
        self.price=price
        self.published=published
        self.state=state
        self.suites=suites
        self.visited=visited
        self.url=url
        self.url_photo=url_photo        

    def price_area(self):
        if self.price != None and self.area != None:
            return self.price/self.area
        
    
# Estrutura para armanezar dados de uma página do ZAP.
class Page:
    def __init__(self, created=None, visited=None, url=None):
        self.url = url
        self.created = created
        self.visited = visited

    def __str__(self):
        return str(vars(self))


# In[3]:

# Criação do banco de dados.

import sqlite3 as sqlite


DATABASE_NAME = 'zap_dataset'
DATABASE_EXTENSION = '.db'

DDL_CREATE_TABLE = 'CREATE TABLE IF NOT EXISTS'
DATETIME_NOW = 'datetime(\'now\',\'localtime\')'

# Helper para criação de triggers.
def __create_trigger_created_on_insert(table_name):
    return 'CREATE TRIGGER IF NOT EXISTS trg_' + table_name + '_insert ' + ' AFTER INSERT ON ' +     table_name +     ' BEGIN         update ' + table_name + ' set created = '+DATETIME_NOW+' where rowid=new.rowid;     END; '

# Helper para criação de chave primária.    
def __create_pk(table_name,field_name):
    return 'CREATE UNIQUE INDEX IF NOT EXISTS pk_'  + table_name + ' ON ' + table_name         + '(' + field_name + ')' 
    

    

# Table HOME.
TABLE_HOME = 'apartamento'
FIELDS_TABLE_HOME = '(area,garagem,cidade,dt_criacao,id,    bairro,preco,dt_publicacao,dt_visita,estado,suites,url,url_photo )'
CREATE_TABLE_HOME = DDL_CREATE_TABLE + ' ' + TABLE_HOME + ' ' + FIELDS_TABLE_HOME
CREATE_PK_HOME = __create_pk(TABLE_HOME, 'id')
CREATE_TRG_HOME_INSERT = __create_trigger_created_on_insert(TABLE_HOME)
INSERT_TABLE_HOME = 'insert into ' + TABLE_HOME + FIELDS_TABLE_HOME + ' values '     '(\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\') '


# Table PAGE.
TABLE_PAGE = 'page'
FIELDS_TABLE_PAGE = '(created,visited,url)'
CREATE_TABLE_PAGE = DDL_CREATE_TABLE + ' ' + TABLE_PAGE + ' ' + FIELDS_TABLE_PAGE
CREATE_PK_PAGE = __create_pk(TABLE_PAGE, 'url')
CREATE_TRG_PAGE_INSERT = __create_trigger_created_on_insert(TABLE_PAGE)
INSERT_TABLE_PAGE = 'insert into ' + TABLE_PAGE + FIELDS_TABLE_PAGE + ' values (\'%s\',\'%s\',\'%s\')' 

# Lists of DML.
CREATE_ALL = [CREATE_TABLE_HOME, CREATE_PK_HOME, CREATE_TRG_HOME_INSERT, CREATE_TABLE_PAGE, CREATE_PK_PAGE,CREATE_TRG_PAGE_INSERT]

# Método único para acessar o banco de dados.
def connect_database():
    return sqlite.connect(DATABASE_NAME+DATABASE_EXTENSION)

# Limbar banco de dados.
def __drop_database(cursor):
    objects = ['trigger','index', 'view','table']
    for obj in objects:
        result = cursor.execute('select \'DROP '+obj+' IF EXISTS \' || name || \';\' FROM SQLITE_MASTER   WHERE TYPE = \''+obj+'\' ')
        drops = result.fetchall()
        for drop in drops:
            __execute_cmd(drop[0], connect_database().cursor())

# Método único para exear SQL's e debugar.    
def __execute_cmd(cmd, cursor):
    debug('SQL Command: ' + cmd)
    result = cursor.execute(cmd)
    debug('Done.')
    return result
    
# Tratamento único para exceções de SQL.    
def __sql_exception(connection,error):
    debug("SQL WARNING: {0}".format(error))
    connection.rollback()
    debug("SQL Command aborted.")

# Criação do banco de dados. Opcionalmente pode-se excluir as tabelas existentes.
def create_database(drop_all=False):
    
    con = connect_database()
    c = con.cursor()
    
    # Drop all objects.
    if drop_all:
        __drop_database(c)
        
    # Create all objects.
    for create_cmd in CREATE_ALL:
        __execute_cmd(create_cmd, con.cursor())

    con.commit()
    con.close()
    
# Salvar uma lista de apartamen.    
def save_homes(homes):
    try:
        con = connect_database()
        for home in homes:
            command = INSERT_TABLE_HOME % (home.area,home.garage,home.city,home.created,home.id,home.neigh,
                home.price,home.published,home.visited,home.state,home.suites,home.url,home.url_photo)
            __execute_cmd(command,con.cursor())
        con.commit()
    except Exception as e:
        __sql_exception(con,e)
    finally:
        con.close()

# Salvar um alista de páginas.		
def save_pages(pages):
    try:
        con = connect_database()
        for page in pages:
            if page.url != None:
                command = INSERT_TABLE_PAGE % (page.created,page.visited,page.url)
                __execute_cmd(command, con.cursor())
            else:
                debug('WARNING: Page instance with null url.')
        con.commit()
    except Exception as e:
        __sql_exception(con,e)
    finally:
        con.close()

# Obter uma lista de páginas do banco de dados, atendendo a determinados critérios.        
def select_pages( where_clause=''):
    pages = None
    try:
        con = connect_database()
        command = 'select * from page ' + where_clause
        rows = __execute_cmd(command, con)
        debug(rows)
        pages = [Page(row[0],row[1],row[2]) for row in rows]
    except Exception as e:
        __sql_exception(con,e)
    finally:
        con.close()
    return pages

# Excluir páginas do banco de dados, atendendo a determinados critérios.
def delete_pages(where_clause=''):
    try: 
        con = connect_database()
        command = 'delete from page ' + where_clause
        __execute_cmd(command,con)
        con.commit()
    except Exception as e:
        __sql_exception(con,e)
    finally:
        con.close()

# Excluir apartamentos do banco de dados, atendendo a determinados critérios.        
def delete_homes(where_clause=''):
    try: 
        con = connect_database()
        command = 'delete from home ' + where_clause
        __execute_cmd(command,con)
        con.commit()
    except Exception as e:
        __sql_exception(con,e)
    finally:
        con.close()      

# Excluir todos os dados do banco.        
def delete_all_data():
    delete_homes()
    delete_pages()

# Marcar uma pagina como visitada.    
def mark_page_as_visited(page):
    try:
        con = connect_database()
        command = 'update page set visited = ' + DATETIME_NOW + '  where url = \'' + page.url + '\''
        __execute_cmd(command,con)
        con.commit()
    except Exception as e:
        __sql_exception(con,e)
    finally:
        con.close()
        
def plant_seed():
    try:
        con = connect_database()
        cmd = 'insert into page (created,url) values ('+DATETIME_NOW+             '\'http://www.zap.com.br/imoveis/rio-de-janeiro+rio-de-janeiro/apartamento-padrao/venda/\')'
        print cmd
        ____execute_cmd(cmd,con)
    except Exception as e:
        __sql_exception(con,e)
    finally:
        con.close()


# In[14]:




# In[4]:

# Helper para registrar o tempo que dura um trecho de código.
def clock(t1, msg):
    t2 = dt.datetime.now()
    delta = t2 - t1
    print msg + ' in %.2f s.' % (delta.seconds)

# Extrair as informações iniciais de um apartametno.    
def extract_minicard(div):
    '''
    Extratcs a Home instance from the mini card presented as the result query.
    @param div - a div tag of the class 'content-minificha'.
    @return home instance.
    '''
    
    home = Home()
    
    # Url.
    home.url = div.a['href']
    
    # Photo url.
    home.url_photo = div.a.img['src']
    
    # Neighborhood, city, state and price tags.
    span_location = div.find('span', class_='location')
    sublocal = span_location.findAll('a')
    
    # Tag indexes.
    IDX_NEIGH = 0
    IDX_CITY = 1
    IDX_STATE = 2
    IDX_PRICE = 1
    
    # Neighborhood.
    home.neigh = sublocal[IDX_NEIGH].string
    
    # City
    home.city = sublocal[IDX_CITY].string
    
    # State.
    home.state = sublocal[IDX_STATE].string
    
    # Price.
    home.price = div.find('a', class_='valorOferta').contents[IDX_PRICE]
    
    details = div.find('a',class_='itemCaracteristicas')
    list_details = [s for s in details.strings]
    for i in range(len(list_details)):
        # Area.
        if list_details[i] == u'Área':
            area = list_details[i+1]
            home.area = re.findall(r'\d+', area)[0]
        
        # Garage.
        if list_details[i] == u'Vagas':
            home.garage = list_details[i+1]
        
        # Suites.
        if list_details[i] == u'Suítes':
            home.suites = list_details[i+1]
        
        # Bedrooms.
        if list_details[i] == u'Dorms':
            home.bedrooms = list_details[i+1]
    
    # Publication date.
    span_date = div.find('span', class_='dtlisted')
    home.published = re.findall(r'(\d+/\d+/\d+)', span_date.string)[0]
    
    # Extract id from URL.
    id = re.findall(r'ID-\d+',home.url)[0]
    home.id = re.findall(r'\d+',id)[0]

    
    return home

# Encontrar apartamentos e links para outras páginas.
def parse_page(page):
    homes,pages = [],[]
    response = None
    
    try:
        response = urllib2.urlopen(page.url).read()
    except Exception as e:
        debug('URL Error: {0} - url: {1}'.format(e,page.url))
        
    if response != None:
        doc = BeautifulSoup(response)
        divs = doc.findAll('div', class_='content-minificha' )
        for div in divs:  
            homes.append(extract_minicard(div))
        next_pages = doc.findAll('a', class_='pagNext')
        for next_page in next_pages:
            url = next_page['href']
            
            # Remove 'request number' from url.
            if url.find('&rn')>0:
                url = url.split('&rn')[0]
            if url != None:
                new_page = Page(url=url)
                pages.append(new_page)
        
    return homes,pages
    
    


# In[6]:

# Método principal.

# 1.a página de apartamentos do ZAP Imóveis na cidade do Rio de Janeiro.
#url = 'http://www.zap.com.br/imoveis/rio-de-janeiro+rio-de-janeiro/apartamento-padrao/venda/'

# Enquanto houver páginas não visitadas.
pages =  select_pages(' where visited is null')
print 'Número de páginas a visitar: %d'%(len(pages))
while len(pages)>0:
    for page in pages:
        t = dt.datetime.now()
        print('Parsing page ' + page.url)
        # Recupera apartamentos e páginas.
        new_homes, new_pages =  parse_page(page)
        clock(t,'Page parsed: ' + page.url)
        mark_page_as_visited(page)    
        save_homes(new_homes)
        save_pages(new_pages)
        
    pages =  select_pages(' where visited == \'None\'')    
    
print('Crawling finished.')


# In[5]:

con = connect_database()
c = con.cursor()
r = c.execute('select * from page  where visited is null')
r.fetchall()

