import react, { useRef } from 'react';
import './ImageUpload.css';

const ImageUpload = ({ images, addImages, multiple }) => {
  const inputFile = useRef(null);

  const handleFileUpload = e => {
    const blobToBase64 = [];
    const targetFiles = e.target.files;
    const targetFilesObject = [...targetFiles];

    targetFilesObject.map(file => {
      let reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onloadend = () => {
        blobToBase64.push(reader.result);
        return addImages([...images, ...blobToBase64]);
      };
      return null;
    });
  };

  const onButtonClick = () => {
    inputFile.current.click();
  };

  return (
    <div>
      <input
        style={{ display: 'none' }}
        ref={inputFile}
        onChange={handleFileUpload}
        type="file"
        multiple={multiple}
      />
      <button className="image-upload-button" onClick={onButtonClick}>
        Upload Photo
      </button>
    </div>
  );
};

export default ImageUpload;
