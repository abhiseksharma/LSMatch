# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 11:40:37 2021

@author: abhis
"""

import time
import Levenshtein
# import numpy as np
# import pandas as pd
#from fuzzywuzzy import fuzz
from Antonym_Synonym import antonym_synonym
import json
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import rdflib


# source = "human.owl"
# target = "mouse.owl"
# synonymFile = "Synonym Anatomy (after limit 100)(List including the concept also)(without camel split).json"
# thresholdValue = 0.95

# allignmentsAboveThold, timeTakenMatching = matching(source, target, synonymFile, thresholdValue)


# graphSource = rdflib.Graph()
# graphSource.open("store", create=True)
# graphSource.parse(source)

# graphTarget = rdflib.Graph()
# graphTarget.open("store", create=True)
# graphTarget.parse(target)


def getURL(allignmentsAboveThold, graphSource, graphTarget):

    allignment = []
    sourceClassNames = dict()
    targetClassNames = dict()
    sourceNoLabel = 0
    targetNoLabel = 0
    classCount = 0
    for sub in graphSource.subjects(predicate = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), object= rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Class')):
        if type(sub) == type(rdflib.term.URIRef("")):
            for classLabel in graphSource.objects(subject = rdflib.term.URIRef(sub), predicate = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label')):
                classCount += 1
                sourceClassNames[str(classLabel.lower().replace('_', ' ').replace('/', ' '))] = str(sub)
    
            # For ontologies like sweet
            if classCount == 0:
                for classLabel in graphTarget.objects(subject = rdflib.term.URIRef(sub), predicate = rdflib.term.URIRef('http://data.bioontology.org/metadata/prefixIRI')):
                    if ':' not in classLabel: 
                        sourceClassNames[str(classLabel.lower().replace('_', ' ').replace('/', ' '))] = str(sub)
    
    classCount = 0
    for sub in graphTarget.subjects(predicate = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), object= rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Class')):
        if type(sub) == type(rdflib.term.URIRef("")):
            for classLabel in graphTarget.objects(subject = rdflib.term.URIRef(sub), predicate = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label')):
                classCount += 1
                targetClassNames[str(classLabel.lower().replace('_', ' ').replace('/', ' '))] = str(sub)
            
            #For ontologies like sweet
            if classCount == 0:
                for classLabel in graphTarget.objects(subject = rdflib.term.URIRef(sub), predicate = rdflib.term.URIRef('http://data.bioontology.org/metadata/prefixIRI')):
                    if ':' not in classLabel: 
                        targetClassNames[str(classLabel.lower().replace('_', ' ').replace('/', ' '))] = str(sub)
    
    if len(sourceClassNames) == 0:
        sourceNoLabel = 1
        # split by / then check if [-1] has # then use accordingly
        for sub in graphSource.subjects(predicate = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), object= rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Class')):
            if type(sub) == type(rdflib.term.URIRef("")):
                className = (str(sub).split("/"))[-1]
                if '#' in className:
                    className = (className.split('#'))[-1]
                sourceClassNames[className.lower().replace('_', ' ').replace('/', ' ')] = str(sub)
        # sourceClassNames = list(set(sourceClassNames[:]))
    
    if len(targetClassNames) == 0:
        targetNoLabel = 1
        for sub in graphTarget.subjects(predicate = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), object= rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Class')):
            if type(sub) == type(rdflib.term.URIRef("")):
                className = (str(sub).split("/"))[-1]
                if '#' in className:
                    className = (className.split('#'))[-1]
                targetClassNames[className.lower().replace('_', ' ').replace('/', ' ')] = str(sub)
        # targetClassNames = list(set(targetClassNames[:]))

    for pair in allignmentsAboveThold:
        allign = []
        sourceLabel = ""
        targetLabel = ""
        try:
            sourceLabel = sourceClassNames[pair[0]]
            targetLabel = targetClassNames[pair[1]]
        except:
            sourceLabel = sourceClassNames[pair[1]]
            targetLabel = targetClassNames[pair[0]]
                
        allign.append(sourceLabel)
        allign.append(targetLabel)
        allign.append('=')
        allign.append(str(allignmentsAboveThold[pair]))

        allignment.append((allign))
    return allignment

            

    







        
# for sub in graphSource.subjects(predicate = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), object= rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Class')):
#     if type(sub) == type(rdflib.term.URIRef("")):
#         for classLabel in graphSource.objects(subject = rdflib.term.URIRef(sub), predicate = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label')):
#             classCount += 1
#             sourceClassNames.append((str(classLabel.lower().replace('_', ' ').replace('/', ' ')), str(sub)))

#         # For ontologies like sweet
#         if classCount == 0:
#             for classLabel in graphTarget.objects(subject = rdflib.term.URIRef(sub), predicate = rdflib.term.URIRef('http://data.bioontology.org/metadata/prefixIRI')):
#                 if ':' not in classLabel: 
#                     sourceClassNames.append((str(classLabel.lower().replace('_', ' ').replace('/', ' ')), str(sub)))

# classCount = 0
# for sub in graphTarget.subjects(predicate = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), object= rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Class')):
#     if type(sub) == type(rdflib.term.URIRef("")):
#         for classLabel in graphTarget.objects(subject = rdflib.term.URIRef(sub), predicate = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label')):
#             classCount += 1
#             targetClassNames.append((str(classLabel.lower().replace('_', ' ').replace('/', ' ')), str(sub)))
        
#         #For ontologies like sweet
#         if classCount == 0:
#             for classLabel in graphTarget.objects(subject = rdflib.term.URIRef(sub), predicate = rdflib.term.URIRef('http://data.bioontology.org/metadata/prefixIRI')):
#                 if ':' not in classLabel: 
#                     targetClassNames.append((str(classLabel.lower().replace('_', ' ').replace('/', ' ')), str(sub)))

# if len(sourceClassNames) == 0:
#     sourceNoLabel = 1
#     # split by / then check if [-1] has # then use accordingly
#     for sub in graphSource.subjects(predicate = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), object= rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Class')):
#         if type(sub) == type(rdflib.term.URIRef("")):
#             className = (str(sub).split("/"))[-1]
#             if '#' in className:
#                 className = (className.split('#'))[-1]
#             sourceClassNames.append((className.lower().replace('_', ' ').replace('/', ' '), str(sub)))
#     sourceClassNames = list(set(sourceClassNames[:]))

# if len(targetClassNames) == 0:
#     targetNoLabel = 1
#     for sub in graphTarget.subjects(predicate = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), object= rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Class')):
#         if type(sub) == type(rdflib.term.URIRef("")):
#             className = (str(sub).split("/"))[-1]
#             if '#' in className:
#                 className = (className.split('#'))[-1]
#             targetClassNames.append((className.lower().replace('_', ' ').replace('/', ' '), str(sub)))
#     targetClassNames = list(set(targetClassNames[:]))
        
        