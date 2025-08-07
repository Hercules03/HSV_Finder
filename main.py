# Import necessary libraries
import cv2
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import numpy as np
import pyperclip
import platform
import os
from typing import Optional, Tuple, List, Any, Union

# Application Configuration
class Config:
    """
    Configuration class containing all application constants and settings.
    
    This class centralizes all configuration values to improve maintainability
    and make it easier to adjust application behavior.
    """
    # Update intervals and timing
    UPDATE_INTERVAL = 50  # milliseconds - reduced for better responsiveness
    DEBOUNCE_DELAY = 150  # milliseconds - debounce rapid changes
    
    # UI Layout
    WINDOW_SIZE = "910x600"
    DEFAULT_FRAME_SIZE = (300, 400)
    PADDING = 5
    
    # HSV Value ranges
    HSV_HUE_MAX = 179
    HSV_SAT_VAL_MAX = 255
    HSV_HUE_MIN = 0
    HSV_SAT_VAL_MIN = 0
    
    # Grid weights
    GRID_WEIGHT_LIGHT = 1
    GRID_WEIGHT_HEAVY = 3
    GRID_WEIGHT_NONE = 0
    
    # Entry field width
    ENTRY_WIDTH = 5
    
    # File types for image loading
    IMAGE_EXTENSIONS_MACOS = "*.png *.jpg *.jpeg *.bmp *.tiff *.tif"
    IMAGE_EXTENSIONS_OTHER = "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.tif"
    
    # Default HSV values
    DEFAULT_LOWER_HSV = [0, 0, 0]
    DEFAULT_UPPER_HSV = [HSV_HUE_MAX, HSV_SAT_VAL_MAX, HSV_SAT_VAL_MAX]

# Define the main class for the HSV Range Finder application
class HSVRangeFinder:
    """
    HSV Range Finder Application.
    
    A GUI application for finding optimal HSV color ranges by loading images
    and adjusting HSV parameters in real-time. Features include:
    
    - Image loading with cross-platform file dialog support
    - Real-time HSV range adjustment with sliders
    - Live preview of filtered and binary mask results
    - Performance optimized with caching and debouncing
    - Error handling and validation for robust operation
    - Copy-to-clipboard functionality for HSV values
    
    Usage:
        app = HSVRangeFinder()
        app.run()
    """
    
    def __init__(self) -> None:
        """
        Initialize the HSV Range Finder application.
        
        Sets up the main window, initializes UI components, HSV slider variables,
        and performance optimization attributes. Creates the complete user interface
        and prepares the application for use.
        """
        self.window: Tk = Tk()
        self.loaded_image: Optional[np.ndarray] = None
        self.hsv_changed: bool = False
        self.show_binary: bool = False
        
        # Performance optimization attributes
        self._cached_hsv_image: Optional[np.ndarray] = None
        self._last_processed_bounds: Optional[Tuple[np.ndarray, np.ndarray]] = None
        self._cached_processed_images: Optional[Tuple[np.ndarray, np.ndarray, np.ndarray]] = None
        self._debounce_timer: Optional[str] = None
        self._last_hsv_change_time: float = 0.0
        
        # Initialize UI components (will be set during setup)
        self.contentFrame: Frame
        self.mainCameraFrame: LabelFrame
        self.resultCameraFrame: LabelFrame
        self.vidLabel1: Label
        self.vidLabel2: Label
        self.controlsFrame: Frame
        self.sliderFrame: LabelFrame
        self.resultFrame: LabelFrame
        self.toggleFrame: Frame
        
        # HSV slider variables
        self.l_h: DoubleVar
        self.l_s: DoubleVar
        self.l_v: DoubleVar
        self.u_h: DoubleVar
        self.u_s: DoubleVar
        self.u_v: DoubleVar
        
        self._setup_window()
        self._setup_ui()
        self._initialize_hsv_values()
    
    def _setup_window(self) -> None:
        """Configure the main application window."""
        self.window.geometry(Config.WINDOW_SIZE)
        self.window.title('HSV Range Finder')
        self.window.resizable(True, True)
        
        # Configure window grid weights
        self.window.rowconfigure(0, weight=Config.GRID_WEIGHT_LIGHT)
        self.window.columnconfigure(0, weight=Config.GRID_WEIGHT_LIGHT)
    
    def _setup_ui(self) -> None:
        """Set up the main user interface components."""
        self._create_main_frames()
        self._create_camera_frames()
        self._create_control_frames()
    
    def _create_main_frames(self) -> None:
        """Create the main layout frames."""
        # Main content frame
        self.contentFrame = Frame(self.window)
        self.contentFrame.grid(row=0, column=0, sticky='nsew')
        self.contentFrame.rowconfigure(0, weight=Config.GRID_WEIGHT_LIGHT)
        
        # Configure columns: spacer, original, result, spacer
        self.contentFrame.columnconfigure(0, weight=Config.GRID_WEIGHT_LIGHT)  # left spacer
        self.contentFrame.columnconfigure(1, weight=Config.GRID_WEIGHT_HEAVY)  # original image
        self.contentFrame.columnconfigure(2, weight=Config.GRID_WEIGHT_HEAVY)  # result image
        self.contentFrame.columnconfigure(3, weight=Config.GRID_WEIGHT_LIGHT)  # right spacer
    
    def _create_camera_frames(self):
        """Create the image display frames."""
        # Main Camera Frame (original image)
        self.mainCameraFrame = LabelFrame(self.contentFrame, text='Original Image')
        self.mainCameraFrame.grid(row=0, column=1, sticky='nsew', 
                                padx=Config.PADDING, pady=Config.PADDING)
        self.mainCameraFrame.rowconfigure(0, weight=Config.GRID_WEIGHT_LIGHT)
        self.mainCameraFrame.columnconfigure(0, weight=Config.GRID_WEIGHT_LIGHT)
        self.vidLabel1 = Label(self.mainCameraFrame)
        self.vidLabel1.grid(row=0, column=0, sticky='nsew')

        # Result Camera Frame (filtered/binary image)
        self.resultCameraFrame = LabelFrame(self.contentFrame, text='Filtered Image')
        self.resultCameraFrame.grid(row=0, column=2, sticky='nsew', 
                                  padx=Config.PADDING, pady=Config.PADDING)
        self.resultCameraFrame.rowconfigure(0, weight=Config.GRID_WEIGHT_LIGHT)
        self.resultCameraFrame.columnconfigure(0, weight=Config.GRID_WEIGHT_LIGHT)
        self.vidLabel2 = Label(self.resultCameraFrame)
        self.vidLabel2.grid(row=0, column=0, sticky='nsew')
    
    def _create_control_frames(self):
        """Create the control panel frames and components."""
        # Main controls frame
        self.controlsFrame = Frame(self.window)
        self.controlsFrame.grid(row=1, column=0, sticky='ew')
        self.window.rowconfigure(1, weight=Config.GRID_WEIGHT_NONE)
        
        # Configure control frame columns
        for i in range(5):  # 5 columns for buttons, sliders, results, toggle
            self.controlsFrame.columnconfigure(i, weight=Config.GRID_WEIGHT_LIGHT)
        
        self._create_load_button()
        self._create_sliders()
        self._create_result_display()
        self._create_toggle_button()
    
    def _create_load_button(self):
        """Create the load image button."""
        self.loadImageBtn = Button(self.controlsFrame, text='Load Image', 
                                 command=self.load_image)
        self.loadImageBtn.grid(row=0, column=0, padx=Config.PADDING, 
                             pady=Config.PADDING, sticky='w')
    
    def _initialize_hsv_values(self):
        """Initialize HSV slider variables and set default values."""
        # Initialize slider variables for HSV range adjustment
        self.l_h = DoubleVar()
        self.l_s = DoubleVar()
        self.l_v = DoubleVar()
        self.u_h = DoubleVar()
        self.u_s = DoubleVar()
        self.u_v = DoubleVar()
        
        # Set default values
        self.l_h.set(Config.DEFAULT_LOWER_HSV[0])
        self.l_s.set(Config.DEFAULT_LOWER_HSV[1])
        self.l_v.set(Config.DEFAULT_LOWER_HSV[2])
        self.u_h.set(Config.DEFAULT_UPPER_HSV[0])
        self.u_s.set(Config.DEFAULT_UPPER_HSV[1])
        self.u_v.set(Config.DEFAULT_UPPER_HSV[2])
    
    def _create_sliders(self):
        """Create the HSV adjustment sliders with reduced code duplication."""
        # Slider Section Frame
        self.sliderFrame = LabelFrame(self.controlsFrame, text='HSV Range Adjustment')
        self.sliderFrame.grid(row=0, column=1, padx=Config.PADDING, 
                            pady=Config.PADDING, sticky='ew')
        
        # Configure slider frame columns (9 columns for 3 HSV components)
        for i in range(9):
            self.sliderFrame.columnconfigure(i, weight=Config.GRID_WEIGHT_LIGHT)
        
        # Create sliders using helper method to reduce duplication
        self._create_hsv_slider_row(0, "Lower", [
            ("Hue", self.l_h, Config.HSV_HUE_MAX, self.lh_changed, self.lh_entry_changed),
            ("Saturation", self.l_s, Config.HSV_SAT_VAL_MAX, self.ls_changed, self.ls_entry_changed),
            ("Value", self.l_v, Config.HSV_SAT_VAL_MAX, self.lv_changed, self.lv_entry_changed)
        ])
        
        self._create_hsv_slider_row(1, "Upper", [
            ("Hue", self.u_h, Config.HSV_HUE_MAX, self.uh_changed, self.uh_entry_changed),
            ("Saturation", self.u_s, Config.HSV_SAT_VAL_MAX, self.us_changed, self.us_entry_changed),
            ("Value", self.u_v, Config.HSV_SAT_VAL_MAX, self.uv_changed, self.uv_entry_changed)
        ])
        
        # Store entry widgets for later initialization
        self._initialize_entry_fields()
    
    def _create_hsv_slider_row(self, row, prefix, slider_configs):
        """Create a row of HSV sliders with labels, sliders, and entries."""
        for col_offset, (name, variable, max_val, slider_cmd, entry_cmd) in enumerate(slider_configs):
            col_base = col_offset * 3
            
            # Create label
            label = Label(self.sliderFrame, text=f'{prefix} {name}:')
            label.grid(row=row, column=col_base)
            
            # Create slider
            slider = Scale(self.sliderFrame, orient='horizontal', 
                          from_=Config.HSV_HUE_MIN if 'Hue' in name else Config.HSV_SAT_VAL_MIN,
                          to=max_val, command=slider_cmd, variable=variable)
            slider.grid(row=row, column=col_base + 1)
            
            # Create entry field
            entry = Entry(self.sliderFrame, width=Config.ENTRY_WIDTH)
            entry.grid(row=row, column=col_base + 2, padx=2)
            entry.bind('<Return>', entry_cmd)
            entry.bind('<FocusOut>', entry_cmd)
            
            # Store references for later use (matching original naming convention)
            prefix_short = 'l' if prefix == 'Lower' else 'u'
            name_short = name.lower()[0]  # h, s, v
            setattr(self, f"{prefix_short}{name_short}Label", label)
            setattr(self, f"{prefix_short}{name_short}Slider", slider)
            setattr(self, f"{prefix_short}{name_short}Entry", entry)
    
    def _initialize_entry_fields(self):
        """Initialize entry fields with default values."""
        entries_and_values = [
            (self.lhEntry, Config.DEFAULT_LOWER_HSV[0]),
            (self.lsEntry, Config.DEFAULT_LOWER_HSV[1]),
            (self.lvEntry, Config.DEFAULT_LOWER_HSV[2]),
            (self.uhEntry, Config.DEFAULT_UPPER_HSV[0]),
            (self.usEntry, Config.DEFAULT_UPPER_HSV[1]),
            (self.uvEntry, Config.DEFAULT_UPPER_HSV[2])
        ]
        
        for entry, value in entries_and_values:
            entry.insert(0, str(int(value)))
    
    def _create_result_display(self):
        """Create the HSV values result display panel."""
        # Result display frame
        self.resultFrame = LabelFrame(self.controlsFrame, text='Get Result')
        self.resultFrame.grid(row=0, column=2, padx=Config.PADDING, 
                            pady=Config.PADDING, sticky='ew')
        
        # Configure result frame columns
        for i in range(4):
            self.resultFrame.columnconfigure(i, weight=Config.GRID_WEIGHT_LIGHT)

        # Lower range section
        self.lrLabel = Label(self.resultFrame, text='HSV Lower Range')
        self.lrLabel.grid(row=0, column=0, columnspan=3)
        
        self.lhShow = Label(self.resultFrame, text='0')
        self.lhShow.grid(row=1, column=0)
        self.lsShow = Label(self.resultFrame, text='0')
        self.lsShow.grid(row=1, column=1)
        self.lvShow = Label(self.resultFrame, text='0')
        self.lvShow.grid(row=1, column=2)

        # Upper range section
        self.urLabel = Label(self.resultFrame, text='HSV Upper Range')
        self.urLabel.grid(row=2, column=0, columnspan=3)
        
        self.uhShow = Label(self.resultFrame, text='0')
        self.uhShow.grid(row=3, column=0)
        self.usShow = Label(self.resultFrame, text='0')
        self.usShow.grid(row=3, column=1)
        self.uvShow = Label(self.resultFrame, text='0')
        self.uvShow.grid(row=3, column=2)

        # Copy buttons
        self.cpyLowerBtn = Button(self.resultFrame, text='Copy', 
                                command=self.get_lowerRange)
        self.cpyLowerBtn.grid(row=0, column=3, rowspan=2)

        self.cpyUpperBtn = Button(self.resultFrame, text='Copy', 
                                command=self.get_upperRange)
        self.cpyUpperBtn.grid(row=2, column=3, rowspan=2)
    
    def _create_toggle_button(self):
        """Create the toggle button for switching between filtered and binary mask view."""
        self.toggleFrame = Frame(self.controlsFrame)
        self.toggleFrame.grid(row=0, column=4, padx=Config.PADDING, 
                            pady=Config.PADDING, sticky='e')
        
        self.toggleBtn = Button(self.toggleFrame, text='Show Binary Mask', 
                              command=self.toggle_result_view)
        self.toggleBtn.pack()

    # Method to copy the lower HSV range to clipboard
    def get_lowerRange(self):
        lowerRange = '{},{},{}'.format(self.get_lh(), self.get_ls(), self.get_lv())
        pyperclip.copy(lowerRange)

    # Method to copy the upper HSV range to clipboard
    def get_upperRange(self):
        upperRange = '{},{},{}'.format(self.get_uh(), self.get_us(), self.get_uv())
        pyperclip.copy(upperRange)


    def load_image(self) -> None:
        """
        Load an image file with comprehensive error handling and validation.
        
        Opens a platform-appropriate file dialog, validates the selected file,
        loads it using OpenCV, and updates the display. Includes extensive
        error handling for various failure modes and user warnings for large files.
        
        Features:
        - Cross-platform file type filtering
        - File existence and validity checking
        - Large file size warnings
        - Image format validation
        - Cache invalidation for performance
        
        Raises:
            Various exceptions are caught and displayed to user via messageboxes
        """
        from tkinter import filedialog
        
        try:
            filetypes = self._get_file_types()
            file_path = self._select_image_file(filetypes)
            
            if not file_path:
                return  # User cancelled
            
            if not self._validate_file_path(file_path):
                return
            
            image = self._load_image_file(file_path)
            if image is not None:
                self.loaded_image = image
                self._invalidate_cache()  # Clear cache when new image is loaded
                self.hsv_changed = True
                self.process_and_display_image()
                
        except Exception as e:
            self._handle_load_error(f"Unexpected error loading image: {str(e)}")
    
    def _get_file_types(self) -> List[Tuple[str, str]]:
        """Get platform-specific file type definitions."""
        if platform.system() == "Darwin":  # macOS
            return [
                ("Image files", Config.IMAGE_EXTENSIONS_MACOS),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("BMP files", "*.bmp"),
                ("All files", "*")
            ]
        else:  # Windows and Linux
            return [
                ("Image files", Config.IMAGE_EXTENSIONS_OTHER),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg;*.jpeg"),
                ("BMP files", "*.bmp"),
                ("All files", "*.*")
            ]
    
    def _select_image_file(self, filetypes: List[Tuple[str, str]]) -> str:
        """Open file dialog and return selected file path."""
        return filedialog.askopenfilename(
            title="Select Image File",
            filetypes=filetypes,
            initialdir=os.path.expanduser("~")
        )
    
    def _validate_file_path(self, file_path: str) -> bool:
        """Validate the selected file path."""
        try:
            # Normalize path for cross-platform compatibility
            file_path = os.path.normpath(file_path)
            
            # Check if file exists
            if not os.path.exists(file_path):
                messagebox.showerror("Error", "Selected file does not exist.")
                return False
                
            # Check if it's actually a file (not a directory)
            if not os.path.isfile(file_path):
                messagebox.showerror("Error", "Selected path is not a file.")
                return False
                
            # Check file size (optional - prevent loading huge files)
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:  # 50MB limit
                result = messagebox.askyesno("Warning", 
                    f"File is large ({file_size / (1024*1024):.1f}MB). Continue loading?")
                if not result:
                    return False
                    
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Error validating file: {str(e)}")
            return False
    
    def _load_image_file(self, file_path: str) -> Optional[np.ndarray]:
        """Load and validate the image file."""
        try:
            image = cv2.imread(file_path)
            if image is None:
                messagebox.showerror("Error", 
                    "Could not load image. Please ensure it's a valid image file.")
                return None
                
            # Validate image properties
            height, width = image.shape[:2]
            if height * width > 10000 * 10000:  # Very large image warning
                result = messagebox.askyesno("Warning", 
                    f"Image is very large ({width}x{height}). This may impact performance. Continue?")
                if not result:
                    return None
                    
            return image
            
        except Exception as e:
            messagebox.showerror("Error", f"Error reading image file: {str(e)}")
            return None
    
    def _handle_load_error(self, error_message):
        """Handle image loading errors."""
        messagebox.showerror("Error", error_message)
        print(f"Image load error: {error_message}")  # For debugging

    def process_and_display_image(self):
        """Process and display images with comprehensive error handling."""
        try:
            if self.loaded_image is None:
                self._clear_image_displays()
                return
            
            # Validate HSV bounds
            hsv_bounds = self._get_validated_hsv_bounds()
            if hsv_bounds is None:
                return
                
            lower_bound, upper_bound = hsv_bounds
            
            # Process image safely
            processed_images = self._process_image_safely(self.loaded_image.copy(), 
                                                        lower_bound, upper_bound)
            if processed_images is None:
                return
                
            original_image, filtered_frame, binary = processed_images
            
            # Display images safely
            self._display_images_safely(original_image, filtered_frame, binary)
            
        except Exception as e:
            self._handle_processing_error(f"Error processing image: {str(e)}")
    
    def _clear_image_displays(self):
        """Clear the image display labels."""
        self.vidLabel1.config(image='')
        self.vidLabel2.config(image='')
    
    def _get_validated_hsv_bounds(self) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """Get and validate HSV bounds from sliders."""
        try:
            lower_bound = np.array([self.l_h.get(), self.l_s.get(), self.l_v.get()])
            upper_bound = np.array([self.u_h.get(), self.u_s.get(), self.u_v.get()])
            
            # Validate bounds
            if np.any(lower_bound < 0) or np.any(upper_bound < 0):
                print("Warning: HSV bounds contain negative values")
                return None
                
            if np.any(lower_bound > upper_bound):
                print("Warning: Lower HSV bounds are greater than upper bounds")
                # Don't return None here as this is a valid use case in some scenarios
                
            return lower_bound, upper_bound
            
        except Exception as e:
            print(f"Error getting HSV bounds: {str(e)}")
            return None
    
    def _process_image_safely(self, image: np.ndarray, lower_bound: np.ndarray, upper_bound: np.ndarray) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """Process image with error handling and caching optimization."""
        try:
            # Check if we can use cached results
            if self._can_use_cached_results(lower_bound, upper_bound):
                return self._cached_processed_images
            
            # Use cached HSV conversion if available, otherwise convert
            if self._cached_hsv_image is None or not self._is_same_image(image):
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                self._cached_hsv_image = hsv
            else:
                hsv = self._cached_hsv_image
            
            # Create mask and filtered image
            mask = cv2.inRange(hsv, lower_bound, upper_bound)
            filtered_frame = cv2.bitwise_and(image, image, mask=mask)
            
            # Create binary image
            gray = cv2.cvtColor(filtered_frame, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)
            
            # Cache the results
            processed_images = (image, filtered_frame, binary)
            self._cached_processed_images = processed_images
            self._last_processed_bounds = (lower_bound.copy(), upper_bound.copy())
            
            return processed_images
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None
    
    def _can_use_cached_results(self, lower_bound: np.ndarray, upper_bound: np.ndarray) -> bool:
        """Check if we can use cached processing results."""
        if (self._cached_processed_images is None or 
            self._last_processed_bounds is None):
            return False
        
        cached_lower, cached_upper = self._last_processed_bounds
        return (np.array_equal(lower_bound, cached_lower) and 
                np.array_equal(upper_bound, cached_upper))
    
    def _is_same_image(self, image: np.ndarray) -> bool:
        """Check if the current image is the same as the cached one."""
        if self.loaded_image is None or self._cached_hsv_image is None:
            return False
        
        # Quick shape comparison first
        return (image.shape == self.loaded_image.shape and 
                np.array_equal(image, self.loaded_image))
    
    def _invalidate_cache(self) -> None:
        """Invalidate all cached images when a new image is loaded."""
        self._cached_hsv_image = None
        self._cached_processed_images = None
        self._last_processed_bounds = None
    
    def _display_images_safely(self, original_image, filtered_frame, binary):
        """Display processed images with error handling."""
        try:
            # Get frame sizes
            size1 = self._get_frame_size(self.mainCameraFrame)
            size2 = self._get_frame_size(self.resultCameraFrame)
            
            # Display original image
            self._display_image_in_label(original_image, self.vidLabel1, size1, is_bgr=True)
            
            # Display filtered or binary image based on toggle
            if self.show_binary:
                self._display_image_in_label(binary, self.vidLabel2, size2, is_bgr=False)
            else:
                self._display_image_in_label(filtered_frame, self.vidLabel2, size2, is_bgr=True)
                
        except Exception as e:
            print(f"Error displaying images: {str(e)}")
    
    def _get_frame_size(self, frame: Frame, default: Optional[Tuple[int, int]] = None) -> Tuple[int, int]:
        """Get dynamic frame size with fallback to default."""
        if default is None:
            default = Config.DEFAULT_FRAME_SIZE
            
        try:
            w = frame.winfo_width()
            h = frame.winfo_height()
            # If not yet rendered, use default
            if w < 10 or h < 10:
                w, h = default
            return (w, h)
        except Exception:
            return default
    
    def _display_image_in_label(self, image, label, size, is_bgr=True):
        """Display a single image in a label with proper conversion."""
        try:
            # Convert color space if needed
            if is_bgr and len(image.shape) == 3:
                display_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            elif not is_bgr and len(image.shape) == 2:
                display_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            else:
                display_image = image
            
            # Convert to PIL and resize
            pil_image = Image.fromarray(display_image)
            pil_image = pil_image.resize(size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage and display
            photo_image = ImageTk.PhotoImage(image=pil_image)
            label.config(image=photo_image)
            label.image = photo_image  # Keep a reference to prevent garbage collection
            
        except Exception as e:
            print(f"Error displaying single image: {str(e)}")
    
    def _handle_processing_error(self, error_message):
        """Handle image processing errors."""
        print(error_message)
        messagebox.showerror("Processing Error", 
            "Error processing image. Please check your image and HSV values.")

    # Periodically update the display to reflect slider changes
    def update_frame(self) -> None:
        """Update frame with debouncing for better performance."""
        if self.hsv_changed:
            # Cancel any pending debounced update
            if self._debounce_timer:
                self.window.after_cancel(self._debounce_timer)
            
            # Schedule a debounced update
            self._debounce_timer = self.window.after(Config.DEBOUNCE_DELAY, self._debounced_update)
            
        self.window.after(Config.UPDATE_INTERVAL, self.update_frame)
    
    def _debounced_update(self) -> None:
        """Perform the actual image processing update after debounce delay."""
        if self.hsv_changed:
            self.process_and_display_image()
            self.hsv_changed = False
        self._debounce_timer = None
    
    def _mark_hsv_changed(self) -> None:
        """Mark HSV values as changed with timestamp for performance optimization."""
        import time
        self.hsv_changed = True
        self._last_hsv_change_time = time.time()

    # HSV value validation and update helpers
    def _validate_and_update(self, entry_widget, variable, display_label, min_val, max_val):
        """Validate entry input and update variable and display"""
        try:
            value = int(entry_widget.get())
            if min_val <= value <= max_val:
                variable.set(value)
                display_label.configure(text=str(value))
                self._mark_hsv_changed()
                return True
        except ValueError:
            pass
        return False
    
    def _update_entry_from_slider(self, entry_widget, variable, display_label):
        """Update entry field and display when slider changes"""
        value = int(variable.get())
        display_label.configure(text=str(value))
        entry_widget.delete(0, END)
        entry_widget.insert(0, str(value))
        self._mark_hsv_changed()
    
    # Lower HSV handlers
    def lh_entry_changed(self, event):
        self._validate_and_update(self.lhEntry, self.l_h, self.lhShow, 0, Config.HSV_HUE_MAX)

    def lh_changed(self, event):
        self._update_entry_from_slider(self.lhEntry, self.l_h, self.lhShow)

    def ls_entry_changed(self, event):
        self._validate_and_update(self.lsEntry, self.l_s, self.lsShow, 0, Config.HSV_SAT_VAL_MAX)

    def ls_changed(self, event):
        self._update_entry_from_slider(self.lsEntry, self.l_s, self.lsShow)

    def lv_entry_changed(self, event):
        self._validate_and_update(self.lvEntry, self.l_v, self.lvShow, 0, Config.HSV_SAT_VAL_MAX)

    def lv_changed(self, event):
        self._update_entry_from_slider(self.lvEntry, self.l_v, self.lvShow)
    
    # Upper HSV handlers
    def uh_entry_changed(self, event):
        self._validate_and_update(self.uhEntry, self.u_h, self.uhShow, 0, Config.HSV_HUE_MAX)

    def uh_changed(self, event):
        self._update_entry_from_slider(self.uhEntry, self.u_h, self.uhShow)

    def us_entry_changed(self, event):
        self._validate_and_update(self.usEntry, self.u_s, self.usShow, 0, Config.HSV_SAT_VAL_MAX)

    def us_changed(self, event):
        self._update_entry_from_slider(self.usEntry, self.u_s, self.usShow)

    def uv_entry_changed(self, event):
        self._validate_and_update(self.uvEntry, self.u_v, self.uvShow, 0, Config.HSV_SAT_VAL_MAX)

    def uv_changed(self, event):
        self._update_entry_from_slider(self.uvEntry, self.u_v, self.uvShow)

    # Getter methods for HSV values
    def get_lh(self) -> str:
        return '{:.0f}'.format(self.l_h.get())

    def get_ls(self) -> str:
        return '{:.0f}'.format(self.l_s.get())

    def get_lv(self) -> str:
        return '{:.0f}'.format(self.l_v.get())

    def get_uh(self) -> str:
        return '{:.0f}'.format(self.u_h.get())

    def get_us(self) -> str:
        return '{:.0f}'.format(self.u_s.get())

    def get_uv(self) -> str:
        return '{:.0f}'.format(self.u_v.get())
    
    def cleanup(self) -> None:
        """
        Release resources and close the application.
        
        Called when the user closes the window. Properly destroys
        the Tkinter window and releases any resources.
        """
        self.window.destroy()

    def run(self) -> None:
        """
        Start the HSV Range Finder application.
        
        Initializes the update loop for real-time image processing,
        sets up proper window close handling, and starts the main
        Tkinter event loop. This method blocks until the application
        is closed by the user.
        
        The update loop runs at the interval defined in Config.UPDATE_INTERVAL
        and includes debouncing for optimal performance.
        """
        # Start updating the frame
        self.update_frame()
        
        # Bind the cleanup method to the window's close event
        self.window.protocol("WM_DELETE_WINDOW", self.cleanup)
        
        # Run the Tkinter event loop
        self.window.mainloop()

    def toggle_result_view(self):
        self.show_binary = not self.show_binary
        if self.show_binary:
            self.resultCameraFrame.config(text='Binary Mask')
            self.toggleBtn.config(text='Show Filtered Image')
        else:
            self.resultCameraFrame.config(text='Filtered Image')
            self.toggleBtn.config(text='Show Binary Mask')
        self.hsv_changed = True
        self.process_and_display_image()

gui = HSVRangeFinder()
gui.run()