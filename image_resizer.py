import os
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox, StringVar, Checkbutton, BooleanVar, Canvas
from tkinter.ttk import Progressbar, Style, Frame, LabelFrame
from PIL import Image, ImageTk

# Declare global variables here
selected_files = []  # List to store paths of selected images
output_dir_var = None
width_var = None
height_var = None
aspect_ratio_locked = None
progress_bar = None
preview_canvas = None
root = None  # root window

def select_images():
    global selected_files
    selected_files = filedialog.askopenfilenames(
        title="Select Images",
        filetypes=[("Image Files", "*.jpg *.jpeg *.png *.gif")]
    )
    if selected_files:
        show_notification(f"{len(selected_files)} images selected.")

def browse_output_dir():
    path = filedialog.askdirectory()
    output_dir_var.set(path)

def calculate_new_dimensions(img, target_width, target_height):
    original_width, original_height = img.size
    aspect_ratio = original_width / original_height
    if aspect_ratio != target_width / target_height and not aspect_ratio_locked.get():
        if target_width / target_height > aspect_ratio:
            target_width = int(target_height * aspect_ratio)
        else:
            target_height = int(target_width / aspect_ratio)
    return target_width, target_height

def update_preview(img):
    # Resize and show preview in the preview canvas
    img_preview = img.resize((300, 300), Image.ANTIALIAS)
    tk_img = ImageTk.PhotoImage(img_preview)
    preview_canvas.create_image(150, 150, image=tk_img)
    preview_canvas.image = tk_img

def resize_images():
    global selected_files
    output_dir = output_dir_var.get().strip()
    try:
        width = int(width_var.get().strip())
        height = int(height_var.get().strip())
    except ValueError:
        show_notification("Width and Height must be numeric values!")
        return

    if not selected_files:
        show_notification("No images selected!")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    progress_bar['maximum'] = len(selected_files)
    progress_bar['value'] = 0

    for idx, input_path in enumerate(selected_files):
        filename = os.path.basename(input_path)
        output_path = os.path.join(output_dir, filename)  # Save with the same format as original

        try:
            with Image.open(input_path) as img:
                new_width, new_height = calculate_new_dimensions(img, width, height)
                img_resized = img.resize((new_width, new_height), Image.ANTIALIAS)
                img_resized.save(output_path)  # Save without changing the format

                if idx == 0:  # Update preview for the first image only
                    update_preview(img_resized)
        except Exception as e:
            show_notification(f"Error resizing {filename}: {e}")
            return

        progress_bar['value'] = idx + 1
        root.update_idletasks()

    show_notification("All selected images resized successfully!")

def show_splash_screen():
    # Create a splash window
    splash = Tk()
    splash.title("Loading...")
    splash.geometry("400x200")
    splash.configure(bg="#1a1a6e")

    Label(splash, text="Image Resizer Pro", font=("Helvetica", 30, "bold"), fg="#4caf50", bg="#1a1a6e").pack(expand=True)
    progress_bar_splash = Progressbar(splash, length=300, mode='indeterminate')
    progress_bar_splash.pack(pady=20)
    progress_bar_splash.start()
    splash.after(2000, lambda: [splash.destroy(), open_main_window()])
    splash.mainloop()

def open_main_window():
    global root
    root = Tk()
    root.title("Image Resizer Pro")
    root.geometry("800x500")
    
    # Initialize variables after root window creation
    global output_dir_var, width_var, height_var, aspect_ratio_locked, preview_canvas
    output_dir_var = StringVar(root)
    width_var = StringVar(root)
    height_var = StringVar(root)
    aspect_ratio_locked = BooleanVar(root)

    # Set default values
    aspect_ratio_locked.set(True)

    # Styling
    style = Style()
    style.theme_use('clam')  # Set modern theme

    title_font = ("Helvetica", 16, "bold")
    label_font = ("Helvetica", 12)
    button_font = ("Helvetica", 10)
    button_bg = "#4caf50"
    button_fg = "#ffffff"
    bg_color = "#e0e0e0"
    fg_color = "#333333"

    root.configure(bg=bg_color)

    # Logo
    Label(root, text="Image Resizer Pro", font=("Helvetica", 30, "bold"), fg="#ff9800", bg=bg_color).pack(pady=10)
    Label(root, text="Resize your images quickly", font=title_font, bg=bg_color).pack(pady=10)

    # Frame for inputs
    frame = LabelFrame(root, text="Resize Options", padding=10)
    frame.pack(pady=20, fill="both", expand=True)

    Button(frame, text="Select Images", command=select_images, font=button_font, bg=button_bg, fg=button_fg).grid(row=0, column=0, padx=(50,10), pady=5)

    Label(frame, text="Output Directory:", font=label_font, bg=bg_color).grid(row=1, column=0, padx=10, pady=5, sticky="e")
    Entry(frame, textvariable=output_dir_var, width=40).grid(row=1, column=1, padx=10, pady=5)
    Button(frame, text="Browse", command=browse_output_dir, font=button_font, bg=button_bg, fg=button_fg).grid(row=1, column=2, padx=10, pady=5)

    Label(frame, text="Width (pixels):", font=label_font, bg=bg_color).grid(row=2, column=0, padx=10, pady=5, sticky="e")
    Entry(frame, textvariable=width_var, width=20).grid(row=2, column=1, padx=10, pady=5)

    Label(frame, text="Height (pixels):", font=label_font, bg=bg_color).grid(row=3, column=0, padx=10, pady=5, sticky="e")
    Entry(frame, textvariable=height_var, width=20).grid(row=3, column=1, padx=10, pady=5)

    Checkbutton(frame, text="Lock Aspect Ratio", variable=aspect_ratio_locked, font=label_font, bg=bg_color).grid(row=4, column=1, padx=10, pady=5)

    Button(root, text="Resize Images", command=resize_images, font=button_font, bg=button_bg, fg=button_fg).pack(pady=20)

    # Progress bar
    global progress_bar
    progress_bar = Progressbar(root, length=400, mode='determinate')
    progress_bar.pack(pady=10)

    # Preview canvas
    preview_canvas = Canvas(root, width=300, height=300, bg=bg_color)
    preview_canvas.pack()

    # Notification label
    global notification
    notification = Label(root, text="", font=("Helvetica", 10), bg=bg_color)
    notification.pack()

    root.mainloop()

def show_notification(message):
    notification.config(text=message, fg="#4caf50")

# Run the splash screen first
show_splash_screen()
