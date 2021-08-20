import argparse
import os

import pandas as pd

import form_read as fr
import img_processing as ip


##  TODO add in analysis script into separate module
## TODO plan class structure
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("pdfFolder")
    parser.add_argument("templatePath")
    parser.add_argument("csvPath")
    args = parser.parse_args()

    # convert pdf to imgs and return path list
    pdfImgList = ip.pdfFolderToImgs(
        args.pdfFolder,
        popplerPath=r"C:\Users\ismail\poppler-0.68.0_x86\poppler-0.68.0\bin",
    )

    df = fr.omrRead(pdfImgList, args.templatePath)

    # import as csv as temporary measure
    # in future run analysis code here
    df.to_csv(args.csvPath, index=False)


if __name__ == "__main__":
    main()
