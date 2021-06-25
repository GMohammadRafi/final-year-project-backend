from mtcnn.mtcnn import MTCNN
from matplotlib import pyplot
from PIL import Image
from numpy import asarray
from scipy.spatial.distance import cosine
from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
from os import path
from app import constants as c, all_images_encoding, all_images

model = VGGFace(model='vgg16', include_top=False, input_shape=(224, 224, 3), pooling='avg')
images_folder = path.join(c.APP_ROOT, "images")
detector = MTCNN()


def extract_face(filename, required_size=(224, 224)):
    pixels = pyplot.imread(path.join(images_folder, filename))
    results = detector.detect_faces(pixels)
    try:
        x1, y1, width, height = results[0]['box']
        x2, y2 = x1 + width, y1 + height
        face = pixels[y1:y2, x1:x2]
        image = Image.fromarray(face)
        image = image.resize(required_size)
        return asarray(image)
    except:
        print("face not found in image")
        return []


def get_embeddings(filenames):
    faces = []
    for f in filenames:
        temp = extract_face(f)
        if len(temp) != 0:
            faces.append(temp)
    samples = asarray(faces, 'float32')
    samples = preprocess_input(samples, version=1)
    yhat = model.predict(samples)
    return yhat


def is_match(known_embedding, candidate_embedding, thresh=0.5):
    score = cosine(known_embedding, candidate_embedding)
    if score <= thresh:
        return True
    else:
        return False


if len(all_images) != 0:
    all_images_encoding.extend(get_embeddings(all_images))
    print("encoded")
