# -*- coding: utf-8 -*-

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

import dataset
from zap_logging import log 
import requests
from simplejson.decoder import JSONDecodeError 

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
def _geocode(address,sensor='false', **geo_args):
    geo_args.update({
        'address': address,
        'sensor': sensor  
    })

    #url = GEOCODE_BASE_URL + u'?' + urllib.urlencode(geo_args)
    #result = simplejson.load(urllib.urlopen(url))
    req = requests.get(GEOCODE_BASE_URL, params=geo_args)
    if req:
        result = req.json()
        return result
    else:
        return None

# Obter dados geográficos de um dado endereço.
def _google(s):
    result = (None,None)
    json = _geocode(s)
    
    ''' Ex: 
    {
        'status': 'OK', 
        'results': [
            {
            'geometry': {
                'location': {'lat': -22.9561176, 'lng': -43.1874765}, 
                'viewport': {
                    'northeast': {
                        'lat': -22.9547686197085, 
                        'lng': -43.18612751970849
                    }, 
                    'southwest': {
                            'lat': -22.9574665802915, 
                            'lng': -43.18882548029149
                    }
                }, 
            'location_type': 'GEOMETRIC_CENTER'
            }, 
            'address_components': [
                '{
                'long_name': 'Rua Dona Mariana', 
                'types': ['route'], 
                'short_name': 'Rua Dona Mariana'
                }, 
                {
                'long_name': 'Botafogo', 
                'types': ['neighborhood', 'political'], 
                'short_name': 'Botafogo'
                }, 
                {
                'long_name': 'Rio', 
                'types': ['locality', 'political'], 
                'short_name': 'Rio'
                }, 
                {
                'long_name': 'Rio de Janeiro', 
                'types': ['administrative_area_level_1', 'political'], 
                'short_name': 'RJ'
                }, 
                {
                'long_name': 'Brazil', 
                'types': ['country', 'political'], 
                'short_name': 'BR'
                },
                {
                'long_name': '22280-020', 
                'types': ['postal_code'], 
                'short_name': '22280-020'
                }
            ], 
            'formatted_address': 'Rua Dona Mariana - Botafogo, Rio - Rio de Janeiro, 22280-020, Brazil',
            'types': ['route']}]}
'''
    if json['status'] == 'OK':
        if len(json['results'])>0:
            first = json['results'][0]
            apt = {}
            apt['gbnelat'] = None
            apt['gbnelng'] = None
            apt['gbswlat'] = None
            apt['gbswlng'] = None
            apt['glat'] = None
            apt['glng'] = None
            apt['cep'] = None
            try:
                # Não é mais necessário.
                # gaddress = first['formatted_address']
                
                if first['geometry'].has_key('bounds'):
                    apt['gbnelat'] = first['geometry']['bounds']['northeast']['lat']
                    apt['gbnelng'] = first['geometry']['bounds']['northeast']['lng']
                    apt['gbswlat'] = first['geometry']['bounds']['southwest']['lat']
                    apt['gbswlng'] = first['geometry']['bounds']['southwest']['lng']
                if first['geometry'].has_key('location'):
                    apt['glat'] = first['geometry']['location']['lat']
                    apt['glng'] = first['geometry']['location']['lng']
                if first.has_key('address_components'):
                    x = [y['short_name'] for y in first['address_components'] if 'postal_code' in y['types']]
                    if len(x) > 0:
                        apt['cep'] = x[0]    
                result = apt
            except Exception as e:
                save_error(e,s)
                result =  None
            
    return (result, json['status'])


        

def geolocalizar_apartamentos():
    '''
    Geolocaliza apartamentos no dataset.
    '''
    
    apartamentos = dataset.apartamentos_para_geolocalizar()
    

    while len(apartamentos) > 0:
        for apt in apartamentos:
            location = ','.join([apt['rua'],apt['bairro'],apt['cidade']])
            log.debug('Geolocalizando {}...'.format( location))
            try:
                (gapt,status) = _google(location)
            except UnicodeEncodeError as e:
                log.error(u'Erro de unicode no apartamento ID:{} '.format(apt['id']))
            # Exemplo de retorno:
            # Rua Dona Mariana - Botafogo, Rio - Rio de Janeiro, 22280-020, Brazil
            if status == 'OK' and gapt != None:
                gapt['id'] = apt['id']
                dataset.atualiza_apartamentos([gapt])
        apartamentos = dataset.apartamentos_para_geolocalizar()
    log.info('Geolocalização de apartamentos com Google terminado.')
                
def geolocaliza_ruas():
    '''
    Geolocaliza apartamentos no dataset.
    '''
    
    ruas = dataset.ruas_para_geolocalizar()
    

    while len(ruas) > 0:
        for r in ruas:
            #r['rua'] = r['rua'].replace(u'Ç','C')
            #r['bairro'] = r['bairro'].replace(u'Ç','C')
            #r['cidade'] =  r['cidade'].replace(u'Ç','C')
            location = u','.join([r['rua'],r['bairro'],r['cidade']])
            log.debug(u'Geolocalizando {}...'.format( location))
            try:
                (grua,status) = _google(location)
                if status == 'OK' and grua != None:
                    grua['rua'] = r['rua']
                    grua['bairro'] = r['bairro']
                    grua['cidade'] = r['cidade']
                    dataset.atualiza_geolocalizacao_ruas([grua])
                elif status == 'OVER_QUERY_LIMIT':
                    log.info('Limite API Google alcançado.')
                    break
                elif status == 'ZERO_RESULTS':
                    log.warn('Endereço {} sem resultados'.format(location))
                    dataset.insere_erro(location, status)
            except UnicodeEncodeError as e:
                log.error(u'Erro de unicode na  rua :{} '.format(location))
            except JSONDecodeError as e:
                log.error(u'Erro ao processar JSON :{} '.format(e))
        if status == 'OVER_QUERY_LIMIT':
            break
        else:
            ruas = dataset.ruas_para_geolocalizar()
    log.info('Geolocalização com Google terminado.')
                
if __name__ == '__main__':
    geolocaliza_ruas()
