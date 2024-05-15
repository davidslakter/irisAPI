import requests
from iris import database
from iris import iris_alerts

active_verifications = {}

#sends the event details to noonlight for verification 
def verifyEvent(event, timeout, temp_event_url):

    url = "https://api-sandbox.noonlight.com/tasks/v1/verifications"

    payload = """{"expiration":{"timeout":%d},"attachments":
        [{"points_of_interest":[],"media_type":"video/mp4",
        "url":"%s"}],"prompt":"%s"}""" % (timeout, 
        temp_event_url, event['crime_name'])

    headers = {
        'Authorization' : "Bearer ---------",
        'accept' : "application/json",
        'content-type' : "application/json"
    }

    response = requests.request("POST", url, data=payload, headers=headers)

    json_response = response.json()
    event_id = json_response["id"]

    print(json_response)

    #map verification ID to event
    active_verifications[event_id] = event
    

def DispatchPolice(name, phone, cancelPin, address):

    url = "https://api-sandbox.noonlight.com/dispatch/v1/alarms"

    payload = "{\"name\":\"%s\", \"phone\":\"%s\",\"location\":{\"address\":{\"line1\":%s, \"line2\":%s, \"city\":%s, \"state\":%s, \"zip\":%s}}," % (name, phone, address.line1, address.line2, address.city, address.state, address.zip)
    payload += "{\"services\":{\"police\":true,\"fire\":false,\"medical\":false}}"
    headers = {
        'accept': "application/json",
        'content-type': "application/json"
    }

    response = requests.request("POST", url, data=payload, headers=headers)

def handleVerifyResult(event_id, conclusive, result):
    #noonlight has verified that a crime is ocurring 
    if conclusive and result == "yes":

        database.addEvent(active_verifications[event_id], True)
        # EMAIL AND TEXT ALERT
        contacts = database.getContacts(active_verifications[event_id]["uid"])
        print("....sending alert(s)....") 
        for contact in contacts:
            # send text
            crime_type = active_verifications[event_id]["crime_name"]
            iris_alerts.sendText(contact.phone, crime_type)
            # send email
            iris_alerts.sendEmail(contact.email, crime_type)

    #noonlight didnt return a result
    elif not conclusive:
        database.addEvent(active_verifications[event_id], False)

    del active_verifications[event_id]
