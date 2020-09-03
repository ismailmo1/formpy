import ismail_omr as imomr
import ismail_pdfImg as imopdf
import os
import argparse

### need to add in template height and width into variable or hardcode in to replace tempImgAligned.shape[0] and [1] - maybe have default value for alignform func??##
## wrap image processing in separate function and put spot size and pctfilled values as arguments##
##for image in pdf file:
##  align image, rotate, threshold
##  perform omr funct
##  find answers for each qn
##  return dataframe
##  add in analysis script into separate module

parser = argparse.ArgumentParser()
parser.add_argument("pdf")
parser.add_argument("template")
args = parser.parse_args()

with open(args.template, 'r') as template:
    jsonTempLoad = json.load(template)


## overlay template mask onto forms and find filled in spots

imgList = [os.path.join("scanTrials", i) for i in os.listdir(r"scanTrials") if i.endswith(".jpg")]

finalAnswers=[]

for formPath in imgList:
    templateSpots =copy.deepcopy(jsonTempLoad)
    scannedFormImg =cv2.imread(formPath)
    if scannedFormImg.shape[0]>scannedFormImg.shape[1]:
        scannedFormImg=cv2.rotate(scannedFormImg, cv2.ROTATE_90_CLOCKWISE)
    alignedScanImg = imomr.alignForm(scannedFormImg, height= tempImgAligned.shape[0], width= tempImgAligned.shape[1], template=False)    
    alignedScanImgThresh = imomr.threshImg(alignedScanImg)

    #showImg(alignedScanImgThresh)

    filledThreshold =0.4
    circleSize = 6

    omrRead =[]

    for qn in templateSpots:
        #print('\n', qn['question'], '\n') 
        for ans in qn['answers']:
            #print(ans)


            mask =np.zeros(alignedScanImgThresh.shape, dtype = "uint8")
            cv2.circle(mask, tuple(ans['coord']), circleSize, 255, -1)        
            maskPixels = cv2.countNonZero(mask)
            mask = cv2.bitwise_and(alignedScanImgThresh, mask)
            pctFilled = cv2.countNonZero(mask)/maskPixels

            if pctFilled>=filledThreshold:
                ans['filled']=True
                cv2.circle(alignedScanImg, tuple(ans['coord']), circleSize, (0,0,255), 2)
                #print(qn['question'], ans['value'], pctFilled)
            else:
                cv2.circle(alignedScanImg, tuple(ans['coord']), circleSize, (0,100,0), 2)
            if pctFilled>0.1:
                cv2.putText(alignedScanImg, str(round(pctFilled, 2)), tuple(ans['coord']),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
    imomr.showImg(alignedScanImg)

## return question:answer pairs

    filledSpots ={'form':formPath.split("\\")[-1]}

    for qn in templateSpots:    
        filledSpots[str(qn['question'])] = []
        for ans in qn['answers']:
            if ans['filled']==True:
                filledSpots[str(qn['question'])].append(ans['value'])

    finalAnswers.append(filledSpots)

## dict to dataframe (let the fun begin)

omrOutput = pd.DataFrame(finalAnswers)


def getDate(rw):
     return "".join([str(i) for i in rw['day1']]) + "".join([str(i) for i in rw['day2']])  + '-' +"".join([str(i) for i in rw['month']])+ '-'+ "".join([str(i) for i in rw['year']])

omrOutput['day']= omrOutput.apply(lambda x: getDate(x), axis=1)

print(omrOutput)


## or mimic csv output style from formscanner to allow reuse of analysis?

## try align scanned image (fingers crossed!)