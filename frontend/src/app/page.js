'use client';
import React, {useState, useCallback, useRef} from 'react';
import axios from 'axios';
import Webcam from 'react-webcam';

export default function Home() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [useCamera, setUseCamera] = useState(false);
    const [facingMode, setFacingMode] = useState('user');
    const [loading, setLoading] = useState(false); // [1
    const webcamRef = useRef(null);

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        setSelectedFile(file);
        setPreview(URL.createObjectURL(file));
    };

    const handleCapture = useCallback(() => {
        const imageSrc = webcamRef.current.getScreenshot();
        setPreview(imageSrc);
        const blob = dataURLtoBlob(imageSrc);
        setSelectedFile(blob);
    }, [webcamRef]);

    const dataURLtoBlob = (dataURL) => {
        const byteString = atob(dataURL.split(',')[1]);
        const mimeString = dataURL.split(',')[0].split(':')[1].split(';')[0];
        const ab = new ArrayBuffer(byteString.length);
        const ia = new Uint8Array(ab);
        for (let i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }
        return new Blob([ab], {type: mimeString});
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            setLoading(true);
            const response = await axios.post('http://localhost:8000/predict', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            const data = response.data;
            if (data.status === 'success') {
                setLoading(false);
                setResult(data);
            } else if (data.status === 'error') {
                setError(data.message);
                setResult(null);
                setLoading(false);
            }
            setResult(data);
            setError(null);
        } catch (error) {
            setError(error.response.data.message);
            setResult(null);
            setLoading(false);
        }
    };

    const handleSwitchCamera = () => {
        setFacingMode(prevState => (prevState === 'user' ? 'environment' : 'user'));
    };

    return (
        <main className="flex min-h-screen flex-col items-center justify-center bg-gray-100 px-6 py-8">
            <div className="container mx-auto max-w-xl">
                <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">Food Recognition</h1>
                <div className="bg-white rounded-lg shadow-lg p-8">
                    <form onSubmit={handleSubmit} className="flex flex-col items-center">
                        <div className="mb-4 w-full">
                            <label className="block text-sm font-medium text-gray-700 mb-2">Upload an Image or Use
                                Camera</label>
                            <input
                                type="file"
                                onChange={handleFileChange}
                                className="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer focus:outline-none mb-4"
                            />
                            <button
                                type="button"
                                onClick={() => setUseCamera(!useCamera)}
                                className="mb-4 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors duration-300"
                            >
                                {useCamera ? 'Stop Camera' : 'Use Camera'}
                            </button>
                            {useCamera && (
                                <div className="flex flex-col items-center">
                                    <Webcam
                                        audio={false}
                                        ref={webcamRef}
                                        screenshotFormat="image/jpeg"
                                        videoConstraints={{facingMode}}
                                        className="mb-4"
                                    />
                                    <button
                                        type="button"
                                        onClick={handleCapture}
                                        className="mb-4 px-4 py-2 bg-green-500 text-white font-semibold rounded-lg hover:bg-green-600 transition-colors duration-300"
                                    >
                                        Capture Photo
                                    </button>
                                    <button
                                        type="button"
                                        onClick={handleSwitchCamera}
                                        className="px-4 py-2 bg-yellow-500 text-white font-semibold rounded-lg hover:bg-yellow-600 transition-colors duration-300"
                                    >
                                        Switch Camera
                                    </button>
                                </div>
                            )}
                            {preview && (
                                <div className="mt-4 flex justify-center">
                                    <img src={preview} alt="Selected File" className="w-64 h-auto"/>
                                </div>
                            )}
                        </div>
                        <button type="submit"
                                className="w-full px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors duration-300">
                            {
                                loading ? 'Loading...' : 'Predict Food'
                            }
                        </button>
                        {result && (
                            <div className="mt-8 flex flex-col items-center w-full">
                                <h2 className="text-2xl font-semibold text-center text-gray-800 mt-4">Prediction
                                    Result</h2>
                                <table className="mt-2 text-center text-gray-600 w-full">
                                    <thead>
                                    <tr>
                                        <th>Nutrient</th>
                                        <th>Amount</th>
                                    </tr>
                                    </thead>
                                    <tbody>
                                    <tr>
                                        <td>Food Name</td>
                                        <td>{result.food_name}</td>
                                    </tr>
                                    <tr>
                                        <td>Calories</td>
                                        <td>{result.nutrition.calories}</td>
                                    </tr>
                                    <tr>
                                        <td>Carbohydrates</td>
                                        <td>{result.nutrition.carbohydrates_total_g} g</td>
                                    </tr>
                                    <tr>
                                        <td>Cholesterol</td>
                                        <td>{result.nutrition.cholesterol_mg} mg</td>
                                    </tr>
                                    <tr>
                                        <td>Total Fat</td>
                                        <td>{result.nutrition.fat_total_g} g</td>
                                    </tr>
                                    <tr>
                                        <td>Saturated Fat</td>
                                        <td>{result.nutrition.fat_saturated_g} g</td>
                                    </tr>
                                    <tr>
                                        <td>Fiber</td>
                                        <td>{result.nutrition.fiber_g} g</td>
                                    </tr>
                                    <tr>
                                        <td>Potassium</td>
                                        <td>{result.nutrition.potassium_mg} mg</td>
                                    </tr>
                                    <tr>
                                        <td>Protein</td>
                                        <td>{result.nutrition.protein_g}</td>
                                    </tr>
                                    <tr>
                                        <td>Serving Size</td>
                                        <td>{result.nutrition.serving_size_g} g</td>
                                    </tr>
                                    <tr>
                                        <td>Sodium</td>
                                        <td>{result.nutrition.sodium_mg} mg</td>
                                    </tr>
                                    <tr>
                                        <td>Sugar</td>
                                        <td>{result.nutrition.sugar_g} g</td>
                                    </tr>
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </form>

                    {error && (
                        <div className="mt-8 p-4 bg-red-100 rounded-lg text-center text-red-600">
                            <p>{error}</p>
                        </div>
                    )}
                </div>
            </div>
        </main>
    );
}
