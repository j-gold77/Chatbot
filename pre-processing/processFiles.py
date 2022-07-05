import os
import tika
from tika import parser
import requests
from rdflib import Graph, Namespace, URIRef
import rdflib
import spacy

# change this directory depending on your local repo location
datasetDir = os.path.abspath('../Project P1/Unibot/Datasets/')
#init parser
tika.initVM()

topicDictionary = dict()

nlp = spacy.load("en_core_web_sm")

#end of code statistic information vars
distinctTopicsTotal = 0
instanceTopicsTotal = dict()

# keep track of lecture count with respect to number of files in file type
lectureTotal = 0
fileTotal = 0
#iterate through all the course folders
for classFolder in os.listdir(datasetDir):
    classDir = os.path.join(datasetDir, classFolder)
    # initialize for final stat about instances of this course
    instanceTopicsTotal[classFolder] = 0
    # get number of lecture files (= number of lectures in course)
    lectureTotal = len(os.listdir(classDir + "/Lectures"))
    #iterate through all the lecture content folders in course folder
    for contentFolder in os.listdir(classDir):
        contentDir = os.path.join(classDir, contentFolder)
        # fileTotal used for calculating lecture number
        fileTotal = len(os.listdir(contentDir))
        # set the index of file going through
        countFile = 1
        #iterate through all the files in the lecture content folder
        for file in os.listdir(contentDir):
            fileDir = os.path.join(contentDir, file)
            if os.path.isfile(fileDir) and not (file.endswith('-text.txt') or file.endswith('-spotlight.ttl')):

                ##### PARSE THE FILE #####
                print("Parsing the file: " + file + "...")
                parsedFile = parser.from_file(fileDir)

                result =  parsedFile['content'].replace('\n', '').replace('\r', '')

                fileTxtDir = os.path.join(contentDir, file.split('.')[0] + "-text" + '.txt')

                #create and write to file
                with open(fileTxtDir, 'w', encoding="utf-8") as textFile:
                    textFile.write(result)
                    textFile.close()
                
                ##### CREATE SPOTLIGHT DATA #####

                # link to file to store spotlight data
                fileSpotlightDir = os.path.join(contentDir, file.split('.')[0] + "-spotlight" + '.ttl')
                
                # holds the content result split into chunks less than 900 words
                resultSpotlight = []
                
                #split string into chunks of characters less than 1000 characters
                resultWords = result.split(' ')
                #lab text file words are VERY long so 300 words is a good chunk size
                
                for i in range(0, len(resultWords), 300):
                    resultSpotlight.append(' '.join(resultWords[i:i+300]))
                    
            
                with open(fileSpotlightDir, 'w', encoding="utf-8") as textFile2:

                    for i in range(0, len(resultSpotlight)):
                        print("Spotlight on this file (chunk " + str(i+1) + "/" + str(len(resultSpotlight)) + ") ... ", end="")
                        
                        headers = {
                            'accept': 'text/turtle',
                        }

                        params = {
                            'text': resultSpotlight[i],
                            'confidence': '0.5',
                        }

                        spotlight = requests.get('https://api.dbpedia-spotlight.org/en/annotate', headers = headers, params = params)
                        response = str(spotlight.text)
                        textFile2.write(response)

                        print("✓")
                    
                    textFile2.close()
                    
                    ##### PROCESS SPOTLIGHT DATA #####
                    g = Graph()
                    g.parse(fileSpotlightDir, format='turtle')

                    # query to get all the entities in the spotlight file
                    triples = g.query('SELECT * WHERE{?s ?p ?o. FILTER(str(?p) = "http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#anchorOf" || str(?p) = "http://www.w3.org/2005/11/its/rdf#taIdentRef")} ORDER BY DESC(?p)')

                    # dictionary to hold the entities
                    entityDict = dict()

                    # store the triples in a dictionary
                    for row in triples:
                        if row.p == rdflib.term.URIRef('http://www.w3.org/2005/11/its/rdf#taIdentRef'):
                            entityDict[str(row.s)] = dict()
                            entityDict[str(row.s)]['dbpedia'] = str(row.o)
                        else:
                            entityDict[str(row.s)]['name'] = str(row.o)

                    # setting the lecture count
                    numberLecture = 0
                    if fileTotal == lectureTotal:
                        numberLecture = str(int(countFile))
                    else:
                        numberLecture = str(int(round((lectureTotal/fileTotal) * countFile)))

                    # make dbpedia the key of result and remove dbpedia from value dictionary
                    entityDict = {v['dbpedia']: {'name': v['name'], 'provenance': f"focudata:{classFolder}-Lecture{numberLecture}"} for k, v in entityDict.items()}
                    
                    ##### PROCESS SPACY PoS DATA #####
                    
                    entityDictCopy = entityDict.copy()

                    # iterate through the entities and add the nouns to the dictionary
                    for k, v in entityDictCopy.items():
                        doc = nlp(entityDictCopy[k]['name'])

                        #get part of speech of label with spacy
                        tokens = [token.pos_ for token in doc]

                        # filter by pos (from most prevalent to not prevalent)
                        if 'VERB' in tokens or ['INTJ'] == tokens or ['X'] == tokens or ['AUX'] == tokens or ['NUM'] == tokens or ['DET'] == tokens or ['PUNCT'] == tokens or ['SYM'] == tokens or ['CCONJ'] == tokens or ['SCONJ'] == tokens:
                            print("Removed entity: ", entityDict[k]['name'], " (", tokens, ")")
                            entityDict.pop(k)
                    
                    # if key in topicDictionary the same as entityDict, add the entity to the list
                    for key, value in entityDict.items():
                        if key in topicDictionary:
                            topicDictionary[key]['provenance'].append(value['provenance'])
                        else:
                            topicDictionary[key] = value
                            topicDictionary[key]['provenance'] = [value['provenance']]
                countFile += 1
                print("Parse Completed.\n")

##### CREATE TOPICS FROM SPOTLIGHT DATA #####


topicPerLec = dict()

with open("topicDump.ttl", "w", encoding="utf-8") as myfile:
    myfile.write("""
@prefix focudata: <http://focu.io/data#> .
@prefix focu: <http://focu.io/schema#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix vivo: <http://vivoweb.org/ontology/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix bibo: <http://purl.org/ontology/bibo/> .
@prefix teach: <http://linkedscience.org/teach/ns#> .
@prefix dbr: <http://dbpedia.org/resource/> .
""")

    for key, value in topicDictionary.items():
        provenances = ', '.join(set(value['provenance']))

        topicName = value['name'].replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_").replace("&", "and").replace("$", "Dollar").replace("'", "").replace("*", "").replace("©", "").replace(",", "").replace("!", "").replace("¯", "")
        if "¼" in topicName or "¶" in topicName or "¡" in topicName:
            continue
        
        # create a dictionary list so we know what topics are in what lectures
        for prov in value['provenance']:
            if prov not in topicPerLec.keys():
                topicPerLec[prov] = [f"<focudata:Topic-{topicName}>"]
            else:
                topicPerLec[prov].append(f"<focudata:Topic-{topicName}>")

        #counter for number of topics created /course
        for course, count in instanceTopicsTotal.items():
            if course in provenances:
                instanceTopicsTotal[course] = count + 1
        
        aTopic = f"""
focudata:Topic-{topicName}
    a focu:Topic ;
    rdfs:label "{value['name']}"@en ;
    focu:topicProvenance {provenances} ;"""
        myfile.write(aTopic)
        dbpediaLink = key.split("/")[-1]
        if "(" in dbpediaLink or "," in dbpediaLink or "'" in dbpediaLink or "" in dbpediaLink or "¡" in dbpediaLink  or "³" in dbpediaLink or "©" in dbpediaLink or "." in dbpediaLink or "!" in dbpediaLink:
            myfile.write(f"""
    rdfs:seeAlso <http://dbpedia.org/resource/{dbpediaLink}> .
    """)
        else:
            myfile.write(f"""
    rdfs:seeAlso dbr:{dbpediaLink} .
    """)
        distinctTopicsTotal += 1
    myfile.close()

# parsing through our course lists and adding the topics in each lecture

#For comp 352
comp352Dir = os.path.abspath('../Project P1/comp352Dump.ttl')

with open(comp352Dir, 'r', encoding="utf-8") as fileIn:
    readFile = fileIn.readlines()

fileLines = []
for line in readFile:
    fileLines.append(line)
    for lec, topics in topicPerLec.items():
        if lec == line.strip():
            fileLines.append('    focu:hasTopic ' + ", ".join(set(topics)) + ";\n")

with open(comp352Dir, 'w', encoding="utf-8") as fileOut:
    fileOut.writelines(fileLines)


#For comp 474
comp474Dir = os.path.abspath('../Project P1/comp474.ttl')

with open(comp474Dir, 'r', encoding="utf-8") as fileIn:
    readFile = fileIn.readlines()

fileLines = []
for line in readFile:
    fileLines.append(line)
    for lec, topics in topicPerLec.items():
        if lec == line.strip():
            fileLines.append('        focu:hasTopic        ' + ", ".join(set(topics)) + ";\n")

with open(comp474Dir, 'w', encoding="utf-8") as fileOut:
    fileOut.writelines(fileLines)


print("---STATISTICS---")
print("Number of distinct topics: ", distinctTopicsTotal, " topics")
print("Number of topic instances/course: ")
for key, value in instanceTopicsTotal.items():
    print("Course ", key, ":", str(value), " topics")
print("Done!")
