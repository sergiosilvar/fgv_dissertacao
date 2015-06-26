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
    '''
    Retorna objeto Beautiful Soup que processa o conteudo do parâmetro "html".
    
    @param html - Conteudo HTML.
    '''
    return BeautifulSoup(html, 'html.parser')

def __extrair_minificha(div):
    '''
    Retorna informacoes de um apartamento de um elemento DIV da classe 
        'content-minificha' de uma pagina HTML de anuncios do ZAP Imoveis.
    
    @param div - Elemento DIV da pagina de classe CSS 'content-minificha' que
        contem informacoes de um apartamento.
    '''
    
    
    apartamento = {}
    
    # Obtem url do anucio especifico do imovel.
    apartamento['url'] = div.a['href']
    
    # Obtm url da foto anunciada do imovel.
    apartamento['url_foto'] = div.a.img['src']
    
    # Neighborhood, city, state and price tags.
    span_location = div.find('span', class_='location')
    sublocal = span_location.findAll('a')
    
    # Indexadres de tags.
    IDX_NEIGH = 0
    IDX_CITY = 1
    IDX_STATE = 2
    IDX_PRICE = 1
    
    # Obtem bairro.
    apartamento['bairro'] = sublocal[IDX_NEIGH].string
    
    # Obtem cidade do imovel.
    apartamento['cidade'] = sublocal[IDX_CITY].string
    
    # Obtem estado do imovel.
    apartamento['estado'] = sublocal[IDX_STATE].string
    
    # Obtem preco do imovel.
    apartamento['preco'] = div.find('a', class_='valorOferta').contents[IDX_PRICE]
    
    details = div.find('a',class_='itemCaracteristicas')
    list_details = [s for s in details.strings]
    for i in range(len(list_details)):
        # Area.
        if list_details[i] == u'Area':
            area = list_details[i+1]
            apartamento['area'] = re.findall(r'\d+', area)[0]
        
        # Garagem.
        if list_details[i] == u'Vagas':
            apartamento['garagem'] = list_details[i+1]
        
        # Suites.
        if list_details[i] == u'Suites':
            apartamento['suites'] = list_details[i+1]
        
        # Quartos.
        if list_details[i] == u'Dorms':
            apartamento['quartos'] = list_details[i+1]
    
    # Data de publicacao.
    span_date = div.find('span', class_='dtlisted')
    apartamento['dt_publicacao'] = re.findall(r'(\d+/\d+/\d+)', span_date.string)[0]
    
    # Extrai codigo identificador do imovel.
    id = re.findall(r'ID-\d+',apartamento['url'])[0]
    apartamento['id'] = re.findall(r'\d+',id)[0]

    # Retorna as informacoes do imovel.
    return apartamento


def __processar_pagina(url):
    '''
    Processa uma pagina de anuncios do ZAP Imoveis e retorna uma lista de
    apartamentos e lista de links para outras paginas de anuncios.     
    
    @param url - Link URL de uma pagina de anuncios do ZAP Imoveis a ser 
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
    '''
    Executa a captura online dos imoveis no classificados ZAP a partir de uma 
    pagina inicial cadastrada no banco de dados.
    '''
    
    log.info('Iniciando captura de apartamentos do zap. Veja log em "log.txt".')
    paginas = d.paginas_nao_visitadas()
    
    # Executa o loop enquanto houver paginas a visitar.
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
    '''
    Metodo interno para captura dos detalhes dos imoveis em modo Thread.
    
    @param apts: lista com informacoes de imoveis.
    '''
    
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
    '''
    Cria e executa três threads para captura das informacoes de imoveis do 
    ZAP Imoveis.
    ''''
    
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
    '''
    Verifica os imoveis que ainda nao tenham sido visitados para recuperar suas
    informacoes especificas, nao disponiveis na lista inicial de anuncios.
    '''
    
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
    '''
    Retorna os detalhes de um imovel.
    
    @param doc - extrato de texto HTML de um imovel.
    '''
    
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
        if divs.p.string.find(u'Outras caracteristicas do imovel'):
            carac_imovel = divs.ul.text.strip()
            
        if divs.p.string.find(u'Caracteristicas das areas comuns'):
            carac_condo = divs.ul.text.strip()    
    
    # Anuncio desativado.
    if len(doc.findAll('div',class_='erro_tit') ) > 0:
        #carac_imovel = doc.find('div', class_='colunainfos').h3.text.strip()
        carac_imovel = doc.find('div', class_='colunainfos').text.strip()
        

    
    return {'descricao':description, 'lat':lat, 'lng':lng, 'condominio':condo, \
        'det_imovel':det_imovel, 'carac_imovel':carac_imovel, \
        'carac_condo': carac_condo}    