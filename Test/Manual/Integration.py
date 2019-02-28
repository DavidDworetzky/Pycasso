import requests
import base64
import os
import json

def make_version_call():
    url = 'http://localhost:5000/version'
    response = requests.get(url)
    return response

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError:
    return False
  return True

def queue_job(content_path, style_path):
    # Neural_Transfer = 1
    # GAN = 2
    # {Type : Job_Type, Source_Image: Base64Image, Target_Image : Base64Image, ImCrop : CropSize}
    # Source Image is content
    # Target Image is style
    url = 'http://localhost:5000/job'
    # get content image
    with open(content_path, "rb") as image:
        f = image.read()
        b = bytearray(f)
        content = base64.encodebytes(b)
    # now get style image
    with open(style_path, "rb") as image:
        f = image.read()
        b = bytearray(f)
        style = base64.encodebytes(b)
    job_type = 1
    imcrop = 500
    data = f'{{"Job_Type" : {job_type},"Source_Image" : "{style}","Target_Image" : "{content}","ImCrop" : {imcrop}}}'
    is_valid_json = is_json(data)
    print(f'data is json: {is_valid_json}')
    print(f'posting data to {url} to queue job')
    response = requests.post(url, data=data)
    #returns job id and image
    return response

print('Making version call')
version = make_version_call()
print(f'api version is : {version.text}')
print(f'status code of response is: {version.status_code}')

wd = os.getcwd()
guitarist =  os.path.join(wd, "data\\guitarist.jpg")
singing_butler = os.path.join(wd, "data\\singingbutler.jpg")
print('Queueing image job')
output = queue_job(guitarist, singing_butler)
print(f'status code of response is: {output.status_code}')