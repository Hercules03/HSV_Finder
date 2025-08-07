# Import necessary libraries
import cv2
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import numpy as np
import pyperclip
import platform
import os

# Define the main class for the HSV Range Finder application
class HSVRangeFinder:
    def __init__(self):
        # Create the main tkinter window
        self.window = Tk()
        self.window.geometry('910x600')
        self.window.title('HSV Range Finder')
        self.window.resizable(1, 1)
        
        # --- Camera Frames ---
        # Use a main content frame with grid
        self.contentFrame = Frame(self.window)
        self.contentFrame.grid(row=0, column=0, sticky='nsew')

        # Configure window grid weights
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.contentFrame.rowconfigure(0, weight=1)
        # Add four columns: 0 (spacer), 1 (original), 2 (result), 3 (spacer)
        self.contentFrame.columnconfigure(0, weight=1)  # left spacer
        self.contentFrame.columnconfigure(1, weight=3)  # original image
        self.contentFrame.columnconfigure(2, weight=3)  # result image
        self.contentFrame.columnconfigure(3, weight=1)  # right spacer

        # Main Camera Frame (centered)
        self.mainCameraFrame = LabelFrame(self.contentFrame, text='Original Image')
        self.mainCameraFrame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        self.mainCameraFrame.rowconfigure(0, weight=1)
        self.mainCameraFrame.columnconfigure(0, weight=1)
        self.vidLabel1 = Label(self.mainCameraFrame)
        self.vidLabel1.grid(row=0, column=0, sticky='nsew')

        # Result Camera Frame (Filtered or Binary Mask, centered)
        self.resultCameraFrame = LabelFrame(self.contentFrame, text='Filtered Image')
        self.resultCameraFrame.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)
        self.resultCameraFrame.rowconfigure(0, weight=1)
        self.resultCameraFrame.columnconfigure(0, weight=1)
        self.vidLabel2 = Label(self.resultCameraFrame)
        self.vidLabel2.grid(row=0, column=0, sticky='nsew')

        # Controls Frame (sliders, buttons, results)
        self.controlsFrame = Frame(self.window)
        self.controlsFrame.grid(row=1, column=0, sticky='ew')
        self.window.rowconfigure(1, weight=0)
        self.controlsFrame.columnconfigure(0, weight=1)
        self.controlsFrame.columnconfigure(1, weight=1)
        self.controlsFrame.columnconfigure(2, weight=1)
        self.controlsFrame.columnconfigure(3, weight=1)
        self.controlsFrame.columnconfigure(4, weight=1) # Added for toggle button

        # Load Image button
        self.loadImageBtn = Button(self.controlsFrame, text='Load Image', command=self.load_image)
        self.loadImageBtn.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.loaded_image = None

        # Initialize slider variables for HSV range adjustment
        self.l_h = DoubleVar()
        self.l_s = DoubleVar()
        self.l_v = DoubleVar()
        self.u_h = DoubleVar()
        self.u_s = DoubleVar()
        self.u_v = DoubleVar()

        # Slider Section
        self.sliderFrame = LabelFrame(self.controlsFrame, text='HSV Range Adjustment')
        self.sliderFrame.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        for i in range(7):
            self.sliderFrame.columnconfigure(i, weight=1)

        # Labels and sliders for lower and upper HSV range values
        self.lhLabel = Label(self.sliderFrame, text='Lower Hue:')
        self.lhLabel.grid(row=0, column=0)
        self.lhSlider = Scale(self.sliderFrame, orient='horizontal', from_=0, to=179, command=self.lh_changed, variable=self.l_h)
        self.lhSlider.grid(row=0, column=1)
        self.lhEntry = Entry(self.sliderFrame, width=5)
        self.lhEntry.grid(row=0, column=2, padx=2)
        self.lhEntry.bind('<Return>', self.lh_entry_changed)
        self.lhEntry.bind('<FocusOut>', self.lh_entry_changed)

        self.lsLabel = Label(self.sliderFrame, text='Lower Saturation:')
        self.lsLabel.grid(row=0, column=3)
        self.lsSlider = Scale(self.sliderFrame, orient='horizontal', from_=0, to=255, command=self.ls_changed, variable=self.l_s)
        self.lsSlider.grid(row=0, column=4)
        self.lsEntry = Entry(self.sliderFrame, width=5)
        self.lsEntry.grid(row=0, column=5, padx=2)
        self.lsEntry.bind('<Return>', self.ls_entry_changed)
        self.lsEntry.bind('<FocusOut>', self.ls_entry_changed)

        self.lvLabel = Label(self.sliderFrame, text='Lower Value:')
        self.lvLabel.grid(row=0, column=6)
        self.lvSlider = Scale(self.sliderFrame, orient='horizontal', from_=0, to=255, command=self.lv_changed, variable=self.l_v)
        self.lvSlider.grid(row=0, column=7)
        self.lvEntry = Entry(self.sliderFrame, width=5)
        self.lvEntry.grid(row=0, column=8, padx=2)
        self.lvEntry.bind('<Return>', self.lv_entry_changed)
        self.lvEntry.bind('<FocusOut>', self.lv_entry_changed)

        self.uhLabel = Label(self.sliderFrame, text='Upper Hue:')
        self.uhLabel.grid(row=1, column=0)
        self.uhSlider = Scale(self.sliderFrame, orient='horizontal', from_=0, to=179, command=self.uh_changed, variable=self.u_h)
        self.uhSlider.grid(row=1, column=1)
        self.uhEntry = Entry(self.sliderFrame, width=5)
        self.uhEntry.grid(row=1, column=2, padx=2)
        self.uhEntry.bind('<Return>', self.uh_entry_changed)
        self.uhEntry.bind('<FocusOut>', self.uh_entry_changed)

        self.usLabel = Label(self.sliderFrame, text='Upper Saturation:')
        self.usLabel.grid(row=1, column=3)
        self.usSlider = Scale(self.sliderFrame, orient='horizontal', from_=0, to=255, command=self.us_changed, variable=self.u_s)
        self.usSlider.grid(row=1, column=4)
        self.usEntry = Entry(self.sliderFrame, width=5)
        self.usEntry.grid(row=1, column=5, padx=2)
        self.usEntry.bind('<Return>', self.us_entry_changed)
        self.usEntry.bind('<FocusOut>', self.us_entry_changed)

        self.uvLabel = Label(self.sliderFrame, text='Upper Value:')
        self.uvLabel.grid(row=1, column=6)
        self.uvSlider = Scale(self.sliderFrame, orient='horizontal', from_=0, to=255, command=self.uv_changed, variable=self.u_v)
        self.uvSlider.grid(row=1, column=7)
        self.uvEntry = Entry(self.sliderFrame, width=5)
        self.uvEntry.grid(row=1, column=8, padx=2)
        self.uvEntry.bind('<Return>', self.uv_entry_changed)
        self.uvEntry.bind('<FocusOut>', self.uv_entry_changed)

        # Labels to display current slider values
        self.resultFrame = LabelFrame(self.controlsFrame, text='Get Result')
        self.resultFrame.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        for i in range(4):
            self.resultFrame.columnconfigure(i, weight=1)

        self.lrLabel = Label(self.resultFrame, text='HSV Lower Range')
        self.lrLabel.grid(row=0, column=0, columnspan=3)

        self.lhShow = Label(self.resultFrame, text='0')
        self.lhShow.grid(row=1, column=0)
        self.lsShow = Label(self.resultFrame, text='0')
        self.lsShow.grid(row=1, column=1)
        self.lvShow = Label(self.resultFrame, text='0')
        self.lvShow.grid(row=1, column=2)

        self.urLabel = Label(self.resultFrame, text='HSV Upper Range')
        self.urLabel.grid(row=2, column=0, columnspan=3)

        self.uhShow = Label(self.resultFrame, text='0')
        self.uhShow.grid(row=3, column=0)
        self.usShow = Label(self.resultFrame, text='0')
        self.usShow.grid(row=3, column=1)
        self.uvShow = Label(self.resultFrame, text='0')
        self.uvShow.grid(row=3, column=2)

        # Buttons to copy the lower and upper HSV range values to clipboard
        self.cpyupperBtn = Button(self.resultFrame, text='Copy', command=self.get_lowerRange)
        self.cpyupperBtn.grid(row=0, column=3, rowspan=3)

        self.cpylowwerBtn = Button(self.resultFrame, text='Copy', command=self.get_upperRange)
        self.cpylowwerBtn.grid(row=3, column=3, rowspan=3)

        # Initialize entry fields with current values
        self.lhEntry.insert(0, '0')
        self.lsEntry.insert(0, '0')
        self.lvEntry.insert(0, '0')
        self.uhEntry.insert(0, '179')
        self.usEntry.insert(0, '255')
        self.uvEntry.insert(0, '255')

        # Toggle button for switching between filtered and binary mask
        self.toggleFrame = Frame(self.controlsFrame)
        self.toggleFrame.grid(row=0, column=4, padx=5, pady=5, sticky='e')
        self.show_binary = False
        self.toggleBtn = Button(self.toggleFrame, text='Show Binary Mask', command=self.toggle_result_view)
        self.toggleBtn.pack()

    # Method to copy the lower HSV range to clipboard
    def get_lowerRange(self):
        lowerRange = '{},{},{}'.format(self.get_lh(), self.get_ls(), self.get_lv())
        pyperclip.copy(lowerRange)

    # Method to copy the upper HSV range to clipboard
    def get_upperRange(self):
        upperRange = '{},{},{}'.format(self.get_uh(), self.get_us(), self.get_uv())
        pyperclip.copy(upperRange)

    # Method to flip the camera feed horizontally
    def flip_horizontal(self):
        # self.flip_horizontal = not self.flip_horizontal
        # self.flip_vertical = False
        pass # No camera flip for image processing
    
    # Method to flip the camera feed vertically
    def flip_vertical(self):
        # self.flip_vertical = not self.flip_vertical
        # self.flip_horizontal = False
        pass # No camera flip for image processing
        
    # Method to switch to the next camera channel
    def next_cam(self):
        # self.camIndex += 1
        # self.cap.release()
        # self.cap = cv2.VideoCapture(self.camIndex)
        # self.camChLabel.config(text='CH:{}'.format(self.camIndex))
        pass # No camera channel switching for image processing

    # Method to switch to the previous camera channel
    def prev_cam(self):
        # self.camIndex -= 1
        # if self.camIndex < 0:
        #     messagebox.showerror("Error! Camera Channel Limitation!", "No previous camera")
        #     self.camIndex = 0
        # else:
        #     self.cap.release()
        #     self.cap = cv2.VideoCapture(self.camIndex)
        #     self.camChLabel.config(text='CH:{}'.format(self.camIndex))
        pass # No camera channel switching for image processing

    def load_image(self):
        from tkinter import filedialog
        import platform
        import os
        
        try:
            # Platform-specific file dialog configuration
            if platform.system() == "Darwin":  # macOS
                # macOS-compatible file types
                filetypes = [
                    ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.tif"),
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg *.jpeg"),
                    ("BMP files", "*.bmp"),
                    ("All files", "*")
                ]
            else:  # Windows and Linux
                # Windows/Linux-compatible file types
                filetypes = [
                    ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.tif"),
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg;*.jpeg"),
                    ("BMP files", "*.bmp"),
                    ("All files", "*.*")
                ]
            
            file_path = filedialog.askopenfilename(
                title="Select Image File",
                filetypes=filetypes,
                initialdir=os.path.expanduser("~")  # Start in user's home directory
            )
            
            if file_path:
                # Normalize path for cross-platform compatibility
                file_path = os.path.normpath(file_path)
                
                # Check if file exists
                if not os.path.exists(file_path):
                    messagebox.showerror("Error", "Selected file does not exist.")
                    return
                
                # Try to load the image
                image = cv2.imread(file_path)
                if image is None:
                    messagebox.showerror("Error", "Could not load image. Please ensure it's a valid image file.")
                    return
                
                self.loaded_image = image
                self.process_and_display_image()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading image: {str(e)}")

    def process_and_display_image(self):
        if self.loaded_image is None:
            # Clear the labels if no image
            self.vidLabel1.config(image='')
            self.vidLabel2.config(image='')
            return
        image = self.loaded_image.copy()
        # Get HSV bounds
        lower_bound = np.array([self.l_h.get(), self.l_s.get(), self.l_v.get()])
        upper_bound = np.array([self.u_h.get(), self.u_s.get(), self.u_v.get()])
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        filtered_frame = cv2.bitwise_and(image, image, mask=mask)
        gray = cv2.cvtColor(filtered_frame, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)
        # Get dynamic sizes for each label's parent frame
        def get_frame_size(frame, default=(300, 400)):
            w = frame.winfo_width()
            h = frame.winfo_height()
            # If not yet rendered, use default
            if w < 10 or h < 10:
                w, h = default
            return (w, h)
        size1 = get_frame_size(self.mainCameraFrame)
        size2 = get_frame_size(self.resultCameraFrame)
        # Display original
        img1 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img1 = Image.fromarray(img1)
        img1 = img1.resize(size1, Image.Resampling.LANCZOS)
        img1 = ImageTk.PhotoImage(image=img1)
        self.vidLabel1.config(image=img1)
        self.vidLabel1.image = img1
        # Display filtered or binary mask based on toggle
        if self.show_binary:
            img2 = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)
        else:
            img2 = cv2.cvtColor(filtered_frame, cv2.COLOR_BGR2RGB)
        img2 = Image.fromarray(img2)
        img2 = img2.resize(size2, Image.Resampling.LANCZOS)
        img2 = ImageTk.PhotoImage(image=img2)
        self.vidLabel2.config(image=img2)
        self.vidLabel2.image = img2

    # Periodically update the display to reflect slider changes
    def update_frame(self):
        self.process_and_display_image()
        self.window.after(100, self.update_frame)

    # Getter method to format lower hue value
    def get_lh(self):
        return '{:.0f}'.format(self.l_h.get())

    # Entry field change handlers
    def lh_entry_changed(self, event):
        try:
            value = int(self.lhEntry.get())
            if 0 <= value <= 179:
                self.l_h.set(value)
                self.lhShow.configure(text=str(value))
        except ValueError:
            pass

    # Update entry fields when sliders change
    def lh_changed(self, event):
        value = int(self.l_h.get())
        self.lhShow.configure(text=str(value))
        self.lhEntry.delete(0, END)
        self.lhEntry.insert(0, str(value))

    # Getter method to format lower saturation value
    def get_ls(self):
        return '{:.0f}'.format(self.l_s.get())

    # Event handler for lower saturation slider change
    def ls_changed(self, event):
        value = int(self.l_s.get())
        self.lsShow.configure(text=str(value))
        self.lsEntry.delete(0, END)
        self.lsEntry.insert(0, str(value))

    # Getter method to format lower value value
    def get_lv(self):
        return '{:.0f}'.format(self.l_v.get())

    # Event handler for lower value slider change
    def lv_changed(self, event):
        value = int(self.l_v.get())
        self.lvShow.configure(text=str(value))
        self.lvEntry.delete(0, END)
        self.lvEntry.insert(0, str(value))

    # Entry field change handlers
    def ls_entry_changed(self, event):
        try:
            value = int(self.lsEntry.get())
            if 0 <= value <= 255:
                self.l_s.set(value)
                self.lsShow.configure(text=str(value))
        except ValueError:
            pass

    # Getter method to format upper hue value
    def get_uh(self):
        return '{:.0f}'.format(self.u_h.get())

    # Event handler for upper hue slider change
    def uh_changed(self, event):
        value = int(self.u_h.get())
        self.uhShow.configure(text=str(value))
        self.uhEntry.delete(0, END)
        self.uhEntry.insert(0, str(value))

    # Entry field change handlers
    def uh_entry_changed(self, event):
        try:
            value = int(self.uhEntry.get())
            if 0 <= value <= 179:
                self.u_h.set(value)
                self.uhShow.configure(text=str(value))
        except ValueError:
            pass

    # Getter method to format upper saturation value
    def get_us(self):
        return '{:.0f}'.format(self.u_s.get())

    # Event handler for upper saturation slider change
    def us_changed(self, event):
        value = int(self.u_s.get())
        self.usShow.configure(text=str(value))
        self.usEntry.delete(0, END)
        self.usEntry.insert(0, str(value))

    # Entry field change handler for upper saturation
    def us_entry_changed(self, event):
        try:
            value = int(self.usEntry.get())
            if 0 <= value <= 255:
                self.u_s.set(value)
                self.usShow.configure(text=str(value))
        except ValueError:
            pass

    # Getter method to format upper value value
    def get_uv(self):
        return '{:.0f}'.format(self.u_v.get())

    # Event handler for upper value slider change
    def uv_changed(self, event):
        value = int(self.u_v.get())
        self.uvShow.configure(text=str(value))
        self.uvEntry.delete(0, END)
        self.uvEntry.insert(0, str(value))

    # Entry field change handlers
    def lv_entry_changed(self, event):
        try:
            value = int(self.lvEntry.get())
            if 0 <= value <= 255:
                self.l_v.set(value)
                self.lvShow.configure(text=str(value))
        except ValueError:
            pass

    # Entry field change handlers
    def uv_entry_changed(self, event):
        try:
            value = int(self.uvEntry.get())
            if 0 <= value <= 255:
                self.u_v.set(value)
                self.uvShow.configure(text=str(value))
        except ValueError:
            pass
    
    # Method to release resources and close the application
    def cleanup(self):
        self.window.destroy()

    # Method to start the application
    def run(self):
        # Create an OpenCV video capture object
        # self.cap = cv2.VideoCapture(self.camIndex)

        # Start updating the frame
        self.update_frame()
        
        # Bind the cleanup method to the window's close event
        self.window.protocol("WM_DELETE_WINDOW", self.cleanup)
        
        # Run the Tkinter event loop
        self.window.mainloop()
        # self.window.after_cancel(self.update_frame)
        # self.cap.release()

    def toggle_result_view(self):
        self.show_binary = not self.show_binary
        if self.show_binary:
            self.resultCameraFrame.config(text='Binary Mask')
            self.toggleBtn.config(text='Show Filtered Image')
        else:
            self.resultCameraFrame.config(text='Filtered Image')
            self.toggleBtn.config(text='Show Binary Mask')
        self.process_and_display_image()

gui = HSVRangeFinder()
gui.run()