import requests
import base64

def make_version_call():
    url = 'http://localhost/version'
    response = requests.get(url)
    return response

def queue_job(content_path, style_path):
    # Neural_Transfer = 1
    # GAN = 2
    # {Type : Job_Type, Source_Image: Base64Image, Target_Image : Base64Image, ImCrop : CropSize}
    # Source Image is content
    # Target Image is style
    url = 'http://localhost/job'
    # get content image
    with open(content_path, "rb") as image:
        f = image.read()
        b = bytearray(f)
        content = base64.decodebytes(b)
    # now get style image
    with open(style_path, "rb") as image:
        f = image.read()
        b = bytearray(f)
        style = base64.decodebytes(b)
    job_type = 1
    imcrop = 500
    data = '''{
            "Job_Type" : {job_type},
            "Source_Image" : {style},
            "Target_Image" : {content},
            "ImCrop" : {imcrop}
        }'''
    response = requests.post(url, data=data)
    #returns job id and image
    return response

queue_job("data/guitarist.jpg", "data/singingbutler.jpg")