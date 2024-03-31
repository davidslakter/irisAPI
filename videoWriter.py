import cv2
from google.cloud import storage

#storage_client = storage.Client.from_service_account_json('iris-service-account-key.json')
#bucket = storage_client.get_bucket('iris-event-images')

def main():
    cap = cv2.VideoCapture("rtsp://admin:xIris345@192.168.1.13/videoMain")
    images = []
    done = False
    while not done:
        ret, image = cap.read()
        if ret:
            try:
                images.append(image)

                if (len(images) == 150):

                    height, width, channel = images[0].shape
                    print(height, width)
                    out = cv2.VideoWriter('sampleVideo.mp4', cv2.VideoWriter_fourcc(*'H264'), 15, (width, height))

                    for i in range(150):
                        out.write(images[i])
                    out.release()

                   #vidBlob = bucket.blob('sampleVideo.mp4')
                    #vidBlob.upload_from_filename(os.getcwd() + '/sampleVideo.mp4')
                    print('done')
                    done = True
            except:
                continue


if __name__ == '__main__':
    main() 