import cv2
import numpy as np


def align_images(image, template):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    orb = cv2.SIFT_create(500)    
    keypoints1, descriptors1 = orb.detectAndCompute(image_gray, None)
    keypoints2, descriptors2 = orb.detectAndCompute(template_gray, None)

    # Match features.
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_SL2)
    matches = matcher.match(descriptors1, descriptors2, None)

    # Sort matches by score
    matches = sorted(matches, key=lambda x: x.distance, reverse=False)
    
    # Remove not so good matches
    num_good_matches = int(len(matches) * 0.15)
    matches = matches[:num_good_matches]
    
    # Extract location of good matches
    points1 = np.zeros((len(matches), 2), dtype=np.float32)
    points2 = np.zeros((len(matches), 2), dtype=np.float32)

    for i, match in enumerate(matches):
        points1[i, :] = keypoints1[match.queryIdx].pt
        points2[i, :] = keypoints2[match.trainIdx].pt
    
    # Find homography
    h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)
    
    # Use homography
    height, width = template_gray.shape
    registered_image = cv2.warpPerspective(image, h, (width, height))

    return registered_image


def denormalise_box_coordinates(start_x_norm, start_y_norm, end_x_norm, end_y_norm, doc_width, doc_height):
    start_x = int(start_x_norm * doc_width)
    end_x = int(end_x_norm * doc_width)
    start_y = int(start_y_norm * doc_height)
    end_y = int(end_y_norm * doc_height)
    
    return start_x, start_y, end_x, end_y


def get_box_coords(start_x, start_y, end_x, end_y):
    return [[start_x, start_y], [end_x, start_y], [end_x, end_y], [start_x, end_y]]