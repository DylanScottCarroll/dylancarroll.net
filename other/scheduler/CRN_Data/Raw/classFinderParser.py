from ctypes import ArgumentError
from bs4 import BeautifulSoup
import re, sys, os, time

DEFAULT_COLOR = 0
DEFAULT_SHADE = 0

TIME_REGEX = "([MTWRF]*) *([0-9]{2}):([0-9]{2})-([0-9]{2}):([0-9]{2}) *(am|pm)"
CREDITS_REGEX = "<font face=\"Verdana\" size=\"-1\">(\d+)<\/font>"

def extractDatas(tr):
    """
    Given a beautiful soup object representing the top tr elements of a course,
    return a tuple of the relevant course datas. 

    Return Format: 
    * (name, crn, credits, [start time, ...], [end time, ...], [days, ...], prof name)
    * All values in the tuple are strings
    * start and end time are expressed as integer minutes since 12:00 am
    * days for a course are expressed as noncontinuous substrings of "mtwrf" e.g. "mwf"
    """

    name = currentTR.contents[1].contents[0].contents[0].string

    crn = ""
    try:
        crn = currentTR.contents[6].contents[0].string
    except:
        print()
        print(currentTR.contents[6])
        input("Hit enter to continue", end="")
        print(end="\r")
    
    credits = ""

    startTimes = []
    endTimes = []
    days = []

    profName = currentTR.contents[10].contents[0].string
    


    nextSibling = tr.next_sibling

    match = re.search(CREDITS_REGEX, str(nextSibling))
    if(match is not None):
        credits = match.groups()[0]
    else:
        credits = "0"

    while True:
        time = str(nextSibling)

        timeTuple = parseTime(time)

        if(timeTuple is not None):
            startTimes.append(timeTuple[0])
            endTimes.append(timeTuple[1])
            days.append(timeTuple[2])
        else:
            break
        
        nextSibling = nextSibling.next_sibling.next_sibling



    return (name, crn, credits, startTimes, endTimes, days, profName)

def parseTime(time):
    """Given a time range of the format in the classfiner page,
    returns a tuple with the information.
    (start time, end time, days)
    
    Start time and end time are expressed as strings of integers representing the number of minutes since midnight
    Days is a substring of "mtwrf" counting which days that time rage occurs on."""
    
    match = re.search(TIME_REGEX, time)
    
    if(match is None): 
        return None
    else:

        groups = match.groups()
        
        days = groups[0].lower()

        startTime = (int(groups[1])%12)*60 + int(groups[2])
        endTime = (int(groups[3])%12)*60 + int(groups[4])

        #If it's pm shift the hours by 12
        if(groups[5].lower() == "pm"):
            startTime += 12*60
            endTime += 12*60

        #If the start time is after the end time, it's actially am
        if(startTime > endTime):
            startTime -= 12*60

        return (str(startTime), str(endTime), days)

def tupleToSaveString(dataTuple):
    """Takes a tuple output from extractDatas() and formats it in the format of the save file"""

    string = "~"
    string += dataTuple[1] + ";" #CRN
    string += dataTuple[0] + ";" #Name
    string += dataTuple[2] + ";" #Credirs
    string += "0;"; #Color
    string += "0;"; #Shade



    for i, startTime in enumerate(dataTuple[3]):
        if i != 0: string += ":"
        string += startTime
    string += ";"

    for i, endTime in enumerate(dataTuple[4]):
        if i != 0: string += ":"
        string += endTime
    string += ";"

    for i, days in enumerate(dataTuple[5]):
        if i != 0: string += ":"
        string += days
    string += ";"


    string += ";" #Group
    string += dataTuple[6]

    return string

def print_progress(i, n):
    completion = (i / n)
    terminal_size = os.get_terminal_size().columns
    width = terminal_size - 7 - 3
    bar_width = int(width*completion)

    terminator = "\n" if i == n else "\r"

    print(f"{completion*100:6.2f}% [" + ("#"*bar_width) + (" "*(width-bar_width)) + "]", end=terminator)

    



if __name__ == "__main__":
    #Read the html text from the file
    if len(sys.argv) != 2:
        raise ArgumentError("Please supply a filename to parse")
    
    filename = sys.argv[1]
    
    f = open(f"{filename}.html", "r", encoding="utf8")
    allText = f.read()
    allText = allText.replace("\n", "")
    f.close()

    #Create the soup object
    soup = BeautifulSoup(allText, 'html.parser')

    if soup is None:
        raise ValueError("Soup is none :(")


    scratchpad_form = soup.find("form", action="https://admin.wwu.edu/pls/wwis/wwsktime.ScratchPad")
    if scratchpad_form is not None:
        scratchpad_form.decompose()

    selTermInputs = soup.findAll("input", attrs={"name": "sel_term"})
    selTermCount = len(selTermInputs)

    saveString = ""
    for i, selTermInput in enumerate(selTermInputs):
        print_progress(i, selTermCount)

        currentTR = selTermInput.parent

        datas = extractDatas(currentTR)
        saveString += tupleToSaveString(datas) + "\n"
    print_progress(selTermCount, selTermCount)

    f = open("output.txt", "w")
    f.write(saveString)
    f.close()

  


