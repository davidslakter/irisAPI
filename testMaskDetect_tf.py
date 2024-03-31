from tensorrtserver.api import *
import cv2
import numpy as np
import base64
import io
import json
import requests
import ctypes
# import tensorflow as tf

cap = cv2.VideoCapture("rtsp://admin:xIris345@71.71.59.130/videoMain")

if not cap.isOpened():
    print('camera open failure')
    exit(1)

ret, frame = cap.read()
if not ret:
    print('no frame retrieved')
    exit(1)

# encoded_image = base64.b64encode(frame).decode('utf-8')

_, arr = cv2.imencode('.jpg', frame)
# inp = np.array(arr, dtype=np.dtype('b'))
# bytes = arr.tobytes()

# context = InferContext('localhost:8001', ProtocolType.GRPC, 'mask_detector', 1)
# result = context.run({'image_bytes': [bytearray(arr) ]}, {'detection_classes_as_text': InferContext.ResultFormat.RAW }, batch_size=1)

with tf.Session(graph=tf.Graph()) as sess:
    tf.saved_model.loader.load(sess, [tf.saved_model.tag_constants.SERVING], 'saved_models/mask_detector/1/model.savedmodel')

    scores, boxes = sess.run(["detection_scores:0", "detection_boxes:0"], feed_dict={"encoded_image_string_tensor:0":[arr.tostring()]}) 

    print(f"Scores : {scores}")
