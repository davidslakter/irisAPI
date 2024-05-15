import tensorflow as tf
import cv2
import numpy as np
from keras import backend as k
from keras.preprocessing import image
from keras.layers import Input 
from google.cloud import storage
import os
from iris.extractor import Extractor
import sys
from random import randint
from iris import noonlight
import datetime
import requests
from tensorrtserver.api import *

service_key = 'iris-service-account-key.json'
storage_client = storage.Client.from_service_account_json(service_key)
BUCKET_NAME = 'elemental-alloy-256522.appspot.com'

bucket = storage_client.get_bucket(BUCKET_NAME)

session = tf.Session(graph=tf.Graph())
with session.graph.as_default():
    k.tensorflow_backend.set_session(session)
    extractor = Extractor('saved_models/image_model.hdf5')

class_names = ['Abuse', 'Arrest', 'Arson', 'Assault', 'Burglary', 'Explosion', 'Fighting',
               'Normal', 'RoadAccidents', 'Robbery', 'Shooting', 'Shoplifting', 'Stealing', 'Vandalism']
class_names.sort()
name_id_map = dict(zip(range(len(class_names)), class_names))

class Iris: 

    def __init__(self, uid, camera):
        self.uid = uid
        self.name = camera["name"]
        self.id = camera["ID"]
        self.location = camera["location"]
        self.url = camera["url"]
        self.stream_type = camera["stream_type"]
        self.person_density = camera["person_density"]
        self.contacts = {}
        self._running = True
        self.last_updated = datetime.datetime.now()

    def terminate(self):
        self._running = False
    
    #get fresh url from angelcam
    def update_url(self):
        angelcam_res = requests.get('https://api.angelcam.com/v1/cameras/' + str(self.id) + '/', 
        headers={'Authorization': 'PersonalAccessToken f73101fcd2984cf39aaed4abad2e41b845d2e1a7'}).json()
        if self.stream_type == "h264":
            self.url = angelcam_res['streams'][1]['url']
        else:
            self.url = angelcam_res['streams'][0]['url']

    def new_capture(self):
        print('new capture! ', self.url)
        return cv2.VideoCapture(self.url)

    def watch(self):
        
        with session.graph.as_default():
            k.tensorflow_backend.set_session(session)
            vs = []
            images = []
            cap = self.new_capture()
            shouldAlert = True
            normal_event_counter = 0
            model1_context = InferContext('localhost:8001', ProtocolType.GRPC, 'iris_model_1', 1, False, 0, True)
            model2_context = InferContext('localhost:8001', ProtocolType.GRPC, 'iris_model_2', 1, False, 0, True)

            while self._running:
                
                #check how long the current url has been used
                url_time_used = (datetime.datetime.now() - self.last_updated).total_seconds()
                if url_time_used > 2400.0:
                    self.update_url()
                    cap = self.new_capture()
                    self.last_updated = datetime.datetime.now()

                ret = cap.grab()
                if True:
                    ret, image = cap.retrieve()
                    if not ret: continue
                    images.append(image)
                    image = cv2.resize(image, dsize=(299, 299),
                    interpolation=cv2.INTER_CUBIC)
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    
                    features = extractor.extract(frame=image)
                    vs.append(features)

                    # Classifies the sequence if it's of length 150
                    if len(vs) >= 150:
                        print('analyzing event')
                        feat_arr = np.array(vs)
                        vs.clear()
                        img_data = [feat_arr]
                        #Probability values for Abnormality and Non-Abnormality
                        model1_result = model1_context.run({ 'input_image': img_data},
                                { 'dense_2/Softmax:0': InferContext.ResultFormat.RAW })
                        
                    
                        ab_prob, normal_prob  = model1_result['dense_2/Softmax:0'][0][0], model1_result['dense_2/Softmax:0'][0][1] 
                    
                        #crime type classification
                        model2_result = model2_context.run({ 'input_image': img_data}, 
                                {'dense_2/Softmax:0': InferContext.ResultFormat.RAW })
                        

                        max_index = np.argmax(model2_result['dense_2/Softmax:0'][0])
                        crime_type = name_id_map[max_index]
                        crime_prob = model2_result['dense_2/Softmax:0'][0][max_index]
                        confidence = round(((ab_prob+crime_prob)/2), 2) #Mean of Abnormality probability and crime_type probability 

                        print(
                        "---------------------------------------------------------------------------")
                        print("Abnormal Probability: " + str(ab_prob) + "\n")
                        print("Normal Probability: " + str(normal_prob) + "\n") 
                        print("Crime classification: " + str(crime_type) +
                        " Probability: " + str(crime_prob))
                        print(
                        "--------------------------------------------------------------------------- \n\n\n")

                        if (ab_prob >= 0.70 and crime_prob >= 0.50) and shouldAlert:
                            print("should verify event")
                            #save array of images as mp4
                            time_started = datetime.datetime.now()
                            height, width, channel = images[0].shape
                            videoName = str(crime_type) + time_started.strftime('%H-%M-%S') + '.mp4'
                            fourcc = cv2.VideoWriter_fourcc(*'avc1')
                            out = cv2.VideoWriter('event_videos/' + videoName, fourcc, 10, (width, height))

                            for i in range(len(images)):
                                out.write(images[i])
                            out.release()
                            #os.system("ffmpeg -y -i event_videos/" + videoName +  " -vcodec libx264 event_videos/" + videoName)
                            
                            vidBlob = bucket.blob(self.uid + '/' + videoName)
                            vidBlob.upload_from_filename(os.getcwd() + '/event_videos/' + videoName)
                            # generate url that expires after 15 minutes
                            temp_url = vidBlob.generate_signed_url(
                                expiration=datetime.timedelta(minutes=15),
                                method='GET'
                            )

                            event = {
                                'uid': self.uid,
                                'camera_name': self.name,
                                'crime_name': crime_type,
                                'location': self.location,
                                'time_started': datetime.datetime.now(),
                                'stream-url': self.url,
                                'event-url': videoName,
                                'confidence': confidence
                            }

                            #verify event with noonlight
                            noonlight.verifyEvent(event, 600, temp_url)

                            shouldAlert = False

                        else:
                            print("Normal")

                            if not shouldAlert:
                                normal_event_counter += 1
                                if normal_event_counter >= 250:
                                    normal_event_counter = 0
                                    shouldAlert = True

                        images.clear()
