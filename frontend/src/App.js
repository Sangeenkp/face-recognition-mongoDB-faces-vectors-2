import './App.css';
import onescreenlogo from './onescreen-logo.png';
import examplefaceimage from './example_face_img.jpg';
import Webcam from 'react-webcam';
import { useState } from 'react';
import ReactModal from 'react-modal';
import ImageUpload from './ImageUpload';
import { config } from './Constants';

function App() {
  const [images, setImages] = useState([]);
  const [checkImage, setCheckImage] = useState([]);
  const [isAddUserModalOpen, setIsAddUserModalOpen] = useState(false);
  const [isCheckUserModalOpen, setIsCheckUserModalOpen] = useState(false);
  const [personName, setPersonName] = useState('');
  const [base64Image, setBase64Image] = useState('');

  const URL = config.url;

  const videoConstraints = {
    width: 1080,
    height: 1080,
    facingMode: 'user',
  };

  const AddUserWebCamComponent = () => (
    <Webcam
      audio={false}
      height={360}
      width={1280}
      screenshotFormat="image/jpeg"
      videoConstraints={videoConstraints}
    >
      {({ getScreenshot }) => (
        <button
          onClick={() => {
            const imageSrc = getScreenshot();
            setImages([...images, imageSrc]);
          }}
          className="webcam-button"
        >
          Capture Photo
        </button>
      )}
    </Webcam>
  );

  const CheckUserWebCamComponent = () => (
    <Webcam
      audio={false}
      height={360}
      width={1280}
      screenshotFormat="image/jpeg"
      videoConstraints={videoConstraints}
    >
      {({ getScreenshot }) => (
        <button
          onClick={() => {
            const imageSrc = getScreenshot();
            setCheckImage([imageSrc]);
          }}
          className="check-user-webcam-button"
        >
          Capture Photo
        </button>
      )}
    </Webcam>
  );

  const sendAddUserRequest = async () => {
    const data = images.map((image, index) => {
      return {
        name: `${personName}_${index + 1}`,
        image,
      };
    });

    const response = await fetch(`${URL}/items/`, {
      method: 'post',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
  };

  const sendCheckUserRequest = async () => {
    const response = await fetch(`${URL}/image/`, {
      method: 'post',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ checkImage }),
    });

    setBase64Image(await response.json());
  };

  const handleAddUserModalClose = () => {
    setIsAddUserModalOpen(false);
    setImages([]);
    setPersonName('');
    setBase64Image('');
  };

  const handleCheckUserModalClose = () => {
    setIsCheckUserModalOpen(false);
    setCheckImage([]);
    setBase64Image('');
  };

  return (
    <div className="App">
      <img src={onescreenlogo} alt="logo" className="logo" />
      <p className="para">Face Recognition</p>
      <img
        src={examplefaceimage}
        alt="face recognition example"
        className="example-face-img"
        width={600}
        height={350}
      />
      <button onClick={() => setIsAddUserModalOpen(true)} className="button">
        Add User
      </button>
      <button onClick={() => setIsCheckUserModalOpen(true)} className="button">
        Recognize User
      </button>

      <ReactModal
        appElement={document.getElementById('root')}
        isOpen={isAddUserModalOpen}
        onRequestClose={handleAddUserModalClose}
        style={{
          overlay: { backgroundColor: 'rgba(0, 0, 0, 0.5)' },
          content: {
            position: 'absolute',
            top: '40px',
            left: '40px',
            bottom: '40px',
            right: '40px',
          },
        }}
      >
        <AddUserWebCamComponent className="webcam-component" />
        <ImageUpload
          images={images}
          addImages={setImages}
          multiple="multiple"
        />
        <div className="input-container">
          <input
            type="text"
            placeholder="Enter your name"
            value={personName}
            onChange={e => setPersonName(e.target.value)}
            className="modal-input"
          />
          {images.length < 5 || !personName ? (
            <button
              title="Take or Upload 5 photos and input name"
              onClick={sendAddUserRequest}
              disabled={images.length < 5 || !personName}
              className="save-button save-button-disabled"
            >
              Save User
            </button>
          ) : (
            <button
              title="Click to save user"
              onClick={sendAddUserRequest}
              className="save-button save-button-enabled"
            >
              Save User
            </button>
          )}
        </div>
        {images.length
          ? images.map((item, index) => {
              return (
                <li key={index} className="add-user-li">
                  <img src={item} alt="" width={100} height={100} />
                </li>
              );
            })
          : null}
      </ReactModal>
      <ReactModal
        appElement={document.getElementById('root')}
        isOpen={isCheckUserModalOpen}
        onRequestClose={handleCheckUserModalClose}
        style={{
          overlay: { backgroundColor: 'rgba(0, 0, 0, 0.5)' },
          content: {
            position: 'absolute',
            top: '40px',
            left: '40px',
            bottom: '40px',
            right: '40px',
          },
        }}
      >
        <CheckUserWebCamComponent className="webcam-component" />
        {checkImage.length < 1 ? (
          <button
            title="Take or Upload a photo first"
            onClick={sendCheckUserRequest}
            disabled={checkImage.length < 1}
            className="check-button check-button-disabled"
          >
            Check User
          </button>
        ) : (
          <button
            title="Click to check user"
            onClick={sendCheckUserRequest}
            className="check-button check-button-enabled"
          >
            Check User
          </button>
        )}
        <ImageUpload images={images} addImages={setCheckImage} multiple="" />
        {checkImage.length
          ? checkImage.map((item, index) => {
              return (
                <li key={index} className="check-image-li">
                  <img src={item} alt="" width={100} height={100} />
                </li>
              );
            })
          : null}
        {base64Image ? (
          <li key="image" className="check-image-li">
            <img
              src={`data:image/jpg;base64,${base64Image}`}
              alt=""
              width={1000}
              height={1000}
            />
          </li>
        ) : null}
      </ReactModal>
    </div>
  );
}

export default App;
