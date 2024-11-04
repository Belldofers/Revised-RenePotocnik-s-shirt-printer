try:
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
    import tkinter as tk
    from tkinter import Canvas, Frame
    from tkinter import ttk
    from tkinter import messagebox, filedialog
    from PIL import Image, ImageTk
    from typing import Optional, Tuple, List

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
SCREEN_DIMENSIONS = (800, 600)  # Example screen dimensions
root = None  # Tkinter root window placeholder
selected_image = None

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

def stop_program():
    global running
    running = 0
    print("Alt+S pressed. Stopping program.")

def pause_program():
    global paused
    paused = not paused
    print("Program paused." if paused else "Program resumed.")

def pullconvertedimg():
    print("pulling converted")
    newimage = Encoding.getconverted()
    print(f"\n{newimage}|a\n")
    resized_image = newimage.resize((212, 236))  # Adjust the size as desired
    resimg = ImageTk.PhotoImage(resized_image)
    print(f"\n{resimg}|a\n")
    newimage_label.config(image=resimg)
    newimage_label.image = resimg  # Keep a reference to avoid garbage collection

def copy_to_recroom(img_data: List[str], delay: float = 0.03) -> None:
    global paused
    global time_label
    global num_strings
    global input_field
    global done_button

    window_title = "Rec Room"
    num_strings = len(img_data)
    monitor_check()  # Make sure to define this function appropriately

    
    keyboard.add_hotkey('ctrl+p', pause_program)

    input_field = (int(SCREEN_DIMENSIONS[0] * 0.5), int(SCREEN_DIMENSIONS[1] * 0.34))
    done_button = (int(SCREEN_DIMENSIONS[0] * 0.08 - 150), int(SCREEN_DIMENSIONS[1] * 0.45))

    # Estimate time
    estimated_time = math.floor((num_strings * (speed_slider.get()*24)) / 60)
    estimated_seconds = round((num_strings * (speed_slider.get()*24)) - (estimated_time * 60))
    time_label.config(text=f"Estimated Time: {estimated_time} min {estimated_seconds} sec")

    time_at_start = time.time()

    for num, string in enumerate(img_data):
        is_window_active(window_title)
        delay = speed_slider.get()
        if not running:
            print('Import cancelled')
            break  # Exit the loop if the program is stopped

        copy_with_pause_check(num, string, delay, time_at_start)  # Start copying with pause check

def copy_with_pause_check(num: int, string: str, delay: float, time_at_start: float) -> None:
    global paused
    global written_strings
    global remaining_minutes
    global remaining_seconds
    written_strings = num
    if paused:
        root.after(100, copy_with_pause_check, num, string, delay, time_at_start)  # Check again after 100 ms
        return

    # Copy current string into clipboard
    pyperclip.copy(string)
    print(f"Copying string #{num + 1}/{num_strings}")

    # Click `List Create` string entry
    pyautogui.click()
    time.sleep(delay)

    # Click on the input field
    pyautogui.click(input_field)
    time.sleep(delay / 2)

    # Paste the string into input field
    pyautogui.hotkey("ctrl", "v")
    time.sleep(delay)

    # Click "Done"
    pyautogui.click(done_button)
    time.sleep(delay)

    # Move down using trigger handle in right hand
    pyautogui.click(button='right')
    time.sleep(delay / 3)

    # Update remaining time
    elapsed_time = time.time() - time_at_start
    remaining_time = max(0, (num_strings * (delay*24)) - elapsed_time)
    remaining_minutes = remaining_time // 60
    remaining_seconds = remaining_time % 60
    time_label.config(text=f"Estimated Time Left: {remaining_minutes} min {remaining_seconds:.1f} sec")
    Update_ui()

def copy_and_paste(num, string, delay, time_at_start):
    global paused
    global input_field
    global done_button
    # Start the copying process
    copy_with_pause_check(num, string, delay, time_at_start)

def choose_image():
    global img_data, selected_image
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        selected_image = Image.open(file_path)
        
        show_image(selected_image)

        print(f"Image selected: {file_path}")
        Update_ui()

def waitforme():
    if selected_image is None:
        print("No image selected!")
        return
    convert_button.config(text="converting...")
    root.after(50, convert)
    Update_ui()

def convert():
    print(dither_enabled)
    global img_data
    global remaining_seconds
    global remaining_minutes
    global num_strings
    if not(img_data is None): 
        img_data = Encoding.main_from_image(dither_enabled, selected_image, list_size=64)  # Adjust this based on your encoding
        num_strings = len(img_data)
        print(num_strings)
        estimated_time = math.floor((num_strings * (speed_slider.get()*24)) / 60)
        estimated_seconds = round((num_strings * (speed_slider.get()*24)) - (estimated_time * 60))
        time_label.config(text=f"Estimated Time: {estimated_time} min {estimated_seconds} sec")
        convert_button.config(text="Done!")
        root.after(2000, finish_delay)
        pullconvertedimg()
        remaining_seconds = estimated_seconds
        remaining_minutes = estimated_time
        Update_ui()

def finish_delay():
    convert_button.config(text="Covert Image")

def show_image(image):
    # Resize the image for display
    global image_label
    if image_label is None:
        print("Error: image_label is not initialized.")
        return  # Exit the function if image_label is not ready
    image = image.resize((250, 250))
    img_tk = ImageTk.PhotoImage(image)
    image_label.config(image=img_tk)
    image_label.image = img_tk  # Keep a reference to avoid garbage collection

def start_program():
    global img_data
    delay = 0.02  # Set your desired delay here
    copy_to_recroom(img_data=img_data, delay=delay)

def toggle_dither():
    global dither_enabled
    dither_enabled = not dither_enabled  # Toggle the dither state
    dither_button.config(text="Dither: On" if dither_enabled else "Dither: Off")  # Update button text

def toggle_ui():
    global is_visible
    is_visible = not is_visible
    toggle_ui_button.config(text="Ui: On" if is_visible else "Ui: Off")  # Update button text
    if not is_visible:
        win32gui.ShowWindow(hWindow, win32con.SW_HIDE)  # Hide the window
    else:
        win32gui.ShowWindow(hWindow, win32con.SW_SHOW)  # Show the window

def timechanged(value):
    Update_ui()

def Update_ui():
    global uimsg
    global written_strings, num_strings, remaining_minutes, remaining_seconds
    if not (img_data is None):
        remaining_minutes = math.floor((num_strings * (speed_slider.get()*24)) / 60)
        remaining_seconds = round((num_strings * (speed_slider.get()*24)) - (remaining_minutes * 60))
        time_label.config(text=f"Estimated Time: {remaining_minutes} min {remaining_seconds} sec")
    # Update the message or perform any other updates here
    uimsg = (f"Delay: {float(speed_slider.get()):.2f}\n"
            f"Line: {written_strings}/{num_strings}\n"
            f"Time Remaining: {remaining_minutes} Minutes | {remaining_seconds} Seconds")
    win32gui.InvalidateRect(hWindow, None, True)  # Request a redraw
    #threading.Timer(0.3, Update_ui).start()  # Call this function again after 0.3 seconds

def stop_program():
    global uimsg
    uimsg = "Program Stopping..."  # Update the text
    #win32gui.InvalidateRect(hWindow, None, True)  # Request a redraw
    #win32gui.UpdateWindow(hWindow)
    #in32gui.PostQuitMessage(0)
    #print("Alt+S pressed. Stopping program.")

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
        100,  # height
        None,  # hWndParent
        None,  # hMenu
        hInstance,
        None  # lpParam
    )
    # Set the window to be layered with transparency
    win32gui.SetLayeredWindowAttributes(hWindow, 0x00FFFFFF, 190, win32con.LWA_ALPHA)  # 190 for ~70% opacity

    keyboard.add_hotkey('alt+s', stop_program)

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

        # Set font properties
        dpiScale = win32ui.GetDeviceCaps(hdc, win32con.LOGPIXELSX) / 60.0
        fontSize = 15

        lf = win32gui.LOGFONT()
        lf.lfFaceName = "Times New Roman"
        lf.lfHeight = int(round(dpiScale * fontSize))
        hf = win32gui.CreateFontIndirect(lf)
        win32gui.SelectObject(hdc, hf)

        # Set text color to black and transparent background for text
        win32gui.SetTextColor(hdc, win32api.RGB(0, 0, 0))
        win32gui.SetBkMode(hdc, win32con.TRANSPARENT)

        # Split message by line and draw each line
        lines = uimsg.split("\n")
        line_height = 25  # Adjust line height as needed
        y_offset = 10  # Initial vertical offset

        for line in lines:
            line_rect = (rect[0] + 10, rect[1] + y_offset, rect[2] - 10, rect[3])
            win32gui.DrawText(hdc, line, -1, line_rect, win32con.DT_LEFT | win32con.DT_NOCLIP | win32con.DT_SINGLELINE)
            y_offset += line_height  # Move down for the next line

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

def main():
    create_win32_window()
    import threading
    keyboard.add_hotkey('alt+s', stop_program)
    threading.Thread(target=run_win32_message_loop, daemon=True).start()
    if monitor_check() == -1:
        exit(input("\nScreen aspect ratio not optimal for importing.\n"
                   "Press enter to exit\n"
                   "> "))
    global img_data, image_label, time_label, convert_button, dither_button, num_strings, dither_enabled, newimage_label
    global speed_slider, toggle_ui_button
    img_data = []
    global root
    root = tk.Tk()
    root.title("RR String Importer")
    root.geometry("700x700")
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

    time_label = tk.Label(data_frame, text="Estimated Time: ", font=("Helvetica", 12), bg=label_bg, fg="lightgray")
    time_label.pack(pady=10)

    newimage_label = tk.Label(data_frame, text="No Image Converted", font=("Helvetica", 12), bg=label_bg, fg="lightgray")
    newimage_label.pack(pady=10)
    
    toggle_ui_button = create_button(data_frame, "Ui: On", toggle_ui)
    toggle_ui_button.pack(pady=10)

    # Buttons
    choose_button = create_button(button_frame, "Choose Image", choose_image)
    choose_button.pack(pady=10)

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

    # Run the application
    root.mainloop()

log = setup_logger()
    
if __name__ == "__main__":
    try:
        main()
        
    except (Exception, KeyboardInterrupt):
        log.exception("ERROR", exc_info=True)
