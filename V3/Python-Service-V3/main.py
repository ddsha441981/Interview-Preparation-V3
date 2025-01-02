import asyncio
import websockets
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

OPENAI_API_KEY = '<YOUR_API_KEY>'
OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

GEMINI_API_KEY = 'YOUR_API_KEY'
GEMINI_API_URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}'

def query_openai(text):
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [{'role': 'user', 'content': text}]
    }
    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        return response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
    except requests.exceptions.RequestException as e:
        logging.error(f"OpenAI API request error: {e}")
        return "Error querying OpenAI API."

def query_gemini(text):
    logging.info("Text Data is: " + text)
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'contents': [{'parts': [{'text': text}]}]
    }
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        
        # Print entire response data for debugging
        # logging.info("Google Gemini API response content: %s", response_data)
        
       
        candidates = response_data.get('candidates', [])
        if not candidates:
            logging.warning("No candidates found in the response.")
            return "No response content available."

        content = candidates[0].get('content', {})
        parts = content.get('parts', [])
        if not parts:
            logging.warning("No parts found in the content.")
            return "No content parts available."

        text_data = ''.join(part.get('text', '') for part in parts)
        
       
        # logging.info("Extracted text from Gemini response: %s", text_data)

        return text_data

    except requests.exceptions.RequestException as e:
        logging.error(f"Google Gemini API request error: {e}")
        return "Error querying Google Gemini API."

async def handle_message(websocket, path):
    logging.info("WebSocket connection opened.")
    try:
       
        message = await websocket.recv()
        logging.info(f"Received message: {message}")

        # Google Gemini APIs
        openai_response = query_openai(message)
        gemini_response = query_gemini(message)
        logging.info("Handle Messages Data------------------------------------ : %s ", gemini_response);

        # Combine responses
        combined_response = (f"OpenAI Response: {openai_response}\n"
                             f"Google Gemini Response: {gemini_response}")

        # Send the combined response
        await websocket.send(combined_response)
        logging.info(f"Sent response: {combined_response}")

    except Exception as e:
        logging.error(f"Error handling message: {e}")
    finally:
        logging.info("WebSocket connection closed.")



async def main():
    logging.info("Starting WebSocket server...")
    async with websockets.serve(handle_message, "localhost", 5000):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())