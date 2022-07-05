import requests

QUERY_PREFIXES = """PREFIX focu: <http://focu.io/schema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX vivo: <http://vivoweb.org/ontology/core#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX bibo: <http://purl.org/ontology/bibo/>
PREFIX teach: <http://linkedscience.org/teach/ns#>
PREFIX dbr: <http://dbpedia.org/resource/>
"""

def QueryFusekiServer(queryBody: str):
    query = QUERY_PREFIXES + ' ' + queryBody
    response = requests.post('http://localhost:3030/Unibot/sparql',
       data={'query': query})

    return response.json()

#--------------------------------------------------------------#
#--------------- COMPETENCY QUESTIONS QUERIES -----------------#
#--------------------------------------------------------------#

def GetCourseDescriptionByName(courseName: str):
    query_var = 'SELECT ?description WHERE { ?course rdf:type vivo:Course . '
    query_var += f'?course rdfs:label "{courseName}"@en . '
    query_var += '?course focu:courseDescription ?description . }'
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Description: ", row['description']['value'])

def GetCourseDescription(courseSubject: str, courseNumber: int):
    query_var = 'SELECT ?description WHERE { ?course focu:hasTitle ?courseTitle . '
    query_var += f'?courseTitle focu:courseSubject "{courseSubject}"@en . '
    query_var += f'?courseTitle focu:courseNumber "{courseNumber}" .'
    query_var += '?course focu:courseDescription ?description . }'
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Description: ", row['description']['value'])

def GetStudentCompetencies(studentId: int):
    query_var = 'SELECT ?topicName WHERE { '
    query_var += f'?student focu:studentID {studentId} . '
    query_var += """?student focu:hasCompleted ?completedCourse .
    ?completedCourse focu:course ?course .
	?course focu:hasTopic ?topic .
	?topic rdfs:label ?topicName ."""
    query_var += " }"
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Topic: ", row['topicName']['value'])

def GetStudentCompetenciesByName(givenName: str, familyName: str):
    query_var = 'SELECT ?topicName WHERE { '
    query_var += '?student rdf:type vivo:Student . '
    query_var += f'?student foaf:givenName "{givenName}"@en . '
    query_var += f'?student foaf:familyName "{familyName}"@en . '
    query_var += """?student focu:hasCompleted ?completedCourse .
    ?completedCourse focu:course ?course .
	?course focu:hasTopic ?topic .
	?topic rdfs:label ?topicName ."""
    query_var += " }"
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Topic: ", row['topicName']['value'])

def GetCoursesAtUniversityThatCoverTopic(universityName: str, topicName: str):
    query_var = 'SELECT ?courseName WHERE { '
    query_var += '?university rdf:type vivo:University . '
    query_var += f'?university rdfs:label "{universityName}"@en . '
    query_var += """?course focu:taughtAt ?university .
	?topic rdf:type focu:Topic . """
    query_var += f'?topic rdfs:label "{topicName}"@en .'
    query_var += """?course focu:hasTopic ?topic .
	?course rdfs:label ?courseName . """
    query_var += " }"
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Course: ", row['courseName']['value'])

def GetEmailOfStudent(studentId: str):
    query_var = 'SELECT ?email WHERE { '
    query_var += f'?student focu:studentID {studentId} . '
    query_var += '?student foaf:mbox ?email . '
    query_var += " }"
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Email: ", row['email']['value'])

def GetCoursesCompletedByStudent(studentId: str):
    query_var = 'SELECT ?courseName WHERE { '
    query_var += f'?student focu:studentID {studentId} . '
    query_var += """?student focu:hasCompleted ?completedCourse .
	?completedCourse focu:course ?course .
	?course rdfs:label ?courseName ."""
    query_var += " }"
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Course: ", row['courseName']['value'])

def GetCoursesOfferedAtUniversity(universityName: str, limit: int):
    query_var = 'SELECT ?courseName WHERE { '
    query_var += '?university rdf:type vivo:University . '
    query_var += f'?university rdfs:label "{universityName}"@en . '
    query_var += """?course focu:taughtAt ?university .
	?course rdfs:label ?courseName . """
    query_var += " } "
    query_var += f'LIMIT {limit}'
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Course: ", row['courseName']['value'])

def GetLecturesWithMostContent(limit: int):
    query_var = 'SELECT ?courseName ?lectureName ?lectureNumber (COUNT(?content) as ?count) WHERE { '
    query_var += """?lecture focu:hasContent ?content .
    ?lecture focu:partOfCourse ?course .
    ?course rdfs:label ?courseName .
	?lecture focu:lectureNumber ?lectureNumber . """
    query_var += 'OPTIONAL  {?lecture rdfs:label ?lectureName . } '
    query_var += " } GROUP BY ?courseName ?lectureName ?lectureNumber ORDER BY DESC(?count) "
    query_var += f'LIMIT {limit}'
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Course name: ", row['courseName']['value'])
        print("Lecture name: ", row['lectureName']['value'])
        print("Lecture number: ", row['lectureNumber']['value'])
        print("Number of lecture content: ", row['count']['value'])
        print()

def GetLecturesInCourse(courseSubject: str, courseNumber: str):
    query_var = 'SELECT ?lectureName ?lectureNumber WHERE { ?course focu:hasTitle ?courseTitle . '
    query_var += f'?courseTitle focu:courseSubject "{courseSubject}"@en . '
    query_var += f'?courseTitle focu:courseNumber {courseNumber} .'
    query_var += """?lecture focu:partOfCourse ?course .
	?lecture focu:lectureNumber ?lectureNumber . """
    query_var += 'OPTIONAL  {?lecture rdfs:label ?lectureName . } '
    query_var += '}'
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        if('lectureName' in row):
            print("Lecture name: ", row['lectureName']['value'])
        print("Lecture number: ", row['lectureNumber']['value'])
        print()

def GetCourseTopicProvenance(courseSubject: str, courseNumber: str, topicName: str):
    query_var = 'SELECT ?provenance WHERE { ?course focu:hasTitle ?courseTitle . '
    query_var += f'?courseTitle focu:courseSubject "{courseSubject}"@en . '
    query_var += f'?courseTitle focu:courseNumber {courseNumber} .'
    query_var += '?course focu:hasTopic ?topic . '
    query_var += f'?topic rdfs:label "{topicName}"@en . '
    query_var += '?topic focu:topicProvenance ?provenance . '
    query_var += '}'
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Provenance: ", row['provenance']['value'])

def GetUniversityStudentAttends(givenName: str, familyName: str):
    query_var = 'SELECT ?universityName WHERE { '
    query_var += '?student rdf:type vivo:Student . '
    query_var += f'?student foaf:givenName "{givenName}"@en . '
    query_var += f'?student foaf:familyName "{familyName}"@en . '
    query_var += """?student focu:studiesAt ?university .
	?university rdfs:label ?universityName . """
    query_var += " }"
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("University: ", row['universityName']['value'])

#--------------------------------------------------------------#
#------------ KNOWLEDGE BASE STATISTICS QUERIES ---------------#
#--------------------------------------------------------------#

def GetTotalNumberOfTriples():
    query_var = 'SELECT (COUNT(*) as ?count) WHERE { ?subject ?predicate ?object}'
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Number of triples: ",row['count']['value'])

def GetTotalNumberOfCourses():
    query_var = 'SELECT (COUNT(*) as ?count) WHERE { ?subject rdf:type vivo:Course}'
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Number of courses: ",row['count']['value'])

def GetTotalNumberOfStudents():
    query_var = 'SELECT (COUNT(*) as ?count) WHERE { ?subject rdf:type vivo:Student}'
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Number of students: ",row['count']['value'])

def GetTotalNumberOfLectures():
    query_var = 'SELECT (COUNT(*) as ?count) WHERE { ?subject rdf:type teach:Lecture}'
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Number of lectures: ",row['count']['value'])

# No RDFS reasoner, so does not fetch subclasses of LectureContent...
def GetTotalNumberOfLectureContent():
    query_var = 'SELECT (COUNT(*) as ?count) WHERE { ?subject rdf:type focu:LectureContent}'
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Number of lecture content: ", row['count']['value'])
        
def GetTotalNumberOfUniversities():
    query_var = 'SELECT (COUNT(*) as ?count) WHERE { ?subject rdf:type vivo:University}'
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Number of universities: ",row['count']['value'])

def GetTotalNumberOfTopics():
    query_var = 'SELECT (COUNT(*) as ?count) WHERE { ?subject rdf:type focu:Topic}'
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Number of topics: ",row['count']['value'])

if __name__ == '__main__':
    # COMPETENCY QUESTIONS QUERIES
    print("------------------------------")
    print("GetCourseDescriptionByName - Intelligent Systems")
    GetCourseDescriptionByName("Intelligent Systems")
    print("------------------------------")
    print("GetCourseDescription - COMP 348")
    GetCourseDescription("COMP", 348)
    print("------------------------------")
    print("GetStudentCompetencies - 46870226")
    GetStudentCompetencies(46870226)
    print("------------------------------")
    print("GetStudentCompetenciesByName - Nathalie Guaytan")
    GetStudentCompetenciesByName("Nathalie", "Guaytan")
    print("------------------------------")
    print("GetCoursesAtUniversityThatCoverTopic - Concordia University, SPARQL")
    GetCoursesAtUniversityThatCoverTopic("Concordia University", "SPARQL")
    print("------------------------------")
    print("GetEmailOfStudent - 46654420")
    GetEmailOfStudent(46654420)
    print("------------------------------")
    print("GetCoursesCompletedByStudent - 46654420")
    GetCoursesCompletedByStudent(46654420)
    print("------------------------------")
    print("GetCoursesOfferedAtUniversity - Concordia University, limit 25")
    GetCoursesOfferedAtUniversity("Concordia University", 25)
    print("------------------------------")
    print("GetLecturesWithMostContent - Limit 1")
    GetLecturesWithMostContent(1)
    print("------------------------------")
    print("GetLecturesInCourse - COMP 352")
    GetLecturesInCourse("COMP", 352)
    print("------------------------------")
    print("GetCourseTopicProvenance - COMP 352, Analysis-of-Algorithms")
    GetCourseTopicProvenance("COMP", 352, "Analysis-of-Algorithms")
    print("------------------------------")
    print("GetUniversityStudentAttends - Mariam Samson")
    GetUniversityStudentAttends("Mariam", "Samson")
    print("------------------------------")
    
    # KB STATS QUERIES
    GetTotalNumberOfTriples()
    GetTotalNumberOfCourses()
    GetTotalNumberOfStudents()
    GetTotalNumberOfLectures()
    GetTotalNumberOfUniversities()
    GetTotalNumberOfTopics()
