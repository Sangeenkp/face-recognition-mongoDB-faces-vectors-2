import re
import os
import base64
import pandas as pd
import shutil
import logging
import yaml
from tqdm import tqdm
from deepface import DeepFace
from deepface.commons import functions
from pymongo import MongoClient, errors

credentials = []
stream = open("config.yml", "r")
dictionary = yaml.full_load(stream)
for key, value in dictionary.items():
    credentials.append(value)

connection = f"mongodb+srv://{credentials[0]}:{credentials[1]}@{credentials[2]}/{credentials[3]}"

client = MongoClient(connection)

database = 'deepface'
collection = 'deepface'

db = client[database]

logger = logging.getLogger(__name__)
model = DeepFace.build_model("Facenet")

def add_identity(identity):
    global logger
    dir = "tests/new_identity"
    perma_dir = "tests/permanent_identities"
    for face in identity:
        base64_data = re.sub('^data:image/.+;base64,', '', face.image)
        img = base64.b64decode(base64_data)
        with open(f"tests/new_identity/{(face.name).lower()}.jpg", "wb") as f:
            f.write(img)
    
    facial_image_paths = []
    for root, directory, files in os.walk("tests/new_identity"):
        for file in files:
            if ".jpg" in file:
                facial_image_paths.append(root+'/'+file)

    instances = []
    for i in tqdm(range(0, len(facial_image_paths))):
        facial_image_path = facial_image_paths[i]
        facial_img = functions.preprocess_face(facial_image_path, target_size=(160, 160), enforce_detection=False)

        embedding = model.predict(facial_img)[0]

        instance = []
        instance.append(facial_image_path)
        instance.append(embedding)
        instances.append(instance)

    df = pd.DataFrame(instances, columns = ["img_name", "embedding"])

    for index, instance in tqdm(df.iterrows(), total = df.shape[0]):
        try:
            db[collection].insert_one({"img_path": instance["img_name"], "embedding": instance["embedding"].tolist()})
        except errors.DuplicateKeyError:
            logger.warning("Identity already exists")
            continue
    
    for file in os.listdir(dir):
        source = os.path.join(dir, file)
        destination = os.path.join(perma_dir, file)
        shutil.copy(source, destination)
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))