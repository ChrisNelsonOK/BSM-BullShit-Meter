"""
Enhanced OCR Pipeline with OpenCV preprocessing, region selection, and caching.

This module provides advanced OCR capabilities including:
- OpenCV-based image preprocessing
- Interactive region selection
- Screenshot caching
- Progress reporting
- Multi-threaded OCR processing
"""

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor
import json

import numpy as np
import pytesseract
from PIL import Image, ImageGrab, ImageDraw, ImageEnhance
import cv2

logger = logging.getLogger(__name__)


class PreprocessingMode(Enum):
    """Available preprocessing modes for different content types."""
    DOCUMENT = "document"  # Clean documents with good contrast
    SCREENSHOT = "screenshot"  # Computer screenshots
    PHOTO = "photo"  # Photos of text (e.g., from camera)
    MIXED = "mixed"  # Mixed content
    AUTO = "auto"  # Automatically detect best mode


@dataclass
class OCRRegion:
    """Represents a region of interest for OCR."""
    x: int
    y: int
    width: int
    height: int
    name: Optional[str] = None
    
    def to_bbox(self) -> Tuple[int, int, int, int]:
        """Convert to bbox format (x1, y1, x2, y2)."""
        return (self.x, self.y, self.x + self.width, self.y + self.height)
    
    def from_bbox(bbox: Tuple[int, int, int, int]) -> 'OCRRegion':
        """Create from bbox format."""
        return OCRRegion(bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1])


@dataclass
class OCRResult:
    """Result from OCR processing."""
    text: str
    confidence: float
    regions: List[OCRRegion]
    preprocessing_mode: PreprocessingMode
    processing_time: float
    cache_hit: bool = False
    error: Optional[str] = None


class OCRCache:
    """Simple in-memory cache for OCR results."""
    
    def __init__(self, max_size: int = 50, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Tuple[OCRResult, float]] = {}
    
    def _get_image_hash(self, image: Image.Image) -> str:
        """Generate a hash for an image."""
        # Convert to bytes and hash
        img_bytes = image.tobytes()
        return hashlib.md5(img_bytes).hexdigest()
    
    def get(self, image: Image.Image) -> Optional[OCRResult]:
        """Get cached result if available and not expired."""
        img_hash = self._get_image_hash(image)
        
        if img_hash in self.cache:
            result, timestamp = self.cache[img_hash]
            if time.time() - timestamp < self.ttl_seconds:
                # Mark as cache hit
                result.cache_hit = True
                return result
            else:
                # Expired, remove from cache
                del self.cache[img_hash]
        
        return None
    
    def put(self, image: Image.Image, result: OCRResult):
        """Cache an OCR result."""
        # Implement simple LRU by removing oldest if at capacity
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        img_hash = self._get_image_hash(image)
        self.cache[img_hash] = (result, time.time())
    
    def clear(self):
        """Clear the cache."""
        self.cache.clear()


class ImagePreprocessor:
    """Advanced image preprocessing using OpenCV."""
    
    @staticmethod
    def pil_to_cv2(image: Image.Image) -> np.ndarray:
        """Convert PIL Image to OpenCV format."""
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    @staticmethod
    def cv2_to_pil(image: np.ndarray) -> Image.Image:
        """Convert OpenCV image to PIL format."""
        return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    def preprocess(self, image: Image.Image, mode: PreprocessingMode) -> Image.Image:
        """Preprocess image based on mode."""
        if mode == PreprocessingMode.AUTO:
            mode = self._detect_best_mode(image)
        
        # Convert to OpenCV format
        cv_image = self.pil_to_cv2(image)
        
        # Apply preprocessing based on mode
        if mode == PreprocessingMode.DOCUMENT:
            processed = self._preprocess_document(cv_image)
        elif mode == PreprocessingMode.SCREENSHOT:
            processed = self._preprocess_screenshot(cv_image)
        elif mode == PreprocessingMode.PHOTO:
            processed = self._preprocess_photo(cv_image)
        else:  # MIXED
            processed = self._preprocess_mixed(cv_image)
        
        # Convert back to PIL
        return self.cv2_to_pil(processed)
    
    def _detect_best_mode(self, image: Image.Image) -> PreprocessingMode:
        """Automatically detect the best preprocessing mode."""
        cv_image = self.pil_to_cv2(image)
        
        # Analyze image characteristics
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Check contrast
        contrast = gray.std()
        
        # Check noise level
        noise_level = self._estimate_noise(gray)
        
        # Check if it looks like a screenshot (sharp edges, consistent colors)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Decision logic
        if contrast > 60 and noise_level < 10 and edge_density > 0.1:
            return PreprocessingMode.SCREENSHOT
        elif contrast > 40 and noise_level < 20:
            return PreprocessingMode.DOCUMENT
        elif noise_level > 30:
            return PreprocessingMode.PHOTO
        else:
            return PreprocessingMode.MIXED
    
    def _estimate_noise(self, gray_image: np.ndarray) -> float:
        """Estimate noise level in image."""
        # Use Laplacian variance as noise metric
        laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
        return laplacian.var()
    
    def _preprocess_document(self, image: np.ndarray) -> np.ndarray:
        """Preprocess clean document images."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply slight blur to reduce noise
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    
    def _preprocess_screenshot(self, image: np.ndarray) -> np.ndarray:
        """Preprocess computer screenshots."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Sharpen
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(gray, -1, kernel)
        
        # Simple thresholding for screenshots
        _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    
    def _preprocess_photo(self, image: np.ndarray) -> np.ndarray:
        """Preprocess photos of text."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Correct skew
        coords = np.column_stack(np.where(denoised > 0))
        if len(coords) > 0:
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = 90 + angle
            if abs(angle) > 0.5:
                (h, w) = denoised.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                denoised = cv2.warpAffine(denoised, M, (w, h),
                                         flags=cv2.INTER_CUBIC,
                                         borderMode=cv2.BORDER_REPLICATE)
        
        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 21, 10
        )
        
        return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    
    def _preprocess_mixed(self, image: np.ndarray) -> np.ndarray:
        """Preprocess mixed content."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Mild denoising
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Adaptive thresholding with larger block size
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 15, 5
        )
        
        return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)


class EnhancedOCR:
    """Enhanced OCR with preprocessing, caching, and region support."""
    
    def __init__(self, cache_size: int = 50):
        self.preprocessor = ImagePreprocessor()
        self.cache = OCRCache(max_size=cache_size)
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def process_image(
        self,
        image: Image.Image,
        mode: PreprocessingMode = PreprocessingMode.AUTO,
        regions: Optional[List[OCRRegion]] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> OCRResult:
        """
        Process an image with OCR.
        
        Args:
            image: PIL Image to process
            mode: Preprocessing mode to use
            regions: Optional list of regions to process
            progress_callback: Optional callback for progress updates
        
        Returns:
            OCRResult with extracted text and metadata
        """
        start_time = time.time()
        
        # Check cache first
        cached_result = self.cache.get(image)
        if cached_result:
            logger.info("OCR cache hit")
            return cached_result
        
        try:
            # Report progress
            if progress_callback:
                progress_callback(10)
            
            # Preprocess image
            logger.info(f"Preprocessing image with mode: {mode}")
            preprocessed = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self.preprocessor.preprocess,
                image,
                mode
            )
            
            if progress_callback:
                progress_callback(30)
            
            # Process regions or full image
            if regions:
                text_results = []
                for i, region in enumerate(regions):
                    if progress_callback:
                        progress = 30 + (50 * i / len(regions))
                        progress_callback(progress)
                    
                    # Crop to region
                    cropped = preprocessed.crop(region.to_bbox())
                    
                    # OCR the region
                    region_text = await self._ocr_image(cropped)
                    text_results.append(region_text)
                
                # Combine results
                full_text = "\n\n".join(text_results)
                confidence = np.mean([self._estimate_confidence(t) for t in text_results])
            else:
                # Process full image
                full_text = await self._ocr_image(preprocessed)
                confidence = self._estimate_confidence(full_text)
                regions = []
            
            if progress_callback:
                progress_callback(90)
            
            # Create result
            result = OCRResult(
                text=full_text,
                confidence=confidence,
                regions=regions,
                preprocessing_mode=mode,
                processing_time=time.time() - start_time,
                cache_hit=False
            )
            
            # Cache the result
            self.cache.put(image, result)
            
            if progress_callback:
                progress_callback(100)
            
            logger.info(f"OCR completed in {result.processing_time:.2f}s with confidence {confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"OCR processing error: {e}")
            return OCRResult(
                text="",
                confidence=0.0,
                regions=regions or [],
                preprocessing_mode=mode,
                processing_time=time.time() - start_time,
                error=str(e)
            )
    
    async def _ocr_image(self, image: Image.Image) -> str:
        """Perform OCR on a preprocessed image."""
        # Try multiple PSM modes for best results
        psm_modes = [6, 3, 4, 8, 11]  # Different page segmentation modes
        results = []
        
        for psm in psm_modes:
            try:
                config = f'--oem 3 --psm {psm}'
                text = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    pytesseract.image_to_string,
                    image,
                    config=config
                )
                
                if text.strip():
                    results.append((text, len(text.strip())))
            except Exception as e:
                logger.debug(f"PSM {psm} failed: {e}")
                continue
        
        # Return the longest valid result
        if results:
            results.sort(key=lambda x: x[1], reverse=True)
            return self._clean_text(results[0][0])
        
        # Fallback to default
        text = await asyncio.get_event_loop().run_in_executor(
            self.executor,
            pytesseract.image_to_string,
            image
        )
        return self._clean_text(text)
    
    def _clean_text(self, text: str) -> str:
        """Clean OCR output text."""
        if not text:
            return ""
        
        import re
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove common OCR artifacts
        text = re.sub(r'[^\w\s\-.,!?;:()\[\]{}"\'/@#$%^&*+=<>]', '', text)
        
        # Remove lines that are mostly noise
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line has reasonable content
            alnum_count = sum(1 for c in line if c.isalnum())
            if len(line) > 0 and (alnum_count / len(line)) > 0.5:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _estimate_confidence(self, text: str) -> float:
        """Estimate confidence based on text quality."""
        if not text:
            return 0.0
        
        # Simple heuristics for confidence
        factors = []
        
        # Length factor
        if len(text) > 10:
            factors.append(0.9)
        elif len(text) > 5:
            factors.append(0.7)
        else:
            factors.append(0.3)
        
        # Word ratio
        words = text.split()
        if words:
            avg_word_len = sum(len(w) for w in words) / len(words)
            if 3 <= avg_word_len <= 10:
                factors.append(0.9)
            else:
                factors.append(0.6)
        
        # Alphanumeric ratio
        alnum_ratio = sum(1 for c in text if c.isalnum()) / len(text)
        factors.append(alnum_ratio)
        
        return np.mean(factors)
    
    def clear_cache(self):
        """Clear the OCR cache."""
        self.cache.clear()
    
    async def close(self):
        """Clean up resources."""
        self.executor.shutdown(wait=True)
