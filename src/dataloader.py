#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# IMPORTANT: READ BEFORE DOWNLOADING, COPYING, INSTALLING OR USING.
#
#  By downloading, copying, installing or using the software you agree to this license.
#  If you do not agree to this license, do not download, install,
#  copy or use the software.
#
#
#       Shanghai ShanMing Information & Technology Ltd. License Agreement
#                For quant trade strategy and library
#
# Copyright (C) 2017, Shanghai ShanMing Information & Technology Ltd., all rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are NOT permitted.
#
# @Time    : 2018/9/2 下午10:43
# @Author  : Gaowei Xu
# @Email   : gaowxu@hotmail.com
# @File    : dataloader.py

import os
import pickle
import random


class Sample(object):
    """
    Class for store samples
    """
    def __init__(self,
                 input_image_full_path,
                 gt_mask_full_path,
                 transform,
                 mode):
        """
        constructor

        :param input_image_full_path: input image full path
        :param gt_mask_full_path: input ground truth mask full path
        :param transform: 'raw', 'cw_90', 'cw_180', 'cw_270', 'h_mirror', 'v_mirror'
        :param mode: 'local_train', 'local_val', 'test'
        """
        self._input_image_full_path = input_image_full_path
        self._gt_mask_full_path = gt_mask_full_path
        self._transform = transform
        self._mode = mode

    @property
    def input_image_full_path(self):
        return self._input_image_full_path

    @property
    def gt_mask_full_path(self):
        return self._gt_mask_full_path

    @property
    def transform(self):
        return self._transform

    @property
    def mode(self):
        return self._mode


class DataLoader(object):
    """
    Data loader of training/validation dataset
    """
    def __init__(
            self,
            train_images_root_dir,
            train_masks_root_dir,
            test_images_root_dir,
            submit_dump_full_path,
            train_batch_size,
            val_batch_size,
            test_batch_size
    ):
        """
        data loader constructor

        :param train_images_root_dir:
        :param train_masks_root_dir:
        :param test_images_root_dir:
        :param submit_dump_full_path:
        """
        self._train_images_root_dir = train_images_root_dir
        self._train_masks_root_dir = train_masks_root_dir
        self._test_images_root_dir = test_images_root_dir
        self._submit_dump_full_path = submit_dump_full_path
        self._train_batch_size = train_batch_size
        self._val_batch_size = val_batch_size
        self._test_batch_size = test_batch_size

        self._train_index = 0
        self._val_index = 0
        self._testa_index = 0

        self._train_samples = list()
        self._val_samples = list()
        self._test_samples = list()

        self.load()

    def load(self):
        """
        prepare all things for model training / validation
        :return:
        """
        local_train_images, local_val_images = self.train_validation_split()
        test_images = os.listdir(self._test_images_root_dir)
        self.augmentation(
            local_train_images=local_train_images,
            local_val_images=local_val_images,
            test_images=test_images
        )
        random.shuffle(self._train_samples)
        random.shuffle(self._val_samples)

    def augmentation(self, local_train_images, local_val_images, test_images):
        """
        data augmentation, each image can be rotated 90 degree, 180 degree,
        270 degree clockwise and mirror transformation along horizontal and
        vertical directions. Each image can be augmented to 6 images (including
        raw image).

        (only for training dataset)

        :param local_train_images: list of string (each element is a image name)
        :param local_val_images:
        :param test_images:
        :return:
        """
        for i, image_name in enumerate(local_train_images):
            for transform in ['raw', 'cw_90', 'cw_180', 'cw_270', 'h_mirror', 'v_mirror']:
                sample = Sample(
                    input_image_full_path=os.path.join(self._train_images_root_dir, image_name),
                    gt_mask_full_path=os.path.join(self._train_masks_root_dir, image_name),
                    transform=transform,
                    mode='local_train'
                )
                self._train_samples.append(sample)

        for i, image_name in enumerate(local_val_images):
            sample = Sample(
                input_image_full_path=os.path.join(self._train_images_root_dir, image_name),
                gt_mask_full_path=os.path.join(self._train_masks_root_dir, image_name),
                transform='raw',
                mode='local_val'
            )
            self._val_samples.append(sample)

        for i, image_name in enumerate(test_images):
            sample = Sample(
                input_image_full_path=os.path.join(self._test_images_root_dir, image_name),
                gt_mask_full_path=None,
                transform='raw',
                mode='test'
            )
            self._test_samples.append(sample)

    def train_validation_split(self, train_val_ratio=5.0):
        """
        split the dataset into training/validation dataset
        :param train_val_ratio:
        :return:
        """
        local_samples = os.listdir(self._train_images_root_dir)
        local_amount = len(local_samples)
        random.shuffle(local_samples)

        train_amount = int(local_amount * train_val_ratio / (train_val_ratio + 1.0))
        val_amount = local_amount - train_amount

        local_train_images = local_samples[0:train_amount]
        local_val_images = local_samples[train_amount:]

        print 'Split dataset into training/validation parts, {} training samples, ' \
              '{} validation samples.'.format(len(local_train_images),
                                              len(local_val_images))
        return local_train_images, local_val_images

    def next_batch(self, mode):
        """
        get next batch for training / validation mode
        :return:
        """

    def reset(self):
        """
        reset index for train/validation

        :return:
        """
        self._train_index = 0
        self._val_index = 0
        self._testa_index = 0


if __name__ == '__main__':
    loader = DataLoader(
        train_images_root_dir='../dataset/train/images/',
        train_masks_root_dir='../dataset/train/masks/',
        test_images_root_dir='../dataset/test/images/',
        submit_dump_full_path='../output/submission.csv',
        train_batch_size=64,
        val_batch_size=64,
        test_batch_size=1
    )

    loader.train_validation_split()
