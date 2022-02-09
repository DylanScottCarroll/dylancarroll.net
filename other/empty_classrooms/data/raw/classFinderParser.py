from bs4 import BeautifulSoup
import re

DEFAULT_COLOR = 0
DEFAULT_SHADE = 0

TIME_REGEX = "([MTWRF]*) *([0-9]{2}):([0-9]{2})-([0-9]{2}):([0-9]{2}) *(am|pm)"
ROOM_REGEX = "([A-Z]{2}\s+\d{3}[A-Z]{0,1})"

def extractDatas(tr):
    """
    Given a beautiful soup object representing the top tr elements of a course,
    return a tuple of the relevant course datas. 

    Return Format: 
    * [(room, name, startTime, endTime, days), ...]
    * All values in the tuple are strings
    * start and end time are expressed as integer minutes since 12:00 am
    * days for a slot are expressed as noncontinuous substrings of "mtwrf" e.g. "mwf"
    """

    name = currentTR.contents[1].contents[0].contents[0].string

    slots = []

    nextSibling = tr.next_sibling

    while True:
        time = str(nextSibling)

        timeTuple = parseTime(time)
        room = parseRoom(time)

        if(timeTuple is not None and room is not None):
            startTime = timeTuple[0]
            endTime = timeTuple[1]
            days = timeTuple[2]

            slots.append( (room, name, startTime, endTime, days) )
        else:
            break
        
        nextSibling = nextSibling.next_sibling.next_sibling



    return slots

def parseRoom(time):
    match = re.search(ROOM_REGEX, time)
    if(match is None): 
        return None
    else: 
        return match.groups()[0]

def parseTime(time):
    """Given a time range of the format in the classfinder page,
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
    
    room, name, startTime, endTime, days = dataTuple

    return f"{name},{startTime},{endTime},{days}"

if __name__ == "__main__":
    #Read the html text from the file
    f = open("Winter_2022_Classes.html", "r")
    allText = f.read().replace("\n", "")
    f.close()

    #Create the soup object
    soup = BeautifulSoup(allText, 'html.parser')

    soup.find("form", action="https://admin.wwu.edu/pls/wwis/wwsktime.ScratchPad").decompose()

    selTermInputs = soup.findAll("input", attrs={"name": "sel_term"})

    rooms = dict()
    for selTermInput in selTermInputs:

        currentTR = selTermInput.parent

        datas = extractDatas(currentTR)

        for data in datas:
            #print(data)
            room = data[0]

            if room not in rooms.keys():
                rooms[room] = set()
            
            rooms[room].add(data)

    output = ""
    keyList = sorted(list(rooms.keys()))
    for key in keyList:
        


        output += key + ":"
        for tuple in rooms[key]:
            current = tupleToSaveString(tuple)

            output += current + ";"

        output += "\n"

    f = open("output.txt", "w")
    f.write(output)
    f.close()

  

