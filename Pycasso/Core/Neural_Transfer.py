import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from PIL import Image
import matplotlib.pyplot as plt

import torchvision.transforms as transforms
import torchvision.models as models
from io import BytesIO
import base64

import copy

#Helper functions for image processing
def image_loader(image_data):
    data['image'] = image_data
    image = Image.open(BytesIO(base64.b64decode(data)))
    # fake batch dimension required to fit network's input dimensions
    image = loader(image).unsqueeze(0)
    return image.to(device, torch.float)
#Get Optimizer for Neural Network
def get_input_optimizer(input_img):
    # this line to show that input is a parameter that requires a gradient
    optimizer = optim.LBFGS([input_img.requires_grad_()])
    return optimizer

#Core of Neural Transfer in python

#Gram Matrix, Content Loss, Style Loss
class ContentLoss(nn.Module):
    def __init__(self, target,):
        super(ContentLoss, self).__init__()
        self.target = target.detach()
    def forward(self, input):
        self.loss = F.mse_loss(input, self.target)
        return input
def gram_matrix(input):
    a, b, c, d = input.size()  # a=batch size(=1)
    # b=number of feature maps
    # (c,d)=dimensions of a f. map (N=c*d)
    features = input.view(a * b, c * d)  # resise F_XL into \hat F_XL
    G = torch.mm(features, features.t())  # compute the gram product
    #return normalized gram matrix
    return G.div(a * b * c * d)

def run_style_transfer(cnn, normalization_mean, normalization_std,
                       content_img, style_img, input_img, num_steps=300,
                       style_weight=1000000, content_weight=1):
    """Run the style transfer."""
    #Building the style transfer model
    model, style_losses, content_losses = get_style_model_and_losses(cnn,
        normalization_mean, normalization_std, style_img, content_img)
    optimizer = get_input_optimizer(input_img)

    #Optimizing
    run = [0]
    while run[0] <= num_steps:

        def closure():
            # correct the values of updated input image
            input_img.data.clamp_(0, 1)

            optimizer.zero_grad()
            model(input_img)
            style_score = 0
            content_score = 0

            for sl in style_losses:
                style_score += sl.loss
            for cl in content_losses:
                content_score += cl.loss

            style_score *= style_weight
            content_score *= content_weight

            loss = style_score + content_score
            loss.backward()

            run[0] += 1
            return style_score + content_score
        optimizer.step(closure)

    # a last correction...
    input_img.data.clamp_(0, 1)

    return input_img

class StyleLoss(nn.Module):
    def __init__(self, target_feature):
        super(StyleLoss, self).__init__()
        self.target = gram_matrix(target_feature).detach()

    def forward(self, input):
        G = gram_matrix(input)
        self.loss = F.mse_loss(G, self.target)
        return input

# create a module to normalize input image so we can easily put it in a
# nn.Sequential
class Normalization(nn.Module):
    def __init__(self, mean, std):
        super(Normalization, self).__init__()
        # .view the mean and std to make them [C x 1 x 1] so that they can
        # directly work with image Tensor of shape [B x C x H x W].
        # B is batch size. C is number of channels. H is height and W is width.
        self.mean = torch.tensor(mean).view(-1, 1, 1)
        self.std = torch.tensor(std).view(-1, 1, 1)

    def forward(self, img):
        # normalize img
        return (img - self.mean) / self.std

class Neural_Transfer:
    def __init__(self, image_size, content_image, style_image):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.image_size = image_size
        # scale imported image and transform it into a torch tensor
        self.loader transforms.Compose([transforms.Resize((self.image_size, self.image_size)),  transforms.ToTensor()])
        #initialize style and content image 
        self.style_image = image_loader(style_image)
        self.content_image = image_loader(content_image)
        self.cnn_normalization_mean = torch.tensor([0.485, 0.456, 0.406]).to(device)
        self.cnn_normalization_std = torch.tensor([0.229, 0.224, 0.225]).to(device)
        self.cnn = models.vgg19(pretrained=True).features.to(device).eval()
        
    def run_transfer(self, num_steps):
        output = run_style_transfer(self.cnn, self.cnn_normalization_mean, self.normalization_std, num_steps = num_steps)
        return output