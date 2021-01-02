# ismail_omr
 
This is a solution to address the wastes in data input and analysis when monitoring Overall Equipment Effectiveness (OEE) in manufacturing. 

Operators will still manually fill out sheets, however they are now just putting marks or dots (similar to multiple choice exams) in the correct fields. The sheets are then scanned in at the end of a shift and analysed automatically. This is achieved through the use of an open source computer vision library (openCV) as well as some other data handling libraries (pandas, numpy). The output of this program is flexible and can be structured as a csv to allow users to analyse further in excel, however the data in this use case was further analysed in python to allow joining with other data taken from ERP systems. 
