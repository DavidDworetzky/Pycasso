# Pycasso
Deep learning server for generating art.


# Getting Started 
Pycasso has a number of image samples that can be used to test the art generation server locally. 
To get started, do the following:
1. Install dependencies
2. Run Pycasso.py
3. Run Integration.py in Test/Manual

## Samples
Integration.py will take some sample images already helpfully included in the folder and run Neural_Transfer on them. 
If you wish to replace your own images, simply add images to the Data folder and change out the queue_job call with your own images.


## Dependencies
1. pip install flask
2. pip install flask-RESTful
3. pip install tinydb
4. pip3 install https://download.pytorch.org/whl/cu100/torch-1.0.1-cp37-cp37m-win_amd64.whl (or whichever .whl is appropriate for your processor)
5. pip3 install torchvision
6. pip install flask_jwt_extended
7. pip install requests

## Roadmap
View Projects, task list for current product roadmap. Next content features will probably include GANs for generating faces, character models, 3d models, as well as text generation with gpt2.
