#!/usr/bin/python
# -*- coding: utf-8 -*-
import pdfkit
import requests
import json
from xml.etree import ElementTree as ET
from subprocess import call

#
# Take a list of issues IDs and return
# - A list of issues with all of their fields
# - A dictionnary of issue types icons
#
def getIssues(issueIDs):
    if len(issueIDs)%2 != 0:
        issueIDs.append("0")

    issues = []
    issueTypesIcons = {}

    for ID in issueIDs:
        issue = getIssue(ID)
        issues.append(issue)

        if issue['issueType'] not in issueTypesIcons.keys():
            icon = getIssueTypeIcon(issue['issueType'], issue['issueTypeIconUrl']);
            issueTypesIcons[issue['issueType']] = icon;

    return issues, issueTypesIcons

#
# Given an issue ID get its data from Jira
#
def getIssue(issueID):
    print("Downloading issue " + issueID)

    if issueID == 0:
        response= {}
    else:
        url = "http://" + host + ":" + port + "/rest/api/latest/issue/" + issueID
        querystring = {"fields": "summary,assignee,issuetype,timetracking,priority"}
        req = requests.get(url, auth=(username, password), params=querystring)
        response = json.loads(req._content)

    try:
        issueType = response['fields']['issuetype']['name'].encode('ascii', 'ignore')
    except:
        issueType = ""

    try:
        issueTypeIconUrl = response['fields']['issuetype']['iconUrl']
    except:
        issueTypeIconUrl = ""
    try:
        summary = response['fields']['summary'].encode('ascii', 'ignore')
    except:
        summary = ""
    try:
        assignee = response['fields']['assignee']['name'].encode('ascii', 'ignore')
    except:
        assignee = ""
    try:
        priority = response['fields']['priority']['name'].encode('ascii', 'ignore')
    except:
        priority = ""
    try:
        estimatedTime = response['fields']['timetracking']['originalEstimate'].encode('ascii', 'ignore')
    except:
        estimatedTime = ""

    issue = dict(
        issueType         = issueType,
        issueTypeIconUrl  = issueTypeIconUrl,
        summary           = summary,
        assignee          = assignee,
        estimatedTime     = "Duree: " + estimatedTime,
        reference         = issueID,
        priority          = "Priorite: " + priority
        )

    return issue

#
# Given a issueType name and the URL to its logo
# returned by Jira, write this image to a file
# which will later be embed in the HTML document
#
def getIssueTypeIcon(issueType, url):
    print("Downloading image " + issueType)
    filename = ""
    if url:
        req = requests.get(url, auth=(username, password))
        data = req._content

        filename = issueType + ".svg"
        with open("tmpFiles/" + filename, "w") as imageFile:
            imageFile.write(data);

    return filename

def generateIssueHTML(issue, typesIcons):
    icon = typesIcons[issue['issueType']]
    br   = ET.Element('br')

    # Create the div containing the issue
    div = ET.Element('div')
    div.set("class", "issue")

    divHeader = ET.Element('div')
    divHeader.set("class", "issue-header")
    div.append(divHeader)

    divContent = ET.Element("div")
    divContent.set("class", "issue-content")
    div.append(divContent)

    divFooter = ET.Element("div")
    divFooter.set("class", "issue-footer")
    div.append(divFooter)


    # Logo of the issue type
    imgIcon = ET.Element('img')
    divHeader.append(imgIcon)
    imgIcon.set('src', icon)

    # Reference of the issue
    spanReference = ET.Element('span')
    divHeader.append(spanReference)
    spanReference.text = issue['reference']

    # Name of the assignee
    spanAssignee = ET.Element('span')
    divHeader.append(spanAssignee)
    spanAssignee.text = issue['assignee']
    spanAssignee.set("class", "assignee")
    div.append(br)

    # Summary of the issue
    spanSummary = ET.Element('span')
    divContent.append(spanSummary)
    spanSummary.text = issue['summary']
    spanSummary.set("class", "summary")
    div.append(br)

    # Priority of the issue
    spanPriority = ET.Element('span')
    divFooter.append(spanPriority)
    spanPriority.text = issue['priority']
    div.append(br)

    # Estimated time to spend
    spanEstimatedTime = ET.Element('span')
    spanEstimatedTime.set("class", "estimated-time")
    divFooter.append(spanEstimatedTime)
    spanEstimatedTime.text = issue['estimatedTime']

    return div

#
# From the list of parsed issues and the list of issues types icons
# generate an HTML document which will later be used to generate
# the final PDF
#
def generateHTML(listOfIssues, typesIcons):
    html = ET.Element('html')
    body = ET.Element('body')
    br   = ET.Element('br')
    html.append(body)
    divs = []

    for issue in listOfIssues:
        div = generateIssueHTML(issue, typesIcons)
        divs.append(div)

    it = iter(divs)
    for x in it:
        div1 = x
        div2 = next(it)
        line = ET.Element('div')
        line.set("class", "container")
        line.append(div1)
        line.append(div2)
        body.append(line)


    ET.ElementTree(html).write(open('./tmpFiles/issues.html', 'w'), encoding='ascii', method='html')

    styleString = """
<style>
.container {
  border: 1px solclass #000;
  display:flex;
  justify-content: center;
  padding: 3px;
  height: 337px;
  font-size: 24
}
.container > div {
  border: 1px solclass #000;
  margin:2px;
}
.issue {
    width: 50%;
    border-left: 10px solid blue;
    border-right: 20px solid white;
    border-bottom: 20px solid white;
    position: relative;
}
.issue-header {
}
.issue-content {
    text-align: center;
    position: absolute;
    top: 20%
}
.issue-footer {
    position: absolute;
    bottom: 0%
}
.assignee {
    float: right;
}
.summary {
    font-weight: bold;
}
.estimated-time {
    float: right;
}
</style>
"""
    with open('./tmpFiles/issues.html', 'a') as f:
        f.write(styleString)

#
# Generate the PDF file from the HTML file generated earlier
#
def generatePDFFromHtml():
    print("Generating PDF")
    pdfkit.from_file('./tmpFiles/issues.html', 'issues.pdf')


#
# Read the config.json file to know
# the jira host and the credentials
#
def readConfig():
    global username
    global password
    global host
    global port

    # Read username and password from config file
    config = json.load(open('./config.json'))

    username = config['username']
    password = config['password']
    host = config['host']
    port = config['port']

#
# Executed no matter what happens
# Delete the tmpFiles folder used to write different
# temporary files during the creation process
#
def cleanup():
    print("Cleaning up tmp files")
    # call(["rm", "-r", "tmpFiles"])

#
# Read the list of issues from a text file in
# the file system
#
def readIssueIDs():
    with open('./issues.txt', 'r') as f:
        content = f.readlines()

    issues = [x.strip() for x in content] 
    return issues

def main():
    try:
        # Create the temp directory
        call(["mkdir", "-p", "tmpFiles"])

        # Initialize needed variables
        readConfig()

        issueList=readIssueIDs()
        if not issueList:
            print("No issues in issues.txt, terminating")
            return

        # Get the issues from Jira
        issues, typesIcons = getIssues(issueList)

        # Generate the HTML file used to create the PDF
        generateHTML(issues, typesIcons)

        # Generate the PDF file to print
        generatePDFFromHtml()
    finally:
        # Remove the temp directory
        cleanup()

if __name__ == "__main__":
    main()
