"""
The definitions of super parameters
"""

#  Manual random-seed
seed = 999

#  Dataset root path
dataroot = "./dataset"


#  Spatial size of training images, all images would be resized as this
image_size = 64  # dont change


#  Number of the workers of dataloader
n_worker = 2


#  Batch size during training
batch_size = 128


#  Number of channels of the output image (3 for RGB images)
nc = 3


#  The input size of generator
nz = 100


#  The channel size of decoder and encoder
ngf = 64  # for decoder(generator)
ndf = 64  # for encoder


#  Use GPU to train or not:
gpu = True


#  Learning Rate
lr = 2e-4


#  Adam beta:
beta_adam = (0.5, 0.999)
beta_vae = 1.1


#  Number of epochs
num_epoch = 10