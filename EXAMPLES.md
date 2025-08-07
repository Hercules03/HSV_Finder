# HSV Range Finder - Usage Examples

This document provides practical examples and use cases for the HSV Range Finder application.

## 🎯 Common Use Cases

### 1. Object Detection Color Ranges

#### Example: Detecting Red Objects
```python
# Typical red color ranges found using HSV Range Finder:
# Lower HSV: [0, 120, 70]
# Upper HSV: [10, 255, 255]

# In your OpenCV code:
import cv2
import numpy as np

# Values obtained from HSV Range Finder
lower_red = np.array([0, 120, 70])
upper_red = np.array([10, 255, 255])

# Apply the mask
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, lower_red, upper_red)
result = cv2.bitwise_and(image, image, mask=mask)
```

#### Example: Detecting Green Objects
```python
# Green color ranges (typically):
# Lower HSV: [40, 40, 40]
# Upper HSV: [80, 255, 255]

lower_green = np.array([40, 40, 40])
upper_green = np.array([80, 255, 255])
```

#### Example: Detecting Blue Objects
```python
# Blue color ranges (typically):
# Lower HSV: [100, 50, 50]
# Upper HSV: [130, 255, 255]

lower_blue = np.array([100, 50, 50])
upper_blue = np.array([130, 255, 255])
```

### 2. Skin Tone Detection

#### Human Skin Detection
```python
# Skin tone ranges (varies by lighting):
# Lower HSV: [0, 20, 70]
# Upper HSV: [20, 255, 255]

lower_skin = np.array([0, 20, 70])
upper_skin = np.array([20, 255, 255])

# Note: Skin detection often requires multiple ranges
# for different skin tones and lighting conditions
```

### 3. Traffic Sign Detection

#### Yellow Sign Detection
```python
# Yellow traffic signs:
# Lower HSV: [20, 100, 100]
# Upper HSV: [30, 255, 255]

lower_yellow = np.array([20, 100, 100])
upper_yellow = np.array([30, 255, 255])
```

## 🔧 Workflow Examples

### Basic Color Isolation Workflow

1. **Load Sample Image**
   - Choose an image with the color you want to isolate
   - Ensure good lighting and clear color representation

2. **Initial Range Setting**
   ```
   Start with broad ranges:
   Lower HSV: [0, 0, 0]
   Upper HSV: [179, 255, 255]
   ```

3. **Narrow Hue Range**
   - Adjust Lower/Upper Hue until only your target color appears
   - For red: try ranges 0-10 or 170-179 (red wraps around)

4. **Refine Saturation**
   - Increase Lower Saturation to remove pale/washed out colors
   - Adjust Upper Saturation if needed

5. **Adjust Value (Brightness)**
   - Set Lower Value to remove dark shadows
   - Adjust Upper Value for bright highlights

### Advanced Multi-Range Detection

For colors that span multiple HSV ranges (like red):

```python
# Red objects often require two ranges due to hue wraparound
lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([10, 255, 255])

lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

# Combine both masks
mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
red_mask = cv2.bitwise_or(mask1, mask2)
```

## 📊 HSV Value Interpretation

### Hue (H) Values Guide
- **0-10**: Red
- **10-25**: Orange
- **25-35**: Yellow
- **35-85**: Green
- **85-125**: Blue
- **125-155**: Purple
- **155-179**: Pink/Magenta

### Saturation (S) Guidelines
- **0-50**: Pale, washed out colors
- **50-150**: Moderate saturation
- **150-255**: Vivid, pure colors

### Value (V) Guidelines
- **0-50**: Very dark colors
- **50-150**: Medium brightness
- **150-255**: Bright colors

## 🎨 Real-World Application Examples

### 1. Fruit Sorting System
```python
# Orange detection for citrus sorting
lower_orange = np.array([10, 100, 100])
upper_orange = np.array([25, 255, 255])

# Apple detection (red varieties)
lower_red_apple = np.array([0, 80, 80])
upper_red_apple = np.array([10, 255, 255])
```

### 2. Sports Ball Tracking
```python
# Tennis ball (yellow-green)
lower_tennis = np.array([25, 50, 50])
upper_tennis = np.array([35, 255, 255])

# Basketball (orange)
lower_basketball = np.array([5, 100, 100])
upper_basketball = np.array([20, 255, 255])
```

### 3. Industrial Quality Control
```python
# Detecting defects by unusual colors
# Good product color range
lower_good = np.array([35, 50, 100])
upper_good = np.array([85, 255, 255])

# Create mask for good products
good_mask = cv2.inRange(hsv, lower_good, upper_good)
# Defects will appear in inverted mask
defect_mask = cv2.bitwise_not(good_mask)
```

## 🔍 Troubleshooting Common Issues

### Issue: Color Not Detected
**Solutions:**
1. Check if lighting conditions match your test image
2. Try expanding the HSV ranges slightly
3. Consider multiple ranges for the same color
4. Verify image preprocessing (blur, noise reduction)

### Issue: Too Much Noise in Detection
**Solutions:**
1. Narrow the saturation range (increase lower bound)
2. Narrow the value range for consistent lighting
3. Apply morphological operations after masking:
   ```python
   kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
   mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
   mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
   ```

### Issue: Inconsistent Detection Across Images
**Solutions:**
1. Test with images from different lighting conditions
2. Use histogram equalization for consistent brightness
3. Consider adaptive HSV ranges based on image analysis

## 💡 Pro Tips

1. **Test Multiple Images**: Always test your HSV ranges on multiple sample images
2. **Document Your Ranges**: Keep a record of successful HSV ranges for different scenarios
3. **Lighting Matters**: Consider the lighting conditions where your application will be used
4. **Post-Processing**: Combine HSV filtering with morphological operations for cleaner results
5. **Multiple Ranges**: Don't hesitate to use multiple HSV ranges for complex color detection

## 📈 Integration with Computer Vision Pipelines

### Complete Object Detection Example
```python
import cv2
import numpy as np

def detect_colored_objects(image, lower_hsv, upper_hsv, min_area=100):
    """
    Complete pipeline for colored object detection
    Args:
        image: Input BGR image
        lower_hsv: Lower HSV bound (from HSV Range Finder)
        upper_hsv: Upper HSV bound (from HSV Range Finder)
        min_area: Minimum contour area to consider
    Returns:
        List of detected object contours
    """
    # Convert to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Create mask using values from HSV Range Finder
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    
    # Clean up the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter by area
    objects = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
    
    return objects, mask

# Usage with HSV values found using HSV Range Finder
lower_target = np.array([25, 50, 50])  # From HSV Range Finder
upper_target = np.array([35, 255, 255])  # From HSV Range Finder

objects, mask = detect_colored_objects(image, lower_target, upper_target)
```

This integration example shows how to use the HSV values you find with the HSV Range Finder in a complete computer vision pipeline.