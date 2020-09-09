import cv2
import numpy as np
from . import img_processing as ip

def getQuestionDetails(questionString, templateQuestionList):
    '''return list of answer dictionaries for a question'''
    index = [ind for ind, qn in enumerate(templateQuestionList) if qn['question']==questionString]
    
    if len(index)==1:
        index = index[0]
    else:
        raise Exception("{} questions returned!".format(len(index)))
    return templateQuestionList[index]['answers']

def showSearchArea(xRange, yRange, img):
    '''
    returns image with square of search area from x and y ranges
    '''    
    outputImg = img.copy()    
    cv2.rectangle(outputImg, (int(min(xRange)),int(min(yRange))), (int(max(xRange)),int(max(yRange))), (0,0,255), 1)
    cv2.putText(outputImg, "Search Area:",(int(min(xRange)),int(min(yRange)-10)),cv2.FONT_HERSHEY_PLAIN, 1, (0,0,0))
    return outputImg

def generateQuestion(xRange, yRange, orient, questionName, answerValues, spotCoordsList, check=False, img=None):
    '''returns question dictionary 
    xRange/yRange = list of x and y coordinates
    orient = 'column' or 'row' or 'grid'
    questionName = str of question to associate with answerValues
    answerValues = list of values to associate with coordinates in xRange, 
    must be sorted from top to bottom (if orient = 'column'),
    left to right (if orient = 'row')
    left to right, then top to bottom - like reading english (if orient = 'grid')
    spotCoordsList = list of all x,y coordinates from template to extract spots within xRange and yRange from.
    '''
    if check==True:
        if type(img)!=np.ndarray:
            raise Exception("need image as numpy array if check==True!")
        else:
            searchAreaImg = showSearchArea(xRange, yRange, img.copy())
            ip.showImg(searchAreaImg, 0)
            #keep asking to change range unless 'n'
            while True:
                if input("change search range? (y/n)") =='n':
                    break
                else:
                    xRangeInput = input("enter new xRange (xStart, xEnd)\n  current: {}".format(xRange))
                    xRange = [int(i) for i in xRangeInput.split(",")]
                    yRangeInput = input("enter new yRange (yStart, yEnd)\n  current: {}".format(yRange))
                    yRange = [int(i) for i in yRangeInput.split(",")]
                    ip.showImg(showSearchArea(xRange, yRange, img.copy()), 0)

    #return list of coordinates within range
    coordList = [i for i in spotCoordsList if xRange[0]<=i[0]<=xRange[1] and yRange[0]<=i[1]<=yRange[1]]
    
    #sort list by x if orient == 'row' or by y if column
    if orient =='row':
        coordList = sorted(coordList, key = lambda x:x[0])
    elif orient =='column':
        coordList = sorted(coordList, key = lambda x:x[1])
    elif orient=='grid':
        coordList = sorted(coordList,key =  lambda x:(x[1], x[0]))
    else:
        raise Exception("orient must be 'column', 'row', or 'grid'")
    
    
    #map coordinates to values
    if len(answerValues) == len(coordList):
        valueCoords = zip(answerValues, coordList)
    else:
        raise Exception("answerValues length: ({}) must match coordList length: ({})".format(len(answerValues), len(coordList)))
        
    
    #add question to template
    questionDict = {'question': questionName, 'answers':[]}
    
    #add in answers
    for val, coord in valueCoords:
        questionDict['answers'].append({'value': val, 'coord':coord, 'filled': False})
    
    return questionDict

def showQuestion(questionString, templateQuestions, img, fontSize, time=0, show=True):
    '''
    puts circle with text of questionString and corresponding answer values from templateQuestions onto img     
    '''
    questionDetails = getQuestionDetails(questionString, templateQuestions)
    questionLocX = questionDetails[0]['coord'][0]-10
    questionLocY = questionDetails[0]['coord'][1]-10
    #put text of question
    cv2.putText(img, questionString, (questionLocX, questionLocY), cv2.FONT_HERSHEY_SIMPLEX, fontSize*1.5, (0,0,0))
    for qn in questionDetails:
        x,y = qn['coord']        
        cv2.circle(img, (x,y), 5, (0,0,255), -1)        
        cv2.putText(img, str(qn['value']), (x+10, y), cv2.FONT_HERSHEY_SIMPLEX, fontSize, (0,0,0))
    if show:
        ip.showImg(img, time)