import React, { useEffect } from 'react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

const AudioCapture = () => {
    const { transcript, resetTranscript } = useSpeechRecognition();

    const startListening = () => {
        SpeechRecognition.startListening({ continuous: true, language: 'en-US' });
    };

    const stopListening = () => {
        SpeechRecognition.stopListening();
    };

    useEffect(() => {
        if (!SpeechRecognition.browserSupportsSpeechRecognition()) {
            alert('Your browser does not support speech recognition.');
        }
    }, []);

    
    return (
        <div style={{ padding: '20px' }}>
            <h1>Transcribe YouTube Video</h1>
            <iframe
                width="560"
                height="315"
                src="https://www.youtube.com/embed/VoL4wixuF_g"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                title="YouTube Video Player"
            ></iframe>
            <div style={{ marginTop: '20px' }}>
                <button onClick={startListening} style={{ marginRight: '10px' }}>
                    Start Listening
                </button>
                <button onClick={stopListening} style={{ marginRight: '10px' }}>
                    Stop Listening
                </button>
                <button onClick={resetTranscript}>
                    Reset Transcript
                </button>
            </div>
            <div style={{ marginTop: '20px', padding: '10px', border: '1px solid #ccc', borderRadius: '4px' }}>
                <h3>Transcript:</h3>
                <p>{transcript}</p>
            </div>
        </div>
    );
};

export default AudioCapture;












// import React from 'react';
// import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

// const AudioCapture = () => {
//     const { transcript, resetTranscript } = useSpeechRecognition();

//     const startListening = () => {
//         SpeechRecognition.startListening({ continuous: true, language: 'en-US' });
//     };

//     const stopListening = () => {
//         SpeechRecognition.stopListening();
//     };

//     if (!SpeechRecognition.browserSupportsSpeechRecognition()) {
//         return <div>Your browser does not support speech recognition.</div>;
//     }

//     return (
//         <div>
//             <h2>YouTube Video with Speech Recognition</h2>
            
//             {/* YouTube Video Embed */}
//             <iframe
//                 width="560"
//                 height="315"
//                 src="https://www.youtube.com/embed/VoL4wixuF_g"
//                 frameBorder="0"
//                 allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
//                 allowFullScreen
//                 title="YouTube Video Player"
//             ></iframe>

//             {/* Buttons to Control Speech Recognition */}
//             <div style={{ marginTop: '20px' }}>
//                 <button onClick={startListening} style={{ marginRight: '10px' }}>Start Listening</button>
//                 <button onClick={stopListening}>Stop Listening</button>
//             </div>

//             {/* Display Transcript */}
//             <div style={{ marginTop: '20px' }}>
//                 <h3>Transcript:</h3>
//                 <p>{transcript}</p>
//             </div>
//         </div>
//     );
// };

// export default AudioCapture;
