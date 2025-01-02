import React, { useState, useEffect } from 'react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import useClipboard from 'react-use-clipboard';
import { Controlled as CodeMirror } from 'react-codemirror2';
import 'codemirror/lib/codemirror.css';
import 'codemirror/theme/monokai.css';
import 'codemirror/mode/javascript/javascript';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import AudioCapture from './AudioCapture';
import ScreenshotReceiver from './screencapture/ScreenshotReceiver';
import DeepgramTranscriber from './DeepgramTranscriber ';

const App = () => {
    const [textToCopy, setTextToCopy] = useState('');
    const [isCopied, setCopied] = useClipboard(textToCopy, { successDuration: 1000 });
    const [capturedText, setCapturedText] = useState(''); 
    const [serverResponse, setServerResponse] = useState(''); 
    const [socket, setSocket] = useState(null);
    const [displayText, setDisplayText] = useState(''); 
    const { transcript, browserSupportsSpeechRecognition } = useSpeechRecognition();

    const themes = ['dracula', 'material', 'idea','eclipse', 'monokai'];
    const theme = themes[Math.floor(Math.random() * themes.length)];

    // useEffect(() => {
    //     const imagePath = '/path/to/your/image.jpg'; // Adjust to your image path
    //     const wsUrl = 'ws://localhost:8765'; // WebSocket server URL
    // },[]);

    useEffect(() => {
        // Initialize WebSocket connection
        const ws = new WebSocket('ws://localhost:7755/ws');
        setSocket(ws);

        ws.onopen = () => {
            console.log('WebSocket connection established');
        };

        ws.onmessage = (message) => {
            console.log('Received message from server:', message.data);
            setServerResponse(message.data);
        };

        ws.onclose = () => {
            console.log('WebSocket connection closed');
        };

        return () => {
            ws.close();
        };
    }, []);

    const startListening = () => {
        if (navigator.mediaDevices && browserSupportsSpeechRecognition) {
            // Capture audio input and noise suppression
            navigator.mediaDevices.getUserMedia({
                audio: {
                    noiseSuppression: true,
                    echoCancellation: true,
                    autoGainControl: true
                }
            }).then(stream => {
                // Create an audio context
                const audioContext = new AudioContext();
                const source = audioContext.createMediaStreamSource(stream);

                const gainNode = audioContext.createGain();
                gainNode.gain.value = 1;

                source.connect(gainNode);

                // Start listening 
                SpeechRecognition.startListening({ continuous: true, language: 'en-US' });
            }).catch(err => {
                console.error('Error accessing the microphone:', err);
            });
        }
    };

    const stopListening = () => {
        SpeechRecognition.stopListening();
        setCapturedText(transcript);

        if (socket) {
            socket.send(transcript); 
        }
    };

    useEffect(() => {
        if (browserSupportsSpeechRecognition) {
            setDisplayText(transcript);
        }
    }, [transcript, browserSupportsSpeechRecognition]);

    if (!browserSupportsSpeechRecognition) {
        return <p>Your browser does not support speech recognition.</p>;
    }

    return (
        <div className="container mt-4">
            <h2 className="mb-4">Interview AI</h2>

            <div className="mb-3">
                <div className="border p-3 rounded" onClick={() => setTextToCopy(displayText)}>
                    {displayText}
                </div>
            </div>

            <div className="btn-group mb-3">
                <button className="btn btn-primary button-spacing" onClick={setCopied}>
                    {isCopied ? 'Copied!' : 'clipboard'}
                </button>
                <button className="btn btn-success button-spacing" onClick={startListening}>Start</button>
                <button className="btn btn-danger button-spacing" onClick={stopListening}>Stop</button>
            </div>

            <div>
                <h3>Server Response:</h3>
                <div className="border p-3 rounded">
                    <CodeMirror
                        value={serverResponse.trim()} 
                        options={{
                            mode: 'javascript',
                            theme: theme,
                            lineNumbers: true,
                            lineWrapping: true,
                            gutters: false, 
                            scrollbarStyle: null,
                            autofocus: true,
                        }}
                        onBeforeChange={(editor, data, value) => {
                            const cleanedResponse = value.replace(/\s+/g, ' ').trim();
                            setServerResponse(cleanedResponse);
                        }}
                    />
                </div>
            </div>
            <div><DeepgramTranscriber/></div>
            {/* <div><AudioCapture/></div> */}
            {/* <div>
            <ScreenshotReceiver />
        </div> */}
        </div>
    );
};

export default App;








// Working Fine 

// import React, { useState, useEffect } from 'react';
// import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
// import useClipboard from 'react-use-clipboard';
// import { Controlled as CodeMirror } from 'react-codemirror2';
// import 'codemirror/lib/codemirror.css';
// import 'codemirror/theme/monokai.css';
// import 'codemirror/mode/javascript/javascript';
// import 'bootstrap/dist/css/bootstrap.min.css';
// import './App.css';

// import AudioCapture from './AudioCapture';

// const App = () => {
//     const [textToCopy, setTextToCopy] = useState('');
//     const [isCopied, setCopied] = useClipboard(textToCopy, { successDuration: 1000 });
//     const [capturedText, setCapturedText] = useState(''); 
//     const [serverResponse, setServerResponse] = useState(''); 
//     const [socket, setSocket] = useState(null);
//     const [displayText, setDisplayText] = useState(''); 
//     const { transcript, browserSupportsSpeechRecognition } = useSpeechRecognition();

//     var themes = ['dracula', 'material', 'idea','eclipse', 'monokai'];
//     var theme = themes[Math.floor(Math.random() * themes.length)];

//     useEffect(() => {
//         // Initialize WebSocket connection
//         const ws = new WebSocket('ws://localhost:7755/ws');
//         setSocket(ws);

//         ws.onopen = () => {
//             console.log('WebSocket connection established');
//         };

//         ws.onmessage = (message) => {
//             console.log('Received message from server:', message.data);
//             setServerResponse(message.data);
//         };

//         ws.onclose = () => {
//             console.log('WebSocket connection closed');
//         };

//         return () => {
//             ws.close();
//         };
//     }, []);


//     useEffect(() => {
//         if (browserSupportsSpeechRecognition) {
//             setDisplayText(transcript);
//         }
//     }, [transcript, browserSupportsSpeechRecognition]);


//     const startListening = () => {
//         SpeechRecognition.startListening({ continuous: true, language: 'en-US' });
//     };

//     const stopListening = () => {
//         SpeechRecognition.stopListening();
//         setCapturedText(transcript);

//         if (socket) {
//             socket.send(transcript); 
//         }
//     };

//     // const resetAll = () => {
//     //     SpeechRecognition.stopListening(); 
//     //     setCapturedText('');
//     //     setDisplayText('');
//     // };
    

//     if (!browserSupportsSpeechRecognition) {
//         return <p>Your browser does not support speech recognition.</p>;
//     }




//     return (
//         <div className="container mt-4">
//             <h2 className="mb-4"> Interview AI</h2>

//             {/* <div className="mb-3">
//                 <div className="border p-3 rounded" onClick={() => setTextToCopy(transcript)}>
//                     {transcript}
//                 </div>
//             </div> */}

//             <div className="mb-3">
//                 <div className="border p-3 rounded" onClick={() => setTextToCopy(displayText)}>
//                     {displayText}
//                 </div>
//             </div>

//             <div className="btn-group mb-3">
//                 <button className="btn btn-primary button-spacing" onClick={setCopied}>
//                     {isCopied ? 'Copied!' : 'clipboard'}
//                 </button>
//                 <button className="btn btn-success button-spacing" onClick={startListening}>Start</button>
//                 <button className="btn btn-danger button-spacing" onClick={stopListening}>Stop</button>
//                 {/* <button className="btn btn-secondary" onClick={resetAll}>Reset Transcript</button> */}
//             </div>

//             <div>
//                 <h3>Server Response:</h3>
//                 <div className="border p-3 rounded">
//                     <CodeMirror
//                         value={serverResponse.trim()} 
//                         options={{
//                             mode: 'javascript',
//                             theme: theme,
//                             lineNumbers: true,
//                             lineWrapping: true,
//                             gutters: false, 
//                             scrollbarStyle: null,
//                             autofocus: true,
//                         }}
//                         onBeforeChange={(editor, data, value) => {
//                             const cleanedResponse = value.replace(/\s+/g, ' ').trim();
//                             setServerResponse(cleanedResponse);
//                         }}
//                     />
//                 </div>
//             </div>
//             <div>
//                 {/* <div><AudioCapture/></div> */}
//             </div>
//         </div>
//     );
// };

// export default App;












// import React, { useState, useEffect } from 'react';
// import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
// import useClipboard from 'react-use-clipboard';
// import { Controlled as CodeMirror } from 'react-codemirror2';
// import 'codemirror/lib/codemirror.css';
// import 'codemirror/theme/monokai.css';

// import 'codemirror/mode/javascript/javascript';

// const App = () => {
//     const [textToCopy, setTextToCopy] = useState('');
//     const [isCopied, setCopied] = useClipboard(textToCopy, { successDuration: 1000 });
//     const [capturedText, setCapturedText] = useState(''); // For storing the transcript
//     const [serverResponse, setServerResponse] = useState(''); // New state variable for server response
//     const [socket, setSocket] = useState(null);
//     const { transcript, browserSupportsSpeechRecognition } = useSpeechRecognition();

//     useEffect(() => {
//         // Initialize WebSocket connection
//         const ws = new WebSocket('ws://localhost:7755/ws');
//         setSocket(ws);

//         ws.onopen = () => {
//             console.log('WebSocket connection established');
//         };

//         ws.onmessage = (message) => {
//             console.log('Received message from server:', message.data);

//             // Store the server's response in serverResponse state
//             setServerResponse(message.data);
//         };

//         ws.onclose = () => {
//             console.log('WebSocket connection closed');
//         };

//         return () => {
//             ws.close();
//         };
//     }, []);

//     const startListening = () => {
//         SpeechRecognition.startListening({ continuous: true, language: 'en-US' });
//     };

//     const stopListening = () => {
//         SpeechRecognition.stopListening();
//         setCapturedText(transcript); // Store the transcript in capturedText state

//         if (socket) {
//             socket.send(transcript);  // Send the captured text to the server via WebSocket
//         }
//     };

//     if (!browserSupportsSpeechRecognition) {
//         return <p>Your browser does not support speech recognition.</p>;
//     }

//     return (
//         <div className="container">
//             <h2>Speech to Text Converter</h2>
//             <br />
//             <p>
//                 A React hook that converts speech from the microphone to text and makes it available to your React components.
//             </p>

//             <div className="main-content" onClick={() => setTextToCopy(transcript)}>
//                 {transcript}
//             </div>

//             <div className="btn-style">
//                 <button onClick={setCopied}>
//                     {isCopied ? 'Copied!' : 'Copy to clipboard'}
//                 </button>
//                 <button onClick={startListening}>Start Listening</button>
//                 <button onClick={stopListening}>Stop Listening</button>
//             </div>

//             <div style={{ margin: 0, padding: 0 }}>
//     <h3>Server Response:</h3>
//     <CodeMirror
//         value={serverResponse.trim()} // Ensure no extra spaces in the content
//         options={{
//             mode: 'javascript',
//             theme:'monokai' ,
//             lineNumbers: true,
//             lineWrapping: true,
//             gutters: false, // Disable gutters if not needed
//             scrollbarStyle: null, // Disable scrollbars if not needed
//             autofocus: true,
//         }}
//         onBeforeChange={(editor, data, value) => {
//             const cleanedResponse = value.replace(/\s+/g, ' ').trim();
//             setServerResponse(cleanedResponse);
//         }}
//     />
// </div>
            
//         </div>
//     );
// };

// export default App;








// import React, { useState, useEffect } from 'react';
// import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
// import useClipboard from 'react-use-clipboard';
// import { Controlled as CodeMirror } from 'react-codemirror2';
// import 'codemirror/lib/codemirror.css';
// import 'codemirror/mode/javascript/javascript'; // Import modes as needed

// const App = () => {
//     const [textToCopy, setTextToCopy] = useState('');
//     const [isCopied, setCopied] = useClipboard(textToCopy, { successDuration: 1000 });
//     const [capturedText, setCapturedText] = useState('');
//     const [socket, setSocket] = useState(null);
//     const { transcript, browserSupportsSpeechRecognition } = useSpeechRecognition();

//     useEffect(() => {
//         // Initialize WebSocket connection
//         const ws = new WebSocket('ws://localhost:7755/ws');
//         setSocket(ws);

//         ws.onopen = () => {
//             console.log('WebSocket connection established');
//         };

//         ws.onmessage = (message) => {
//             console.log('Received message from server:', message.data);

//             // Handle the message received from Spring Boot (processed by Python)
//             setCapturedText(message.data); // Set the received data to state or perform other actions
//         };

//         ws.onclose = () => {
//             console.log('WebSocket connection closed');
//         };

//         return () => {
//             ws.close();
//         };
//     }, []);

//     const startListening = () => {
//         SpeechRecognition.startListening({ continuous: true, language: 'en-US' });
//     };

//     const stopListening = () => {
//         SpeechRecognition.stopListening();
//         setCapturedText(transcript);

//         if (socket) {
//             socket.send(transcript);  // Send the captured text to the server
//         }
//     };

//     if (!browserSupportsSpeechRecognition) {
//         return <p>Your browser does not support speech recognition.</p>;
//     }

//     return (
//         <div className="container">
//             <h2>Speech to Text Converter</h2>
//             <br />
//             <p>
//                 A React hook that converts speech from the microphone to text and makes it available to your React components.
//             </p>

//             <div className="main-content" onClick={() => setTextToCopy(transcript)}>
//                 <CodeMirror
//                     value={transcript}
//                     options={{
//                         mode: 'javascript', // Change mode as needed
//                         lineNumbers: true,
//                     }}
//                     onBeforeChange={(editor, data, value) => {
//                         setTextToCopy(value);
//                     }}
//                 />
//             </div>

//             <div className="btn-style">
//                 <button onClick={setCopied}>
//                     {isCopied ? 'Copied!' : 'Copy to clipboard'}
//                 </button>
//                 <button onClick={startListening}>Start Listening</button>
//                 <button onClick={stopListening}>Stop Listening</button>
//             </div>

//             <div>
//                 <h3>Processed Text:</h3>
//                 <CodeMirror
//                     value={capturedText}
//                     options={{
//                         mode: 'javascript', // Change mode as needed
//                         lineNumbers: true,
//                     }}
//                     onBeforeChange={(editor, data, value) => {
//                         setCapturedText(value);
//                     }}
//                 />
//             </div>
//         </div>
//     );
// };

// export default App;



//Working fine 
// import React, { useState, useEffect } from 'react';
// import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
// import useClipboard from 'react-use-clipboard';

// const App = () => {
//     const [textToCopy, setTextToCopy] = useState('');
//     const [isCopied, setCopied] = useClipboard(textToCopy, { successDuration: 1000 });
//     const [capturedText, setCapturedText] = useState('');
//     const [socket, setSocket] = useState(null);
//     const { transcript, browserSupportsSpeechRecognition } = useSpeechRecognition();

//     useEffect(() => {
//         // Initialize WebSocket connection
//         const ws = new WebSocket('ws://localhost:7755/ws');
//         setSocket(ws);

//         ws.onopen = () => {
//             console.log('WebSocket connection established');
//         };

//         ws.onmessage = (message) => {
//             console.log('Received message from server:', message.data);

//             // Handle the message received from Spring Boot (processed by Python)
//             setCapturedText(message.data); // Set the received data to state or perform other actions
//         };

//         ws.onclose = () => {
//             console.log('WebSocket connection closed');
//         };

//         return () => {
//             ws.close();
//         };
//     }, []);

//     const startListening = () => {
//         SpeechRecognition.startListening({ continuous: true, language: 'en-US' });
//     };

//     const stopListening = () => {
//         SpeechRecognition.stopListening();
//         setCapturedText(transcript);

//         if (socket) {
//             socket.send(transcript);  // Send the captured text to the server
//         }
//     };

//     if (!browserSupportsSpeechRecognition) {
//         return <p>Your browser does not support speech recognition.</p>;
//     }

//     return (
//         <div className="container">
//             <h2>Speech to Text Converter</h2>
//             <br />
//             <p>
//                 A React hook that converts speech from the microphone to text and makes it available to your React components.
//             </p>

//             <div className="main-content" onClick={() => setTextToCopy(transcript)}>
//                 {transcript}
//             </div>

//             <div className="btn-style">
//                 <button onClick={setCopied}>
//                     {isCopied ? 'Copied!' : 'Copy to clipboard'}
//                 </button>
//                 <button onClick={startListening}>Start Listening</button>
//                 <button onClick={stopListening}>Stop Listening</button>
//             </div>

//             <div>
//                 <h3>Processed Text:</h3>
//                 <p>{capturedText}</p>
//             </div>
//         </div>
//     );
// };

// export default App;








// import React, { useState, useEffect } from 'react';
// import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
// import useClipboard from 'react-use-clipboard';
// import WebSocketComponent from './WebSocketComponent';

// const App = () => {
//     const [textToCopy, setTextToCopy] = useState('');
//     const [isCopied, setCopied] = useClipboard(textToCopy, { successDuration: 1000 });
//     const [capturedText, setCapturedText] = useState('');
//     const [socket, setSocket] = useState(null);
//     const { transcript, browserSupportsSpeechRecognition } = useSpeechRecognition();

//     useEffect(() => {
//         // Initialize WebSocket connection
//         const ws = new WebSocket('ws://localhost:7755/ws');
//         setSocket(ws);

//         ws.onopen = () => {
//             console.log('WebSocket connection established');
//         };

//         ws.onmessage = (message) => {
//             console.log('Received message:', message.data);
//         };

//         ws.onclose = () => {
//             console.log('WebSocket connection closed');
//         };

//         return () => {
//             ws.close();
//         };
//     }, []);

//     const startListening = () => {
//         SpeechRecognition.startListening({ continuous: true, language: 'en-IN' });
//     };

//     const stopListening = () => {
//         SpeechRecognition.stopListening();
//         setCapturedText(transcript);

//         if (socket) {
//             socket.send(transcript);
//         }
//     };

//     if (!browserSupportsSpeechRecognition) {
//         return <p>Your browser does not support speech recognition.</p>;
//     }

//     return (
//         <div className="container">
//             <h2>Speech to Text Converter</h2>
//             <br />
//             <p>
//                 A React hook that converts speech from the microphone to text and makes it available to your React components.
//             </p>

//             <div className="main-content" onClick={() => setTextToCopy(transcript)}>
//                 {transcript}
//             </div>

//             <div className="btn-style">
//                 <button onClick={setCopied}>
//                     {isCopied ? 'Copied!' : 'Copy to clipboard'}
//                 </button>
//                 <button onClick={startListening}>Start Listening</button>
//                 <button onClick={stopListening}>Stop Listening</button>
//             </div>

//           
//         </div>
//     );
// };

// export default App;



// import { useEffect, useState } from 'react';
// import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
// import useClipboard from 'react-use-clipboard';

// const App = () => {
//     const [textToCopy, setTextToCopy] = useState('');
//     const [isCopied, setCopied] = useClipboard(textToCopy, { successDuration: 1000 });
//     const [capturedText, setCapturedText] = useState('');
//     const [socket, setSocket] = useState(null);
//     const { transcript, browserSupportsSpeechRecognition } = useSpeechRecognition();

//     useEffect(() => {
//         const ws = new WebSocket('ws://localhost:7755/ws');
//         setSocket(ws);

//         ws.onopen = () => {
//             console.log('WebSocket connection established');
//         };

//         ws.onmessage = (message) => {
//             console.log('Received message:', message.data);
//         };

//         ws.onclose = () => {
//             console.log('WebSocket connection closed');
//         };

//         return () => {
//             ws.close();
//         };
//     }, []);

//     const startListening = () => {
//         SpeechRecognition.startListening({ continuous: true, language: 'en-IN' });
//     };

//     const stopListening = () => {
//         SpeechRecognition.stopListening();
//         setCapturedText(transcript);

//         if (socket) {
//             socket.send(transcript);
//         }
//     };

//     if (!browserSupportsSpeechRecognition) {
//         return null;
//     }

//     return (
//         <>
//             {/* Your existing JSX code here */}
//         </>
//     );
// };

// export default App;










// import "./App.css"
// import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
// import useClipboard from "react-use-clipboard";
// import {useState} from "react";


// const App = () => {
//     const [textToCopy, setTextToCopy] = useState();
//     const [isCopied, setCopied] = useClipboard(textToCopy, {
//         successDuration:1000
//     });



//     const startListening = () => SpeechRecognition.startListening({ continuous: true, language: 'en-IN' });
//     const { transcript, browserSupportsSpeechRecognition } = useSpeechRecognition();

//     if (!browserSupportsSpeechRecognition) {
//         return null
//     }

    // return (
    //     <>
    //         <div className="container">
    //             <h2>Speech to Text Converter</h2>
    //             <br/>
    //             <p>A React hook that converts speech from the microphone to text and makes it available to your React
    //                 components.</p>

    //             <div className="main-content" onClick={() =>  setTextToCopy(transcript)}>
    //                 {transcript}
    //             </div>

    //             <div className="btn-style">

    //                 <button onClick={setCopied}>
    //                     {isCopied ? 'Copied!' : 'Copy to clipboard'}
    //                 </button>
    //                 <button onClick={startListening}>Start Listening</button>
    //                 <button onClick={SpeechRecognition.stopListening}>Stop Listening</button>

    //             </div>

    //         </div>

    //     </>
    // );
// };

// export default App;