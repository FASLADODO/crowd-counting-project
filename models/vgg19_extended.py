import torch
import torch.nn as nn
import torch.utils.model_zoo as model_zoo
import torch.nn.functional as F

from utils.models import make_layers


_all_ = ['vgg19']
model_urls = {
    'vgg19': 'https://download.pytorch.org/models/vgg19-dcbb9e9d.pth',
}

class VGGExtended(nn.Module):
    def __init__(self, features):
        super(VGGExtended, self).__init__()
        self.features = features
        self.reg_layer = nn.Sequential(
            nn.Conv2d(512, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
        )
        self.pred_layer = nn.Conv2d(128, 1, 1)
        self.conv_logvar = nn.Conv2d(128, 1, 1)


    def forward(self, x, aleatoric=False):
        x = self.features(x)
        x = F.upsample_bilinear(x, scale_factor=2)
        x = self.reg_layer(x)
        pred = torch.abs(self.pred_layer(x))
        if aleatoric:
            logvar = F.softplus(self.conv_logvar(x))
            return pred, logvar
        return pred


cfg = {
    'E': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 256, 'M', 512, 512, 512, 512, 'M', 512, 512, 512, 512]
}

def vgg19(aleatoric=False):
    """VGG 19-layer model (configuration "E")
        model pre-trained on ImageNet
    """
    model = VGGExtended(make_layers(cfg['E']))
    model.load_state_dict(model_zoo.load_url(model_urls['vgg19']), strict=False)
    return model
