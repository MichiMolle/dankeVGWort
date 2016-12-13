# dankeVGWort
Python-Script for fetching files from moodle. Gets all files of the courses you're enrolled in.
Pretty bad coding-style but working for elearning-System of University of Bamberg.

It let's you get files for all your courses, or just the ones you select.
Files are stored in subfolders sorted by semester. External links are written in a .txt-file for every course.

Works fine for all filetypes except videos.



#Prerequisites
Script requires Python3 + the following packages:

* Requests
* BeautifulSoup4

#Usage
In the commandline type:
```
python dankeVGWort.py
```

After that you're asked for your ID and password, from there everything is self-explanatory.