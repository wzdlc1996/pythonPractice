from impts import *
from hyperParam import nc, nz, ngf, ndf


def weight_ini(m):
    classname = m.__class__.__name__
    if classname.find("Conv") != -1:
        nn.init.normal_(m.weight.data, 0., 0.02)
    elif classname.find("BatchNorm") != -1:
        nn.init.normal_(m.weight.data, 1., 0.02)
        nn.init.constant_(m.bias.data, 0)


class Decoder(nn.Module):
    def __init__(self):
        super().__init__()

        self.main = nn.Sequential(
            # Input channel: nz. Output channel: ngf * 8
            # In practice: input: [n_data, nz, 1, 1], output: [n_data, ngf*8, 4, 4]
            nn.ConvTranspose2d(nz, ngf * 8, 4, bias=False),
            nn.BatchNorm2d(ngf * 8),
            nn.ReLU(True),
            # In practice: input: [n_data, ngf*8, 4, 4], output: [n_data, ngf*4, 8, 8]
            nn.ConvTranspose2d(ngf * 8, ngf * 4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ngf * 4),
            nn.ReLU(True),
            # In practice: input: [n_data, ngf*4, 8, 8], output: [n_data, ngf*2, 16, 16]
            nn.ConvTranspose2d(ngf * 4, ngf * 2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ngf * 2),
            nn.ReLU(True),
            # In practice: input: [n_data, ngf*2, 16, 16], output: [n_data, ngf, 32, 32]
            nn.ConvTranspose2d(ngf * 2, ngf, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ngf),
            nn.ReLU(True),
            # In practice: input: [n_data, ngf, 32, 32], output: [n_data, nc, 64, 64]
            nn.ConvTranspose2d(ngf, nc, 4, 2, 1, bias=False),
            nn.Tanh()
        )
        self.apply(weight_ini)

    def forward(self, x):
        return self.main(x)


class Encoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.main = nn.Sequential(
            nn.Conv2d(nc, ndf, 4, 2, 1, bias=False),
            nn.LeakyReLU(0.2, inplace=True),
            #
            nn.Conv2d(ndf, ndf * 2, 4, 2, 1, bias=False),
            nn.LeakyReLU(0.2, inplace=True),
            #
            nn.Conv2d(ndf*2, ndf*4, 4, 2, 1, bias=False),
            nn.LeakyReLU(0.2, inplace=True),
            #
            nn.Conv2d(ndf*4, ndf*8, 4, 2, 1, bias=False),
            nn.LeakyReLU(0.2, inplace=True),
            #
            nn.Conv2d(ndf*8, nz, 4, 2, 0, bias=False),
            nn.LeakyReLU(0.2, inplace=True)
        )
        self.lin_mu = nn.Linear(nz, nz)
        self.lin_sig = nn.Linear(nz, nz)
        self.apply(weight_ini)

    def forward(self, x):
        z = self.main(x)
        sq_z = z.view(-1, nz)
        mu, sigma = self.lin_mu(sq_z), self.lin_sig(sq_z)
        return nn.Tanh()(mu), nn.Tanh()(sigma) + 1


if __name__ == "__main__":
    from datald import Dataloader

    r = next(iter(Dataloader))
    x: torch.Tensor = r[0]
    print(x.size())

    enc = Encoder()
    mu, sig = enc(x)

    print(mu.size())
    print(sig.size())
    print(mu)
    print(sig)
