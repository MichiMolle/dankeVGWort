import os
import shutil
import datetime
import requests
from getpass import getpass
from bs4 import BeautifulSoup

s = requests.Session()
print("***DankeVGWort.py - VC-Kurs-Material Fetching-Skript***")
print("=======================================================")

username = input('ba-ID: ')
password = getpass(prompt='password: ')

print("logging in...") 
req = s.post('https://vc.uni-bamberg.de/moodle/login/index.php', data={'username': username, 'password': password})
print("getting course list...")
req = s.get('https://vc.uni-bamberg.de/moodle/my/index.php?mynumber=-2')

soup = BeautifulSoup(req.text, 'html.parser')
soup = soup.find("div", { "class" : "course_list" })
soup = soup.findAll("h2", {"class" : "title"})

courses = []

for noodle in soup:
    noodle = noodle.find("a")
    noodle = [noodle['title'],noodle['href']]
    courses.append(noodle)


print("--> I detected "+str(len(courses))+" courses:")

for index, noodle in enumerate(courses):
    print("["+str(index+1)+"]: " + noodle[0])

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

print("Alright sweetheart, let's go!")
print("=============================")


now = datetime.datetime.now()
basedir = "./vc_dump_"+username+"_"+str(now.day).zfill(2)+"-"+str(now.month).zfill(2)+"-"+str(now.year)+"_"+str(now.hour).zfill(2)+"h"+str(now.minute).zfill(2)+"min"
os.makedirs(basedir)


for index,course in enumerate(courses):
#course = courses[6]
    print("")
    print("=============================")
    print("Fetching material from Course '"+course[0]+"'")
    print("=============================")
    req = s.get(course[1])
    
    
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
    
        
        
    coursepath = semesterpath+"/"+course[0].replace("/","_")
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
            filename = filename.replace(" ", "_")
            filename = filename.replace(",","")
            filename = filename.replace(".","")
            filename = filename.replace("-","")
            filename = filename.replace(":","")
            filename = filename.replace("ß","ss")
            filename = filename.replace("%","")
            filename = filename.replace("/","")
            filename = filename.replace("(","")
            filename = filename.replace(")","")
            filename = filename.replace('"',"")
            filename = filename.replace("_&_","_")
        
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
                link= file["href"]
                filename = file.find("span", {"class" : "fp-filename"}).text
                filename = filename[:filename.rfind(".")]
                filename = filename.replace(" ", "_")
                filename = filename.replace(",","")
                filename = filename.replace(".","")
                filename = filename.replace("-","")
                filename = filename.replace(":","")
                filename = filename.replace("ß","ss")
                filename = filename.replace("%","")
                filename = filename.replace("/","")
                filename = filename.replace("(","")
                filename = filename.replace(")","")
                filename = filename.replace('"',"")
                filename = filename.replace("_&_","_")

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
            
        with open(path, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
            print("Downloading file "+str(index+1)+" of "+str(len(resources))+": "+path[path.rfind("/")+1:])
        del response
        
    if(len(urls)>0):
        print("I'll write all external links into 'links.txt' for you, Darling")
        text_file = open(coursepath+"/"+"links.txt", "w")
        for url in urls:
            print("writing...")
            text_file.write(url[0]+"\t"+url[1]+"\n")
        print("done!")
        text_file.close()
            
        
        
    
