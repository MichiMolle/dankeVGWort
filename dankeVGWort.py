'''
DankeVGWort.py - VC-Kurs-Material Fetching-Skript

This script goes through all hyperlinks inside a moodle account to fetch the files provided in a course.

DankeVGWort.py is provided by the author, without any warranty.
'''

import sys
import platform
import os
import shutil
import datetime
import requests
from getpass import getpass
from bs4 import BeautifulSoup

#SETTINGS
page_login = 'https://vc.uni-bamberg.de/moodle/login/index.php' #URL of login page
page_course_list = 'https://vc.uni-bamberg.de/moodle/my/index.php?mynumber=-2' #URL of page containing list of all subscribed courses

logging = True

#OS-Information (needed for some Windows-specific bugfixes)
osystem = platform.system()



#function for removing discouraged characters from file/foldernames
def removeCriticalCharacters(string):
    string = string.replace(" ", "_")
    string = string.replace(",","")
    string = string.replace(".","")
    string = string.replace("-","")
    string = string.replace(":","")
    string = string.replace("ß","ss")
    string = string.replace("%","")
    string = string.replace("/","")
    string = string.replace("(","")
    string = string.replace(")","")
    string = string.replace('"',"")
    string = string.replace("_&_","_")
    string = string.replace('*',"")
    string = string.replace('>',"")
    string = string.replace('<',"")
    string = string.replace('"',"")
    string = string.replace('|',"")
    
    return string



s = requests.Session()  #session is needed to stay logged in 
print("")
print("***DankeVGWort.py - VC-Kurs-Material Fetching-Skript***")
print("=======================================================")
print("")

errors = [] #list of all errors produced while processing requests for logging

#login dialog
username = input('ba-ID: ')
password = getpass(prompt='password: ')
print("")

print("logging in...") 
req = s.post(page_login, data={'username': username, 'password': password}) #perform login
print("getting course list...")
req = s.get(page_course_list) #get page with list of all subscribed courses

#process html-response to get list of Course-Titles and URLs
course_list = BeautifulSoup(req.text, 'html.parser')
course_list = course_list.find("div", { "class" : "course_list" })
course_list = course_list.findAll("h2", {"class" : "title"})

courses = []

for course in course_list:
    course = course.find("a")
    course = [course['title'],course['href']]
    courses.append(course)
##processing done

#print list of subscribed courses and wait for user response
print("")
print("--> I detected "+str(len(courses))+" courses:")
print("")

for index, course in enumerate(courses):
    print("["+str(index+1)+"]: " + course[0])

print("")
print("What do you want to do? (Enter corresponding number):")
print("")
print("1: Grab'em all!")
print("2: Get everything except...")
print("3: Get only...")
print("")

choice = input("choice: ")

if(choice=="1"):
    courses = courses
elif(choice=="2"):
    exclude = input("Which courses do you want to exclude? (Enter seperated by comma):")
    exclude = exclude.replace(" ","")
    exclude = str.split(exclude, ",")
    
    exclude = list(map(int, exclude))
    
    for i in sorted(exclude, reverse=True):
        del courses[i-1]
    
elif(choice=="3"):
    include = input("Which courses do you want? (Enter seperated by comma):")
    include = include.replace(" ","")
    include = str.split(include, ",")
    
    include = list(map(int, include))
    
    c = [ courses[i-1] for i in include]
    courses = c
else:
    print("That wasn't a valid choice! Restart script and start again!")
    sys.exit()

print("Alright sweetheart, let's go!")
print("=============================")


now = datetime.datetime.now()
basedir = "./vc_dump_"+username+"_"+str(now.day).zfill(2)+"-"+str(now.month).zfill(2)+"-"+str(now.year)+"_"+str(now.hour).zfill(2)+"h"+str(now.minute).zfill(2)+"min"
os.makedirs(basedir)

#Iterate over courses to get Resource-URLS and download them
for index,course in enumerate(courses):

    print("")
    print("=============================")
    print("Fetching material from Course '"+course[0]+"'")
    print("=============================")
    req = s.get(course[1])
    
    #-->Get breadcrumbs for Semester-Information. This is specific to University of Bamberg - moodle
    soup = BeautifulSoup(req.text, 'html.parser')
    soup = soup.find("div", {"class": "breadcrumb"})
    soup = soup.findAll("li")
    
    semester = ""
    
    for noodle in soup:
        if "semester" in noodle.text:
            semester = noodle.text[5:]
            semester = semester.replace("/","_")
        if(semester !=""):
            semesterpath = basedir+"/"+semester
            if not os.path.exists(semesterpath):
                os.makedirs(semesterpath)
        else:
            semesterpath = basedir
    #-->
        
    #compute and create folder path for current course  
    coursename = removeCriticalCharacters(course[0])

    if(osystem=="Windows" and len(coursename)>30): #fixing string length issue on windows machines 
        coursename = coursename[:30]
    
    coursepath = semesterpath+"/"+coursename
    os.makedirs(coursepath)
    
    soup = BeautifulSoup(req.text, 'html.parser')
    soup = soup.find("div", {"id" : "region-main"})
    soup = soup.findAll("a")
        
    folders = []
    resources = []
    urls = []
    
    for noodle in soup:
        if "/folder/" in noodle["href"]:
            littlesoup = BeautifulSoup(str(noodle), "html.parser")
            littlesoup = littlesoup.find("span", {"class" : "instancename"})
            foldername = littlesoup.text[:-12]
            folders.append([foldername, noodle["href"]])
        elif "/url/" in noodle["href"]:
            littlesoup = BeautifulSoup(str(noodle), "html.parser")
            littlesoup = littlesoup.find("span", {"class" : "instancename"})
            linktitle = littlesoup.text[:-4]
            try:
                linkurl = s.get(noodle["href"])
                linkurl = linkurl.url
            except:
                linkurl = "link broken"
            
            if "vc.uni-bamberg.de" in linkurl:
                linkurl = s.get(linkurl)
                urlsoup = BeautifulSoup(linkurl.text, "html.parser")
                urlsoup = urlsoup.find("div", {"class" : "urlworkaround"})
                if urlsoup:
                    urlsoup = urlsoup.find("a")
                    linkurl = urlsoup["href"]
                else:
                    linkurl = "link broken"
            
            urls.append([linktitle, linkurl])
                    
        elif "/resource/" in noodle["href"]:
            littlesoup = BeautifulSoup(str(noodle), "html.parser")
            littlesoup = littlesoup.find("span", {"class" : "instancename"})
            filename = littlesoup.text[:-6]
            filename = removeCriticalCharacters(filename)
        
            if(osystem=="Windows" and len(filename)>30): #fixing filename length issue on windows machines 
                filename = filename[:30]        
        
            resources.append([filename, noodle["href"]])
             
        elif "/teaching/" in noodle["href"]:
            filename = noodle["href"]
            filename = filename[filename.rfind("/")+1: filename.rfind(".")]
            resources.append([filename, noodle["href"]])
            
    if(len(folders)>0):
        print("Digging through folders...")
        for folder in folders:
            req = s.get(folder[1])
            soup = BeautifulSoup(req.text, 'html.parser')
            soup = soup.find("div", {"id" : "region-main"})
            soup = soup.findAll("a")
            for file in soup:
                if file:
                    link= file["href"]
                else:
                    link = "Link is broken"
                
                filename = file.find("span", {"class" : "fp-filename"})
                if filename:                
                    filename = filename.text
                    filename = filename[:filename.rfind(".")]
                    filename = removeCriticalCharacters(filename)
                else:
                    continue

                if "/" in filename:
                    print(filename)
                    filename = filename[filename.rfind("/"):]
                resources.append([filename, link])
        
    
    print("Hey Ya! I found "+str(len(resources))+" files and "+str(len(urls))+" external links!")
    print("=============================")
    print("")
    print("Let me get that for ya!")
    print("")
    
    for index, resource in enumerate(resources):
        url = resource[1]
        response = s.get(url, stream=True)
        fileextension = response.url[response.url.rfind("."):]
           
        if "?" in fileextension:
            fileextension = fileextension[:fileextension.find("?")]
            
        if(len(fileextension) > 5 or fileextension ==".php"):
            fileextension = input('Filename: "'+resource[0]+'" Extension "'+fileextension+'" seems unlikely! Please enter extension manually (Default ".pdf"): ')
            if(fileextension == ""):
                fileextension=".pdf"
        response = s.get(url, stream=True)
        
        path =  coursepath+"/"+resource[0]+fileextension      
        modpath = path
        pindex = 0
        while(os.path.exists(modpath) == True):
            pindex = pindex+1
            modpath = coursepath+"/"+resource[0]+"("+str(pindex)+")"+fileextension
        
        path = modpath
        
        try:    
            with open(path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
                print("Downloading file "+str(index+1)+" of "+str(len(resources))+": "+path[path.rfind("/")+1:])
            del response
        except:
            print("Could not download file '"+path+"'")
            errors.append("Error while fetching file "+filename+" from course '"+course[0])
        
    if(len(urls)>0):
        print("I'll write all external links into 'links.txt' for you, Darling")
        text_file = open(coursepath+"/"+"links.txt", "w")
        for url in urls:
            print("writing...")
            text_file.write(url[0]+"\t"+url[1]+"\n")
        print("done!")
        text_file.close()
            
        
if(logging == True and len(errors)>0):
    log_file = open(basedir+"/"+"ErrorLog.txt", "w")
    for error in errors:
        log_file.write(error)
    
