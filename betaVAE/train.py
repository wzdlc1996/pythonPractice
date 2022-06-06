from itertools import chain
from impts import *

from model import Encoder, Decoder
from hyperParam import gpu, beta_adam, beta_vae, num_epoch, lr, nz
from datald import Dataloader


img_list = []
loss_list = []
ind = 0
ind_slc = 500
sav_slc = 500

device = torch.device("cuda:0" if gpu and torch.cuda.is_available() else "cpu")
enc = Encoder().to(device)
dec = Decoder().to(device)

mse = nn.MSELoss()
optimizer = optim.Adam(
    params=chain(
        enc.parameters(),
        dec.parameters()
    ),
    lr=lr,
    betas=beta_adam
)

fix_noise = torch.randn(64, nz, 1, 1, device=device)

print("Starting Training Loop...")

for epoch in range(num_epoch):
    for i, data in enumerate(Dataloader):
        enc.zero_grad()
        dec.zero_grad()

        x = data[0].to(device)
        mu, sigma = enc(x)

        assert mu.size() == sigma.size()
        epsilon = torch.randn(mu.size(), device=device)

        z = mu + sigma * epsilon
        z = z.view(-1, nz, 1, 1)
        res = dec(z)

        zero = torch.zeros(mu.size(), device=device)
        ones = torch.ones(sigma.size(), device=device)

        loss = mse(res, x) + beta_vae * (mse(zero, mu) + mse(ones, sigma))
        loss.backward()
        lossv = loss.mean().item()
        optimizer.step()

        if ind % ind_slc == 0:
            print(
                f"[{epoch}/{num_epoch}][{i}/{len(Dataloader)}]:\t"
                f"Loss=%.3f" % lossv
            )

        if ind % sav_slc == 0 or ((epoch == num_epoch-1) and ind==len(Dataloader)-1):
            with torch.no_grad():
                fake = dec(fix_noise).detach().cpu()

            img_list.append(vutils.make_grid(fake, padding=2, normalize=True))

            plt.figure(figsize=(8, 8))
            plt.axis("off")
            plt.title("Fake Images")
            plt.imshow(np.transpose(img_list[-1], (1, 2, 0)))
            plt.savefig(f"./data_gen/fake_{epoch}_{ind}.pdf")
            plt.close()

        ind += 1

# Plot the fake images from the last epoch
plt.figure(figsize=(8, 8))
plt.axis("off")
plt.title("Fake Images")
plt.imshow(np.transpose(img_list[-1],(1,2,0)))
plt.savefig("./imgs_fake.pdf")
