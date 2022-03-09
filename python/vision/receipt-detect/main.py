#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pythonProject.main
# Date: 2022/03/09
# Filename: main

from __future__ import annotations

__author__ = "Yoshi Truong"
__date__ = "2022/03/09"

import argparse
import os

import cv2
import imutils
from imutils import perspective
import tqdm

import utils


DEBUG = False


def get_images(path: str) -> list[str]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Cannot find input file/folder {path}")
    if os.path.isfile(path):
        if utils.is_image(path):
            return [path]
        else:
            raise ValueError(f"Specified path is not an image: {path}")
    else:
        # Folder
        return [os.path.join(path, filename) for filename in os.listdir(path) if utils.is_image(filename)]


def process_image(image_path: str):
    orig = cv2.imread(image_path)
    image = orig.copy()
    image = imutils.resize(image, width=500)
    ratio = orig.shape[1] / float(image.shape[1])

    filename, ext = os.path.splitext(image_path)
    ext = ext[1:]
    output_path = f"{filename}.out.{ext}"

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    if DEBUG:
        cv2.imwrite(f"{filename}.edge.{ext}", edged)

    contours = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    receipt_contour = None
    # loop over the contours
    for c in contours:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # if our approximated contour has four points, then we can
        # assume we have found the outline of the receipt
        if len(approx) == 4:
            receipt_contour = approx
            break
    # if the receipt contour is empty then our script could not find the outline; we should be notified
    if receipt_contour is None:
        raise Exception(("Could not find receipt outline. "
                         "Try debugging your edge detection and contour steps."))

    if DEBUG:
        output = image.copy()
        cv2.drawContours(output, [receipt_contour], -1, (0, 255, 0), 2)
        cv2.imwrite(f"{filename}.outline.{ext}", output)

    receipt = perspective.four_point_transform(orig, receipt_contour.reshape(4, 2) * ratio)
    cv2.imwrite(output_path, receipt)


def main(args):
    images = get_images(args.input)
    for image in tqdm.tqdm(images):
        process_image(image)


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Extract a receipt from an image.")
    parser.add_argument("input", type=str, help="Path to input file or folder")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debugging visualization")
    args = parser.parse_args()
    DEBUG = args.debug
    main(args)
