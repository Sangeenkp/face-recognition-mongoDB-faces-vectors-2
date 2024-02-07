import re
import os
import base64
import pandas as pd
import cv2
import dlib
from sklearn.decomposition import DictionaryLearning
import yaml
from imutils.face_utils import rect_to_bb
from deepface import DeepFace
from deepface.commons import functions
from pymongo import MongoClient

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

model = DeepFace.build_model("Facenet")

PREDICTIONS_DIRECTORY = 'tests/predictions'
Dlib_shape_predictor = "dlib-shape-predictor/shape_predictor_68_face_landmarks.dat"

frontal_face_detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor(Dlib_shape_predictor)

faces = []
names = []
base64_img = ''

def verify_identity(image):
    global names, faces, base64_img
    base64_data = re.sub('^data:image/.+;base64,', '', image)
    img = base64.b64decode(base64_data)
    with open("tests/predictions/img_result.jpg", "wb") as f:
        f.write(img)
    
    target_img_path = cv2.imread(os.path.join(PREDICTIONS_DIRECTORY, "img_result.jpg"))
    gray_img = cv2.cvtColor(target_img_path, cv2.COLOR_BGR2GRAY)
    rects = frontal_face_detector(gray_img, 2) # 2 is the upsampling rate

    if len(rects):
        for i, rect in enumerate(rects):
            (x, y, w, h) = rect_to_bb(rect)
            coordinates = [False if i < 0 else True for i in (x, y, w, h)]
            if False in coordinates:
                continue

            detected_face = gray_img[y:y+h, x:x+w]
            cv2.imwrite(f"tests/predictions/face_{i}.jpg", detected_face)
            detected_face = f"tests/predictions/face_{i}.jpg"
            faces.append((x, x+w, y, y+h))
            target_img = functions.preprocess_face(detected_face, target_size=(160, 160), enforce_detection=False)
            target_embedding = model.predict(target_img)[0].tolist()

            query = db[collection].aggregate( [
                {
                    "$addFields": { 
                        "target_embedding": target_embedding
                    }
                }
                , {"$unwind": { "path": "$embedding", "includeArrayIndex": "embedding_index"}}
                , {"$unwind": { "path": "$target_embedding", "includeArrayIndex": "target_index" }}
                
                , {
                    "$project": {
                        "img_path": 1,
                        "embedding": 1,
                        "target_embedding": 1,
                        "compare": {
                            "$cmp": ['$embedding_index', '$target_index']
                        }
                    }
                }
                , {"$match": {"compare": 0}}

                , {
                "$group": {
                    "_id": "$img_path",
                    "distance": {
                            "$sum": {
                                "$pow": [{
                                    "$subtract": ['$embedding', '$target_embedding']
                                }, 2]
                            }
                    }
                }
                }
                , { 
                    "$project": {
                        "_id": 1,
                        "distance": {"$sqrt": "$distance"}
                    }
                }
                , { 
                    "$project": {
                        "_id": 1,
                        "distance": 1,
                        "cond": { "$lte": [ "$distance", 20 ] }
                    }
                }
                , {"$match": {"cond": True}}
                , { "$sort": { "distance" : 1 } }
                , { "$limit": 10 }
            ] )

            top_5_results = []
            top_value = 0
            for i, j in enumerate(query):
                if i == 0:
                    top_value = j['distance']
                if i == 5:
                    break
                top_5_results.append(j['_id'].split('/')[-1].split('_')[0].lower())

            if len(top_5_results) > 3:
                path = []
                for i in top_5_results:
                    path.append(i)
                path = pd.Series(path)
                if path.value_counts().to_list()[0] > 3 and top_value < 12:
                    names.append(path.value_counts().index.to_list()[0])
                else:
                    names.append("Unknown")
            else:
                names.append("Unknwon")
            
            for i, face in enumerate(faces):
                cv2.rectangle(target_img_path, (face[0], face[2]), (face[1], face[3]), (0, 255, 0), 3)
                cv2.rectangle(target_img_path, (face[0], face[2]-20), (face[1], face[2]), (0, 255, 0), cv2.FILLED)
                cv2.putText(target_img_path, names[i], (face[0], face[2]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 2)
                cv2.imwrite(f"tests/predictions/face_img_result.jpg", target_img_path)

        faces.clear()
        names.clear()

        with open("tests/predictions/face_img_result.jpg", "rb") as f:
            base64_img = base64.b64encode(f.read())
        return base64_img.decode('utf-8')
    else:
        cv2.rectangle(target_img_path, (0, 30), (150, 0), (0, 255, 0), cv2.FILLED)
        cv2.putText(target_img_path, "No faces detected", (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 2)
        cv2.imwrite(os.path.join(PREDICTIONS_DIRECTORY, "face_img_result.jpg"), target_img_path)

        with open("tests/predictions/face_img_result.jpg", "rb") as f:
            base64_img = base64.b64encode(f.read())
        return base64_img.decode('utf-8')
