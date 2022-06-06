"""
Is the script to illustrate the dataset
"""
from impts import *
from datald import Dataloader

if __name__ == "__main__":
    device = torch.device("cpu")
    real_batch = next(iter(Dataloader))

    plt.figure(figsize=(8, 8))
    plt.axis("off")
    plt.title("Training Images")
    plt.imshow(np.transpose(
        vutils.make_grid(real_batch[0][:64], padding=2, normalize=True),
        (1, 2, 0)
    ))
    plt.savefig("./imgs_real.pdf")

