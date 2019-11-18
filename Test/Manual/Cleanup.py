import os

def enumerate_directory(filter):
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    matched_files = [f for f in files if filter(f)]
    return matched_files

def clean_images():
    #clean jpg files
    files = enumerate_directory(lambda x : '.jpg' in x)
    for file in files:
        os.remove(file)

def clean_datastore():
    #clean json files for datastore
    files = enumerate_directory(lambda x: '.json' in x)
    for file in files:
        os.remove(file)

#clean images
clean_images()
#clean datastore
clean_datastore()