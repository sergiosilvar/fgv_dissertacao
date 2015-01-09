
# coding: utf-8

# FGV - Modelagem e Mineração de Dados
# 
# Trabalho 2: Heatmap de imóveis do ZAP
# 
# Sérgio da Silva Rodrigues
# 
# Geolocalizar as ruas dos apartamentos com Google Maps.

# 46.016 registros no total.
# 18.619 registros sem logradouro.
# 35.792 registros sem lat/lng na página.
# 
# 

# In[ ]:

import simplejson, urllib
import sqlite3 as db
import IPython

con = db.connect('zap.db')

# Helper para trocar valor nulo por vazio.
def check_null(s):
    if s != None: return s.replace(' ','+')+','
    return u''

# Método único para registrar erros.
def save_error(e,cmt):
    msg = 'ERROR: ' + str(e) + ' - ' + cmt
    print msg
    f = open('error.txt', 'a')
    f.write('\n')
    f.write(msg)
    f.close()

api_key = '<coloque sua key aqui>'

GEOCODE_BASE_URL = 'http://maps.googleapis.com/maps/api/geocode/json'

# Obter geolocalização do Google Maps para um dado endereço.
def geocode(address,sensor='false', **geo_args):
    geo_args.update({
        'address': address,
        'sensor': sensor  
    })

    url = GEOCODE_BASE_URL + u'?' + urllib.urlencode(geo_args)
    result = simplejson.load(urllib.urlopen(url))
    
    return result

# Obter dados geográficos de um dado endereço.
def google(s):
    result = (None,None)
    json = geocode(s)
    
    if json['status'] == 'OK':
        if len(json['results'])>0:
            first = json['results'][0]
            gaddress = None
            gbnelat = None
            gbnelng = None
            gbswlat = None
            gbswlng = None
            glat = None
            glng = None
            try:
                gaddress = first['formatted_address']
                if first['geometry'].has_key('bounds'):
                    gbnelat = first['geometry']['bounds']['northeast']['lat']
                    gbnelng = first['geometry']['bounds']['northeast']['lng']
                    gbswlat = first['geometry']['bounds']['southwest']['lat']
                    gbswlng = first['geometry']['bounds']['southwest']['lng']
                if first['geometry'].has_key('location'):
                    glat = first['geometry']['location']['lat']
                    glng = first['geometry']['location']['lng']
                result = (gaddress,gbnelat,gbnelng,gbswlat,gbswlng,glat,glng)
            except Exception as e:
                save_error(e,s)
                result =  None
            
    return (result, json['status'])

def save_loc_details(con, values, id_loc):
    rowcount = 0
    sql = u'update location set gaddress = ?, glat=?, glng=?, gbnelat=?, gbnelng=?, gbswlat=?, gbswlng=?, visited=datetime(\'now\',\'localtime\')  where id_loc='+str(id_loc)+';'
    try:
        rowcount = con.execute(sql, values).rowcount
        con.commit()
    except Exception as e:
        con.rollback()
        save_error(e, 'ID: ' + str(id_loc))
        
    return rowcount
        


# In[ ]:

# Método principal.

# Selecionar apartametnos de interesse.
#sql = 'select id_loc,street,neigh,city from location where glat is  null and visited is null'
sql = 'select id_loc,street,neigh,city from vw_pending '
rows = con.execute(sql).fetchall()
count = 1
for r in rows:
    id_loc = r[0]
    location = check_null(r[1]) + u','+ check_null(r[2]) + u',' + check_null(r[3])
    if location[0]==',': location = location[1:]
    print 'Querying ' + str(id_loc)
    try:
        (values,status) = google(location)
    except UnicodeEncodeError as e:
        save_error(e,'ID: ' + str(id_loc))
    if status == 'OK' and values != None:
        save_loc_details(con, values, id_loc)
        print 'Saved: ' +str(id_loc) + ' - Count: ' + str(count)
        count += 1
        if count % 15 ==0:
            IPython.core.display.clear_output()
    else: 
        print 'Fail: ' +  status
        
    

