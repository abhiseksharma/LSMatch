#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 16:49:50 2019

@author: abhisek
"""

import requests
from bs4 import BeautifulSoup

def antonym_synonym(term, need = 'syno'):
    '''
        need can be anto, syno, both
        inType can be str and list
    '''
    file = open("WebPage.txt", "w", encoding="utf-8",  errors="ignore")
    parser = "html.parser"
    #url = "https://www.thesaurus.com/browse/" + term
    #term = "hello"
    url = "https://tuna.thesaurus.com/relatedWords/"+ term +"?limit=100"
    # Option powerthesaurus.org https://www.powerthesaurus.org/term/synonyms
    webText = BeautifulSoup(requests.get(url).text, parser)
    webText = str(webText)
    webText = webText.replace("{\"similarity", "\n{\"similarity")
    file.write(webText)
    file.close()
    
    file = open("WebPage.txt", "r",  encoding="utf-8",  errors="ignore")
    
    # strings = ""
    # while(True):
    #     line = file.readline()
    #     if "</html>" in line:
    #         break
    #     if "similarity" in line:
    #         strings = line
    
    # strings = str(strings)
    # strings = strings[strings.find('[')+1:]
    # strings = strings[strings.find('['):]
    
    # sims = strings.split('},')
    
    synonyms = []
    antonyms = []
    #for sim in sims:
    while(True):
        sim = file.readline()
        if sim == "":
            break
        if "\"similarity\":\"" in sim:
            #sim = sim + '}'
            indexStartSim = sim.find("\"similarity\":\"")
            indexEndSim = sim.find("\"", indexStartSim + 14)
            #print(sim)
            value = int(sim[indexStartSim + 14 : indexEndSim])
            indexStartTerm= sim.find("\"term\":\"")
            indexEndTerm = sim.find("\"", indexStartTerm+8)
            if value >=10:
                synonyms.append(sim[indexStartTerm + 8 : indexEndTerm])
            elif value < 0:
                antonyms.append(sim[indexStartTerm + 8 : indexEndTerm])
                
    synonyms = list(set(synonyms))
    antonyms = list(set(antonyms))
    ''' need to remove this joining (if using as list)'''
    # if inType == 'str':
    #     synonyms = " ".join(synonyms)
    #     antonyms = " ".join(antonyms)
    if need == 'both':
        return synonyms, antonyms
    if need == 'anto':
        return antonyms
    return synonyms

#
#word = 'dentate gyrus granule cell layer'
#for term in word.split():
#    print(antonym_synonym(term))