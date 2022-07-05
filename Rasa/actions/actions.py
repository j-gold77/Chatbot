# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import queries


# 1. What is [course] about?
class ActionCourseInfo(Action):

     def name(self) -> Text:
         return "action_course_info"

     def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
            course = tracker.slots['course']
            test = course.split()
            if len(test) <= 1:
                dispatcher.utter_message(text=f'Sorry I don\'t have any information about that course...')  
            else:
                y = int (test[1])
                answer = queries.GetCourseDescription(test[0].upper(),y)
                if course is None or not course or answer is None or not answer:
                    dispatcher.utter_message(text=f'Sorry I don\'t have any information about that course...')
                else:
                    dispatcher.utter_message(text=f'If you are asking about {course}, then {answer[0]}')
            return []
            return []

# 2. Which [topics] is [student] competent in?
class ActionStudenCompetentcyInfo(Action):
    
    def name(self) -> Text:
        return "action_student_competentcy_info"
    
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        student = tracker.slots['student']
        temp = student.split()
     
        
        if len(temp) <= 1:
            dispatcher.utter_message(text=f'Sorry you must provide a first and last name capitalized for me to answer about student compententcies.')
        elif student is None or not student:
            dispatcher.utter_message(text=f'Sorry that is not a student')
        else:
            answer = queries.GetStudentCompetenciesByName(temp[0],temp[1])
            dispatcher.utter_message(text=f"If you are asking about {tracker.slots['student']}, here are the topics:")
            dispatcher.utter_message(text=f"{answer}")


        return []
     
# 6. Which [courses] are offered at [university] X?
class ActionCourseOfferedatUniversityInfo(Action):
    
    def name(self) -> Text:
        return "action_courses_offered_at_university_info"
    
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        university = tracker.slots['university']
        
        if university is None or not university:
            dispatcher.utter_message(text=f'Sorry that does not seem to be a university.')
        else:
            answer = queries.GetCoursesOfferedAtUniversity(university, 10)
            if len(answer) == 0:
                dispatcher.utter_message(text=f"Unibot does not have any courses recorded at {tracker.slots['university']}.")
            else:    
                dispatcher.utter_message(text=f"Here are the courses offered at {tracker.slots['university']} limited to 10:")
                for course in answer:
                    dispatcher.utter_message(text=f"- {course[0]} ({course[1]} {course[2]})")
        return []

# 5. What are the [courses] [student] S has completed?
class ActionStudentCourseCompletionInfo(Action):
    
    def name(self) -> Text:
        return "action_student_course_completions_info"
    
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        sid = tracker.slots['student_id']
        student_id = int(sid)
        answer = queries.GetCoursesCompletedByStudent(student_id)
        
        if student_id is None or not student_id:
            dispatcher.utter_message(text=f'Sorry that does not seem to be a valid student ID.')
        elif len(answer)==0:
            dispatcher.utter_message(text=f'This student has not completed any courses.')
        else:      
            dispatcher.utter_message(text=f"Here are the courses completed by {tracker.slots['student_id']}: ")
            for course in answer:
                dispatcher.utter_message(text=f"- {course[0]} ({course[1]} {course[2]})")
        return []     

class ActionStudentEmailInfo(Action):
    
    def name(self) -> Text:
        return "action_student_email_info"
    
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        sid = tracker.slots['student_id']
        student_id = None
        answer = None
        if sid.isdigit():
            student_id = int(sid)
            answer = queries.GetEmailOfStudent(student_id)
        
        if student_id is None or not student_id:
            dispatcher.utter_message(text=f'Sorry that does not seem to be a valid student ID (no apostrophes accepted!).')
        elif len(answer)==0:
            dispatcher.utter_message(text=f'Either Student has no email or that is not a valid ID.')
        else:      
            dispatcher.utter_message(text=f"Here is the email for {tracker.slots['student_id']}, '{answer[0]}'. ")
        return []     

# 3. Which [courses] in [university] cover [topic]?
class ActionTopicsCoveredAtUniversityInfo(Action):
    
    def name(self) -> Text:
        return "action_course_topics_at_university_info"
    
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        university = tracker.slots['university']
        topic = tracker.slots['topic']
        answer = queries.GetCoursesAtUniversityThatCoverTopic(university,topic)
        if university is None or not university or topic is None or not topic:
            dispatcher.utter_message(text=f'Hmm, I am not sure what you mean by that.')
        elif len(answer)==0:
             dispatcher.utter_message(text=f'Hmm, Either that course is not covered or You have made a spelling error (check capitalization).')
        else:
            dispatcher.utter_message(text=f"At {tracker.slots['university']}, the topic {tracker.slots['topic']} appears in:")
            for course in answer:
                dispatcher.utter_message(text=f"- {course[0]} ({course[1]} {course[2]})")
        return []            
    
# 7. What [lecture] in [course] has the most [lecture content]?
class ActionMostLectureContentInCourseInfo(Action):
    
    def name(self) -> Text:
        return "action__most_lecture_content_in_course_info"
    
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        course = tracker.slots['course']
        courseSubject = course.split()[0]
        courseNumber = int (course.split()[1])
        answer = queries.GetLecturesWithMostContent(courseSubject.upper(),courseNumber)
                          
        if course is None or not course:
            dispatcher.utter_message(text=f'Hmm, I am not sure what you mean by that.')
        elif len(answer) == 0:
            dispatcher.utter_message(text=f'Either {course} has no lecture content recorded, or you made a mistake.')
        else:
            print("--------------")
            print(answer)
            dispatcher.utter_message(text=f"The lecture for {course} with the most lecture content is lecture {answer[1]} - {answer[0]} with {answer[2]} lecture content.")
        return []      

# 8. What [lectures] do I need to attend for [course]?
class ActionCourseAttendanceLectureInfo(Action):
    
    def name(self) -> Text:
        return "action_course_attendance_lecture_info"
    
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        course = tracker.slots['course']
        test = course.split()
        y = int (test[1])
        answer = queries.GetLecturesInCourse(test[0].upper(),y)
                          
        if course is None or not course:
            dispatcher.utter_message(text=f'Hmm, I am not sure what you mean by that.')
        elif answer==0:
            dispatcher.utter_message(text=f'Either there are no courses for that class or you made a mistake.')
        else:
            if len(answer) == 0:
                dispatcher.utter_message(text=f"Unibot does not have any lectures associated to {course}.")
            else:
                dispatcher.utter_message(text=f"The lectures for {course} you must attend are:")
                for lecture in answer:
                    dispatcher.utter_message(text=f"{lecture[0]} - {lecture[1]}")
        return []         

# 9. Where in [course] was [topic] introduced?
class ActionTopicInCourseInfo(Action):
    
    def name(self) -> Text:
        return "action_topic_in_course_info"
    
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        topicName = tracker.slots['topic']
        course = tracker.slots['course']
        courseSubject = course.split()[0]
        courseNumber = int (course.split()[1])

        answer = queries.GetCourseTopicProvenance(courseSubject.upper(),courseNumber,topicName)
        print(topicName)
        print(answer)
        if topicName is None or not topicName or course is None or not course:
            dispatcher.utter_message(text=f'Interesting, I am not sure what you mean by that.')
        elif answer is None or not answer or answer.count == 0:
            dispatcher.utter_message(text=f'Either there are no topics associated to your course or you made a mistake. Make sure you spelt your topic correctly (case sensitive)!')
        else:
            dispatcher.utter_message(text=f'Topic {topicName} was covered in {answer[0]}.')
        return []      

class ActionStudentAtUniversityInfo(Action):
    
    def name(self) -> Text:
        return "action_student_at_university_info"
    
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        studentId = tracker.slots['student_id']
        answer = queries.GetUniversityStudentAttendsBy(studentId)
        if studentId is None or not studentId:
            dispatcher.utter_message(text=f'Interesting, I am not sure what you mean by that.')
        elif answer is None or not answer or answer.count == 0:
            dispatcher.utter_message(text=f'Either there are no students associated to that student ID or you made a mistake.')
        else:
            dispatcher.utter_message(text=f'The university {studentId} attends is {answer[0]}.')

        return []      

# 11. Which topics are covered in [course_event]? topics with resource URI
class ActionTopicsCoveredCourseEventInfo(Action):
    
    def name(self) -> Text:
        return "action_topics_covered_course_event_info"
    
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course = tracker.slots['course']
        courseSubject = course.split()[0]
        courseNumber = int (course.split()[1])
        courseEvent = tracker.slots['course_event']
        answer = queries.GetAllTopicsInCourse(courseSubject.upper(),courseNumber)
        print(answer)
        print(courseEvent)
        if courseEvent is None or not courseEvent or course is None or not course:
            dispatcher.utter_message(text=f'Interesting, I am not sure what you mean by that.')
        elif answer is None or not answer or answer.count == 0:
            dispatcher.utter_message(text=f'Either your course does not have any topics or you made a mistake. Make sure you spelt your course event correctly (case sensitive)!')
        else:
            resourceLabel = 0
            topicLabel = 1
            topicLink = 2
            lectureNumber = 3
            resourceUri = 4
            flag=-1
            for resource in answer: 
                if(resource[resourceLabel]==courseEvent):
                    if(flag==-1):
                        dispatcher.utter_message(text=f'Topics covered in {resource[resourceLabel]} are:')
                    flag =0
                    dispatcher.utter_message(text=f' - {resource[topicLabel]} found in {resource[resourceUri]}')
        return []      

# action_courses_cover_topic_info
class ActionCoursesCoverTopicInfo(Action):
    
    def name(self) -> Text:
        return "action_courses_cover_topic_info"
    
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        topicDbr = tracker.slots['topic']
        answer = queries.GetAllCoursesTopicAppearsIn(topicDbr)
        if topicDbr is None or not topicDbr:
            dispatcher.utter_message(text=f'Interesting, I am not sure what you mean by that.')
        elif answer is None or not answer or answer.count == 0:
            dispatcher.utter_message(text=f'Either your topic does not appear or you made a mistake. Please make sure you spelt your topic correctly (case sensitive)!')
        else:
            dispatcher.utter_message(text=f'{topicDbr} is covered in: ')
            for course in answer:
                courseName = course[0]
                courseSubject = course[1]
                courseNumber = course[2]
                count = course[3]
                dispatcher.utter_message(text=f'{courseSubject} {courseNumber} - {courseName} ({count} times)')
        return []      