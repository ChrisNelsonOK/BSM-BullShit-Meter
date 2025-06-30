import sys
import time
import pyautogui
import pytesseract
from PIL import Image, ImageGrab
from typing import Optional, Tuple
import subprocess
import os

# Platform-specific imports
try:
    if sys.platform == 'win32':
        import win32clipboard
except ImportError:
    pass

try:
    import pyperclip
except ImportError:
    pass

# Disable pyautogui failsafe for better user experience
pyautogui.FAILSAFE = False

class TextCapture:
    """Handles text selection capture and screenshot OCR."""
    
    def __init__(self):
        self.last_clipboard_content = ""
    
    def get_selected_text(self) -> Optional[str]:
        """Attempt to get currently selected text via clipboard."""
        try:
            # Store current clipboard content
            if sys.platform == 'darwin':
                # macOS
                result = subprocess.run(['pbpaste'], capture_output=True, text=True)
                original_clipboard = result.stdout
            elif sys.platform == 'win32':
                # Windows
                try:
                    import win32clipboard
                    win32clipboard.OpenClipboard()
                    try:
                        original_clipboard = win32clipboard.GetClipboardData()
                    except:
                        original_clipboard = ""
                    win32clipboard.CloseClipboard()
                except ImportError:
                    try:
                        import pyperclip
                        original_clipboard = pyperclip.paste()
                    except ImportError:
                        original_clipboard = ""
            else:
                # Linux
                try:
                    import pyperclip
                    original_clipboard = pyperclip.paste()
                except:
                    original_clipboard = ""
            
            # Copy current selection
            pyautogui.hotkey('ctrl', 'c') if sys.platform != 'darwin' else pyautogui.hotkey('cmd', 'c')
            time.sleep(0.1)  # Wait for clipboard to update
            
            # Get new clipboard content
            if sys.platform == 'darwin':
                result = subprocess.run(['pbpaste'], capture_output=True, text=True)
                new_content = result.stdout
            elif sys.platform == 'win32':
                try:
                    import win32clipboard
                    win32clipboard.OpenClipboard()
                    try:
                        new_content = win32clipboard.GetClipboardData()
                    except:
                        new_content = ""
                    win32clipboard.CloseClipboard()
                except ImportError:
                    try:
                        import pyperclip
                        new_content = pyperclip.paste()
                    except ImportError:
                        new_content = ""
            else:
                try:
                    import pyperclip
                    new_content = pyperclip.paste()
                except:
                    new_content = ""
            
            # Restore original clipboard if no new selection
            if new_content == original_clipboard:
                return None
            
            # Restore original clipboard content
            if sys.platform == 'darwin':
                subprocess.run(['pbcopy'], input=original_clipboard, text=True)
            elif sys.platform == 'win32':
                try:
                    import win32clipboard
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardText(original_clipboard)
                    win32clipboard.CloseClipboard()
                except ImportError:
                    try:
                        import pyperclip
                        pyperclip.copy(original_clipboard)
                    except ImportError:
                        pass
            else:
                try:
                    import pyperclip
                    pyperclip.copy(original_clipboard)
                except:
                    pass
            
            return new_content.strip() if new_content else None
            
        except Exception as e:
            print(f"Error getting selected text: {e}")
            return None
    
    def capture_screenshot_area(self, x: int, y: int, width: int, height: int) -> Optional[Image.Image]:
        """Capture a specific area of the screen."""
        try:
            screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            return screenshot
        except Exception as e:
            print(f"Error capturing screenshot area: {e}")
            return None
    
    def capture_full_screenshot(self) -> Optional[Image.Image]:
        """Capture the full screen."""
        try:
            screenshot = ImageGrab.grab()
            return screenshot
        except Exception as e:
            print(f"Error capturing full screenshot: {e}")
            return None
    
    def extract_text_from_image(self, image: Image.Image) -> str:
        """Extract text from image using OCR with improved processing."""
        try:
            # Preprocess image for better OCR
            processed_image = self._preprocess_image_for_ocr(image)
            
            # Use multiple OCR configurations for better results
            configs = [
                r'--oem 3 --psm 6',  # Uniform block of text
                r'--oem 3 --psm 3',  # Fully automatic page segmentation
                r'--oem 3 --psm 4',  # Single column of text
                r'--oem 3 --psm 8',  # Single word
                r'--oem 3 --psm 13'  # Raw line - treat as single text line
            ]
            
            best_text = ""
            best_confidence = 0
            
            for config in configs:
                try:
                    # Get text with confidence data
                    data = pytesseract.image_to_data(processed_image, config=config, output_type=pytesseract.Output.DICT)
                    
                    # Calculate average confidence
                    confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    # Get text
                    text = pytesseract.image_to_string(processed_image, config=config)
                    
                    # Clean and validate text
                    cleaned_text = self._clean_ocr_text(text)
                    
                    if cleaned_text and avg_confidence > best_confidence:
                        best_text = cleaned_text
                        best_confidence = avg_confidence
                        
                except Exception as config_error:
                    print(f"OCR config '{config}' failed: {config_error}")
                    continue
            
            # If no good result, try simple fallback
            if not best_text:
                text = pytesseract.image_to_string(processed_image)
                best_text = self._clean_ocr_text(text)
            
            return best_text
            
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""
    
    def _preprocess_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """Preprocess image to improve OCR accuracy."""
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Resize if too small (OCR works better on larger images)
            width, height = image.size
            if width < 300 or height < 100:
                scale_factor = max(300/width, 100/height, 2.0)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Enhance contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            return image
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return image
    
    def _clean_ocr_text(self, text: str) -> str:
        """Clean OCR text by removing common artifacts and noise."""
        if not text:
            return ""
        
        import re
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common OCR artifacts
        # Remove isolated single characters that are likely noise
        text = re.sub(r'\b[^\w\s]\b', '', text)
        
        # Remove lines with mostly non-alphanumeric characters (likely noise)
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Calculate ratio of alphanumeric characters
            alnum_chars = sum(1 for c in line if c.isalnum())
            if len(line) > 0 and (alnum_chars / len(line)) > 0.3:
                clean_lines.append(line)
        
        # Join lines back together
        cleaned_text = '\n'.join(clean_lines)
        
        # Final cleanup
        cleaned_text = cleaned_text.strip()
        
        return cleaned_text
    
    def get_text_from_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[str]:
        """Get text from screenshot, optionally from a specific region."""
        try:
            if region:
                x, y, width, height = region
                image = self.capture_screenshot_area(x, y, width, height)
            else:
                image = self.capture_full_screenshot()
            
            if image:
                text = self.extract_text_from_image(image)
                return text if text else None
            
            return None
        except Exception as e:
            print(f"Error getting text from screenshot: {e}")
            return None

class InteractiveScreenshotCapture:
    """Interactive screenshot capture with region selection."""
    
    def __init__(self):
        self.start_pos = None
        self.end_pos = None
        self.capturing = False
    
    def capture_region_interactive(self) -> Optional[Tuple[int, int, int, int]]:
        """Capture a region interactively (this would need a GUI overlay)."""
        # This is a simplified version - in a real implementation,
        # you'd create a transparent overlay window for region selection
        try:
            # For now, just capture the full screen and let user specify region
            # In a full implementation, this would show a selection overlay
            screen_width, screen_height = pyautogui.size()
            
            # Return full screen region as fallback
            return (0, 0, screen_width, screen_height)
        except Exception as e:
            print(f"Error in interactive capture: {e}")
            return None

def setup_tesseract():
    """Setup tesseract OCR based on platform."""
    if sys.platform == 'darwin':
        # macOS - common homebrew path
        tesseract_path = '/opt/homebrew/bin/tesseract'
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            # Try alternative path
            tesseract_path = '/usr/local/bin/tesseract'
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
    elif sys.platform == 'win32':
        # Windows - common installation paths
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break
    
    # Linux typically has tesseract in PATH