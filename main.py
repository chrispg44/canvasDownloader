from canvasapi import Canvas
import os 
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
from course_vars import CANVAS_URL,API_TOKEN,COURSE_ID


class DownloadCourse:
  def __init__(self,CANVAS_URL,API_TOKEN,COURSE_ID):
    self.canvas = Canvas(CANVAS_URL, API_TOKEN)
    self.course = self.canvas.get_course(COURSE_ID) 

  #make new directory
  def makeDir(self,dirName):
    os.makedirs(dirName, exist_ok=True)
  
  
  #download vids.  this way much faster than canvas api .download() 
  def downloadVids(self,url, fileName, savedPath):
    with requests.get(url, stream=True) as r:
      r.raise_for_status()  # raise error if download failed

      saveToPath = str(savedPath) + "/" + str(fileName)
      with open(saveToPath, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
          if chunk:  # filter out keep-alive chunks
              f.write(chunk)
  
    print(f"Download complete: {savedPath}")


  #download all content in Canvas 'Files' tab
  def downloadFiles(self):
    self.makeDir("Files")   #make 'Files' dir
    
    try:
      for file in self.course.get_files():
  
        strFile = str(file)
        if ".mov" in strFile or ".mp4" in strFile:   #skip .mov and .mp4 takes too long         #TODO: add .mp3 file support 
          print(file.url)
          self.downloadVids(file.url, file, "./Files") #downloads vids faster
          continue 

        print(file)
        downloadPath = "./Files/{}".format(file)
        file.download(downloadPath)
  
    except Exception as e:
      print(f"'No permission for 'Files'tab : {e}")
  
  #download all content in Canvas 'Modules' tab
  def downloadModules(self):
    self.makeDir("Modules")   #make 'Modules' dir

    try:
      for module in self.course.get_modules(): #go through all modules 
        print(f"📦 Module: {module.name}")
        for item in module.get_module_items():

          if item.type == "ExternalUrl":   #append external urls to txt file
            with open("./Modules/external_links.txt", "a", encoding="utf-8") as f:
              line = f"{module.name} - {item.title}: {item.external_url}\n"
              f.write(line)
              print(f"📝 Saved: {line.strip()}")

          elif item.type == "File":
            file_obj = self.course.get_file(item.content_id)  # get the file using ID
            print(f"⬇️ Downloading: {file_obj.filename}")
            downloadPath = "./Modules/{}".format(file_obj.filename)
            file_obj.download(downloadPath)
    except Exception as e:
      print(f"'Likely no student permission for 'Modules'tab : {e}")

  #download all content in Canvas 'Assignments' tab
  def downloadAssignments(self):
    self.makeDir("Assignments")  #make 'Assignments' dir

    try:
      for assignment in self.course.get_assignments():
        title = assignment.name.replace("/", "-")  # clean filename

        fileName = f"./Assignments/{title}.html"
        try:
          html = assignment.description or "<!-- No description -->"
          with open(fileName, "w", encoding="utf-8") as f:
              f.write(str(assignment.get_submission))
          print(f"✅ Saved: {fileName}")
        except Exception as e:
          print(f"❌ Failed to save {title}: {e}")

    except Exception as e:
      print(f"'Likely no student permission for 'Assignments'tab : {e}")
  
  

  #.extract ID entire entire URL  - .get_file() only works with ID
  def urlToID(self,url): #convert url to id 
    pattern = re.compile(r"/files/(\d+)") #get file id 
    match = pattern.search(url)
    if match:
      fileID = int(match.group(1))
      return fileID
    return None

  #get lecture name from full URL
  def getVidName(self,currStr):
    temp = currStr.split('/')  
    videoName = temp[-1].split(".mp4")[0]
    return videoName
  

  #download generic html structure from 'Pages' tab 
  def downloadGenericHTMLPages(self,page,title):
    with open(f"Pages/{title}/{title}.html", "w", encoding="utf-8") as f:
        f.write(page.body)
    print(f"✅ Saved: Pages/{title}/{title}.html")
    
  '''
  page object has 
    -page.title
    -page.body
    -page.url
    -page.created_at
    -page.updated_at
  '''
  #can download 'Pages' content in depth 
  def downloadPages(self):
  
    self.makeDir("Pages")   #make 'Pages' dir

    try:
      for page in self.course.get_pages():  #get all pages
          page_obj = self.course.get_page(page.url) # load full content of associated page 
          title = page.title.replace("/", "-")    #don't confuse file with path name
          #downloadPath = "./Pages/{}".format(title)
          Path(f"Pages/{title}").mkdir(exist_ok=True)
    
          self.downloadGenericHTMLPages(page_obj,title)
    
    
          #download all content within each page (in depth)
          soup = BeautifulSoup(page_obj.body, "html.parser")
    
          for a_tag in soup.find_all("a", href=True):
              href = a_tag["href"]
    
              urlStr = str(href)
      
              #format: https://lever.cs.ucla.edu/[professor]/[class]/Lecturex.mp4
              if urlStr.endswith(".mp4"): #download lectures (may take a few min)
                vidName = self.getVidName(urlStr)
                self.downloadVids(href, vidName, f"Pages/{title}")
                continue
    
              
              fileID = self.urlToID(href)    #convert url to id
              if fileID is None:
                continue
              #get all pdfs 
              try:
                  file = self.course.get_file(fileID)
                  if file.filename.endswith(".pdf"):
                      print(f"⬇️ Downloading {file.filename} from page {title}")
                      file.download(f"Pages/{title}/{file.filename}")
            
              except Exception as e:
                  print(f"⚠️ Couldn't download file {fileID}: {e}")

    except Exception as e:
      print(f"'Likely no student permission for 'Pages'tab : {e}")
  

  #doesnt work rn. modify later. see which tabs in specific course available
  def getTabs(self):
    tabs = self.course.get_tabs()
    print(tabs)

  

#- - - - - -RUN PROGRAM - - - - - - - - - - - -  - - - - - -
if __name__ == "__main__":
  courseToDownload = DownloadCourse(CANVAS_URL, API_TOKEN, COURSE_ID)

  courseToDownload.downloadModules()     #download modules   #9/3/26 note: modules still works great
  #courseToDownload.downloadFiles() #download files
  #courseToDownload.downloadPages()

