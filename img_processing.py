import cv2
import numpy as np
from pdf2image import convert_from_path
from pathlib import Path
import os

def pdfFolderToImgs(pdfFolderPath, outputLoc='pdfFolder', deletePdf = True, popplerPath=r"C:\Users\ismail.mohammed\poppler-0.68.0\bin"):
    '''
    returns list of img paths
    convert all pdfs in pdfFolderPath to imgs with pdfFileName + page number in outputLoc
    popplerPath = location of \poppler-0.68.0\bin
                (ensure poppler is installed and in path)    
    '''
    pdfPaths = [file for file in os.listdir(pdfFolderPath) if file.endswith('.pdf')]
    if outputLoc == 'pdfFolder':
        outputLoc = Path(pdfFolderPath)
    else:
        outputLoc = Path(outputLoc)
            
    imgPaths =[]
    # #saving pdf as images
    for pdf in pdfPaths:
        imgNum = 1
        pdfPath= Path.joinpath(Path(pdfFolderPath), Path(pdf))
        pages = convert_from_path(pdfPath, poppler_path=popplerPath)
        for i,p in enumerate(pages):
            #if rotation needed? - shouldnt need if scanned properly - (maybe add label to sheet: SCAN THIS WAY ->)
            #p = p.rotate(180, expand=True)            
            imgPath = Path.joinpath(outputLoc, str(pdf.split('.')[0]) +'pg_' + str(imgNum) +".jpg")
            p.save(imgPath)
            imgPaths.append(imgPath)
            imgNum+=1
    
    #delete pdf files 
    if deletePdf:
        for pdf in pdfPaths:
            os.remove(Path.joinpath(Path(pdfFolderPath), Path(pdf)))
    
    #conv path obj to strings (cv2 needs paths as strings)    
    return [str(imgPath) for imgPath in imgPaths]

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

#img_processing.py
def alignForm(img, width=0, height=0, isTemplate = False):
    '''apply perspective transformation to align form with template
    img = input form as np.array (use cv2.imread)
    width = use template image width (i.e. template['metadata']['shape'][1])
    height = use template image height (i.e. template['metadata']['shape'][0])
    isTemplate = if defining template: set to True to ensure the image is scaled down to 
    fit screen when showing image, will override width and height with euclidean distances of outer border'''
    

    # enhance image to improve contour detection
    
    #only resize if template - otherwise image will be resized with warp transform anyways
    xScale = 0.5
    yScale = 0.5
    if isTemplate == True:
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
    if width == 0 or isTemplate==True:
        maxWidth = max(int(widthA), int(widthB))
    else:
        maxWidth = width
    if height == 0 or isTemplate==True:
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