import pandas as pd
import re

outputPath = "./opendata/output.csv"

mergedData = pd.read_csv(outputPath, header=0, encoding='utf-8')

file = open("turtleDump.ttl", 'w')

print("Processing catalog data...")

file.write("""
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

count = 0
for row in mergedData.iterrows():
    result = ""

    description = str(row[1]["Descr"])
    description = re.sub(r'"*', '', description)

    label = ' '.join(str(row[1]["Long Title"]).splitlines())
    label = re.sub(r'"*', '', label)
    # a
    courseDescription = "Description: {} Prerequisite: {}, Degree: {}, Career: {}, Program: {}, Department: {}, Faculty: {}.".format(description, row[1]["Pre Requisite Description"], row[1]["Degree"], row[1]["Career"], str(row[1]["Program"]).replace("\n", ''), row[1]["Department"], row[1]["Faculty"])
    
    courseDescription = ' '.join(courseDescription.splitlines())
    
    course = """
focudata:{}{}
    a focu:Course ;
    vivo:courseCredits "{}"^^xsd:float ;
    rdfs:label "{}"@en ;
    focu:courseDescription "{}"@en ;
    focu:hasTitle focudata:{}{}-Title ;
    focu:taughtAt focudata:ConcordiaUniversity.
""".format(row[1]["Subject"], row[1]["Catalog"], row[1]["Class Units"], label, courseDescription, row[1]["Subject"], row[1]["Catalog"])


    courseTitle = """
focudata:{}{}-Title
    a focu:CourseTitle ;
    focu:courseSubject "{}"@en ;
    focu:courseNumber "{}" .
""".format(row[1]["Subject"], row[1]["Catalog"], row[1]["Subject"], row[1]["Catalog"])

    # debug
    print(row[1]["Subject"], row[1]["Catalog"])
    
    # ignores comp352/comp 474 courses
    if row[1]["Subject"] == "COMP" and (row[1]["Catalog"] == "352" or row[1]["Catalog"] == "474" or row[1]["Catalog"] == "6741"):
        # skip
        continue
    else:
        result = course + courseTitle

    result = result.replace("nan", "None")

    file.write(result)
    count += 1


print("Processing Complete (", count, " courses).")
file.close()
