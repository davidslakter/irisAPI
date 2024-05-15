from flask import Blueprint, request
import requests
import json


angel_proxy = Blueprint('angel_proxy', __name__)


@angel_proxy.route('/clients/', methods=['POST'])
def add_angel_client_account():
    form_data = { "client_id": "Bft8PAC2j4QQnUEn5VlmQygU4AqyWhmeQRC9Ra8g", "scope": "client_create", "grant_type":"password", "username": "david@xiris.ai", "password": "Inventor571"}
    res = requests.post('https://my.angelcam.com/oauth/token/', data=form_data).json()
    parent_access_token = res['access_token']
    print(request.form)
    return requests.post('https://api.angelcam.com/v1/clients/', headers={'Authorization': 'Bearer ' + parent_access_token}, data=request.form).content, 201

@angel_proxy.route('/oauth/token/', methods=['POST'])
def get_access_token():
    request['client_id'] = 'Bft8PAC2j4QQnUEn5VlmQygU4AqyWhmeQRC9Ra8g'
    scopes = ['camera_access', 'camera_create', 'camera_delete', 'arrow_client_access', 'arrow_client_manage', 'streams_detect']
    request['scope'] = ' '.join(scopes)
    return requests.post('https://my.angelcam.com/oauth/token/', data=request.json).content

@angel_proxy.route('/cameras/<cam_id>/', methods=['GET'])
def get_camera_details(cam_id):
    return requests.get('https://api.angelcam.com/v1/cameras/' + cam_id + '/', 
    headers={'Authorization': 'PersonalAccessToken ---'}).content

@angel_proxy.route('/stream-detection/', methods=['POST']) 
def start_stream_detection():
    print(request.data)
    return requests.post('https://api.angelcam.com/v1/cameras/stream-detection/', 
            headers={'Authorization': 'PersonalAccessToken ---', 'Content-Type': 'application/json'}, data=request.data).content

@angel_proxy.route('/stream-detection/<session_id>/', methods=['GET'])
def get_detection_result(session_id):
    return requests.get('https://api.angelcam.com/v1/cameras/stream-detection/' + session_id + '/', 
          headers={'Authorization': 'PersonalAccessToken ---'}).content

@angel_proxy.route('/arrow-clients/', methods=['POST'])
def add_arrow_client():
    return requests.post('https://api.angelcam.com/v1/arrow-clients/', 
          headers={'Authorization': 'PersonalAccessToken ---'}, data=request.json).content


@angel_proxy.route('/arrow-clients/<uuid>/', methods=['GET'])
def get_arrow_client_detail(uuid):
    return requests.get('https://api.angelcam.com/v1/arrow-clients/' + uuid + '/', 
          headers={'Authorization': 'PersonalAccessToken ---'}).content

@angel_proxy.route('/arrow-clients/<uuid>/scan-network/', methods=['POST'])
def scan_arrow_network(uuid):
    return requests.get('https://api.angelcam.com/v1/arrow-clients/' + uuid + '/scan-network', 
        headers={'Authorization': 'PersonalAccessToken ---'}, data=request.json).content


@angel_proxy.route('/arrow-clients/<uuid>/services/', methods=['GET'])
def get_arrow_services(uuid):
      return requests.get('https://api.angelcam.com/v1/arrow-clients/' + uuid + '/services', 
          headers={'Authorization': 'PersonalAccessToken ---'}).content


@angel_proxy.route('/ipv4/', methods=['GET'])
def get_public_ip():
    return request.remote_addr, 200

