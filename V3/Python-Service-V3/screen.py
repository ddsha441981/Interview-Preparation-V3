import keyboard
import pyautogui
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import re
import asyncio
import websockets
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Path to the Tesseract executable (update this if you are on Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'  # Update the path if necessary

def preprocess_image(image):
    """Preprocess the image for better OCR accuracy."""
    # Convert image to grayscale
    gray_image = image.convert('L')
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(2)  # Increase contrast
    # Apply a slight blur to remove noise
    processed_image = enhanced_image.filter(ImageFilter.SHARPEN)
    return processed_image

def filter_text(text):
    """Filter text to separate code from plain text."""
    code_lines = []
    plain_text_lines = []

    # Improved regular expression to identify code-like lines
    code_pattern = re.compile(r'^\s*(\b(?:class|def|import|from|return|if|else|for|while|try|except|finally|with|yield|assert|pass|break|continue|print|raise)\b.*|^[ \t]*[\w_]+\s*[:\[\]{}\(\)\=\+\-\*/%<>!&|]+.*)$')

    lines = text.split('\n')
    for line in lines:
        if code_pattern.match(line):
            code_lines.append(line)
        else:
            plain_text_lines.append(line)
    
    return '\n'.join(code_lines), '\n'.join(plain_text_lines)

def handle_encoding_errors(text):
    """Handle characters that cannot be encoded in 'charmap'."""
    return text.encode('utf-8', 'replace').decode('utf-8')

def capture_area(left, top, width, height):
    """Capture a specific area of the screen."""
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    return screenshot

def capture_and_stitch_screenshots():
    """Capture screenshots while scrolling and stitch them together."""
    screenshots = []
    scroll_height = 800  # Adjust this value based on your screen size and scroll increment

    # Capture the initial view
    main_screenshot = capture_area(0, 0, pyautogui.size().width, pyautogui.size().height)
    screenshots.append(main_screenshot)

    current_scroll_position = 0
    while True:
        pyautogui.scroll(-scroll_height)
        current_scroll_position -= scroll_height
        
        screenshot = capture_area(0, current_scroll_position, pyautogui.size().width, pyautogui.size().height)
        screenshots.append(screenshot)
        
        if screenshots[-1].tobytes() == screenshots[-2].tobytes():
            break

    # Capture additional nested areas (if needed)
    nested_scroll_areas = [
        (100, 200, 300, 400),
        (500, 600, 300, 400)
    ]
    for (left, top, width, height) in nested_scroll_areas:
        nested_screenshot = capture_area(left, top, width, height)
        screenshots.append(nested_screenshot)

    # Stitch all screenshots together
    total_height = sum(screenshot.size[1] for screenshot in screenshots)
    stitched_image = Image.new('RGB', (screenshots[0].size[0], total_height))
    y_offset = 0
    for screenshot in screenshots:
        stitched_image.paste(screenshot, (0, y_offset))
        y_offset += screenshot.size[1]

    return stitched_image

async def handle_connection(websocket, path):
    logging.info("WebSocket connection established.")
    try:
        while True:
            if keyboard.is_pressed('print screen'):
                logging.info("Print Screen button pressed. Capturing full-page screenshot...")
                
                stitched_image = capture_and_stitch_screenshots()

                logging.info("Extracting text from screenshot...")
                preprocessed_image = preprocess_image(stitched_image)
                extracted_text = pytesseract.image_to_string(preprocessed_image)
                
                if extracted_text.strip() == "":
                    logging.warning("No text extracted from the image.")
                
                logging.info(f"Extracted text: {extracted_text}")
                
                code_text, plain_text = filter_text(extracted_text)
                logging.info(f"Filtered code text: {code_text}")
                logging.info(f"Filtered plain text: {plain_text}")

                text_to_send = f"Code:\n{code_text}\n\nPlain Text:\n{plain_text}"
                text_to_send = handle_encoding_errors(text_to_send)
                logging.info(f"Sending text: {text_to_send}")  # Log the data to be sent
                
                # Write the extracted and filtered text to a file
                file_path = "extracted_text.txt"
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(text_to_send)
                logging.info(f"Text data written to file: {file_path}")

                # Send the text as a string
                await websocket.send(text_to_send.encode('utf-8'))
                logging.info("Filtered text sent.")
                
                # Close the connection after sending the text
                await websocket.close()
                logging.info("WebSocket connection closed after sending text.")
                break  # Exit the loop after processing one message
            
            else:
                await asyncio.sleep(0.1)
    except websockets.ConnectionClosed as e:
        logging.error(f"WebSocket connection closed: {e}")
    except Exception as e:
        logging.error(f"Error occurred: {e}")

async def main():
    start_server = websockets.serve(handle_connection, "localhost", 8000)
    await start_server
    logging.info("WebSocket server started on ws://localhost:8000")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())






# import keyboard
# import pyautogui
# from PIL import Image
# import pytesseract
# import re
# import asyncio
# import websockets
# import logging

# # Configure logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# # Path to the Tesseract executable (update this if you are on Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'  # Update the path if necessary

# def filter_text(text):
#     """Filter text to separate code from plain text."""
#     code_lines = []
#     plain_text_lines = []

#     # Regular expression to identify code-like lines (simple example)
#     code_pattern = re.compile(r'^\s*([A-Za-z_]\w*\s*=\s*.*|^\s*[\w\s]+\s*\(\s*\)\s*\{.*\})')

#     lines = text.split('\n')
#     for line in lines:
#         if code_pattern.match(line):
#             code_lines.append(line)
#         else:
#             plain_text_lines.append(line)
    
#     return '\n'.join(code_lines), '\n'.join(plain_text_lines)

# def capture_and_stitch_screenshots():
#     """Capture screenshots while scrolling and stitch them together."""
#     screenshots = []
#     scroll_height = 800  # Adjust this value based on your screen size and scroll increment
    
#     def capture_area(left, top, width, height):
#         screenshot = pyautogui.screenshot(region=(left, top, width, height))
#         return screenshot

#     # Capture the initial view
#     main_screenshot = capture_area(0, 0, pyautogui.size().width, pyautogui.size().height)
#     screenshots.append(main_screenshot)

#     current_scroll_position = 0
#     while True:
#         pyautogui.scroll(-scroll_height)
#         current_scroll_position -= scroll_height
        
#         screenshot = capture_area(0, current_scroll_position, pyautogui.size().width, pyautogui.size().height)
#         screenshots.append(screenshot)
        
#         if screenshots[-1].tobytes() == screenshots[-2].tobytes():
#             break

#     # Capture additional nested areas
#     nested_scroll_areas = [
#         (100, 200, 300, 400),
#         (500, 600, 300, 400)
#     ]
#     for (left, top, width, height) in nested_scroll_areas:
#         nested_screenshot = capture_area(left, top, width, height)
#         screenshots.append(nested_screenshot)

#     # Stitch all screenshots together
#     total_height = sum(screenshot.size[1] for screenshot in screenshots)
#     stitched_image = Image.new('RGB', (screenshots[0].size[0], total_height))
#     y_offset = 0
#     for screenshot in screenshots:
#         stitched_image.paste(screenshot, (0, y_offset))
#         y_offset += screenshot.size[1]

#     return stitched_image

# import os

# async def handle_connection(websocket, path):
#     logging.info("WebSocket connection established.")
#     try:
#         while True:
#             if keyboard.is_pressed('print screen'):
#                 logging.info("Print Screen button pressed. Capturing full-page screenshot...")
                
#                 stitched_image = capture_and_stitch_screenshots()

#                 logging.info("Extracting text from screenshot...")
#                 extracted_text = pytesseract.image_to_string(stitched_image)
                
#                 if extracted_text.strip() == "":
#                     logging.warning("No text extracted from the image.")
                
#                 logging.info(f"Extracted text: {extracted_text}")
                
#                 code_text, plain_text = filter_text(extracted_text)
#                 logging.info(f"Filtered code text: {code_text}")
#                 logging.info(f"Filtered plain text: {plain_text}")

#                 text_to_send = f"Code:\n{code_text}\n\nPlain Text:\n{plain_text}"
#                 logging.info(f"Sending text: {text_to_send}")  # Log the data to be sent
                
#                 # Write the extracted and filtered text to a file
#                 file_path = "extracted_text.txt"
#                 with open(file_path, 'w') as file:
#                     file.write(text_to_send)
#                 logging.info(f"Text data written to file: {file_path}")

#                 # Send the text as a string
#                 await websocket.send(text_to_send.encode('utf-8'))
#                 logging.info("Filtered text sent.")
                
#                 # Close the connection after sending the text
#                 await websocket.close()
#                 logging.info("WebSocket connection closed after sending text.")
#                 break  # Exit the loop after processing one message
            
#             else:
#                 await asyncio.sleep(0.1)
#     except websockets.ConnectionClosed as e:
#         logging.error(f"WebSocket connection closed: {e}")
#     except Exception as e:
#         logging.error(f"Error occurred: {e}")


# async def main():
#     start_server = websockets.serve(handle_connection, "localhost", 8000)
#     await start_server
#     logging.info("WebSocket server started on ws://localhost:8000")
#     await asyncio.Future()

# if __name__ == "__main__":
#     asyncio.run(main())













# import keyboard
# import pyautogui
# from PIL import Image
# import pytesseract
# import re
# import asyncio
# import websockets
# import logging

# # Configure logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# # Path to the Tesseract executable (update this if you are on Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'  # Update the path if necessary

# def filter_text(text):
#     """Filter text to separate code from plain text."""
#     code_lines = []
#     plain_text_lines = []

#     # Regular expression to identify code-like lines (simple example)
#     code_pattern = re.compile(r'^\s*([A-Za-z_]\w*\s*=\s*.*|^\s*[\w\s]+\s*\(\s*\)\s*\{.*\})')

#     lines = text.split('\n')
#     for line in lines:
#         if code_pattern.match(line):
#             code_lines.append(line)
#         else:
#             plain_text_lines.append(line)
    
#     return '\n'.join(code_lines), '\n'.join(plain_text_lines)

# def capture_and_stitch_screenshots():
#     """Capture screenshots while scrolling and stitch them together."""
#     screenshots = []
#     scroll_height = 800  # Adjust this value based on your screen size and scroll increment
    
#     def capture_area(left, top, width, height):
#         screenshot = pyautogui.screenshot(region=(left, top, width, height))
#         return screenshot

#     # Capture the initial view
#     main_screenshot = capture_area(0, 0, pyautogui.size().width, pyautogui.size().height)
#     screenshots.append(main_screenshot)

#     current_scroll_position = 0
#     while True:
#         pyautogui.scroll(-scroll_height)
#         current_scroll_position -= scroll_height
        
#         screenshot = capture_area(0, current_scroll_position, pyautogui.size().width, pyautogui.size().height)
#         screenshots.append(screenshot)
        
#         if screenshots[-1].tobytes() == screenshots[-2].tobytes():
#             break

#     # Capture additional nested areas
#     nested_scroll_areas = [
#         (100, 200, 300, 400),
#         (500, 600, 300, 400)
#     ]
#     for (left, top, width, height) in nested_scroll_areas:
#         nested_screenshot = capture_area(left, top, width, height)
#         screenshots.append(nested_screenshot)

#     # Stitch all screenshots together
#     total_height = sum(screenshot.size[1] for screenshot in screenshots)
#     stitched_image = Image.new('RGB', (screenshots[0].size[0], total_height))
#     y_offset = 0
#     for screenshot in screenshots:
#         stitched_image.paste(screenshot, (0, y_offset))
#         y_offset += screenshot.size[1]

#     return stitched_image

# async def handle_connection(websocket, path):
#     logging.info("WebSocket connection established.")
#     try:
#         while True:
#             if keyboard.is_pressed('print screen'):
#                 logging.info("Print Screen button pressed. Capturing full-page screenshot...")
                
#                 stitched_image = capture_and_stitch_screenshots()

#                 logging.info("Extracting text from screenshot...")
#                 extracted_text = pytesseract.image_to_string(stitched_image)
                
#                 if extracted_text.strip() == "":
#                     logging.warning("No text extracted from the image.")
                
#                 logging.info(f"Extracted text: {extracted_text}")
                
#                 code_text, plain_text = filter_text(extracted_text)
#                 logging.info(f"Filtered code text: {code_text}")
#                 logging.info(f"Filtered plain text: {plain_text}")

#                 text_to_send = f"Code:\n{code_text}\n\nPlain Text:\n{plain_text}"
#                 logging.info(f"Sending text: {text_to_send}")  # Log the data to be sent
                
#                 # Send the text as a string
#                 await websocket.send(text_to_send)
#                 logging.info("Filtered text sent.")
                
#                 while keyboard.is_pressed('print screen'):
#                     await asyncio.sleep(0.1)
#             else:
#                 await asyncio.sleep(0.1)
#     except websockets.ConnectionClosed as e:
#         logging.error(f"WebSocket connection closed: {e}")
#     except Exception as e:
#         logging.error(f"Error occurred: {e}")

# async def main():
#     start_server = websockets.serve(handle_connection, "localhost", 8000)
#     await start_server
#     logging.info("WebSocket server started on ws://localhost:8000")
#     await asyncio.Future()

# if __name__ == "__main__":
#     asyncio.run(main())














# import keyboard
# import pyautogui
# from PIL import Image
# import pytesseract
# import re
# import asyncio
# import websockets
# import logging

# # Configure logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# # Path to the Tesseract executable (update this if you are on Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'  # Update the path if necessary

# def filter_text(text):
#     """Filter text to separate code from plain text."""
#     code_lines = []
#     plain_text_lines = []

#     # Regular expression to identify code-like lines (simple example)
#     code_pattern = re.compile(r'^\s*([A-Za-z_]\w*\s*=\s*.*|^\s*[\w\s]+\s*\(\s*\)\s*\{.*\})')

#     lines = text.split('\n')
#     for line in lines:
#         if code_pattern.match(line):
#             code_lines.append(line)
#         else:
#             plain_text_lines.append(line)
    
#     return '\n'.join(code_lines), '\n'.join(plain_text_lines)

# def capture_and_stitch_screenshots():
#     """Capture screenshots while scrolling and stitch them together."""
#     screenshots = []
#     scroll_height = 800  # Adjust this value based on your screen size and scroll increment
    
#     def capture_area(left, top, width, height):
#         screenshot = pyautogui.screenshot(region=(left, top, width, height))
#         return screenshot

#     # Capture the initial view
#     main_screenshot = capture_area(0, 0, pyautogui.size().width, pyautogui.size().height)
#     screenshots.append(main_screenshot)

#     current_scroll_position = 0
#     while True:
#         pyautogui.scroll(-scroll_height)
#         current_scroll_position -= scroll_height
        
#         screenshot = capture_area(0, current_scroll_position, pyautogui.size().width, pyautogui.size().height)
#         screenshots.append(screenshot)
        
#         if screenshots[-1].tobytes() == screenshots[-2].tobytes():
#             break

#     # Capture additional nested areas
#     nested_scroll_areas = [
#         (100, 200, 300, 400),
#         (500, 600, 300, 400)
#     ]
#     for (left, top, width, height) in nested_scroll_areas:
#         nested_screenshot = capture_area(left, top, width, height)
#         screenshots.append(nested_screenshot)

#     # Stitch all screenshots together
#     total_height = sum(screenshot.size[1] for screenshot in screenshots)
#     stitched_image = Image.new('RGB', (screenshots[0].size[0], total_height))
#     y_offset = 0
#     for screenshot in screenshots:
#         stitched_image.paste(screenshot, (0, y_offset))
#         y_offset += screenshot.size[1]

#     return stitched_image

# async def handle_connection(websocket, path):
#     logging.info("WebSocket connection established.")
#     try:
#         while True:
#             if keyboard.is_pressed('print screen'):
#                 logging.info("Print Screen button pressed. Capturing full-page screenshot...")
                
#                 stitched_image = capture_and_stitch_screenshots()

#                 logging.info("Extracting text from screenshot...")
#                 extracted_text = pytesseract.image_to_string(stitched_image)
                
#                 if extracted_text.strip() == "":
#                     logging.warning("No text extracted from the image.")
                
#                 logging.info(f"Extracted text: {extracted_text}")
                
#                 code_text, plain_text = filter_text(extracted_text)
#                 logging.info(f"Filtered code text: {code_text}")
#                 logging.info(f"Filtered plain text: {plain_text}")

#                 text_to_send = f"Code:\n{code_text}\n\nPlain Text:\n{plain_text}"
#                 logging.info(f"Sending text: {text_to_send}")  # Log the data to be sent
#                 await websocket.send(text_to_send.encode('utf-8'))
#                 logging.info("Filtered text sent.")
                
#                 while keyboard.is_pressed('print screen'):
#                     await asyncio.sleep(0.1)
#             else:
#                 await asyncio.sleep(0.1)
#     except websockets.ConnectionClosed as e:
#         logging.error(f"WebSocket connection closed: {e}")
#     except Exception as e:
#         logging.error(f"Error occurred: {e}")

# async def main():
#     start_server = websockets.serve(handle_connection, "localhost", 8000)
#     await start_server
#     logging.info("WebSocket server started on ws://localhost:8000")
#     await asyncio.Future()

# if __name__ == "__main__":
#     asyncio.run(main())










# import keyboard
# import pyautogui
# from PIL import Image
# import pytesseract
# import io
# import asyncio
# import websockets
# import logging
# import re
# import cv2
# import numpy as np

# # Configure logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# # Path to the Tesseract executable (update this if you are on Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'  # Update the path if necessary

# def filter_text(text):
#     """Filter text to separate code from plain text."""
#     code_lines = []
#     plain_text_lines = []

#     # Regular expression to identify code-like lines (simple example)
#     code_pattern = re.compile(r'^\s*([A-Za-z_]\w*\s*=\s*.*|^\s*[\w\s]+\s*\(\s*\)\s*\{.*\})')

#     lines = text.split('\n')
#     for line in lines:
#         if code_pattern.match(line):
#             code_lines.append(line)
#         else:
#             plain_text_lines.append(line)
    
#     return '\n'.join(code_lines), '\n'.join(plain_text_lines)

# def capture_and_stitch_screenshots():
#     """Capture screenshots while scrolling and stitch them together."""
#     screenshots = []
#     scroll_height = 800  # Adjust this value based on your screen size and scroll increment
    
#     # Function to capture a screenshot of a specific area
#     def capture_area(left, top, width, height):
#         screenshot = pyautogui.screenshot(region=(left, top, width, height))
#         return screenshot

#     # Capture the main area of the page
#     main_screenshot = capture_area(0, 0, pyautogui.size().width, pyautogui.size().height)
#     screenshots.append(main_screenshot)

#     # Scroll and capture more screenshots
#     current_scroll_position = 0
#     while True:
#         pyautogui.scroll(-scroll_height)
#         current_scroll_position -= scroll_height
        
#         # Capture the visible part of the page
#         screenshot = capture_area(0, current_scroll_position, pyautogui.size().width, pyautogui.size().height)
#         screenshots.append(screenshot)
        
#         # Simple check: If the last two screenshots are identical, stop scrolling
#         if screenshots[-1].tobytes() == screenshots[-2].tobytes():
#             break

#     # Example of capturing nested scrollable areas (manual configuration required)
#     nested_scroll_areas = [
#         (100, 200, 300, 400),  # Example coordinates for a nested scrollable area
#         (500, 600, 300, 400)   # Example coordinates for another nested scrollable area
#     ]
#     for (left, top, width, height) in nested_scroll_areas:
#         nested_screenshot = capture_area(left, top, width, height)
#         screenshots.append(nested_screenshot)

#     # Stitch screenshots together
#     total_height = sum(screenshot.size[1] for screenshot in screenshots)
#     stitched_image = Image.new('RGB', (screenshots[0].size[0], total_height))
#     y_offset = 0
#     for screenshot in screenshots:
#         stitched_image.paste(screenshot, (0, y_offset))
#         y_offset += screenshot.size[1]

#     return stitched_image

# async def handle_connection(websocket, path):
#     logging.info("WebSocket connection established.")
#     try:
#         while True:
#             if keyboard.is_pressed('print screen'):
#                 logging.info("Print Screen button pressed. Capturing full-page screenshot...")
                
#                 # Capture and stitch the screenshots
#                 stitched_image = capture_and_stitch_screenshots()

#                 # Perform OCR on the stitched screenshot
#                 logging.info("Extracting text from screenshot...")
#                 extracted_text = pytesseract.image_to_string(stitched_image)
#                 logging.info(f"Extracted text: {extracted_text}")

#                 # Filter extracted text
#                 code_text, plain_text = filter_text(extracted_text)
#                 logging.info(f"Filtered code text: {code_text}")
#                 logging.info(f"Filtered plain text: {plain_text}")

#                 # Send extracted text over WebSocket
#                 await websocket.send(f"Code:\n{code_text}\n\nPlain Text:\n{plain_text}".encode('utf-8'))
#                 logging.info("Filtered text sent.")
                
#                 # To avoid sending multiple texts for a single press
#                 while keyboard.is_pressed('print screen'):
#                     await asyncio.sleep(0.1)
#             else:
#                 await asyncio.sleep(0.1)
#     except websockets.ConnectionClosed as e:
#         logging.error(f"WebSocket connection closed: {e}")
#     except Exception as e:
#         logging.error(f"Error occurred: {e}")

# async def main():
#     start_server = websockets.serve(handle_connection, "localhost", 8000)
#     await start_server
#     logging.info("WebSocket server started on ws://localhost:8000")
#     await asyncio.Future()  # Run forever

# if __name__ == "__main__":
#     asyncio.run(main())













# import keyboard
# import pyautogui
# from PIL import Image
# import pytesseract
# import io
# import asyncio
# import websockets
# import logging
# import re

# # Configure logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# # Path to the Tesseract executable (update this if you are on Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'  # Update the path if necessary

# def filter_text(text):
#     """Filter text to separate code from plain text."""
#     code_lines = []
#     plain_text_lines = []

#     # Regular expression to identify code-like lines (simple example)
#     code_pattern = re.compile(r'^\s*([A-Za-z_]\w*\s*=\s*.*|^\s*[\w\s]+\s*\(\s*\)\s*\{.*\})')

#     lines = text.split('\n')
#     for line in lines:
#         if code_pattern.match(line):
#             code_lines.append(line)
#         else:
#             plain_text_lines.append(line)
    
#     return '\n'.join(code_lines), '\n'.join(plain_text_lines)

# def capture_and_stitch_screenshots():
#     """Capture screenshots while scrolling and stitch them together."""
#     screenshots = []
#     scroll_height = 800  # Adjust this value based on your screen size and scroll increment

#     # Capture the first screenshot
#     screenshot = pyautogui.screenshot()
#     screenshots.append(screenshot)

#     # Scroll and capture more screenshots
#     while True:
#         pyautogui.scroll(-scroll_height)
#         screenshot = pyautogui.screenshot()
#         screenshots.append(screenshot)
        
#         # Simple check: If the last two screenshots are identical, stop scrolling
#         if screenshots[-1].tobytes() == screenshots[-2].tobytes():
#             break

#     # Stitch screenshots together
#     total_height = sum(screenshot.size[1] for screenshot in screenshots)
#     stitched_image = Image.new('RGB', (screenshots[0].size[0], total_height))
#     y_offset = 0
#     for screenshot in screenshots:
#         stitched_image.paste(screenshot, (0, y_offset))
#         y_offset += screenshot.size[1]

#     return stitched_image

# async def handle_connection(websocket, path):
#     logging.info("WebSocket connection established.")
#     try:
#         while True:
#             if keyboard.is_pressed('print screen'):
#                 logging.info("Print Screen button pressed. Capturing full-page screenshot...")
                
#                 # Capture and stitch the screenshots
#                 stitched_image = capture_and_stitch_screenshots()

#                 # Perform OCR on the stitched screenshot
#                 logging.info("Extracting text from screenshot...")
#                 extracted_text = pytesseract.image_to_string(stitched_image)
#                 logging.info(f"Extracted text: {extracted_text}")

#                 # Filter extracted text
#                 code_text, plain_text = filter_text(extracted_text)
#                 logging.info(f"Filtered code text: {code_text}")
#                 logging.info(f"Filtered plain text: {plain_text}")

#                 # Send extracted text over WebSocket
#                 await websocket.send(f"Code:\n{code_text}\n\nPlain Text:\n{plain_text}".encode('utf-8'))
#                 logging.info("Filtered text sent.")
                
#                 # To avoid sending multiple texts for a single press
#                 while keyboard.is_pressed('print screen'):
#                     await asyncio.sleep(0.1)
#             else:
#                 await asyncio.sleep(0.1)
#     except websockets.ConnectionClosed as e:
#         logging.error(f"WebSocket connection closed: {e}")
#     except Exception as e:
#         logging.error(f"Error occurred: {e}")

# async def main():
#     start_server = websockets.serve(handle_connection, "localhost", 8000)
#     await start_server
#     logging.info("WebSocket server started on ws://localhost:8000")
#     await asyncio.Future()  # Run forever

# if __name__ == "__main__":
#     asyncio.run(main())









# import keyboard
# from PIL import ImageGrab, Image
# import io
# import asyncio
# import websockets
# import pytesseract
# import logging
# import re

# # Configure logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# # Path to the Tesseract executable (update this if you are on Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'  # Update the path if necessary

# def filter_text(text):
#     """Filter text to separate code from plain text."""
#     code_lines = []
#     plain_text_lines = []

#     # Regular expression to identify code-like lines (simple example)
#     code_pattern = re.compile(r'^\s*([A-Za-z_]\w*\s*=\s*.*|^\s*[\w\s]+\s*\(\s*\)\s*\{.*\})')

#     lines = text.split('\n')
#     for line in lines:
#         if code_pattern.match(line):
#             code_lines.append(line)
#         else:
#             plain_text_lines.append(line)
    
#     return '\n'.join(code_lines), '\n'.join(plain_text_lines)

# async def handle_connection(websocket, path):
#     logging.info("WebSocket connection established.")
#     try:
#         while True:
#             if keyboard.is_pressed('print screen'):
#                 # Capture screenshot
#                 logging.info("Print Screen button pressed. Capturing screenshot...")
#                 screenshot = ImageGrab.grab()
#                 buffer = io.BytesIO()
#                 screenshot.save(buffer, format='PNG')
#                 screenshot_data = buffer.getvalue()

#                 # Perform OCR on the screenshot
#                 logging.info("Extracting text from screenshot...")
#                 screenshot_image = Image.open(io.BytesIO(screenshot_data))
#                 extracted_text = pytesseract.image_to_string(screenshot_image)
#                 logging.info(f"Extracted text: {extracted_text}")

#                 # Filter extracted text
#                 code_text, plain_text = filter_text(extracted_text)
#                 logging.info(f"Filtered code text: {code_text}")
#                 logging.info(f"Filtered plain text: {plain_text}")

#                 # Send extracted text over WebSocket (you can choose to send code_text, plain_text, or both)
#                 await websocket.send(f"Code:\n{code_text}\n\nPlain Text:\n{plain_text}".encode('utf-8'))
#                 logging.info("Filtered text sent.")
                
#                 # To avoid sending multiple texts for a single press
#                 while keyboard.is_pressed('print screen'):
#                     await asyncio.sleep(0.1)
#             else:
#                 await asyncio.sleep(0.1)
#     except websockets.ConnectionClosed as e:
#         logging.error(f"WebSocket connection closed: {e}")
#     except Exception as e:
#         logging.error(f"Error occurred: {e}")

# async def main():
#     start_server = websockets.serve(handle_connection, "localhost", 8000)
#     await start_server
#     logging.info("WebSocket server started on ws://localhost:8000")
#     await asyncio.Future()  # Run forever

# if __name__ == "__main__":
#     asyncio.run(main())














# # import keyboard
# # from PIL import ImageGrab
# # import io
# # import asyncio
# # import websockets

# # async def handle_connection(websocket, path):
# #     print("WebSocket connection established.")
# #     try:
# #         while True:
# #             if keyboard.is_pressed('print screen'):
# #                 # Capture screenshot
# #                 screenshot = ImageGrab.grab()
# #                 buffer = io.BytesIO()
# #                 screenshot.save(buffer, format='PNG')
# #                 screenshot_data = buffer.getvalue()
                
# #                 # Send screenshot data
# #                 await websocket.send(screenshot_data)
# #                 print("Screenshot sent.")
                
# #                 # To avoid sending multiple screenshots for a single press
# #                 while keyboard.is_pressed('print screen'):
# #                     await asyncio.sleep(0.1)
# #             else:
# #                 await asyncio.sleep(0.1)
# #     except websockets.ConnectionClosed as e:
# #         print(f"WebSocket connection closed: {e}")

# # async def main():
# #     start_server = websockets.serve(handle_connection, "localhost", 8000)
# #     await start_server
# #     print("WebSocket server started on ws://localhost:8000")
# #     await asyncio.Future()  # Run forever

# # if __name__ == "__main__":
# #     asyncio.run(main())
