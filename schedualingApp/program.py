import PySimpleGUI as sg
import os
import xml.etree.ElementTree as et
import xml.dom.minidom
import textwrap
from datetime import datetime


fileName = "schedual.xml"
maxTitleLength = 60
maxDescriptionLength = 300
# Define the window layout
mainLayout = [
    [sg.Text("center console", font = ("Arial",11,"bold"))],
    [sg.Button("GENERATE SCHEDUAL")],
    [sg.Button("CURRENT ACTIVITY")],
    [sg.Button("QUIT")],
    [sg.Button("DELETE DATA AND QUIT",button_color='#c61a09')]
]
schedualRemoveLayout = [
    [sg.Text("remove entries", font = ("Arial",11,"bold"))],
    [sg.Button("Monday"),
        sg.Button("Tuesday"),
        sg.Button("Wednesday"),
        sg.Button("Thursday")],
    [sg.Button("Friday"),
        sg.Button("Saturday"),
        sg.Button("Sunday")]
]
schedualAddLayout = [
    [sg.Text("add schedual items", font = ("Arial",11,"bold"))],
    
    [sg.Text("select day", font = ("Arial",11))],
    [sg.Combo(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday','Saturday','Sunday'], key='day_input',readonly=True,font = ("Aerial",8))],
    
    [sg.Text("start time (24 hour format)", font = ("Arial",11))],
    #hour and minute are separate to reduce risk of formating errors for better user experience
    [sg.Text("hour",font = ("Aerial",8)),sg.Text("minute",font = ("Aerial",8), pad = (10,0))],
    [sg.Input('00', enable_events=True, key='start_hour_input',size = (2,1)),sg.Input('00', enable_events=True, key='start_minute_input',size = (2,1),pad=(10,0))],
    
    [sg.Text("end time (24 hour format)", font = ("Arial",11))],
    [sg.Text("hour",font = ("Aerial",8)),sg.Text("minute",font = ("Aerial",8), pad = (10,0))],
    [sg.Input('00', enable_events=True, key='end_hour_input',size = (2,1)),sg.Input('00', enable_events=True, key='end_minute_input',size = (2,1),pad=(10,0))],
    
    [sg.Text(f"title (max {maxTitleLength} characters)", font = ("Arial",11))],
    [sg.Input(' ', enable_events=True, key='title_input',size = (50,20))],
    
    [sg.Text(f"description (max {maxDescriptionLength} characters)", font = ("Arial",11))],
    [sg.Input(' ', enable_events=True, key='description1_input',size = (50,20))],
    
    [sg.Button("submit",key = "submit_input")],
    
    [sg.Text("error message: ", font = ("Arial",11))],
    [sg.Text(" ", font = ("Arial",11), key = "error_message")],
]

layout = [[sg.TabGroup([[sg.Tab('main', mainLayout), 
                         sg.Tab('del', schedualRemoveLayout), 
                         sg.Tab('add',schedualAddLayout)]])]]

# Create the window
mainwindow = sg.Window(title="My Window", layout=layout, margins=(10, 10), background_color="black",finalize=True)

class SchedualValues:
  def __init__(self, dayString, startTime, endTime, titleString,descriptionString): #times are in hh:mm:ss format
    self.day = dayString
    self.starttime = startTime
    self.endtime = endTime
    self.title = titleString
    self.description1 = descriptionString
    

def CreateXMLFile(fileName):
    if os.path.exists(fileName):
        return
    root = et.Element("schedual") 
    tree = et.ElementTree(root) 
    with open (fileName, "wb") as files : 
        tree.write(files) 
    return

def queryXML(fileName):
    tree = et.parse(fileName)
    root = tree.getroot()
    schedual_list = []
    for schedualEntry in root.findall('schedualEntry'):
        day = schedualEntry.find('day').text
        starttime = schedualEntry.find('starttime').text
        endtime = schedualEntry.find('endtime').text
        title = schedualEntry.find('title').text
        description1 = schedualEntry.find('description1').text
        schedual_dict = {"Day": day, "Start Time": starttime, "End Time": endtime, "Title": title, "Description": description1}
        schedual_list.append(schedual_dict)
    # Sort the list by starttime in ascending order
    schedual_list = sorted(schedual_list, key=lambda d: datetime.strptime(d["Start Time"], "%H:%M"))
    return schedual_list

def AddEntry(schedualClass,fileName):
    tree = et.parse(fileName)
    root = tree.getroot()

    sub1 = et.Element("schedualEntry")
    root.append(sub1)
    
    day = et.SubElement(sub1,"day")
    day.text = schedualClass.day
    
    starttime = et.SubElement(sub1,"starttime")
    starttime.text = schedualClass.starttime
    
    endtime = et.SubElement(sub1,"endtime")
    endtime.text = schedualClass.endtime
    
    title = et.SubElement(sub1,"title")
    title.text = schedualClass.title
    
    description1 = et.SubElement(sub1,"description1")
    description1.text = schedualClass.description1
    
    # Write the ElementTree back to the file
    with open(fileName, "wb") as files:
        xml_string = et.tostring(root, encoding="utf-8", short_empty_elements=True)
        pretty_xml = xml.dom.minidom.parseString(xml_string).toprettyxml() 
        files.write(pretty_xml.encode('utf-8'))
    return

def RemoveEntry(button_key, fileName, window):
    tree = et.parse(fileName)
    root = tree.getroot()

    # Split the button_key into the individual values
    _, day, starttime, endtime, title, description = button_key.split('-')

    for sub1 in root.findall('schedualEntry'):
        if (sub1.find('day').text == day and
            sub1.find('starttime').text == starttime and
            sub1.find('endtime').text == endtime and
            sub1.find('title').text == title and
            sub1.find('description1').text == description):
            root.remove(sub1)

    # Write the ElementTree back to the file
    with open(fileName, "wb") as files:
        tree.write(files)
        
    # Close and reopen the window to show changes, since the elements cannot be removed
    window.close()
    # Get new dict to display the results
    schedual_dict_list = queryXML(fileName)
    DisplayDayResults(day, schedual_dict_list, window)
    

CreateXMLFile(fileName)

def HandleDay(event):
    if event == "Monday" or event == "Tuesday" or event == "Wednesday" or event == "Thursday" or event == "Friday" or event == "Saturday" or event == "Sunday":
        return event
    else:
        return "empty"
    
def DisplayDayResults(dayName, schedual_dict_list, window):
    #since added elements cannot be removed, a secondary window is created to view and remove the elements
    new_layout = []
    for schedual_dict in schedual_dict_list:
        if(dayName == schedual_dict["Day"]):
            new_element = [
                sg.Text(f"{schedual_dict['Title']}"),
                sg.Text(f"{schedual_dict['Start Time']}"),
                sg.Text(f"{schedual_dict['End Time']}"),
                #give button a unique key to determine which element to remove
                sg.Button('del', key = f"del-{schedual_dict['Day']}-{schedual_dict['Start Time']}-{schedual_dict['End Time']}-{schedual_dict['Title']}-{schedual_dict['Description']}")
            ]
            new_layout.append(new_element)

    # Define the new column
    new_column = sg.Column(new_layout, key='scroll_field')

    # Define the new layout for the window
    layout = [[new_column]]
    window = sg.Window(f'{dayName}', layout, finalize=True)

    return window

def ValidateForm (day,startHour,startMinute,endHour,endMinute,title,description1,window):
    #since the elements have default values, null references do not need to be handled
    validated = True
    errorMessage = "[PASSED] form validated successfully"
    startTime = "00:00"
    endTime = "00:00"
    #validate day
    if day != "Monday" and day != "Tuesday" and day != "Wednesday" and day != "Thursday" and day != "Friday" and day != "Saturday" and day != "Sunday":
        validated = False
        errorMessage = "[FAILED]: day is invalid"
    #validate that start time is numeric in the form hh:mm
    if (startHour.isnumeric() and len(startHour) == 2) and (startMinute.isnumeric() and len(startMinute) == 2):
        startTime = f"{startHour}:{startMinute}"
    else:
        validated = False
        errorMessage = "[FAILED]: start time is invalid"
        
    if (endHour.isnumeric() and len(endHour) == 2) and (endMinute.isnumeric() and len(endMinute) == 2):
        endTime = f"{endHour}:{endMinute}"
    else:
        validated = False
        errorMessage = "[FAILED]: end time is invalid"
    
    #since there is no way to limit the input size of the element, the max size needs to be handled here
    if (len(title) > maxTitleLength):
        validated = False
        errorMessage = "[FAILED]: title length exceeds the character limit"
    
    if(len(description1) > maxDescriptionLength):
        validated = False
        errorMessage = "[FAILED]: description length exceeds the character limit"
        
    if validated:
        schedualClass = SchedualValues(day,startTime,endTime,title,description1)
        AddEntry(schedualClass, fileName)
        
        #reset the form to enter new values
        window['day_input'].Update(' ')
        window['start_hour_input'].Update('00')
        window['start_minute_input'].Update('00')
        window['end_hour_input'].Update('00')
        window['end_minute_input'].Update('00')
        window['title_input'].Update(' ')
        window['description1_input'].Update(' ')
    
    #the form is not reset when failed to comply with useability principles
    window['error_message'].Update(errorMessage)
    return

def GenerateSchedual(schedual_dict_list):
    day_dict = {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        day_dict[day].append([sg.Text(f"{day}")])
    for schedual_dict in schedual_dict_list:
        day= schedual_dict['Day'] 
        new_element = sg.Frame('', [[sg.Text(f"title: {textwrap.fill(schedual_dict['Title'],10)}")],
                                    [sg.Text(f"desc: {textwrap.fill(schedual_dict['Description'],20)}",font = ('Aerial',8))],
                                    [sg.Text(f"start time: {schedual_dict['Start Time']}")],
                                    [sg.Text(f"end time: {schedual_dict['End Time']}")]])
        day_dict[day].append([new_element])  # Wrap new_element in a list

    # Create a column for each weekday
    columns = [sg.Column(day_dict[day], key=f'scroll_field_{day}',vertical_alignment='top',scrollable=True,vertical_scroll_only=True,size = (None,300)) for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]
    layout = [columns]

    window = sg.Window('schedual', layout, finalize=True,size = (1080,360))
    return window

def ShowCurrentActivity(schedual_dict_list):
    currentTime = datetime.now()
    currentDay = currentTime.strftime("%A")
    currentHourMinute = currentTime.strftime("%H:%M")
    
    displayedResult = None
    
    for entry in schedual_dict_list:
        if (currentDay == entry["Day"]) and (currentHourMinute < entry["End Time"]) and (currentHourMinute > entry["Start Time"]):
            displayedResult = entry
            break
    if displayedResult is None:
        return
    
    new_element = [sg.Frame('', [   [sg.Text("Title", font = ("Arial",11,"bold"))],
                                    [sg.Text(f"{textwrap.fill(displayedResult['Title'],50)}")],
                                    [sg.Text("Description", font = ("Arial",11,"bold"))],
                                    [sg.Text(f"{textwrap.fill(displayedResult['Description'],50)}",font = ('Aerial',8))],
                                    [sg.Text("Start Time", font = ("Arial",11,"bold"))],
                                    [sg.Text(f"{displayedResult['Start Time']}")],
                                    [sg.Text("End Time", font = ("Arial",11,"bold"))],
                                    [sg.Text(f"{displayedResult['End Time']}")],
                                    [sg.Text("Current Time:", font = ("Arial",11,"bold"))],
                                    [sg.Text(f"{currentHourMinute}", font = ("Arial",11,"bold"))],
                                ]
                            )
                   ]
    layout = [new_element]

    window = sg.Window('schedual', layout, finalize=True,size = (200,300))
    return window
    
    
while True:
    window, event, values = sg.read_all_windows(timeout=5000) #run rest of code every five seconds without input
    
    schedual_dict_list = queryXML(fileName)
    
    dayValue = HandleDay(event)
    if dayValue != "empty":
        secondaryWindow = DisplayDayResults(dayValue,schedual_dict_list,window)
        continue
        
    
    if event == "QUIT" or event == sg.WIN_CLOSED:
        if window == mainwindow:
            break
        else:
            window.close()
    elif 'del' in event:
        RemoveEntry(event, fileName, window)
    elif event == "submit_input":
        ValidateForm(
            values["day_input"],
            values["start_hour_input"],
            values["start_minute_input"],       
            values["end_hour_input"],
            values["end_minute_input"],
            values["title_input"],
            values["description1_input"],
            window
        )
    elif event == "DELETE DATA AND QUIT":
        if os.path.exists(fileName):
            os.remove(fileName)
            break
    elif event == "GENERATE SCHEDUAL":
        GenerateSchedual(schedual_dict_list)
    elif event == "CURRENT ACTIVITY":
        ShowCurrentActivity(schedual_dict_list)
        
    elif callable(event):
        event()

mainwindow.close()
