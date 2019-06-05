       #!/usr/bin/python3

import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import os
import json
from datetime import date,timedelta

hostName = "159.122.217.62"
#hostName = ""
hostPort = 8082

class MyServer(BaseHTTPRequestHandler):

    #	GET is for clients geting the predi
   
    def do_GET(self):
        if self.path == "/":
            Temp = "./logon.html"
        elif self.path == "/home.html":
            Temp = "." + self.path    
        elif self.path == "/base.css":
            Temp = "." + self.path    
            exists = os.path.exists(Temp)
            if exists:
                handle = open(Temp, "r")
                read_data = handle.read()
                self.send_response(200)
                self.send_header("Content-type", "text/css")
                self.end_headers()     
                self.wfile.write(bytes(read_data.encode("utf-8")))
                handle.close
            return
                        
        else: 
            return
        
        exists = os.path.exists(Temp)
        if exists:
            handle = open(Temp, "r")
            read_data = handle.read()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()     
            self.wfile.write(bytes(read_data.encode("utf-8")))
            handle.close
            
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("This file no longer exists or has been moved/edited".encode("utf-8")))
                    
        return

	

#	POST is for submitting data.


    def do_POST(self):
        if self.path=="/logon":
            content_length = int(self.headers['Content-Length'])            
            post_data = self.rfile.read(content_length)          
            
            DPost_Data = (str(post_data.decode("utf-8")))
            DPost_Data = DPost_Data.split("&")

            if DPost_Data[0]=="Password=":
                Temp = "./home.html"          
                exists = os.path.exists(Temp)
                if exists:
                    handle = open(Temp, "r")
                    read_data = handle.read()
                    read_data = addActivities(read_data)
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()     
                    self.wfile.write(bytes(read_data.encode("utf-8")))
                    handle.close
            else:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()     
                self.wfile.write(bytes("Failed Authentication. Goodbye".encode("utf-8")))

        if self.path=="/confirm":
            content_length = int(self.headers['Content-Length'])            
            post_data = self.rfile.read(content_length)          
            
            DPost_Data = (str(post_data.decode("utf-8")))
            DPost_Data = DPost_Data.split("&")
 

            Temp = "./confirm.html"          
            exists = os.path.exists(Temp)
            if exists:
                handle = open(Temp, "r")
                read_data = handle.read()

                read_data = addData(read_data, DPost_Data)
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()     
                self.wfile.write(bytes(read_data.encode("utf-8")))
                handle.close

        if self.path=="/Confirmation":
            
            content_length = int(self.headers['Content-Length'])            
            post_data = self.rfile.read(content_length)          
            
            DPost_Data = (str(post_data.decode("utf-8")))
            DPost_Data = DPost_Data.split("&")

            # Add a quote to start of line
            DPostFinal = "\""
            
            for DPost in DPost_Data:
                DPostFinal += processField(DPost)
                DPostFinal += "\",\""
            
            #remove the last ,"
            DPostFinal = DPostFinal[:-2]
            DPostFinal += "\n"
 
            read_data = "<html><head></head><body><h2>York Step Counter</h2>" + \
            "<table border=\"0.1\" style=\"width:50%\">" + \
            "<tr><th>Name,Activity,Minutes,Date,Steps</th></tr>" + \
            "<tr><td>" + DPostFinal + "</td><td></td></tr>" + \
            "</table>" + \
            "<form method=\"POST\" action=\"AddSteps\">" + \
            "<a href=\"home.html\"> Cancel </a><input type=\"submit\" value=\"Confirm\">" + \
            "</form></body></html>"

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(read_data.encode("utf-8")))
        
        if self.path=="/AddSteps":
            stepsData = "./StepsData.csv"
            print("incomming http: ", self.path)
            content_length = int(self.headers['Content-Length'])            
            post_data = self.rfile.read(content_length)          
            
            DPost_Data = (str(post_data.decode("utf-8")))
            DPost_Data = DPost_Data.split("&")

            # Add a quote to start of line
            DPostFinal = "\""
            
            for DPost in DPost_Data:
                DPostFinal += processField(DPost)
                DPostFinal += "\",\""
            
            #remove the last ,"
            DPostFinal = DPostFinal[:-2]
            DPostFinal += "\n"
            
            with open(stepsData, 'a') as f:
                f.writelines(DPostFinal)
                f.close
            
            Temp = "./success.html"          
            exists = os.path.exists(Temp)
            if exists:
                handle = open(Temp, "r")
                read_data = handle.read()

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()     
                self.wfile.write(bytes(read_data.encode("utf-8")))
                handle.close
            
        return


def processField(DPost1):
    # just take the value or if no value then a space
        DPostFinal = DPost1.split("=")
        DPostFinal = validateData(DPostFinal)
        return DPostFinal[1]

def addActivities(read_data):
    
    html_parts = read_data.split("##ActivityMarker##")
    fh = open('activities.json')
    data = json.load(fh)
    fh.close
    activities = data["activities"]
    for activity in activities:
        html_parts.insert(len(html_parts)-1,"<option value=\"" + activity["activityType"] + "\">" + activity["activityTypeDisplayText"] + " (" + str(activity["stepsMultipler"]) + ")" +  "</option>\n")

    return '\n'.join(html_parts)

def addData(read_data,DPost_Data):

    steps=0
    mins=0
    stepsMultiplier=0
    totalsteps=0
    
    for DPost in DPost_Data:
        DPostFinal = DPost.split("=")
        DPostFinal = validateData(DPostFinal)
        if DPostFinal[0]=="Steps":
            steps=int(DPostFinal[1])
        if DPostFinal[0]=="Activity":
            stepsMultiplier = getStepsMultiplier(DPostFinal[1])
        if DPostFinal[0]=="Minutes":
            mins=int(DPostFinal[1])
        #substitue the vars in the confirm page
        read_data = read_data.replace("##"+DPostFinal[0]+"Marker##",DPostFinal[1])

    # calculate the total steps
    totalsteps=steps+stepsMultiplier*mins
    read_data = read_data.replace("##TotalStepsMarker##",'{:.0f}'.format(totalsteps))

    return read_data

def getStepsMultiplier(activityToFind):
    fh = open('activities.json')
    data = json.load(fh)
    fh.close
    activities = data["activities"]
    for activity in activities:
        if activity["activityType"]==activityToFind:
            stepsMultipler = activity["stepsMultipler"]
            return stepsMultipler

    return 0

def validateData(DPostFinal):
    # fix blank date to yesterday
    if DPostFinal[0]=="Date" and DPostFinal[1]=="":
        DPostFinal[1] = (date.today() - timedelta(1)).strftime("%Y-%m-%d")
    # the query params a space gets substitued with a + fix that
    if DPostFinal[0]=="Name":
        DPostFinal[1] = DPostFinal[1].replace("+"," ")
    # only numerics on mins and steps
    if DPostFinal[0]=="Minutes" and DPostFinal[1].isdigit()==False:
        DPostFinal[1]="0"
    if DPostFinal[0]=="Steps" and DPostFinal[1].isdigit()==False:
        DPostFinal[1]="0"
    return DPostFinal

myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))


        
