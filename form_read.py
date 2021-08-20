import copy
import json

import cv2
import numpy as np
import pandas as pd

from . import img_processing as ip


def omrRead(
    imgList, templatePath, filledThresh=0.4, circleSize=6, showOmr=False
):
    """
    returns pandas dataframe of img files as rows and question/answers as columns
    imgList: list of img file paths (readable by cv2.imread)
    template: path to template json file
    fillThresh: what fraction of circle should be filled in to register as an answer
    circleSize: size of circle to overlay on spot from template:
                larger size = more forgiving on alignment but requires larger fillThresh
    showOmr: display each img after detection
    """

    with open(templatePath, "r") as jsonFile:
        jsonTempLoad = json.load(jsonFile)
    template = jsonTempLoad

    finalAnswers = []
    for formPath in imgList:
        templateQuestions = copy.deepcopy(template["questions"])
        scannedFormImg = cv2.imread(formPath)

        # rotate img if portrait instead of landscape

        if scannedFormImg.shape[0] > scannedFormImg.shape[1]:
            scannedFormImg = cv2.rotate(scannedFormImg, cv2.ROTATE_90_CLOCKWISE)
        alignedScanImg = ip.alignForm(
            scannedFormImg,
            height=template["metadata"]["shape"][0],
            width=template["metadata"]["shape"][1],
            isTemplate=False,
        )
        alignedScanImgThresh = ip.threshImg(alignedScanImg)

        for qn in templateQuestions:

            for ans in qn["answers"]:

                mask = np.zeros(alignedScanImgThresh.shape, dtype="uint8")
                cv2.circle(mask, tuple(ans["coord"]), circleSize, 255, -1)
                maskPixels = cv2.countNonZero(mask)
                mask = cv2.bitwise_and(alignedScanImgThresh, mask)
                pctFilled = cv2.countNonZero(mask) / maskPixels

                if pctFilled >= filledThresh:
                    ans["filled"] = True
                    cv2.circle(
                        alignedScanImg,
                        tuple(ans["coord"]),
                        circleSize,
                        (0, 0, 255),
                        2,
                    )
                    cv2.putText(
                        alignedScanImg,
                        str(round(pctFilled, 2)),
                        tuple(ans["coord"]),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 0),
                        2,
                    )
                else:
                    cv2.circle(
                        alignedScanImg,
                        tuple(ans["coord"]),
                        circleSize,
                        (0, 100, 0),
                        2,
                    )

        if showOmr:
            ip.showImg(alignedScanImg)

        ## return question:answer pairs

        filledSpots = {"form": formPath.split("\\")[-1]}

        for qn in templateQuestions:
            filledSpots[str(qn["question"])] = []
            for ans in qn["answers"]:
                if ans["filled"] == True:
                    filledSpots[str(qn["question"])].append(ans["value"])

        finalAnswers.append(filledSpots)

    return pd.DataFrame(finalAnswers)
