try:
    import itertools
    import threading
    import win32api
    import win32con
    import win32gui
    import win32ui
    import ctypes
    import time
    import math
    import keyboard
    import sys
    import os
    import requests
    import io
    import pygetwindow as gw
    import tkinter as tk
    from tkinter import Canvas, Frame
    from tkinter import ttk
    from tkinter import messagebox, filedialog
    from PIL import Image, ImageTk
    from typing import Optional, Tuple, List
    from urllib.parse import urlparse
    

    import pyautogui
    import pyperclip
    from PIL import ImageGrab

    import Encoding
    from common import setup_logger, is_window_active, color_in_coords
except Exception as e:
    exit(input(f"ERROR: {e}"))
SCREEN_DIMENSIONS = []
running = 1
paused = False
dither_enabled = False
img_data = None
num_strings = 0
running = True
time_label = None
input_field = None
done_button = None
remaining_minutes = 0
remaining_seconds = 0
uimsg = "No Data Yet"
written_strings = 0
is_visible = True
stop_animation = True
stop_animation_import = True
SCREEN_DIMENSIONS = (800, 600)  # Example screen dimensions
root = None  # Tkinter root window placeholder
selected_image = None
link_var=""
flexible = False
ImageName = "No Image"
running = False
delay = 0.05
time_at_start = 0
def return_to_importer():
    root.deiconify()  # Show the window if it is hidden
    root.lift()       # Bring the window to the front
    root.focus_force()  # Set focus to the window

keyboard.add_hotkey('alt+p', return_to_importer)

def monitor_check():
    global SCREEN_DIMENSIONS
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    SCREEN_DIMENSIONS = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    if round(SCREEN_DIMENSIONS[0] / SCREEN_DIMENSIONS[1], 2) != 1.78:
        return -1
    return 1

def pause_program():
    global paused
    paused = not paused
    print("Program paused." if paused else "Program resumed.")

def get_fixed_scale(image):
    scaleportion=image.size[1]/250
    newx=round(image.size[0]/scaleportion)
    newy=round(image.size[1]/scaleportion)
    return newx, newy

def fix_image_scale(image):
    global flexible
    if flexible:
        imagesc = image.resize(get_fixed_scale(image))
        return imagesc
    else:
        return image
        

def pullconvertedimg():
    global flexible
    print("pulling converted")
    newimage = Encoding.getconverted()
    resized_image=fix_image_scale(newimage)
    resized_image=resized_image.resize(get_fixed_scale(resized_image))
    resimg = ImageTk.PhotoImage(resized_image)
    newimage_label.config(image=resimg)
    newimage_label.image = resimg  # Keep a reference to avoid garbage collection
def is_rec_room_active():
        """Check if 'Rec Room' is the active window."""
        try:
            # Get the active window
            active_window = gw.getActiveWindow()
            if active_window is not None:  # Ensure there is an active window
                return "Rec Room" in active_window.title  # Checks if "Rec Room" is in the title
            return False
        except Exception as e:
            print(f"Error checking active window: {e}")
            return False
        
def focus_string_importer():
    # Bring the Tkinter window to the foreground
    root.deiconify()  # Show the window if it is minimized
    root.focus_force()  # Set focus to the Tkinter window

def copy_to_recroom(img_data: List[str], db: float = 0.3) -> None:
    cancel_button.pack()

    global paused
    global time_label
    global num_strings
    global input_field
    global done_button
    global running
    global stop_animation_import
    global remaining_minutes, remaining_seconds
    global written_strings
    global delay
    global time_at_start
    running = True
    
    num_strings = len(img_data)
    monitor_check()  # Ensure monitor_check is defined properly
    
    # Set hotkey for pausing
    keyboard.add_hotkey('ctrl+p', pause_program)

    input_field = (int(SCREEN_DIMENSIONS[0] * 0.5), int(SCREEN_DIMENSIONS[1] * 0.34))
    done_button = (int(SCREEN_DIMENSIONS[0] * 0.08 - 150), int(SCREEN_DIMENSIONS[1] * 0.45))

    # Estimate time calculation
    estimated_time = math.floor((num_strings * (delay * 24)) / 60)
    estimated_seconds = round((num_strings * (delay * 24)) - (estimated_time * 60))
    # Schedule UI update for estimated time
    root.after(0, lambda: time_label.config(text=f"Estimated Time: {estimated_time} min {estimated_seconds} sec"))

    time_at_start = time.time()

    for num, string in enumerate(img_data):
        isrecroom()
        if not running:
            print('Import cancelled')
            break  # Exit the loop if the program is stopped

        # Use the helper function with pause check
        copy_with_pause_check(num, string, time_at_start)
    print("Importing Finished!")
    stop_animation_import = True
    remaining_seconds = 0
    remaining_minutes = 0
    written_strings = 0
    Update_ui()


def isrecroom():
    global time_at_start
    global running
    while not is_rec_room_active():
            if not running:
                break
            time.sleep(0.5)  # Sleep for a short time before checking again
            time_at_start = time_at_start+0.5

def copy_with_pause_check(num: int, string: str, time_at_start: float) -> None:
    global paused
    global written_strings
    global remaining_minutes
    global remaining_seconds
    global delay
    written_strings = num

    # Copy current string into clipboard
    pyperclip.copy(string)
    print(f"Copying string #{num + 1}/{num_strings}")
    Update_ui()
    # Click `List Create` string entry
    pyautogui.click()
    time.sleep(delay)
    isrecroom()
    # Click on the input field
    pyautogui.click(input_field)
    time.sleep(delay / 2)
    isrecroom()
    # Paste the string into input field
    pyautogui.hotkey("ctrl", "v")
    time.sleep(delay)
    isrecroom()
    # Click "Done"
    pyautogui.click(done_button)
    time.sleep(delay)
    isrecroom()
    # Move down using trigger handle in right hand
    pyautogui.click(button='right')
    time.sleep(delay / 3)
    isrecroom()
    # Update remaining time (calculate on main thread)
    elapsed_time = time.time() - time_at_start
    remaining_time = max(0, (math.floor((num_strings * (speed_slider.get() * 24)))) - elapsed_time)
    print(remaining_time)
    remaining_minutes = int(remaining_time // 60)
    remaining_seconds = round(remaining_time % 60)
    
    
    Update_ui()
    # Schedule UI update for estimated time left
    root.after(0, lambda: time_label.config(
        text=f"Estimated Time Left: {round(remaining_minutes)} min {remaining_seconds:.1f} sec"
    ))
    

def choose_image():
    global img_data, selected_image, ImageName
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        selected_image = Image.open(file_path)
        ImageName = os.path.basename(file_path)
        show_image(selected_image)

        print(f"Image selected: {file_path}")
        Update_ui()

def animate_button_text(button, pretext, getbool):
    """Animates the convert button text to show 'Converting.', 'Converting..', etc."""
    states = itertools.cycle([f"{pretext}.", f"{pretext}..", f"{pretext}..."])
    def update_text():
        # Dynamically access the global variable based on the name passed as getbool
        if globals()[getbool]:
            button.config(text="Done!")
        else:
            button.config(text=next(states))
            root.after(500, update_text)  # Change every 500 ms for smooth animation

    update_text()

def waitforme():
    if selected_image is None:
        print("No image selected!")
        return

    global stop_animation
    stop_animation = False  # Reset the stop flag
    animate_button_text(convert_button, "Converting", "stop_animation")  # Start animation loop
    #convert_button.config(text="converting...")
    root.after(50, convert)
    Update_ui()

def convert():
    # Run the encoding operation in a separate thread and use a callback for UI updates
    def run_encoding():
        global img_data, num_strings

        # Perform the encoding operation
        image_to_convert = fix_image_scale(selected_image)
        img_data = Encoding.main_from_image(dither_enabled, image_to_convert, list_size=64)

        # Get the number of encoded strings for UI updates
        num_strings = len(img_data)
        
        # Schedule the UI update on the main thread once encoding is complete
        root.after(0, encoding_complete_callback)
    
    # Start the encoding thread
    threading.Thread(target=run_encoding, daemon=True).start()

def encoding_complete_callback():
    global remaining_seconds, remaining_minutes, stop_animation
    stop_animation = True
    # Calculate the estimated time
    estimated_time = math.floor((num_strings * (speed_slider.get() * 24)) / 60)
    estimated_seconds = round((num_strings * (speed_slider.get() * 24)) - (estimated_time * 60))

    # Update the UI with estimated time and conversion status
    time_label.config(text=f"Estimated Time: {estimated_time} min {estimated_seconds} sec")
    convert_button.config(text="Done!")

    # Schedule the finishing delay and image update
    root.after(2000, finish_delay)
    pullconvertedimg()

    remaining_seconds = estimated_seconds
    remaining_minutes = estimated_time
    Update_ui()

def finish_delay():
    convert_button.config(text="Convert Image")

def show_image(imageshow):
    print(f"Chosen Image Size: {imageshow.size}")
    # Resize the image for display
    global image_label, ImageName
    if image_label is None:
        print("Error: image_label is not initialized.")
        return  # Exit the function if image_label is not ready 
    originalscaledimage = fix_image_scale(imageshow)
    scaledimage = imageshow.resize(get_fixed_scale(imageshow))
    print(f"the finished scaled {scaledimage}")
    img_tk = ImageTk.PhotoImage(image=scaledimage)
    image_label.config(image=img_tk)
    image_label.image = img_tk  # Keep a reference to avoid garbage collection
    image_label_size.config(text=f"Image: {ImageName}\n\n[Image Size]\nWidth:{originalscaledimage.size[0]}\nHeight: {originalscaledimage.size[1]}")

def start_program():
    global img_data
    global delay
    global stop_animation_import
    if img_data:
        print("Starting Import")
        stop_animation_import = False
        animate_button_text(start_button, "Importing", "stop_animation_import")
        threading.Thread(target=copy_to_recroom, args=(img_data, 0.03)).start()
    else: 
        print("Can not start import because there is no image converted")

def toggle_dither():
    global dither_enabled
    dither_enabled = not dither_enabled  # Toggle the dither state
    dither_button.config(text="Dither: On" if dither_enabled else "Dither: Off")  # Update button text

def toggle_flex():
    global selected_image
    global flexible
    flexible = not flexible  # Toggle the dither state
    flex_button.config(text="Flex: On" if flexible else "Flex: Off")  # Update button text
    show_image(selected_image)

def toggle_ui():
    global is_visible
    is_visible = not is_visible
    toggle_ui_button.config(text="Ui: On" if is_visible else "Ui: Off")  # Update button text
    if not is_visible:
        win32gui.ShowWindow(hWindow, win32con.SW_HIDE)  # Hide the window
    else:
        win32gui.ShowWindow(hWindow, win32con.SW_SHOW)  # Show the window

def timechanged(value):
    global delay
    global remaining_minutes, remaining_seconds
    delay = speed_slider.get()
    remaining_minutes = math.floor((num_strings * (speed_slider.get() * 24)) / 60)
    remaining_seconds = round((num_strings * (speed_slider.get() * 24)) - (remaining_minutes * 60))
    Update_ui()

def Update_ui():
    global uimsg
    global written_strings, num_strings, remaining_minutes, remaining_seconds
    if not (img_data is None):
        time_label.config(text=f"Estimated Time: {remaining_minutes} min {remaining_seconds} sec")
    # Update the message or perform any other updates here
    uimsg = (f"Delay: {float(speed_slider.get()):.2f}\n"
            f"Line: {written_strings}/{num_strings}\n"
            f"Time Remaining: {round(remaining_minutes)} Minutes | {round(remaining_seconds)} Seconds\n"
            "You can press alt+s to return to the string importer menu.\n"
            "(The Importing process will automatically pause)")
            
    win32gui.InvalidateRect(hWindow, None, True)  # Request a redraw
    #threading.Timer(0.3, Update_ui).start()  # Call this function again after 0.3 seconds


def create_win32_window():
    global hWindow
    hInstance = win32api.GetModuleHandle()
    className = 'MyWindowClassName'
    wndClass = win32gui.WNDCLASS()
    wndClass.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
    wndClass.lpfnWndProc = wndProc
    wndClass.hInstance = hInstance
    wndClass.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW)
    wndClass.lpszClassName = className
    wndClassAtom = win32gui.RegisterClass(wndClass)

    exStyle = win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST
    style = win32con.WS_POPUP | win32con.WS_VISIBLE | win32con.WS_DISABLED

    hWindow = win32gui.CreateWindowEx(
        exStyle,
        wndClassAtom,
        None,  # WindowName
        style,
        100,  # x
        100,  # y
        500,  # width
        150,  # height
        None,  # hWndParent
        None,  # hMenu
        hInstance,
        None  # lpParam
    )
    # Set the window to be layered with transparency
    win32gui.SetLayeredWindowAttributes(hWindow, 0x00FFFFFF, 190, win32con.LWA_ALPHA)  # 190 for ~70% opacity

    keyboard.add_hotkey('alt+s', focus_string_importer)

def wndProc(hWnd, message, wParam, lParam):
    global uimsg
    if message == win32con.WM_PAINT:
        hdc, paintStruct = win32gui.BeginPaint(hWnd)

        # Fill the window with a solid color background (e.g., light yellow)
        rect = win32gui.GetClientRect(hWnd)
        background_color = 0x00FFCC00  # Example color: light yellow
        background_brush = win32gui.CreateSolidBrush(background_color)
        win32gui.FillRect(hdc, rect, background_brush)

        # Draw a white outline around the window
        outline_pen = win32gui.CreatePen(win32con.PS_SOLID, 3, win32api.RGB(255, 255, 255))  # White pen
        win32gui.SelectObject(hdc, outline_pen)
        win32gui.SelectObject(hdc, background_brush)
        win32gui.Rectangle(hdc, 0, 0, rect[2], rect[3])

        # Set font properties for default text size
        dpiScale = win32ui.GetDeviceCaps(hdc, win32con.LOGPIXELSX) / 60.0
        default_font_size = 16  # Default font size
        small_font_size = 10     # Smaller font size for lines 4 and 5

        # Create default font
        lf_default = win32gui.LOGFONT()
        lf_default.lfFaceName = "Times New Roman"
        lf_default.lfHeight = int(round(dpiScale * default_font_size))
        hf_default = win32gui.CreateFontIndirect(lf_default)
        lf_small = win32gui.LOGFONT()
        lf_small.lfFaceName = "Times New Roman"
        lf_small.lfHeight = int(round(dpiScale * small_font_size))
        hf_small = win32gui.CreateFontIndirect(lf_small)
        win32gui.SelectObject(hdc, hf_default)

        # Set text color to black and transparent background for text
        win32gui.SetTextColor(hdc, win32api.RGB(0, 0, 0))
        win32gui.SetBkMode(hdc, win32con.TRANSPARENT)

        # Split message by line and draw each line
        lines = uimsg.split("\n")
        line_height = 27  # Adjust line height as needed
        y_offset = 10  # Initial vertical offset

        for i, line in enumerate(lines):
            line_rect = (rect[0] + 10, rect[1] + y_offset, rect[2] - 10, rect[3])
            
            # Check if this is line 4 or 5 (index starts from 0, so 3 and 4)
            if i == 3 or i == 4:  # Lines 4 and 5
                # Create smaller font for these lines
                win32gui.SelectObject(hdc, hf_small)
            else:
                # Use default font for other lines
                win32gui.SelectObject(hdc, hf_default)

            # Draw the text
            win32gui.DrawText(hdc, line, -1, line_rect, win32con.DT_LEFT | win32con.DT_NOCLIP | win32con.DT_SINGLELINE)
            y_offset += line_height  # Move down for the next line

        # Clean up and release the device context
        win32gui.DeleteObject(hf_default)
        win32gui.DeleteObject(hf_small)
        win32gui.EndPaint(hWnd, paintStruct)
        return 0

    elif message == win32con.WM_DESTROY:
        print('Closing the window.')
        win32gui.PostQuitMessage(0)
        return 0

    else:
        return win32gui.DefWindowProc(hWnd, message, wParam, lParam)
    
def run_win32_message_loop():
    win32gui.PumpMessages()

def chose_link(*args):
    global selected_image, ImageName
    # This function will be called whenever the content of link_input changes
    new_input = link_var.get()
    print(f"Link input changed: {new_input}")
    
    try:
        # Attempt to fetch the image from the provided link
        response = requests.get(new_input)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        
        # Open the image using PIL
        image_data = io.BytesIO(response.content)
        selected_image = Image.open(image_data)
        parsed_url = urlparse(new_input)
        # Get domain and main path (first part only)
        domain = parsed_url.netloc
        path = parsed_url.path.strip('/').split('/')[0]  # Get first path segment
        ImageName=f"{domain}/{path}" if path else domain
        # Show the image
        show_image(selected_image)

        print(f"Image selected: {new_input}")
        Update_ui()  # Call the function to update the UI as needed
    except Exception as e:
        print(f"Failed to fetch image: {e}")

def on_entry_click(event):
    """Function to handle entry focus to clear placeholder text and select all text."""
    if link_input.get() == "Paste a link here":
        link_input.delete(0, "end")  # Clear the placeholder
        link_input.config(fg="black")  # Change text color to black
    link_input.select_range(0, tk.END)  # Select all text in the entry

def on_focusout(event):
    """Function to handle losing focus to restore placeholder text."""
    if link_input.get() == "":
        link_input.insert(0, "Paste a link here")  # Restore placeholder
        link_input.config(fg="lightgray")  # Change text color to light gray

def import_cancel():
    print("Cancelled")
    global running
    global stop_animation_import
    global written_strings
    running = False
    stop_animation_import = True
    cancel_button.pack_forget()
    root.after(2000, resetstartbutton)
    written_strings = 0
    Update_ui()

def resetstartbutton():
    start_button.config(text="Start Program")

def main():
    create_win32_window()
    import threading
    threading.Thread(target=run_win32_message_loop, daemon=True).start()
    if monitor_check() == -1:
        exit(input("\nScreen aspect ratio not optimal for importing.\n"
                   "Press enter to exit\n"
                   "> "))
    global img_data, image_label, time_label, convert_button, dither_button, num_strings, dither_enabled, newimage_label
    global speed_slider, toggle_ui_button, link_input, flex_button, image_label_size, start_button, cancel_button
    global link_var
    img_data = []
    global root
    root = tk.Tk()
    root.title("RR String Importer")
    root.geometry("800x900")
    root.configure(bg="#2c2f33")  # Dark background for a modern look

    # Custom button creation function for consistent style
    def create_button(master, text, command):
        return tk.Button(
            master, text=text, font=("Helvetica", 12), bg=button_bg_color, fg=text_color, 
            activebackground="#5a6cb2", relief="flat", command=command, width=20, height=2
        )
    
    # Style settings
    button_bg_color = "#7289da"
    text_color = "white"
    label_bg = "#2c2f33"

    # Main Frame to contain widgets with padding for spacing
    main_frame = tk.Frame(root, bg=label_bg)
    main_frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Create a grid layout
    for i in range(2):  # Two columns
        main_frame.grid_columnconfigure(i, weight=1)

    # Title Label
    title_label = tk.Label(
        main_frame, text="RR String Importer", font=("Helvetica", 16, "bold"), bg=label_bg, fg=text_color
    )
    title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="ew")  # Span both columns

    # Create a frame for buttons on the left
    button_frame = tk.Frame(main_frame, bg=label_bg)
    button_frame.grid(row=1, column=0, padx=(10, 20), sticky="ns")  # Stick to the left

    # Create a frame for data labels on the right
    data_frame = tk.Frame(main_frame, bg=label_bg)
    data_frame.grid(row=1, column=1, padx=(20, 10), sticky="ns")  # Stick to the right

    # Display Labels
    image_label = tk.Label(data_frame, text="No Image Selected", font=("Helvetica", 12), bg=label_bg, fg="lightgray")
    image_label.pack(pady=10)
    image_label_size = tk.Label(data_frame, text="", font=("Helvetica", 8), bg=label_bg, fg="lightgray")
    image_label_size.pack(pady=2)

    newimage_label = tk.Label(data_frame, text="No Image Converted", font=("Helvetica", 12), bg=label_bg, fg="lightgray")
    newimage_label.pack(pady=10)
    
    toggle_ui_button = create_button(data_frame, "Ui: On", toggle_ui)
    toggle_ui_button.pack(pady=10)

    # Buttons
    choose_button = create_button(button_frame, "Choose Image", choose_image)
    choose_button.pack(pady=10)
    link_var = tk.StringVar()
    link_var.trace("w", chose_link)
    link_input = tk.Entry(button_frame, textvariable=link_var, fg="lightgray", font=("Helvetica", 12))
    link_input.insert(0, "Paste a link here")  # Set initial placeholder text
    link_input.bind("<FocusIn>", on_entry_click)  # Bind focus in event
    link_input.bind("<FocusOut>", on_focusout)  # Bind focus out event
    link_input.pack(pady=10)

    flex_button = create_button(button_frame, "Flex: Off", toggle_flex)
    flex_button.pack(pady=10)
    time_label = tk.Label(button_frame, text="This chooses whether the image is scaled relative\n to 250 height or not scaled at all \nRecommended off for printing shirts", font=("Helvetica", 6), bg=label_bg, fg="lightgray")
    time_label.pack(pady=10)

    dither_button = create_button(button_frame, "Dither: Off", toggle_dither)
    dither_button.pack(pady=10)

    convert_button = create_button(button_frame, "Convert Image", waitforme)
    convert_button.pack(pady=10)
    
    delay_Label = tk.Label(button_frame, text="Delay Time (s)", font=("Helvetica", 12), bg=label_bg, fg="lightgray")
    delay_Label.pack(pady=10)
    
    speed_slider = tk.Scale(button_frame, from_=0.05, to=0.5, resolution=0.01, orient=tk.HORIZONTAL,
                      bg="#7289da", sliderlength=30, length=300, highlightbackground="#7289da",
                      troughcolor="#7289da", fg="white", activebackground="#5a6cb2", command=timechanged)
    speed_slider.pack()

    start_button = create_button(button_frame, "Start Program", start_program)
    start_button.pack(pady=10)
    
    cancel_button = tk.Button(button_frame, text="Cancel", command=import_cancel, height=1, width=12,
                              font=("Helvetica", 10), bg=button_bg_color, fg=text_color, activebackground="#5a6cb2", relief="flat")
    cancel_button.pack_forget()  # Hide the cancel button initially

    
    time_label = tk.Label(button_frame, text="Estimated Time: ", font=("Helvetica", 12), bg=label_bg, fg="lightgray")
    time_label.pack(pady=10)

    # Run the application
    root.mainloop()

log = setup_logger()
    
if __name__ == "__main__":
    try:
        main()
        
    except (Exception, KeyboardInterrupt):
        log.exception("ERROR", exc_info=True)
        input()
