# iris_API

***folder on the VM is located at /home/iris_API



## Starting the Triton Inference server (docker container)

```
nvidia-docker run --rm --shm-size=1g --ulimit memlock=-1 --ulimit stack=67108864 -p8000:8000 -p8001:8001 -p8002:8002 -v/home/iris_API/api/saved_models/:/models nvcr.io/nvidia/tritonserver:20.03-py3 trtserver --model-repository=/models --strict-model-config=false

```
if using K80 gpu add:
``
--min-supported-compute-capability=3.5
``

## start the API for Development

Start the development docker container 

```
docker run -it --rm --mount type=bind,source=/home/iris_API,target=/app --network=host davidcslakter/iris_container
```

go into app directory
``
cd ../app/api/iris
``
 and start flask development server with
``
python3 index.py
``


## start the API for Deployment

With the triton server running, run the docker-compose configuration 

```
docker-compose up --build
```

## add and remove cameras to iris

sample curl **POST** request to add iris to a camera:
```
curl --header "Authorization: sOdsw212" --data "uid=5g1AOVd5aEX0kvOyhfvw1ez57CF2&camera_name=test_cam&stream_type=h264&connection_type=direct&stream_url=rtsp://admin:xIris345@71.71.59.30/videoMain&camera_location=front_entrance" https://cameras.xiris.ai:8443/cameras/

```
if succeeded, the request will return a ID to identify the camera under the user and the streamURL for the camera

sample curl **DELETE** request to remove a camera of id **123456**:

```
curl -X "DELETE" --header "Authorization: sOdsw212" --data "uid=5g1AOVd5aEX0kvOyhfvw1ez57CF2" https://cameras.xiris.ai:8443/cameras/123456/
```

if the request suceeded the response will be 204 containing no content

## Get status of the server
```
curl https://cameras.xiris.ai:8443/status/
```
The response will include the gpu usage of the server as well as the number of cameras being run currently on the server
