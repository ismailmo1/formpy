
import cv2
import numpy as np
import pandas as pd
import copy
import json

def showImg(img, time=0):
    '''img = single np.array or list of np.array imgs
    displays all in window with window name = window(i) where i = index'''
    if type(img) != list:
        cv2.imshow("window", img)        
    else:
        for i, im in enumerate(img):
            cv2.imshow("window"+str(i), im)
    cv2.waitKey(time)
    if time==0:
        cv2.destroyAllWindows()

def threshImg(img, minThresh=100, maxThresh=255):   
    '''apply grayscale conversion and thresholding to image
    returns image''' 
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, imgThresh = cv2.threshold(imgGray, minThresh, maxThresh, cv2.THRESH_BINARY_INV)
    
    return imgThresh



def alignForm(img, width=0, height=0, template = False):
    '''apply perspective transformation to align form with template
    img = input form as np.array (use cv2.imread)
    width = use template image width (i.e. templateImg.shape[1])
    height = use template image height (i.e. templateImg.shape[0])
    template = if defining template: set to True to ensure the image is scaled down to 
    fit screen when showing image, will override width and height with euclidean distances of outer border'''
    

    # enhance image to improve contour detection
    
    #only resize if template - otherwise image will be resized with warp transform anyways
    xScale = 0.5
    yScale = 0.5
    if template == True:
        imgResize = cv2.resize(img, (0,0), fx= xScale, fy=yScale, interpolation= cv2.INTER_AREA)
        print("AlignImage: img resized by {}{} in width and {}{} in height".format(int(xScale*100),'%', int(yScale*100), '%'))
    else:
        imgResize = img
        
    imgGray = cv2.cvtColor(imgResize, cv2.COLOR_BGR2GRAY)
    imgBilat = cv2.bilateralFilter(imgGray, 11,500,0)
    imgEdges = cv2.Canny(imgBilat, 20,100 )
    
    ##find outer rectangle##
    
    conts = cv2.findContours(imgEdges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    #find top 10 biggest contours by area
    areas =[]
    for c in conts[0]:
        areas.append([c, cv2.contourArea(c)])


    sortedLengths = sorted(areas, key=lambda x:x[1], reverse=True)
    topConts = sortedLengths[:10]

    #find outer rectangle 
    outerBoxCnt = None
    for c in topConts:
        # approximate the contour
        peri = cv2.arcLength(c[0], True)
        #approximate curve to check if its rectangular
        approx = cv2.approxPolyDP(c[0], 0.015 * peri, True)
        if len(approx) == 4:
            outerBoxCnt = approx
            break

    pts = outerBoxCnt.reshape(4,2)

    #ordered from 0-3: top left, top right, bottom right, bottom left (go clockwise around rect)
    orderedPts = np.zeros((4,2), dtype='float32')

    #largest sum of x+y = bottom right
    #smallest sum of x+y = top left
    orderedPts[0] = pts[np.argmin(pts.sum(axis=1))]
    orderedPts[2] = pts[np.argmax(pts.sum(axis=1))]

    #smallest difference x-y = top right
    orderedPts[1] = pts[np.argmin(np.diff(pts, axis=1))]
    #largest difference x-y = bottom left
    orderedPts[3] = pts[np.argmax(np.diff(pts, axis=1))]

    #unpack ordered pts to find widths and heights
    (tl, tr, br, bl) = orderedPts

    #use euclidean distances (finally a use for pythagoras lol) - taken from pyimagesearch.com
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))

    #find max heights/widths - i.e from top/bottom, left/right
    if width == 0 or template==True:
        maxWidth = max(int(widthA), int(widthB))
    else:
        maxWidth = width
    if height == 0 or template==True:
        maxHeight = max(int(heightA), int(heightB))
    else:
        maxHeight = height

    #initialise dst array for transformation
    dst = np.array([
        [0, 0],
        [maxWidth-1, 0],
        [maxWidth -1, maxHeight-1 ],
        [0, maxHeight-1]], dtype = "float32")

    #transformation matrix
    matrix = cv2.getPerspectiveTransform(orderedPts, dst)

    #transform image and resize to original size (map spots to correct locations)
    return cv2.warpPerspective(imgResize, matrix, (maxWidth, maxHeight))

## access answers of question (use this to check filled status from image?)

def getQuestionDetails(questionString, templateList):
    '''return list of answer dictionaries for a question'''
    index = [ind for ind, qn in enumerate(templateList) if qn['question']==questionString]
    
    if len(index)==1:
        index = index[0]
    else:
        raise Exception("{} questions returned!".format(len(index)))
    return templateList[index]['answers']

### define generic function to generate questions for template

def generateQuestion(xRange, yRange, orient, questionName, answerValues, spotCoordsList):
    '''returns question dictionary 
    xRange/yRange = list of x and y coordinates
    orient = 'column' or 'row' or 'grid'
    questionName = str of question to associate with answerValues
    answerValues = list of values to associate with coordinates in xRange, 
    must be sorted from top to bottom (if orient = 'column'),
    left to right (if orient = 'row')
    left to right, then top to bottom - like reading english (if orient = 'grid')
    spotCoordsList = list of all coordinates from template to extract spots within xRange and yRange from.
    '''
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

## helper function to visualise questions/values

def showQuestion(questionString, templateList, img, fontSize, time=0, show=True):
    questionDetails = getQuestionDetails(questionString, templateList)
    questionLocX = questionDetails[0]['coord'][0]-10
    questionLocY = questionDetails[0]['coord'][1]-10
    #put text of question
    cv2.putText(img, questionString, (questionLocX, questionLocY), cv2.FONT_HERSHEY_SIMPLEX, fontSize*1.5, (0,0,0))
    for qn in questionDetails:
        x,y = qn['coord']        
        cv2.circle(img, (x,y), 5, (0,0,255), -1)        
        cv2.putText(img, str(qn['value']), (x+10, y), cv2.FONT_HERSHEY_SIMPLEX, fontSize, (0,0,0))
    if show:
        showImg(img, time)
