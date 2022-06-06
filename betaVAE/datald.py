"""
Is the dataloader for Celeb-A Faces dataset
"""
from impts import *

dataset = dset.ImageFolder(
    root=hyperParam.dataroot,
    transform=transforms.Compose([
        transforms.Resize(hyperParam.image_size),
        transforms.CenterCrop(hyperParam.image_size),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
)

Dataloader = torch.utils.data.DataLoader(
    dataset,
    batch_size=hyperParam.batch_size,
    shuffle=True,
    num_workers=hyperParam.n_worker
)
