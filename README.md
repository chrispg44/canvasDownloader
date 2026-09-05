# Canvas Downloader

Canvas Downloader is for downloading course content from a Canvas based course. It works with any school that uses Canvas.

What it does
- Able to download everything in the 'Modules', 'Files', and 'Assignments' tab 


Authentication (API token)
You must provide a Canvas API token to authenticate with the Canvas API. Create one in your Canvas account (usually under Account Settings → Approved Integrations or Access Tokens) and put it in `API_TOKEN`. 

Configuration
- Go in `course_vars.py` to set your Canvas base URL, API token, and course id. 

Example `course_vars.py` — you must set these values:

```python
# REPLACE with your school Canvas homepage URL, API token, and course ID
CANVAS_URL = "https://bruinlearn.ucla.edu" #REPLACE: with canvas homepage url (string) -  Ex: UCLA canvas url used here 
API_TOKEN = ""   #REPLACE: api_token goes here (string)
COURSE_ID = 1   #REPLACE: courseID goes here (int) - found in web browser URL of course to download (CANVAS_URL/{some_number_here} )
```

Usage
1. Set all 3 values in `course_vars.py`
2. Run the script:

```bash
python3 main.py
```

Selective downloads
You control what you want to download between Modules,Files,Pages by commenting/uncommenting the code below:

```python
courseToDownload.downloadModules()     # download modules
#courseToDownload.downloadFiles()     # download files
#courseToDownload.downloadPages()     # download pages
```

Notes
- Some content may be unavailable depending on what tabs your instruction made available to students.

