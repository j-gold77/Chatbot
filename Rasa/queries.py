import requests

QUERY_PREFIXES = """PREFIX focu: <http://focu.io/schema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX bibo: <http://purl.org/ontology/bibo/>
PREFIX teach: <http://linkedscience.org/teach/ns#>
PREFIX dbr: <http://dbpedia.org/resource/>
"""

def QueryFusekiServer(queryBody: str):
    query = QUERY_PREFIXES + ' ' + queryBody
    response = requests.post('http://localhost:3030/Unibot/',
       data={'query': query})

    return response.json()

#--------------------------------------------------------------#
#--------------- COMPETENCY QUESTIONS QUERIES -----------------#
#--------------------------------------------------------------#

def GetCourseDescriptionByName(courseName: str) -> list:
    query_var = 'SELECT ?description WHERE { ?course rdf:type focu:Course . '
    query_var += f'?course rdfs:label "{courseName}"@en . '
    query_var += '?course focu:courseDescription ?description . }'
    res = QueryFusekiServer(query_var)
    results = []
    for row in res['results']['bindings']:
        results.append(row['description']['value'])
    return results

def GetCourseDescription(courseSubject: str, courseNumber: int) -> list:
    query_var = 'SELECT ?description WHERE { ?course focu:hasTitle ?courseTitle . '
    query_var += f'?courseTitle focu:courseSubject "{courseSubject}"@en . '
    query_var += f'?courseTitle focu:courseNumber "{courseNumber}" .'
    query_var += '?course focu:courseDescription ?description . }'
    res = QueryFusekiServer(query_var)
    results = []
    for row in res['results']['bindings']:
        results.append(row['description']['value'])
    return results

def GetStudentCompetencies(studentId: int) -> list:
    query_var = 'SELECT ?topicName WHERE { '
    query_var += f'?student focu:studentID {studentId} . '
    query_var += """?student focu:hasCompleted ?completedCourse .
	?completedCourse focu:relatedCourse ?course .
	?lecture focu:partOfCourse ?course .
	?lecture focu:hasTopic ?topic .
    ?topic rdfs:label ?topicName ."""
    query_var += " }"
    res = QueryFusekiServer(query_var)
    results = []
    for row in res['results']['bindings']:
        results.append(row['topicName']['value'])
    return results

def GetStudentCompetenciesByName(givenName: str, familyName: str) -> list:
    query_var = 'SELECT ?topicName WHERE { '
    query_var += '?student rdf:type focu:Student . '
    query_var += f'?student foaf:givenName "{givenName}"@en . '
    query_var += f'?student foaf:familyName "{familyName}"@en . '
    query_var += """?student focu:hasCompleted ?completedCourse .
    ?completedCourse focu:relatedCourse ?course .
    ?lecture focu:partOfCourse ?course .
    ?lecture focu:hasTopic ?topic .
	?topic rdfs:label ?topicName . """
    query_var += " }"
    res = QueryFusekiServer(query_var)
    results = []
    for row in res['results']['bindings']:
        results.append(row['topicName']['value'])
    return results


def GetCoursesAtUniversityThatCoverTopic(universityName: str, topicName: str) -> list:
    query_var = 'SELECT ?courseName ?courseSubject ?courseNumber WHERE { '
    query_var += '?university rdf:type focu:University . '
    query_var += f'?university rdfs:label "{universityName}"@en . '
    query_var += """?course focu:taughtAt ?university .
	?topic rdf:type focu:Topic . """
    query_var += f'?topic rdfs:label "{topicName}"@en .'
    query_var += """
    ?lecture focu:partOfCourse ?course .
    ?lecture focu:hasTopic ?topic .
    ?course focu:hasTitle ?courseTitle .
  	?course rdfs:label ?courseName .
  	?courseTitle focu:courseSubject ?courseSubject .
  	?courseTitle focu:courseNumber ?courseNumber .  """
    query_var += " }"
    res = QueryFusekiServer(query_var)
    results = []
    for row in res['results']['bindings']:
        courseName = row['courseName']['value']
        courseSubject = row['courseSubject']['value']
        courseNumber = row['courseNumber']['value']
        results.append((courseName, courseSubject, courseNumber))
    return results

def GetEmailOfStudent(studentId: str) -> list:
    query_var = 'SELECT ?email WHERE { '
    query_var += f'?student focu:studentID {studentId} . '
    query_var += '?student foaf:mbox ?email . '
    query_var += " }"
    res = QueryFusekiServer(query_var)
    results = []
    for row in res['results']['bindings']:
        results.append(row['email']['value'])
    return results

def GetCoursesCompletedByStudent(studentId: str) -> list:
    query_var = 'SELECT ?courseName ?courseSubject ?courseNumber WHERE { '
    query_var += f'?student focu:studentID {studentId} . '
    query_var += """?student focu:hasCompleted ?completedCourse .
	?completedCourse focu:relatedCourse ?course .
    ?course focu:hasTitle ?courseTitle .
  	?course rdfs:label ?courseName .
  	?courseTitle focu:courseSubject ?courseSubject .
  	?courseTitle focu:courseNumber ?courseNumber ."""
    query_var += " }"
    res = QueryFusekiServer(query_var)
    results = []
    for row in res['results']['bindings']:
        courseName = row['courseName']['value']
        courseSubject = row['courseSubject']['value']
        courseNumber = row['courseNumber']['value']
        results.append((courseName, courseSubject, courseNumber))
    return results

def GetCoursesOfferedAtUniversity(universityName: str, limit: int) -> list:
    query_var = 'SELECT ?courseName ?courseSubject ?courseNumber  WHERE { '
    query_var += '?university rdf:type focu:University . '
    query_var += f'?university rdfs:label "{universityName}"@en . '
    query_var += """?course focu:taughtAt ?university .
    ?course focu:hasTitle ?courseTitle .
  	?course rdfs:label ?courseName .
  	?courseTitle focu:courseSubject ?courseSubject .
  	?courseTitle focu:courseNumber ?courseNumber . """
    query_var += " } "
    query_var += f'LIMIT {limit}'
    res = QueryFusekiServer(query_var)
    results = []
    for row in res['results']['bindings']:
        courseName = row['courseName']['value']
        courseSubject = row['courseSubject']['value']
        courseNumber = row['courseNumber']['value']
        results.append((courseName, courseSubject, courseNumber))
    return results

# Note: returned lecture names may be empty
def GetLecturesWithMostContent(courseSubject: str, courseNumber: str) -> list:

    query_var= 'SELECT ?lectureName ?lectureNumber (COUNT(?lectureNumber) as ?count) WHERE { '
    query_var+= '?lecture focu:hasContent ?content .'
    query_var+= '?lecture focu:partOfCourse ?course .'
    query_var+= '?course focu:hasTitle ?courseTitle .'
    query_var+= f'?courseTitle focu:courseSubject "{courseSubject}"@en .'
    query_var+= f'?courseTitle focu:courseNumber "{courseNumber}" .'
    query_var+= '?lecture focu:lectureNumber ?lectureNumber .'
    query_var+= '?lecture rdfs:label ?lectureName .'
    query_var+= '} GROUP BY ?lectureName ?lectureNumber ORDER BY DESC(?count) LIMIT 1'

    res = QueryFusekiServer(query_var)
    print(query_var)
    print(res)
    results = []
    for row in res['results']['bindings']:
        lectureName = row['lectureName']['value']
        lectureNumber = row['lectureNumber']['value']
        numberLectureContent = row['count']['value']
        results.append(lectureName)
        results.append(lectureNumber)
        results.append(numberLectureContent)
    return results

# Note: returned lecture names may be empty
def GetLecturesInCourse(courseSubject: str, courseNumber: str) -> list:
    query_var = 'SELECT ?lectureName ?lectureNumber WHERE { ?course focu:hasTitle ?courseTitle . '
    query_var += f'?courseTitle focu:courseSubject "{courseSubject}"@en . '
    query_var += f'?courseTitle focu:courseNumber "{courseNumber}" .'
    query_var += """?lecture focu:partOfCourse ?course .
	?lecture focu:lectureNumber ?lectureNumber . """
    query_var += 'OPTIONAL  {?lecture rdfs:label ?lectureName . } '
    query_var += '} ORDER BY ?lectureNumber'
    print(query_var)
    res = QueryFusekiServer(query_var)
    print(res)
    results = []
    for row in res['results']['bindings']:
        lectureName = ""
        if('lectureName' in row):
            lectureName = row['lectureName']['value']
        lectureNumber = row['lectureNumber']['value']
        results.append((lectureNumber, lectureName))
    return results

# topic name is case sensitive
def GetCourseTopicProvenance(courseSubject: str, courseNumber: str, topicName: str) -> list:
    query_var = 'SELECT ?provenance WHERE { ?course focu:hasTitle ?courseTitle . '
    query_var += f'?courseTitle focu:courseSubject "{courseSubject}"@en . '
    query_var += f'?courseTitle focu:courseNumber "{courseNumber}" .'
    query_var += '?courseLecture focu:partOfCourse ?course .  '
    query_var += '?topic focu:partOfLecture ?courseLecture .'
    query_var += f'?topic rdfs:label "{topicName}"@en . '
    query_var += '?topic focu:topicProvenance ?provenance . '
    query_var += '?provenance a focu:LectureContentSlides .'
    query_var += '} limit 1'
    print(query_var)
    res = QueryFusekiServer(query_var)
    print(res)
    results = []
    for row in res['results']['bindings']:
        results.append(row['provenance']['value'])
    return results


def GetUniversityStudentAttends(givenName: str, familyName: str) -> list:
    query_var = 'SELECT ?universityName WHERE { '
    query_var += '?student rdf:type focu:Student . '
    query_var += f'?student foaf:givenName "{givenName}"@en . '
    query_var += f'?student foaf:familyName "{familyName}"@en . '
    query_var += """?student focu:studiesAt ?university .
	?university rdfs:label ?universityName . """
    query_var += " }"
    res = QueryFusekiServer(query_var)
    results = []
    for row in res['results']['bindings']:
        results.append(row['universityName']['value'])
    return results

# intent: about_student_at_university action: action_student_at_university_info 
def GetUniversityStudentAttendsBy(studentId: str) -> list:
    query_var = 'SELECT ?universityName WHERE { '
    query_var += '?student rdf:type focu:Student . '
    query_var += f'?student focu:studentID {studentId} . '
    query_var += """?student focu:studiesAt ?university .
	?university rdfs:label ?universityName . """
    query_var += " }"
    res = QueryFusekiServer(query_var)
    results = []
    for row in res['results']['bindings']:
        results.append(row['universityName']['value'])
    return results

# about_topics_covered_course_event
def GetAllTopicsInCourse(courseSubject: str, courseNumber: int) -> list:
    query_var = 'SELECT DISTINCT ?resourceLabel ?topicLabel ?topicLink ?lectureNumber ?resourceUri WHERE { '
    query_var += '?course focu:hasTitle ?courseTitle . '
    query_var += f'?courseTitle focu:courseSubject "{courseSubject}"@en . '
    query_var += f'?courseTitle focu:courseNumber "{courseNumber}" . '
    query_var += """?topic focu:partOfLecture ?lecture .
  	?lecture focu:partOfCourse ?course .
    ?topic rdfs:label ?topicLabel .
    ?topic rdfs:seeAlso ?topicLink .
    ?lecture focu:lectureNumber ?lectureNumber .
    ?topic focu:topicProvenance ?resourceUri .
  	?lecture focu:hasContent ?resourceUri .
    ?resourceUri rdfs:label ?resourceLabel . """
    query_var += " }"
    print(query_var)
    res = QueryFusekiServer(query_var)
    results = []
    for row in res['results']['bindings']:
        resourceLabel = row['resourceLabel']['value']
        topicLabel = row['topicLabel']['value']
        topicLink = row['topicLink']['value']
        lectureNumber = row['lectureNumber']['value']
        resourceUri = row['resourceUri']['value']
        results.append((resourceLabel,topicLabel, topicLink, lectureNumber, resourceUri))
    return results

# action_topics_covered_course_event_info
def GetAllCoursesTopicAppearsIn(topicDbrName: str) -> list:
    query_var = 'SELECT ?courseName ?courseSubject ?courseNumber (COUNT(?topic) AS ?count) WHERE { '
    query_var += f'?topic rdfs:seeAlso dbr:{topicDbrName} . '
    query_var += """?topic focu:partOfLecture ?lecture .
  	?lecture focu:partOfCourse ?course .
  	?course focu:hasTitle ?courseTitle .
  	?course rdfs:label ?courseName .
  	?courseTitle focu:courseSubject ?courseSubject .
  	?courseTitle focu:courseNumber ?courseNumber . """
    query_var += " } "
    query_var += """GROUP BY ?courseName ?courseSubject ?courseNumber
    ORDER BY ?count"""

    res = QueryFusekiServer(query_var)
    results = []
    for row in res['results']['bindings']:
        courseName = row['courseName']['value']
        courseSubject = row['courseSubject']['value']
        courseNumber = row['courseNumber']['value']
        count = row['count']['value']
        results.append((courseName, courseSubject, courseNumber, count))
    return results

def GetDetailedTopicProvenance(topicName: str) -> list:
    query_var = 'SELECT DISTINCT ?course ?lecture ?lectureNumber ?resourceURI WHERE { '
    query_var += f'?topic rdfs:label "{topicName}"@en . '
    query_var += """?topic focu:partOfLecture ?lecture .
	?lecture focu:lectureNumber ?lectureNumber .
	?topic focu:topicProvenance ?resourceURI .
  	?lecture focu:hasContent ?resourceURI .
  	?lecture focu:partOfCourse ?course . """
    query_var += " }"
    res = QueryFusekiServer(query_var)
    results = []
    for row in res['results']['bindings']:
        course = row['course']['value']
        lecture = row['lecture']['value']
        lectureNumber = row['lectureNumber']['value']
        resourceURI = row['resourceURI']['value']
        results.append((course, lecture, lectureNumber, resourceURI))
    return results

def GetTopicsCoveredInCourseEvent(fileName: str) -> list:
    query_var = 'SELECT DISTINCT ?topicLabel ?topicLink WHERE { '
    query_var += f'?topic focu:topicProvenance <{fileName}> . '
    query_var += """?topic rdfs:label ?topicLabel .
    ?topic rdfs:seeAlso ?topicLink . """
    query_var += " }"
    res = QueryFusekiServer(query_var)
    results = []
    for row in res['results']['bindings']:
        topicLabel = row['topicLabel']['value']
        topicLink = row['topicLink']['value']
        results.append((topicLabel, topicLink))
    return results

#--------------------------------------------------------------#
#------------ KNOWLEDGE BASE STATISTICS QUERIES ---------------#
#--------------------------------------------------------------#

def GetTotalNumberOfTriples():
    query_var = 'SELECT (COUNT(*) as ?count) WHERE { ?subject ?predicate ?object}'
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Number of triples: ",row['count']['value'])

def GetTotalNumberOfCourses():
    query_var = 'SELECT (COUNT(*) as ?count) WHERE { ?subject rdf:type focu:Course}'
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Number of courses: ",row['count']['value'])

def GetTotalNumberOfStudents():
    query_var = 'SELECT (COUNT(*) as ?count) WHERE { ?subject rdf:type focu:Student}'
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
    query_var = 'SELECT (COUNT(*) as ?count) WHERE { ?subject rdf:type focu:University}'
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Number of universities: ",row['count']['value'])

def GetTotalNumberOfTopics():
    query_var = 'SELECT (COUNT(*) as ?count) WHERE { ?subject rdf:type focu:Topic}'
    res = QueryFusekiServer(query_var)
    for row in res['results']['bindings']:
        print("Number of topics: ",row['count']['value'])

def Assignment1Queries():
    # COMPETENCY QUESTIONS QUERIES
    print("------------------------------")
    print("GetCourseDescriptionByName - Intelligent Systems")
    print(GetCourseDescriptionByName("Intelligent Systems"))
    print("------------------------------")
    print("GetCourseDescription - COMP 348")
    print(GetCourseDescription("COMP", 348))
    print("------------------------------")
    print("GetStudentCompetencies - 46870226")
    print(GetStudentCompetencies(46870226))
    print("------------------------------")
    print("GetStudentCompetenciesByName - Nathalie Guaytan")
    print(GetStudentCompetenciesByName("Nathalie", "Guaytan"))
    print("------------------------------")
    print("GetCoursesAtUniversityThatCoverTopic - Concordia University, SPARQL")
    print(GetCoursesAtUniversityThatCoverTopic("Concordia University", "SPARQL"))
    print("------------------------------")
    print("GetEmailOfStudent - 46654420")
    print(GetEmailOfStudent(46654420))
    print("------------------------------")
    print("GetCoursesCompletedByStudent - 46654420")
    print(GetCoursesCompletedByStudent(46654420))
    print("------------------------------")
    print("GetCoursesOfferedAtUniversity - Concordia University, limit 25")
    print(GetCoursesOfferedAtUniversity("Concordia University", 25))
    print("------------------------------")
    print("GetLecturesWithMostContent - Limit 1")
    print(GetLecturesWithMostContent("COMP", 352))
    print("------------------------------")
    print("GetLecturesInCourse - COMP 352")
    print(GetLecturesInCourse("COMP", 352))
    print("------------------------------")
    print("GetCourseTopicProvenance - COMP 352, Analysis-of-Algorithms")
    print(GetCourseTopicProvenance("COMP", 352, "Analysis-of-Algorithms"))
    print("------------------------------")
    print("GetUniversityStudentAttends - Mariam Samson")
    print(GetUniversityStudentAttends("Mariam", "Samson"))
    print("------------------------------")
    
    # KB STATS QUERIES
    GetTotalNumberOfTriples()
    GetTotalNumberOfCourses()
    GetTotalNumberOfStudents()
    GetTotalNumberOfLectures()
    GetTotalNumberOfUniversities()
    GetTotalNumberOfTopics()

def Assignment2Queries():
    output = ""
    output += "------------------------------\n"
    
    output += "GetAllTopicsInCourse - COMP 352\n"
    results = GetAllTopicsInCourse("COMP", 352)  
    for result in results:
        output += f'{result[0]}\t{result[1]}\tLecture {result[2]}\t{result[3]}\n'
    
    output += "\n------------------------------\n"
    
    output += "GetAllCoursesTopicAppearsIn - Algorithm\n"
    results = GetAllCoursesTopicAppearsIn("Algorithm")
    for result in results:
        output += f'{result[0]} ({result[1]} {result[2]})\tCount: {result[3]}\n'
    
    output += "\n------------------------------\n"

    output += "GetDetailedTopicProvenance - time complexity\n"
    results = GetDetailedTopicProvenance("time complexity")
    for result in results:
        output += f'{result[0]} -> {result[1]} (Lecture {result[2]}) -> {result[3]}\n'
    
    file = open("Assignment2QueriesOutput.txt", "w", encoding='utf-8')
    file.write(output)
    file.close()

if __name__ == '__main__':
    Assignment2Queries()
    