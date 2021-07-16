# cgpaGuesser
Guess your prospective CGPA.
## Automated Edition
It scrapes data from your transcript. However, not all school's transcripts are compatible. If you encounter problems, switch to the Manual Edition.
### Usage
- Download your transcript while ticking the "SEMESTER NO" box.
- Rename it to '1.pdf'. If your OS is not displaying file extensions, rename it to '1'.
- Move it to the directory containing the app.
- Run app.
## Manual Edition
Coming soon.
## Clarification about .exe files
I am unable to upload them due to:
- file size limit
- file count limit
- bandwidth usage limit (the first two could be overcome by file compressor, but this not)

So I have decided to explain how to create your executable files by yourself.
## Making .exe File Recipe
Assuming you already have the pyinstaller library, install the libraries in the 'requirements.txt'.

- for onefile (it may cause an upload filesize limit  problem) use this command
pyinstaller --exclude-module PyQt5 --onefile "cgpaGuesser - Automated Edition.py" --add-data "C:\Users\yourUserName\AppData\Local\Programs\Python\Python39\Lib\site-packages\tabula\tabula-1.0.4-jar-with-dependencies.jar;tabula" 

- for multiple files (it looks messy and may cause file count limit problem while uploading to somewhere) use this command
pyinstaller --exclude-module PyQt5 "cgpaGuesser - Automated Edition.py" --add-data "C:\Users\yourUserName\AppData\Local\Programs\Python\Python39\Lib\site-packages\tabula\tabula-1.0.4-jar-with-dependencies.jar;tabula" 

Note 1: Make sure you have adjusted "\yourUserName" parts. Moreover, the path of 'tabula-1.0.4-jar-with-dependencies.jar' may be different in your system, so change it accordingly.
Note 2: If you are using different versions of Python and/or tabula-py, change 'Python39' and/or 'tabula-1.0.4-jar-with-dependencies.jar' parts.

Reference:
https://stackoverflow.com/questions/56550410/unable-to-execute-my-script-when-converting-it-to-exe
