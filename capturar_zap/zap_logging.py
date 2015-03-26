'''
Created on 25/05/2014

@author: sergio
'''
import logging

logFormatter = logging.Formatter('%(asctime)s - %(module)s:%(lineno)s - %(levelname)s >> %(message)s')
#log.basicConfig(format='%(asctime)s - %(module)s:%(lineno)s - %(levelname)s - %(message)s', level=log.DEBUG)



log = logging.getLogger()
log.setLevel(logging.ERROR)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
log.addHandler(consoleHandler)

'''
fileHandler = logging.FileHandler("captura.log")
fileHandler.setFormatter(logFormatter)
log.addHandler(fileHandler)
'''