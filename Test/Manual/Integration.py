import requests
import base64
import os
import json
from datetime import datetime

default_format = '%Y-%m-%d %H:%M:%S'
#refactor these later into a command prompt
run_style_transfer = False
run_deep_dream = True

#Status response data object
class Status_Response:
  def __init__(self, start_date, end_date, id, status):
    self.start_date = start_date
    self.end_date = end_date
    self.id = id
    self.status = status

def make_version_call():
    url = 'http://localhost:5000/version'
    response = requests.get(url)
    return response

def make_device_call():
    url = 'http://localhost:5000/device'
    response = requests.get(url)
    return response

def make_statuses_call(job_id, auth_token = None):
    url = f'http://localhost:5000/job?id={job_id}'
    response = requests.get(url, headers={'Authorization': f'Bearer {auth_token}'})
    return response

def strip_datetime_fraction(time_string):
  return time_string.split('.')[0]

def format_statuses_response(text):
  statuses_array = json.loads(text)
  statuses = []
  for response in statuses_array:
    start = response['create_date']
    end = response['end_date']
    #format dates
    start_date = datetime.strptime(strip_datetime_fraction(start), default_format) if start != '' else datetime.now()
    end_date = datetime.strptime(strip_datetime_fraction(end), default_format) if end != '' else datetime.now()
    #get id
    id = response['id']
    #get statuses
    status = response['status']
    statuses.append(Status_Response(start_date, end_date, id, status))
  return statuses

def print_statuses_response(statuses):
  for status in statuses:
    print(status.start_date)
    print(status.end_date)
    print(status.id)
    print(status.status)
    print(f'total calltime: {status.end_date - status.start_date}')

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError:
    return False
  return True

def validate_input_files(files):
  print('Validating files for integration script')
  wd = os.getcwd()
  for file in files:
    filePath = os.path.join(wd, file)
    print(filePath)
    if not os.path.exists(filePath):
      raise Exception(f'Input file does not exist: {filePath}')
  print('Paths validated')

def queue_style_job(content_path, style_path, auth_token = None):
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
    data = f'{{"Job_Type" : {job_type},"Source_Image" : "{content}","Target_Image" : "{style}","ImCrop" : {imcrop}}}'
    is_valid_json = is_json(data)
    print(f'data is json: {is_valid_json}')
    print(f'posting data to {url} to queue job')
    response = requests.post(url, data=data, headers={'Authorization': f'Bearer {auth_token}'})
    #returns job id and image
    return response
def queue_deep_dream_job(content_path, auth_token = None):
    # Neural_Transfer = 1
    # GAN = 2
    # Deep_Dream = 3
    # {Type : Job_Type, Source_Image: Base64Image, Target_Image : Base64Image, ImCrop : CropSize}
    # Source Image is content
    url = 'http://localhost:5000/job'
    # get content image
    with open(content_path, "rb") as image:
        f = image.read()
        b = bytearray(f)
        content = base64.encodebytes(b)
    job_type = 3
    imcrop = 500
    data = f'{{"Job_Type" : {job_type},"Source_Image" : "{content}","ImCrop" : {imcrop}}}'
    is_valid_json = is_json(data)
    print(f'data is json: {is_valid_json}')
    print(f'posting data to {url} to queue job')
    response = requests.post(url, data=data, headers={'Authorization': f'Bearer {auth_token}'})
    #returns job id and image
    return response


def create_user(auth_token = None, admin = True):
  url = 'http://localhost:5000/adminuser' if admin else 'http://localhost:5000/user'
  first = 'David'
  last = 'Dworetzky'
  name = 'Ddworetzky' if admin else 'Dworetzky'
  email = 'fake@email.com'
  password = 'fakepassword'
  data = f'{{"First": "{first}", "Last": "{last}", "Name": "{name}", "Email" : "{email}", "Password" : "{password}"}}'
  is_valid_json = is_json(data)
  print(f'data is json: {is_valid_json}')
  print(f'posting data to {url} to create user')
  response = requests.post(url, data=data, headers={'Authorization': f'Bearer {auth_token}'})
  #returns user object
  return response
def login():
  url = "http://localhost:5000/login"
  name = 'Ddworetzky'
  password = 'fakepassword'
  data = f'{{"Name" : "{name}", "Password": "{password}"}}'
  is_valid_json = is_json(data)
  print(f'data is json: {is_valid_json}')
  print(f'posting data to {url} to login')
  response = requests.post(url, data=data)
  #returns login response
  return response
  

def get_users(user_id, auth_token = None):
  url = f'http://localhost:5000/user?id={user_id}'
  response = requests.get(url, headers={'Authorization': f'Bearer {auth_token}'})
  return response

#validations of script pre-reqs
validate_input_files(["data\\guitarist.jpg", "data\\singingbutler.jpg"])
#version call
print('Making version call')
version = make_version_call()
print(f'api version is : {version.text}')
print(f'status code of response is: {version.status_code}')

#device call
print('Making device call')
device = make_device_call()
print(f'device status is : {device.text}')
print(f'device code of response is: {device.status_code}')

auth_token = None
#users

print('Making create users call - admin')
user_output = create_user(auth_token=auth_token, admin=True)
print(f'status code of response is: {user_output.status_code} ')
print('user is:')
print(user_output.text)

#login

print('Making call to login')
login_output = login()
print(f'status code of response is: {login_output.status_code} ')
print('output object is:')
print(login_output.text)

#get auth token
auth_token = json.loads(login_output.text)['access_token']
print('Auth token is:')
print(auth_token)

print('Making create users call')
user_output = create_user(auth_token=auth_token, admin=False)
print(f'status code of response is: {user_output.status_code} ')
print('user is:')
print(user_output.text)

#now get users

print('Getting users')
users_output = get_users(-1, auth_token= auth_token)
print(f'users code of response is: {users_output.status_code}')
print('users are:')
print(users_output.text)

#now queue jobs 
if run_style_transfer:
  wd = os.getcwd()
  guitarist =  os.path.join(wd, "data\\guitarist.jpg")
  singing_butler = os.path.join(wd, "data\\singingbutler.jpg")
  print('Queueing image job')
  output = queue_style_job(guitarist, singing_butler, auth_token= auth_token)
  print(f'status code of response is: {output.status_code}')
  print('output content')
  print(output.text)

#now queue deep dream job
if run_deep_dream:
  wd = os.getcwd()
  guitarist = os.path.join(wd, "data\\guitarist.jpg")
  print('Queueing deep dream job')
  output = queue_deep_dream_job(guitarist, auth_token = auth_token)
  print(f'status code of response is: {output.status_code}')
  print('output content')
  print(output.text)

print('Making statuses call')
statuses = -1
statuses_output = make_statuses_call(statuses, auth_token= auth_token)
print(f'status code of response is: {statuses_output.status_code} ')
print('statuses are:')
print(statuses_output.text)
statuses = format_statuses_response(statuses_output.text)
print_statuses_response(statuses)







