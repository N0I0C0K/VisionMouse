import torchvision
import torch

from torch.nn import Module
from functools import partial

from torchvision.models.detection.retinanet import RetinaNetClassificationHead


class RetinaNet_ResNet50:
    def __init__(
        self,
        num_classes: int,
        img_size: int,
        img_mean: list[float],
        img_std: list[float],
    ) -> None:
        model = torchvision.models.detection.retinanet_resnet50_fpn_v2(
            pretrained=False,
            pretrained_backbone=False,
            num_classes=num_classes,
        )
        num_anchors = model.head.classification_head.num_anchors
        norm_layer = partial(torch.nn.GroupNorm, 32)

        model.head.classification_head = RetinaNetClassificationHead(
            in_channels=256,
            num_anchors=num_anchors,
            num_classes=num_classes,
            norm_layer=norm_layer,
        )

        model.transform.min_size = img_size
        model.transform.max_size = img_size

        model.transform.image_mean = img_mean
        model.transform.image_std = img_std

        self.model = model

        self.load_state_dict = self.model.load_state_dict
        self.eval = self.model.eval
        self.to = self.model.to
        self.forward = self.model.forward


def get_model() -> RetinaNet_ResNet50:
    return RetinaNet_ResNet50()
