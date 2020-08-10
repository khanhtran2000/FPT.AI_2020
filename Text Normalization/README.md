## Text Standardization

This is a part of the Speech-to-Text project. Text standardization takes place after customers audio are converted to text. As the texts produced by the recognizer are compiled of words only, they need to be standardized. There are many specific tasks in text standardizing, such as transform word numerals into numbers, standardize date formats, social security numbers or other data that have a standard format, etc.

There are three phases of this project:
- Phase 1: Create dataset	
  * Step 1.1: Data Collecting
  * Step 1.2: Data Preprocessing
  * Step 1.3: Data Creating
  Build a tool that automatically converts raw text -> text thuần STT, including number, time, date, special characters, signs formatting, ...
  BIO tagging for the text thuần based on the tool, including B-NUMBER, B-CAPITAL, B-DATETIME, B-PERIOD, B-QUESTIONMARK, B-EXCLAIMATIONMARK, ...
- Phase 2: Train model
- Phase 3: Postprocessing
