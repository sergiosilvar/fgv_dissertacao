# -*- coding: utf-8 -*-
"""
Created on Fri Mar 07 23:25:50 2014

@author: sergio
"""

# <codecell>
import urllib2
import logging as log

import bs4
import os
from numpy import in1d

log.basicConfig(format='%(levelname)s :> %(asctime)s :> %(message)s', level=log.DEBUG)

DIR = './json/'

# <codecell>

# Links

# Índice FIPE ZAP
# http://www.zap.com.br/imoveis/fipe-zap/

# Apartamentos na Tijuca, 2 quartos, todo o período.
def troca_espaco_url(s):
    return s.replace(' ','%20')


def indice_json(estado, cidade, bairro, num_quartos):
    # http://www.zap.com.br/imoveis/fipe-zap/ajax.aspx?metodo=obterdadosgraficoindicezapimoveis&tipo=apartamento&transacao=venda&estado=rio%20de%20janeiro&cidade=rio%20de%20janeiro&bairro=tijuca&periodo=todoperiodo&qtddormitorios=2
    estado = estado.replace(' ','%20')
    cidade = cidade.replace(' ', '%20')
    bairro = bairro.replace(' ', '%20')
    url_indice = 'http://www.zap.com.br/imoveis/fipe-zap/ajax.aspx?metodo=obterdadosgraficoindicezapimoveis&tipo=apartamento&transacao=venda&estado=%s&cidade=%s&bairro=%s&periodo=todoperiodo&qtddormitorios=%d'%(estado,cidade,bairro,num_quartos)
    u = urllib2.urlopen(url_indice)
    txt = u.read()
    u.close()
    return txt


    

def download_indices_json(estado,cidade,bairro,num_quartos,pasta):
    if pasta[::-1] != '/':
        pasta += '/'
    fname = pasta+'%d_indices.json'%( num_quartos)
    f = None
    success = True
    try:
        f = open(fname,'w')
        ind = indice_json(estado,cidade,bairro,num_quartos)
        f.write(ind)
    except Exception as e:
        success = False
        print 'ERRO ao salvar indices de "%s": %s'%(bairro,e.message)
    finally:
        f.close()
    return success    
    
# <codecell>
    
def obtem_estados_zap():
    log.debug('Obtendo lista de estados da página inicial do ZAP.')
    url_inicial = 'http://www.zap.com.br/imoveis/fipe-zap'
    pag = urllib2.urlopen(url_inicial)
    soup = bs4.BeautifulSoup(pag.read())   
    
    sel = soup.find(id='ctl00_ContentPlaceHolder1_ucEstatisticas_drpEstadoPreco')
    pag.close()

    if sel != None:
        log.debug('Estados encontrado.')
    else:
        log.debug('Estados nao encontrado. Usando lista hardcoded.')

        return ['Acre',
            'Alagoas',
            'Amapa',
            'Amazonas',
            'Bahia',
            'Ceara',
            'Distrito Federal',
            'Espirito Santo',
            'Goias',
            'Internacional',
            'Maranhao',
            'Mato Grosso',
            'Mato Grosso do Sul',
            'Minas Gerais',
            'Para',
            'Paraiba',
            'Parana',
            'Pernambuco',
            'Piaui',
            'Rio de Janeiro',
            'Rio Grande do Norte',
            'Rio Grande do Sul',
            'Santa Catarina',
            'Sao Paulo',
            'Sergipe',
            'Tocantins']
        
    return sel

def obtem_cidades_zap(estado):
    if estado==None:
        msg = 'Estado não foi definido.'
        log.error(msg)
        raise Exception(msg)
    url = 'http://www.zap.com.br/imoveis/fipe-zap/ajax.aspx?metodo=ObterCidadesPrecoMedioImovel&estado=%s'%(troca_espaco_url(estado))
    pag = urllib2.urlopen(url)

    # JSON no formato [..., {"Valor":"visconde de maua", "Texto": "Visconde de Mau\xe1"\r\n  }...]
    cidades_json = eval(pag.read())
    pag.close()    
    cidades = [c['Valor'] for c in cidades_json]
    return cidades


def obtem_bairros_zap(estado,cidade):
    estado = troca_espaco_url(estado)
    cidade = troca_espaco_url(cidade)
    url_bairros = 'http://www.zap.com.br/imoveis/fipe-zap/ajax.aspx?metodo=ObterBairrosPrecoMedioImovel&estado=%s&cidade=%s'%(estado,cidade)
    pag = urllib2.urlopen(url_bairros)
    bairros_json = eval(pag.read())
    pag.close()
    bairros = [b['Valor'] for b in bairros_json]
    return bairros


def cria_pasta(pasta):
    log.debug('Verificando existência da pasta "%s"...'%(pasta))
    if pasta.find('*') < 0: 
        if os.path.isdir(pasta):
            log.debug('Pasta "%s" encontrada.' %(pasta))
        else:
            os.makedirs(pasta)
            log.debug('Pasta "%s" criada.' %(pasta))
            return True
        
# <codecell>
        
def download_fipezap(estados=None,cidades=None,bairros=None,num_quartos=None):
    if cidades != None and estados == None  :
        log.error('Definiu cidade mas não definiu estado.')
        return
    if bairros != None and cidades == None:
        log.error('Definiu bairro mas não definiu cidade.')
        return
        
    if estados == None:
        estados = obtem_estados_zap()
        
    for e in estados:
        pasta_est = DIR + e.lower()
        cria_pasta(pasta_est)
        
        if cidades == None:
            log.debug('Buscando cidades de "%s"...'%(e))
            cidades = obtem_cidades_zap(e)

        for c in cidades:
            pasta_c = pasta_est + '/' + c
            cria_pasta(pasta_c)
            
            if bairros == None:
                log.debug('Buscando bairros de "%s","%s"...' %(c,e))                
                bairros = obtem_bairros_zap(e,c)

            for b in bairros:
                pasta_b = pasta_c + '/' + b
                if cria_pasta(pasta_b):

                    if num_quartos == None:
                        num_quartos = range(4)

                    for q in num_quartos:
                        #pasta_q = pasta_b+'/'+str(q)
                        #cria_pasta(pasta_q)
                        log.debug('Buscando índices FIPE ZAP de "%s","%s","%s" para %d quartos...'%(b,c,e,q))
                        download_indices_json(e,c,b,q,pasta_b)
            
        
    
# <codecell>      
# Lista de cidades de RN
# http://www.zap.com.br/imoveis/fipe-zap/ajax.aspx?metodo=ObterCidadesPrecoMedioImovel&estado=rio%20grande%20do%20norte

# Lista de alugueis
# http://www.zap.com.br/imoveis/fipe-zap/ajax.aspx?metodo=obterdadosgraficoindicezapimoveis&tipo=apartamento&transacao=aluguel&estado=rio%20de%20janeiro&cidade=rio%20de%20janeiro&bairro=leblon&periodo=todoperiodo&qtddormitorios=0

# <codecell>


if __name__ == '__main__':
    download_fipezap('rio de janeiro', 'rio de janeiro')