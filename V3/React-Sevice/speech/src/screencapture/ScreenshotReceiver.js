import React, { useEffect, useState } from 'react';

const ScreenshotReceiver = () => {
  const [textData, setTextData] = useState('');

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000');

    ws.onopen = () => {
      console.log('WebSocket connection opened.');
    };

    ws.onmessage = (event) => {
      // Ensure the received data is treated as text
      const text = typeof event.data === 'string' ? event.data : new TextDecoder().decode(event.data);
      console.log('Received text:', text);
      setTextData(text);
    };

    ws.onclose = (event) => {
      console.log(`WebSocket connection closed: ${event.reason}`);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div>
      <h2>Received Text Data</h2>
      <pre>{textData}</pre>
    </div>
  );
};

export default ScreenshotReceiver;









// import React, { useEffect, useState } from 'react';

// const ScreenshotReceiver = () => {
//   const [textData, setTextData] = useState('');

//   useEffect(() => {
//     const ws = new WebSocket('ws://localhost:8000');
    
//     ws.binaryType = 'blob'; // Set the type of data to receive as binary blobs

//     ws.onopen = () => {
//       console.log('WebSocket connection opened.');
//     };

//     ws.onmessage = (event) => {
//       const reader = new FileReader();
//       reader.onload = () => {
//         const text = reader.result;
//         console.log('Received text:', text);
//         setTextData(text);
//       };
//       reader.readAsText(event.data);
//     };

//     ws.onclose = (event) => {
//       console.log(`WebSocket connection closed: ${event.reason}`);
//     };

//     ws.onerror = (error) => {
//       console.error('WebSocket error:', error);
//     };

//     return () => {
//       ws.close();
//     };
//   }, []);

//   return (
//     <div>
//       <h2>Received Text Data</h2>
//       <pre>{textData}</pre>
//     </div>
//   );
// };

// export default ScreenshotReceiver;









// import React, { useEffect, useState } from 'react';

// const ScreenshotReceiver = () => {
//   const [imageUrl, setImageUrl] = useState(null);

//   useEffect(() => {
//     const ws = new WebSocket('ws://localhost:8000/screenshot');
    
//     ws.binaryType = 'blob'; // Set the type of data to receive as binary blobs

//     ws.onopen = () => {
//       console.log('WebSocket connection opened.');
//     };

//     ws.onmessage = (event) => {
//       const imgUrl = URL.createObjectURL(event.data);
//       setImageUrl(imgUrl);
//     };

//     ws.onclose = (event) => {
//       console.log(`WebSocket connection closed: ${event.reason}`);
//     };

//     ws.onerror = (error) => {
//       console.error('WebSocket error:', error);
//     };

//     return () => {
//       ws.close();
//     };
//   }, []);

//   return (
//     <div>
//       <h2>Receiving screenshots...</h2>
//       {imageUrl && <img src={imageUrl} alt="Screenshot" style={{ width: '100%', height: 'auto' }} />}
//     </div>
//   );
// };

// export default ScreenshotReceiver;
