import logging
import sys
from rdflib import Graph, URIRef, RDFS
from AlignmentFormat import serialize_mapping_to_tmp_file
from collections import defaultdict
from gettingURI import getURL

# import time
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



def match_rdflib(source_graph, target_graph, input_alignment, synonymFile):
    alignment = []

    graphSource = source_graph
    graphTarget = target_graph
    # reference = referenceFile
#     synonymFile = "oaei-resources/Synonym Anatomy.json"
    thresholdValue = 0.95

    sourceClassNames = []
    targetClassNames = []
    sourceNoLabel = 0
    targetNoLabel = 0
    classCount = 0
    for sub in graphSource.subjects(predicate = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), object= rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Class')):
        if type(sub) == type(rdflib.term.URIRef("")):
            for classLabel in graphSource.objects(subject = rdflib.term.URIRef(sub), predicate = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label')):
                classCount += 1
                sourceClassNames.append(str(classLabel.lower().replace('_', ' ').replace('/', ' ')))

            # For ontologies like sweet
            if classCount == 0:
                for classLabel in graphTarget.objects(subject = rdflib.term.URIRef(sub), predicate = rdflib.term.URIRef('http://data.bioontology.org/metadata/prefixIRI')):
                    if ':' not in classLabel:
                        sourceClassNames.append(str(classLabel.lower().replace('_', ' ').replace('/', ' ')))

    classCount = 0
    for sub in graphTarget.subjects(predicate = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), object= rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Class')):
        if type(sub) == type(rdflib.term.URIRef("")):
            for classLabel in graphTarget.objects(subject = rdflib.term.URIRef(sub), predicate = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label')):
                classCount += 1
                targetClassNames.append(str(classLabel.lower().replace('_', ' ').replace('/', ' ')))

            #For ontologies like sweet
            if classCount == 0:
                for classLabel in graphTarget.objects(subject = rdflib.term.URIRef(sub), predicate = rdflib.term.URIRef('http://data.bioontology.org/metadata/prefixIRI')):
                    if ':' not in classLabel:
                        targetClassNames.append(str(classLabel.lower().replace('_', ' ').replace('/', ' ')))

    if len(sourceClassNames) == 0:
        sourceNoLabel = 1
        # split by / then check if [-1] has # then use accordingly
        for sub in graphSource.subjects(predicate = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), object= rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Class')):
            if type(sub) == type(rdflib.term.URIRef("")):
                className = (str(sub).split("/"))[-1]
                if '#' in className:
                    className = (className.split('#'))[-1]
                sourceClassNames.append(className.lower().replace('_', ' ').replace('/', ' '))
        sourceClassNames = list(set(sourceClassNames[:]))

    if len(targetClassNames) == 0:
        targetNoLabel = 1
        for sub in graphTarget.subjects(predicate = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), object= rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Class')):
            if type(sub) == type(rdflib.term.URIRef("")):
                className = (str(sub).split("/"))[-1]
                if '#' in className:
                    className = (className.split('#'))[-1]
                targetClassNames.append(className.lower().replace('_', ' ').replace('/', ' '))
        targetClassNames = list(set(targetClassNames[:]))

    # Creating matrix for similarity
    # choosing smaller class as source
    if len(targetClassNames) < len(sourceClassNames):
        sourceClassNames, targetClassNames = targetClassNames[:], sourceClassNames[:]


    # Making Synonym dict
    stopWord = set(stopwords.words('english'))
    stopWords = []
    for word in stopWord:
        if len(word) >= 2:
            stopWords.append(word)
    def creating_synonym_dict(sourceNames):
#         i = 0
        for name in sourceNames:
#             print(i)
#             i += 1
            #name = 'other limb bone'
            name = name.lower().replace('_', ' ').replace('/', ' ')
            index = name
            if index not in synonym_dict:
                name = name.split()
                name = [word for word in name if word not in stopWords]
                name = " ".join(name)
                synos = antonym_synonym(name)
                synos.append(name)
                synonym_dict[index] = synos


    #synonym_dict = dict()
    if synonymFile != "":
        f = open(synonymFile)
        synonym_dict = json.load(f)
#     else:
#         synonym_dict = dict()
#     creating_synonym_dict(sourceClassNames)

    # Applying similarity measures

    # Synonym
    def get_similarity(s1, s2):
        '''Finding similarity between strings using synonyms'''
        '''
        1. Remove words like of, the, in, and, etc. from string(done)
        2. Split string in list(done)
        3. Find synonyms of one list and compare 2nd list, if exist assign 0.9 as score(done)
        '''
        score = 0

        '''if term contain stop word'''

        ''' To remove stopwords from in between'''
        #s2 = "head and neck muscle"
        s2 = s2.split()
        s2 = [word for word in s2 if word not in stopWords]
#         s2 = " ".join(s2)
        #print(s2)

        s1 = s1.split()
        s1 = [word for word in s1 if word not in stopWords]
#         s1 = " ".join(s1)

        score = 0
        for name in s2:
            for concept in s1:
                if name == concept or name in synonym_dict[concept]:
                    score += 1
                    break
        return (score/(len(s2)))
        #for s in s2: not required or wrong

#         if s2 in synonym_dict[s1]:
#             score = 100
#         return score

    # Calculating Score
    pairFound = dict()
    # totalAlignmentAboveThreshold = 0
    # startMatching  = time.time()
    total = len(sourceClassNames)
    i = 0
    for sC in sourceClassNames:
#         print(str(i) + "/"+ str(total))
        i += 1
        for tC in targetClassNames:
            ''' Comented because i don't need exact class match now '''
            #sC, tC = sClass.lower().replace('_', ' ').replace('/', ' '), tClass.lower().replace('_', ' ').replace('/', ' ')
            score = Levenshtein.ratio(sC, tC) # * 100
            #score = fuzz.ratio(sC, tC)
            if score < 0.95:
#           I should try it like this
#             if score < 0.5:
#                 score = get_similarity(sC, tC)
#
                score = get_similarity(sC, tC)
#                 score = score/200
            if score >= 0.5:
                pairFound[tuple((sC, tC))] =  score
            # if score >= threshold:
            #     totalAlignmentAboveThreshold += 1
                #print(sClass + " - " + tClass)
            ''' commented because this was really heavy and searching the rows
            #and columns every time and increasing the time 10X'''
            #similarity.loc[sClass][tClass] = score

    # endMatching  = time.time()
    # # endTotal = time.time()
    # #timeTakenLavenstien = (end-start)
    # timeTakenMatching = (endMatching - startMatching)
    # wholeTime = (endTotal - startTotal)


    # Checking Precision and Recall
    pairValues = []

    totalCorrect = 0
    for i in pairValues:
        #if type(i) == np.float64:
        if i >= thresholdValue:
            totalCorrect += 1

    thold = thresholdValue
    # referenceA = len(pairs)
    totalAboveThold = 0
    for value in pairFound.values():
        if value >= thold:
            totalAboveThold += 1

    allignmentsAboveThold = dict()
    thold = thresholdValue
    for pair in pairFound.keys():
        if pairFound[pair] >= thold:
            allignmentsAboveThold[pair] = pairFound[pair]


    alignment = getURL(allignmentsAboveThold, source_graph, target_graph)

#     print(alignment)

    return alignment
#     return [('http://one.de', 'http://two.de', '=', 1.0)]

def get_file_from_url(location):
    from urllib.parse import unquote, urlparse
    from urllib.request import url2pathname, urlopen

    if location.startswith("file:"):
        return open(url2pathname(unquote(urlparse(location).path)))
    else:
        return urlopen(location)


def match(source_url, target_url, input_alignment_url):
    logging.info("Python matcher info: Match " + source_url + " to " + target_url)

    # in case you want the file object use
    # source_file = get_file_from_url(source_url)
    # target_file = get_file_from_url(target_url)

#     print("source" + source_url)

    source_graph = Graph()
    source_graph.parse(source_url)
    logging.info("Read source with %s triples.", len(source_graph))

    target_graph = Graph()
    target_graph.parse(target_url)
    logging.info("Read target with %s triples.", len(target_graph))


    synonymFile = ""

    for sub, obj in source_graph.subject_objects(predicate = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')):
#         print(sub)

        conferenceList = ['cmt', 'conference', 'confOf', 'edas', 'ekaw', 'iasted', 'sigkdd']

        if "mouse" in sub or "human" in sub:
            synonymFile = "oaei-resources/Synonym Anatomy (single word synonyms).json"
            break
        elif "HP" in sub or "MP" in sub:
            synonymFile = "oaei-resources/Synonym_HP-MP.json"
            break
        elif "DOID" in sub or "ORDO" in sub:
            synonymFile = "oaei-resources/Synonym_DOID-ORDO.json"
            break
        elif "FLOPO_" in sub or "TO_" in sub:
            synonymFile = "oaei-resources/Synonym_flopo-pto.json"
            break
        elif any(conferenceTag in sub for conferenceTag in conferenceList):
            synonymFile = "oaei-resources/Synonym_Conference.json"
            break
        elif "ENVO_" in sub or "sweetontology" in sub:
            synonymFile = "oaei-resources/Synonym_Envo-Sweet.json"
            break

    input_alignment = None
    # if input_alignment_url is not None:


    resulting_alignment = match_rdflib(source_graph, target_graph, input_alignment, synonymFile)

    # in case you have the results in a pandas dataframe, make sure you have the columns
    # source (uri), target (uri), relation (usually the string '='), confidence (floating point number)
    # in case relation or confidence is missing use: df["relation"] = '='  and  df["confidence"] = 1.0
    # then select the columns in the right order (like df[['source', 'target', 'relation', 'confidence']])
    # because serialize_mapping_to_tmp_file expects an iterbale of source, target, relation, confidence
    # and then call .itertuples(index=False)
    # example: alignment_file_url = serialize_mapping_to_tmp_file(df[['source', 'target', 'relation', 'confidence']].itertuples(index=False))

    alignment_file_url = serialize_mapping_to_tmp_file(resulting_alignment)
    return alignment_file_url


def main(argv):
    if len(argv) == 2:
        print(match(argv[0], argv[1], None))
    elif len(argv) >= 3:
        if len(argv) > 3:
            logging.error("Too many parameters but we will ignore them.")
        print(match(argv[0], argv[1], argv[2]))
    else:
        logging.error(
            "Too few parameters. Need at least two (source and target URL of ontologies"
        )


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO
    )
    main(sys.argv[1:])
