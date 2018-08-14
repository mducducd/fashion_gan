import io
import os
import requests
import numpy as np
from PIL import Image


def get_image_feature_by_path(img_path, feature_size=64):
    files = {'file': open(img_path, 'rb')}
    return __get_image_feature(files, feature_size)


def get_image_feature_by_image(img, feature_size=64):
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    files = {'file': ('img.jpg', img_bytes.getvalue(), 'image/jpeg')}
    return __get_image_feature(files, feature_size)


def __get_image_feature(files, feature_size):
    if feature_size == 64:
        url = 'http://akiwi.eu/mxnet/feature/'
    elif feature_size == 50:
        url = 'http://akiwi.eu/feature/fv50/'
    elif feature_size == 2000:
        url = 'http://akiwi.eu/mxnet/feature/raw/'
    else:
        raise ValueError('Invalid feature size')
    response = requests.post(url, files=files, timeout=10)

    if response.status_code == 200:
        response_feature = response.content
        return response_feature
    else:
        raise ValueError('Could not get feature vector for image. Response: ',
                         response)


def download_feature_vectors(files, save_dir, feature_size=64):
    extension = '.raw' if feature_size == 2000 else '.npy'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for idx, file in enumerate(files):
        if idx % 100 == 0:
            print('Downloaded {} / {}'.format(idx, len(files)))

        save_path = os.path.join(save_dir, os.path.basename(file).split('.jpg')[0] + extension)
        if os.path.exists(save_path):
            continue

        feature = get_image_feature_by_path(file, feature_size)
        feature = np.frombuffer(feature, dtype=np.uint8)
        np.save(save_path, feature)


def download_feature_vectors_114(files, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for idx, file in enumerate(files):
        try:
            if idx % 100 == 0:
                print('Downloaded {} / {}'.format(idx, len(files)))

            save_path = os.path.join(save_dir, os.path.basename(file).split('.jpg')[0] + '.npy')
            if os.path.exists(save_path):
                continue

            feature64 = get_image_feature_by_path(file, feature_size=64)
            feature50 = get_image_feature_by_path(file, feature_size=50)
            feature = feature64 + feature50

            feature = np.frombuffer(feature, dtype=np.uint8)
            np.save(save_path, feature)

        except Exception as e:
            print('Problem with file {}: {}'.format(file, e))


def save_feature_vectors_from_model(files, save_dir, model, data_transforms):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for idx, file in enumerate(files):
        try:
            if idx % 100 == 0:
                print('Downloaded {} / {}'.format(idx, len(files)))

            save_path = os.path.join(save_dir, os.path.basename(file).split('.jpg')[0] + '.npy')
            if os.path.exists(save_path):
                continue

            feature = get_image_feature_from_model(file, model, data_transforms)
            np.save(save_path, feature)

        except Exception as e:
            print('Problem with file {}: {}'.format(file, e))


def get_image_feature_from_model(img_path, model, data_transforms):
    img = Image.open(img_path).convert('RGB')
    feature = model(data_transforms(img).unsqueeze(0))
    feature = feature.squeeze().data.numpy()
    return feature


def concat_feature_vectors(feature_A_dir, feature_B_dir, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for idx, file in enumerate(os.listdir(feature_A_dir)):
        if idx % 1000 == 0:
            print('Downloaded {}'.format(idx))

        save_path = os.path.join(save_dir, file)

        if os.path.exists(save_path):
            continue

        try:
            feature_A = load_feature_bytes(os.path.join(feature_A_dir, file))
            feature_B = load_feature_bytes(os.path.join(feature_B_dir, file))

            feature = feature_A + feature_B
            with open(save_path, 'wb') as f:
                f.write(feature)

        except:
            print('Unable to find matching file: {}'.format(file))



def load_feature_bytes(path):
    with open(path, 'rb') as f:
        b = f.read()
    return b


def load_feature_vector(path):
    with open(path, 'rb') as f:
        b = f.read()
    return np.frombuffer(b, dtype=np.uint8)


