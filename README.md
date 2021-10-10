# formpy

This is a solution to automate data entry when collecting data by non-digital forms.

Use formpy's API to rapidly create templates that act as a blueprint for your forms. Distribute the forms (i.e. empty templates that can be filled in by respondents), scan them in and use the predefined templates to analyse the images for answers. Easily read in answers to a pandas dataframe or save as csv to have your data available in a clean format for further analytics/processing.

1. Create a multiple choice form and define your template with formpy's Template class interface.

2. Save your templates as a json to maximise reusability for your next project/script.

3. Print and distribute your forms and collect all the data.

4. Use formpy's Form interface to read in the forms and detect answers from the scanned images.

5. Export to your favourite format (csv, pandas.DataFrame, excel) and analyse to your hearts content!
