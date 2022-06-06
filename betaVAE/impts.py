from __future__ import print_function
import argparse
import os
import random
import hyperParam

import torch
import torch.nn as nn
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.optim as optim
import torch.utils.data

import torchvision.datasets as dset
import torchvision.transforms as transforms
import torchvision.utils as vutils

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# from IPython.display import HTML


#  Initiate the rng by manual seed
random.seed(hyperParam.seed)
torch.manual_seed(hyperParam.seed)