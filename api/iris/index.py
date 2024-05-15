from flask import Flask, request, abort
from threading import Thread
from collections import defaultdict
import hmac
import hashlib
import base64
from iris import database
from iris import inference
from iris import noonlight
import requests
from iris import Contact
from flask_cors import CORS
from iris.angelcam_proxy_routes import angel_proxy
from prometheus_client.parser import text_string_to_metric_families
from iris import app

app.register_blueprint(angel_proxy)
CORS(app)

active_instances = defaultdict(dict)

@app.route('/cameras/', methods=['POST'])
def startInference():
    uid = str(request.form['uid'])

    if database.isAuthenticated(uid, request.headers['Authorization']):
        angeldata = {
                'name': request.form['camera_name'],
                'type': request.form['stream_type'],
                'connection_type': request.form['connection_type'],
                'url': request.form['stream_url']
                }


        angelcam_res = requests.post('https://api.angelcam.com/v1/cameras/', headers={'Authorization': 'PersonalAccessToken f73101fcd2984cf39aaed4abad2e41b845d2e1a7'}, data=angeldata)

        if angelcam_res.status_code == 201:
            angel_json = angelcam_res.json()
            camera_id = angel_json['id']
            stream_url = angel_json['streams'][0]['url']
            stream_type = angel_json['type']
            if stream_type == "h264":
                stream_url = angel_json['streams'][1]['url']

            camera = {
                    'name': angel_json['name'],
                    'ID': camera_id,
                    'url': stream_url,
                    'stream_type': stream_type,
                    'location': str(request.form['camera_location']),
                    'person_density': 0
                    }

            Iris_Instance = inference.Iris(uid, camera)

            # add existing contacts from db to iris instance
            database.updateContacts(Iris_Instance)

            #start the inferencing in a new thread
            t = Thread(target=Iris_Instance.watch)
            t.start()

            print("new camera thread started")

            #store the reference of the class
            active_instances[uid][str(camera_id)] = Iris_Instance

            #add the camera to the database
            database.addCamera(uid, camera)

            return angelcam_res.content, 201

        return 'bad request to angelcam', angelcam_res.status_code

    return 'unauthorized', 401

@app.route('/cameras/<camera_id>/', methods=['PATCH', 'DELETE'])
def stopInference(camera_id):
    uid = request.form['uid']
    
    if request.method == 'DELETE':
        if database.isAuthenticated(uid, request.headers['Authorization']):
            req_url = 'https://api.angelcam.com/v1/cameras/' + camera_id + '/'
            angelcam_res = requests.delete(req_url, headers={'Authorization': 'PersonalAccessToken f73101fcd2984cf39aaed4abad2e41b845d2e1a7'})
            if angelcam_res.status_code != 204:
                return 'internal error removing camera', angelcam_res.status_code

            #get the class instance and terminate it
            instance = active_instances[uid][str(camera_id)]
            instance.terminate()
            del active_instances[uid][str(camera_id)]

            print("removing: ", camera_id)
            #remove the camera from the database
            database.removeCamera(uid, int(camera_id))
            
            return '', 204
        
        return 'unauthorized', 401

    if request.method == 'PATCH':
        if database.isAuthenticated(uid, request.headers['Authorization']):
            # update density for iris instance
            person_density = request.form['person_density']
            instance = active_instances[uid][str(camera_id)]
            instance.person_density = person_density

            # update value in db
            database.updateThreshold(uid, int(camera_id), person_density)
            print(f'Updating: {camera_id}')

            return '', 204

        return 'unauthorized', 401

@app.route('/verifiedEvent', methods=['POST'])
def verified():
    print('new verification result')
    signature = hmac.new(b'NEMCfBwyRr9zTjCtm9pECykyM', request.data, hashlib.sha256).digest()
    decodeSig = base64.b64encode(signature).decode()
    if hmac.compare_digest(decodeSig, request.headers.get('X-Noonlight-Signature')):
        jsonData = request.get_json()
        print('recieved verification result', jsonData)

        #handle the verified result
        if jsonData['conclusive']:
            noonlight.handleVerifyResult(jsonData['id'], True, jsonData['result'])
        else:
            noonlight.handleVerifyResult(jsonData['id'], False, jsonData['error'])
        return '', 204

    #request not authentic
    return '', 401

@app.route('/contacts/', methods=['POST'])
def addContact():
    uid = request.form['uid']
    if database.isAuthenticated(uid, request.headers['Authorization']):

        new_contact = Contact.Contact(request.form)

        # check if user has active camera instances 
        if uid not in active_instances.keys():
            # need to check if contact_key already in database
            contact_key = hash(new_contact)
            while not database.verifyContactKey(uid, contact_key):
                contact_key = hash(new_contact)

            database.addContact(uid, new_contact)
            return '', 204

        # add contact to matching uid iris instances
        uid_instances = active_instances[uid]
        for camera in uid_instances.keys():
            iris_instance = uid_instances[camera]

            # create key for contact
            contact_key = hash(new_contact)
            # generate keys until there's a unique key
            while contact_key in iris_instance.contacts.keys():
                contact_key = hash(new_contact)

            # add contact to contact dict
            iris_instance.contacts[contact_key] = new_contact

            # add contact to database
            database.addContact(uid, new_contact)

        return '', 204

    return 'unauthorized', 401

@app.route('/contacts/<contact_id>/', methods=['DELETE'])
def deleteContact(contact_id):
    uid = request.form['uid']
    if database.isAuthenticated(uid, request.headers['Authorization']):

        if uid in active_instances.keys():
            uid_instances = active_instances[uid]
            for camera in uid_instances.keys():
                iris_instance = uid_instances[camera]

                # remove contact from dict
                del iris_instance.contacts[int(contact_id)]

                # remove contact from database
                database.removeContact(uid, int(contact_id))  
        else:
            database.removeContact(uid, int(contact_id))

        return '', 204

    return 'unauthorized', 401

@app.route('/status/', methods=['GET'])
def getStatus():
    num_active = 0
    for uid in active_instances:
        num_active += len(active_instances[uid])

    if num_active == 0:
        active_status = 'There are no active Iris instances.'
    elif num_active == 1:
        active_status = 'There is 1 active Iris instance.'
    else:
        active_status = 'There are {num_active} active Iris instances.'

    metrics_url = 'http://localhost:8002/metrics'
    metrics = requests.get(metrics_url).text

    gpu_status = "GPU METRICS:\n"
    for family in text_string_to_metric_families(metrics):
        for sample in family.samples:
            gpu_status += "{0}: {2}".format(*sample)
            gpu_status += "\n"

    message = f'\n{active_status}\n\n{gpu_status}'
    return message, 200

if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=8443)
