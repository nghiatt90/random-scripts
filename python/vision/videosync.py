import cv2
import numpy as np
import os
from tqdm import tqdm


DIR = '/home/nghiatruong/Desktop'
INPUT_1 = os.path.join(DIR, 'GOPR1806.MP4')
INPUT_2 = os.path.join(DIR, '20190715_180940.mp4')
INPUT_3 = os.path.join(DIR, '20190715_181200.mp4')
RIGHT_SYNC_1 = 1965
LEFT_SYNC_1 = 1700
RIGHT_SYNC_2 = 5765
LEFT_SYNC_2 = 1282


def add_frame_id(video, output_dir):
    reader = cv2.VideoCapture(video)
    if not reader.isOpened():
        return -1
    os.makedirs(output_dir, exist_ok=True)
    frame_count = int(reader.get(cv2.CAP_PROP_FRAME_COUNT))

    for frame_id in tqdm(range(frame_count)):
        has_frame, frame = reader.read()
        if not has_frame:
            break
        cv2.imwrite(os.path.join(output_dir, f'{frame_id}.jpg'), frame)

    reader.release()
    return 0


def get_meta(video):
    reader = cv2.VideoCapture(video)
    if not reader.isOpened():
        return None, None, None
    width = int(reader.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(reader.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(reader.get(cv2.CAP_PROP_FRAME_COUNT))
    return width, height, frame_count


w1, h1, fc1 = get_meta(INPUT_1)
h2, w2, fc2 = get_meta(INPUT_2)
ratio = h1 / h2
w2 = int(w2*ratio)+1
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
writer = cv2.VideoWriter(os.path.join(DIR, 'output.avi'), fourcc, 29.97, (w1+w2+10, h1))
border = np.zeros((h1, 10, 3), dtype='uint8')
filler = np.zeros((h1, w2, 3), dtype='uint8')

reader1 = cv2.VideoCapture(INPUT_1)
reader2 = cv2.VideoCapture(INPUT_2)
reader3 = cv2.VideoCapture(INPUT_3)

last_shape = (h1, w1+w2+10, 3)
for fid in tqdm(range(fc2+RIGHT_SYNC_1-LEFT_SYNC_1)):
    _, right_frame = reader1.read()
    if fid < RIGHT_SYNC_1-LEFT_SYNC_1:
        left_frame = filler
    else:
        _, left_frame = reader2.read()
        left_frame = cv2.transpose(left_frame)
        left_frame = cv2.resize(left_frame, None, fx=ratio, fy=ratio)
        left_frame = cv2.flip(left_frame, 1)
    new_frame = np.concatenate([left_frame, border, right_frame], axis=1)
    # cv2.imshow('out', new_frame)
    writer.write(new_frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

for fid in tqdm(range(fc2+RIGHT_SYNC_1-LEFT_SYNC_1, RIGHT_SYNC_2-LEFT_SYNC_2)):
    _, right_frame = reader1.read()
    new_frame = np.concatenate([filler, border, right_frame], axis=1)
    # cv2.imshow('out', new_frame)
    writer.write(new_frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

for fid in tqdm(range(RIGHT_SYNC_2-LEFT_SYNC_2, fc1)):
    r1, right_frame = reader1.read()
    if not r1:
        break
    r3, left_frame = reader3.read()
    if not r3:
        left_frame = filler
    else:
        left_frame = cv2.transpose(left_frame)
        left_frame = cv2.resize(left_frame, None, fx=ratio, fy=ratio)
        left_frame = cv2.flip(left_frame, 1)
    new_frame = np.concatenate([left_frame, border, right_frame], axis=1)
    # cv2.imshow('out', new_frame)
    writer.write(new_frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break


reader1.release()
reader2.release()
writer.release()
cv2.destroyAllWindows()
