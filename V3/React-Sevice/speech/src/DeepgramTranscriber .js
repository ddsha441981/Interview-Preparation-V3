        import React, { useState, useEffect } from 'react';

        const DeepgramTranscriber = () => {
          const [transcript, setTranscript] = useState('');
          const [isRecording, setIsRecording] = useState(false);
        
          let mediaRecorder;
          let socket;
        
          const startRecording = async () => {
            try {
              setIsRecording(true);
        
              // Capture audio from the user's microphone
              const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
              mediaRecorder = new MediaRecorder(stream);
        
              // Initialize the WebSocket connection to Deepgram
              socket = new WebSocket(`wss://api.deepgram.com/v1/listen?access_token=<YOUR-TOKEN>`);
        
              socket.onopen = () => {
                console.log('Connected to Deepgram');
              };
        
              socket.onmessage = (message) => {
                const receivedData = JSON.parse(message.data);
                const newTranscript = receivedData.channel.alternatives[0].transcript;
                if (newTranscript) {
                  setTranscript((prevTranscript) => prevTranscript + ' ' + newTranscript);
                }
              };
        
              socket.onerror = (error) => {
                console.error('WebSocket Error:', error.message);
                if (error.target.readyState === WebSocket.CLOSED) {
                  console.error('WebSocket connection was closed unexpectedly.');
                } else if (error.target.readyState === WebSocket.CONNECTING) {
                  console.error('WebSocket connection is still attempting to connect.');
                } else if (error.target.readyState === WebSocket.CLOSING) {
                  console.error('WebSocket connection is in the process of closing.');
                }
              };
              
        
              socket.onclose = () => {
                console.log('WebSocket connection closed');
              };
        
              mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0 && socket.readyState === WebSocket.OPEN) {
                  socket.send(event.data);
                }
              };
        
              mediaRecorder.start(250); // Send data every 250ms
            } catch (error) {
              console.error('Error starting recording:', error);
              setIsRecording(false);
            }
          };
        
          const stopRecording = () => {
            setIsRecording(false);
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
              mediaRecorder.stop();
            }
            if (socket) {
              socket.close();
            }
          };
        
          useEffect(() => {
            return () => {
              if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
              }
              if (socket) {
                socket.close();
              }
            };
          }, []);
        
          return (
            <div>
              <h1>Deepgram Real-Time Transcriber</h1>
              <button onClick={isRecording ? stopRecording : startRecording}>
                {isRecording ? 'Stop Recording' : 'Start Recording'}
              </button>
              <p>Transcript: {transcript}</p>
            </div>
          );
        };
        
        export default DeepgramTranscriber;
        
     