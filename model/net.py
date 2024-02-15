import torchvision
import torch
import albumentations as alb

from torch.nn import Module
from functools import partial

from albumentations.pytorch import ToTensorV2

from torchvision.models.detection.retinanet import RetinaNetClassificationHead

from .utils import DEVICE

classes = [
    "call",
    "dislike",
    "fist",
    "four",
    "like",
    "mute",
    "ok",
    "one",
    "palm",
    "peace",
    "rock",
    "stop",
    "stop_inverted",
    "three",
    "two_up",
    "two_up_inverted",
    "three2",
    "peace_inverted",
    "no_gesture",
]

IMG_SIZE = 224
IMG_MEAN = [0.54, 0.499, 0.473]
IMG_STD = [0.231, 0.232, 0.229]


class RetinaNet_ResNet50:
    def __init__(
        self,
        num_classes: int,
        img_size: int,
        img_mean: list[float],
        img_std: list[float],
    ) -> None:
        model = torchvision.models.detection.retinanet_resnet50_fpn_v2(
            weights=None,
            num_classes=num_classes,
            weights_backbone=None,
        ).to(DEVICE)
        num_anchors = model.head.classification_head.num_anchors
        norm_layer = partial(torch.nn.GroupNorm, 32)

        model.head.classification_head = RetinaNetClassificationHead(
            in_channels=256,
            num_anchors=num_anchors,
            num_classes=num_classes,
            norm_layer=norm_layer,
        ).to(DEVICE)

        model.transform.min_size = (img_size,)  # type: ignore
        model.transform.max_size = img_size

        model.transform.image_mean = img_mean
        model.transform.image_std = img_std

        self.model = model

        self.load_state_dict = self.model.load_state_dict
        self.eval = self.model.eval
        self.forward = self.model.forward


def get_model(ckp_file_path: str) -> RetinaNet_ResNet50:
    model = RetinaNet_ResNet50(
        len(classes) + 1,
        IMG_SIZE,
        IMG_MEAN,
        IMG_STD,
    )
    ckp = torch.load(ckp_file_path, DEVICE)
    model.load_state_dict(ckp["MODEL_STATE"])
    model.eval()
    return model


def get_transforms() -> alb.Compose:
    longest_maxsize = alb.LongestMaxSize(IMG_SIZE, p=1)
    pad = alb.PadIfNeeded(IMG_SIZE, IMG_SIZE, value=[144, 144, 144], border_mode=0, p=1)

    transforms = [longest_maxsize, pad, ToTensorV2()]
    return alb.Compose(
        transforms,
    )
