# -*- coding: utf-8 -*-

'''
Created on 06/05/2014

@author: sergio
'''
import re
import requests
from bs4 import BeautifulSoup
import thread
import dataset as d
from zap_logging import log
import threading


def __processa_html(html):
    return BeautifulSoup(html, 'html.parser')

def __extrair_minificha(div):
    '''
    Retorna informações de um apartamento de um elemento DIV da classe 
        'content-minificha' de uma página HTML de anúncios do ZAP Imóveis.
    @param div - Elemento DIV da página de classe CSS 'content-minificha' que
        contém informações de um apartamento.
    '''
    
    
    apartamento = {}
    
    # Url.
    apartamento['url'] = div.a['href']
    
    # Photo url.
    apartamento['url_foto'] = div.a.img['src']
    
    # Neighborhood, city, state and price tags.
    span_location = div.find('span', class_='location')
    sublocal = span_location.findAll('a')
    
    # Tag indexes.
    IDX_NEIGH = 0
    IDX_CITY = 1
    IDX_STATE = 2
    IDX_PRICE = 1
    
    # Neighborhood.
    apartamento['bairro'] = sublocal[IDX_NEIGH].string
    
    # City
    apartamento['cidade'] = sublocal[IDX_CITY].string
    
    # State.
    apartamento['estado'] = sublocal[IDX_STATE].string
    
    # Price.
    apartamento['preco'] = div.find('a', class_='valorOferta').contents[IDX_PRICE]
    
    details = div.find('a',class_='itemCaracteristicas')
    list_details = [s for s in details.strings]
    for i in range(len(list_details)):
        # Area.
        if list_details[i] == u'Área':
            area = list_details[i+1]
            apartamento['area'] = re.findall(r'\d+', area)[0]
        
        # Garage.
        if list_details[i] == u'Vagas':
            apartamento['garagem'] = list_details[i+1]
        
        # Suites.
        if list_details[i] == u'Suítes':
            apartamento['suites'] = list_details[i+1]
        
        # Bedrooms.
        if list_details[i] == u'Dorms':
            apartamento['quartos'] = list_details[i+1]
    
    # Publication date.
    span_date = div.find('span', class_='dtlisted')
    apartamento['dt_publicacao'] = re.findall(r'(\d+/\d+/\d+)', span_date.string)[0]
    
    # Extract id from URL.
    id = re.findall(r'ID-\d+',apartamento['url'])[0]
    apartamento['id'] = re.findall(r'\d+',id)[0]

    
    return apartamento


def __processar_pagina(url):
    '''
    Processa uma página de anúncios do ZAP Imóveis e retorna uma lista de
    apartamentos e lista de links para outras páginas de anúncios.     
    @param url - Link URL de uma página de anúncios do ZAP Imóveis a ser 
        processada.
    '''   
    apartamentos,paginas = [],[]
    response = None
    
    response = requests.get(url).text
    doc = __processa_html(response) 
    
    
    divs = doc.findAll('div', class_='content-minificha' )
    for div in divs:  
        apartamentos.append(__extrair_minificha(div))
    next_pages = doc.findAll('a', class_='paginacao_link')
    for next_page in next_pages:
        if 'ativo' in next_page['class']:
            continue                
        url = next_page['href']
        
        # Remove 'request number' from url.
        if url.find('&rn')>0:
            url = url.split('&rn')[0]
        if url != None:
            paginas.append({'url':url})
        
    if response != None:
        
        return apartamentos,paginas
    return None

    
def captura_apartamentos():
    log.info('Iniciando captura de apartamentos do zap. Veja log em "log.txt".')
    paginas = d.paginas_nao_visitadas()
    
    while  len(paginas) > 0:
        try:
            url = paginas[0]['url']
            log.info('Processando pagina "{}".'.format(url))
            apartamentos,paginas = __processar_pagina(url)
            log.info('Pagina "{}" processada.'.format(url))
            
            d.insere_paginas(paginas)
            d.insere_imoveis(apartamentos)
            d.registra_visita_pagina(url)
        except Exception as e:
            log.error(e)
        finally:
            paginas = d.paginas_nao_visitadas()
    log.info('Nao ha paginas a visitar. Captura de apartmentos terminado.')


        
        

def __captura_thread(apts,tmp=None):
    log.debug('Tread  com {} apartamentos criada.'.format(len(apts)) )
    for ap in apts: 
        try:
            response = requests.get(ap['url'])
        except Exception as e:
            log.error('Erro apt ID = {}. Msg: {}'.format(ap['id'],e))
            #d.insere_erro(ap['id'],e)
            continue
        
        text = response.text
        response.close()

        if text != None:
            try:
                doc = __processa_html(text)
                det = extrai_detalhes(doc)
                det['id'] = ap['id']
                det['dt_visita'] =  d.dia_hoje()
                d.atualiza_imoveis([det])
            except Exception as e:
                log.error('Erro apt ID = {}. Msg: {}'.format(ap['id'],e))
                d.insere_erro(ap['id'],e)
               


def captura_detalhes_thread():
    apts = d.imoveis_nao_visitados()
    qtd = len(apts)
    log.debug('Capturando detalhes de {} apartamentos por TRHREAD.'.format(len(apts)) )
    #thread.start_new_thread(__captura_thread, (1,))
    th1=threading.Thread( target=__captura_thread, args = ( apts[:qtd/3], ) )
    th1.start()
    th2=threading.Thread( target=__captura_thread, args = ( apts[qtd/3:qtd*2/3], ) )
    th2.start()
    th3=threading.Thread( target=__captura_thread, args = ( apts[qtd*2/3:qtd], ) )
    th3.start()
    log.debug('Fim da captura de detalhes dos apartamentos por TRHREAD.')
    return th1,th2,th3

def captura_detalhes():
    apts = d.imoveis_nao_visitados()
    while len(apts)>0:
        log.debug('Capturando detalhes de {} apartamentos.'.format(len(apts)) )
        for ap in apts: 
            response = requests.get(ap['url'])
            text = response.text
            response.close()

            if text != None:
                try:
                    doc = __processa_html(text)
                    det = extrai_detalhes(doc)
                    det['id'] = ap['id']
                    det['dt_visita'] =  d.dia_hoje()
                    d.atualiza_imoveis([det])
                except Exception as e:
                    log.error('Erro apt ID = {}. Msg: {}'.format(ap['id'],e))
                    d.insere_erro(ap['id'],e)
        apts = d.imoveis_nao_visitados()
    log.debug('Fim da captura de detalhes dos apartamentos.')

def extrai_detalhes(doc):
    def __is_number(s):
        try:
            float(s)
            return True
        except Exception:
            return False
    
    description,lat,lng,condo = None, None, None, None
    
    img = doc.find('img', class_='fichaMapa')
    if img != None:
        url_geo = img['src']
        start = url_geo.rindex('/')+1
        end = url_geo.rindex('.png')
        coord = url_geo[start:end].split('_')
        if (len(coord) ==2  and 
            __is_number(coord[0]) and __is_number(coord[1])):
            lat, lng = coord
        else:
            onclick = img['onclick']
            start = onclick.index(u'abreMapa(')+len(u'abreMapa(')
            end = start + 29
            coord =  onclick[start:end].split(',')
            if (len(coord) == 2 and
                __is_number(coord[0]) and __is_number(coord[1])):
                lat,lng = coord

        
    h3_desc = doc.find('h3', attrs={'itemprop':'description'})
    if h3_desc != None: 
        description = unicode(h3_desc.text)
    
    #div_details = [str(s) for s in doc.findAll('div', class_='fc-maisdetalhes')]
    #feature_home,feature_condo = div_details
        
    li = doc.find(id='ctl00_ContentPlaceHolder1_resumo_liCondominio')
    if li != None:
            condo = unicode(li.find('span', class_='featureValue').string).replace('R$','').strip()
    
    det_imovel = ''
    for uls in doc.findAll('ul', class_='fc-detalhes'):
            det_imovel = det_imovel + uls.text.strip()+'\n'
    det_imovel = None if det_imovel.strip() == '' else det_imovel
            

    carac_imovel = None
    carac_condo = None
    for divs in doc.findAll('div', class_='fc-maisdetalhes'):
        if divs.p.string.find(u'Outras características do imóvel'):
            carac_imovel = divs.ul.text.strip()
            
        if divs.p.string.find(u'Características das áreas comuns'):
            carac_condo = divs.ul.text.strip()    
    
    # Anúncio desativado.
    if len(doc.findAll('div',class_='erro_tit') ) > 0:
        #carac_imovel = doc.find('div', class_='colunainfos').h3.text.strip()
        carac_imovel = doc.find('div', class_='colunainfos').text.strip()
        

    
    return {'descricao':description, 'lat':lat, 'lng':lng, 'condominio':condo, \
        'det_imovel':det_imovel, 'carac_imovel':carac_imovel, \
        'carac_condo': carac_condo}

        
if __name__ == '__main__':
    #url = 'http://www.zap.com.br/imoveis/rio-de-janeiro+rio-de-janeiro/apartamento-padrao/venda/'
    #apartamentos,paginas = __processar_pagina(url)
    #captura_detalhes_thread()
    captura_detalhes()
    #captura_apartamentos()
    