import torch
from torchvision import models, transforms
import numpy as np
from PIL import Image, ImageFilter, ImageChops
import uuid
from io import BytesIO
import base64

#Helper functions for image processing -> loading
#TODO refactor this for various image processing deep learning processes into one class
def image_loader(image_data, loader, device, debug=True):
    decoded = base64.b64decode(image_data)
    #create temp file for processing
    temp_name = str(uuid.uuid4())
    #if debug flag, write out image to directory
    if(debug):
        with open(f"{temp_name}.jpg", 'wb') as f:
            f.write(decoded)
    b = BytesIO(decoded)
    b.seek(0)
    image = Image.open(b)
    # fake batch dimension required to fit network's input dimensions
    image = loader(image).unsqueeze(0)
    return image.to(device, torch.float)

class Deep_Dream:
    def __init__(self, image_size, content_image, num_iterations = 5, num_downscales = 20, blend_alpha = 0.6, lr = 0.2, layer= 28, debug=True):
        self.debug = debug
        self.image_size = image_size
        self.content_image = content_image
        #number of iterations to update the content image through the layer's gradient
        self.num_iterations = num_iterations
        self.num_downscales = num_downscales
        self.blend_alpha = blend_alpha
        self.lr = lr
        #layer through which we maximize activations
        self.layer = layer
        #Cuda device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = models.vgg16(pretrained = True)
        #if cuda is available
        if torch.cuda.is_available():
            model = model.cuda()
        # vgg16 uses 224 as the image dimension
        imSize = 224
        transformMean = [0.485, 0.456, 0.406]
        transformStd = [0.229, 0.224, 0.225]
        #define normalization transforms for image processing of deep dream images
        transformNormalize = transforms.Normalize(mean = transformMean, std = transformStd)
        self.transformPreprocess = transforms.Compose([transforms.Resize((imSize, imSize)), transforms.ToTensor(), transformNormalize])
        self.tensorMean = torch.Tensor(transformMean)
        if torch.cuda.is_available():
            self.tensorMean = self.tensorMean.cuda()
        self.tensorStd = torch.Tensor(transformStd)
        if torch.cuda.is_available():
            self.tensorStd = self.tensorStd.cuda()
        #make modules available from vgg16 model
        self.modules = list(self.model.features.modules())
    def Convert_To_Image(self, input):
        return input * self.tensorStd + self.tensorMean
    #runs the deep dream image transform on our input content_image
    def deep_dream(self, image, num_steps, layer):
        transform_image = self.transformPreprocess(image).unsqueeze(0)
        if torch.cuda.is_available():
            transform_image = transform_image.cuda()
        input = torch.autograd.Variable(transform_image, requires_grad=True)
        #zero grad on VGG16 model
        self.model.zero_grad()
        for i in range(num_steps):
            output = input
            for layer_id in range(layer):
                output = self.modules[layer_id + 1](output)
            loss = output.norm()
            loss.backward()
            #adjust input data depending on learning rate
            input.data = input.data + self.lr * input.grad.data
        input = input.data.squeeze()
        input.transpose_(0,1)
        input.transpose_(1,2)
        input = np.clip(self.Convert_To_Image(input), 0, 1)
        return Image.fromarray(np.uint8(input * 255))
        #common alias for image job processor
    def deep_dream_recursive(self, image, num_steps, layer, num_downscales):
        if num_downscales > 0:
            #scale down the image
            image_small = image.filter(ImageFilter.GaussianBlur(2))
            small_size = (int(image.size[0]/2), int(image.size[1]/2))
            if (small_size[0] == 0 or small_size[1] == 0):
                small_size = image.size
            image_small = image_small.resize(small_size, Image.ANTIALIAS)

            # run deep dream on the downscaled image
            image_small = self.deep_dream_recursive(image, num_steps, layer, num_downscales - 1)

            #scale the image back
            image_large = image_small.resize(image.size, Image.ANTIALIAS)

            # Blend the images
            image = ImageChops.blend(image, image_large, self.blend_alpha)
        image_result = self.deep_dream(image, num_steps, layer)
        image_result = image_result.resize(image.size)
        return image_result
    def run_job(self, num_steps):
        #load image with loader helper
        loaded_image = image_loader(self.content_image, self.loader, self.device)
        return self.deep_dream_recursive(self.content_image, self.num_iterations, self.layer, self.num_downscales)


        

    