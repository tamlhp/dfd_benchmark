from pytorchcv.model_provider import get_model
import torch.nn as nn
import torch


class Pooling(nn.Module):
    def __init__(self):
        super(Pooling, self).__init__()

        self.p1 = nn.AdaptiveAvgPool2d((1,1))
        self.p2 = nn.AdaptiveMaxPool2d((1,1))

    def forward(self, x):
        x1 = self.p1(x)
        x2 = self.p2(x)
        return (x1+x2) * 0.5


class Head(torch.nn.Module):
    def __init__(self, in_f, out_f):
        super(Head, self).__init__()

        self.f = nn.Flatten()
        self.l = nn.Linear(in_f, 512)
        self.d = nn.Dropout(0.5)
        self.o = nn.Linear(512, out_f)
        self.b1 = nn.BatchNorm1d(in_f)
        self.b2 = nn.BatchNorm1d(512)
        self.r = nn.ReLU()

    def forward(self, x):
        x = self.f(x)
        x = self.b1(x)
        x = self.d(x)

        x = self.l(x)
        x = self.r(x)
        x = self.b2(x)
        x = self.d(x)

        out = self.o(x)
        out = nn.Sigmoid()(out)
        return out

class FCN(torch.nn.Module):
    def __init__(self, base, in_f):
        super(FCN, self).__init__()
        self.base = base
        self.h1 = Head(in_f, 1)

    def forward(self, x):
        x = self.base(x)
        return self.h1(x)

def xception():
    model = get_model("xception", pretrained=False)
    model = nn.Sequential(*list(model.children())[:-1]) # Remove original output layer
    model[0].final_block.pool = nn.Sequential(nn.AdaptiveAvgPool2d((1,1)))
    model = FCN(model, 2048)
    return model


class FCN2(torch.nn.Module):
    def __init__(self, base):
        super(FCN2, self).__init__()
        self.base = base

    def forward(self, x):
        x = self.base(x)
        print(x.size(-1))
        x = nn.Linear(x.size(-1), 1)(x)
        print(x.size)
        x = nn.Sigmoid()(x)
        return x
def xception2():
    model = get_model("xception", pretrained=False)
    model = nn.Sequential(*list(model.children())[:-1]) # Remove original output layer
    model[0].final_block.pool = nn.Sequential(nn.Flatten())
    model = FCN2(model)
    return model

from torchsummary import summary
model = xception2()
summary(model,(3,256,256))