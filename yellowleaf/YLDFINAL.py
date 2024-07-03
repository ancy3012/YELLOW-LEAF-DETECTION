import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import ImageTk, Image
from tkinter import PhotoImage
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import datetime
import time
import base64
import os  # Import the os module for working with file paths
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import inch

# Global variable for the folder path
output_folder_path = "output_folder"  # Change this to the desired folder name

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

def create_grid_image(output_image_path, tree_coordinates):
    # Create a new PDF document
    doc = SimpleDocTemplate(output_image_path, pagesize=letter)
    
    # Create a list for the table data
    data = [["Tree Number", "X Coordinate", "Y Coordinate"]]

    # Add tree coordinates to the data list
    for idx, (x, y) in enumerate(tree_coordinates):
        data.append([idx + 1, x, y])

    # Create a table with the data
    table = Table(data, colWidths=[1 * inch, 1 * inch, 1 * inch])

    # Style the table with grid lines
    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ])
    table.setStyle(style)

    # Build the table and save it to the output_image_path
    elements = []
    elements.append(table)
    doc.build(elements)

def analyze_image(image_path, show_coordinates):
    # Read the image
    img = cv2.imread(image_path)

    # Convert to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define the green color range
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([70, 255, 255])

    # Create a mask for green pixels
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # Find the contours of the green regions
    contours_green, hierarchy_green = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Modify the yellow color range
    lower_yellow = np.array([15, 100, 100])
    upper_yellow = np.array([30, 255, 255])

    # Create a mask for yellow pixels
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # Find the contours of the yellow regions
    contours_yellow, hierarchy_yellow = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    tree_number = 1  # Initialize tree number
    affected_tree_counter = 0  # Counter variable to keep track of affected trees
    red_dot_counter = 0  # Counter variable to keep track of red dots

    # Initialize a list to store the coordinates of the numbered trees
    tree_coordinates = []

    for c in contours_yellow:
        # Find the center and radius of the contour
        (x, y), radius = cv2.minEnclosingCircle(c)
        # Convert to integer values
        center = (int(x), int(y))
        radius = int(radius)

        # Set a threshold to ignore minute circles (adjust as needed)
        min_radius_threshold = 10

        if radius > min_radius_threshold:
            # Increase the radius by 10%
            radius = int(radius * 1.1)
            # Draw a red circle
            cv2.circle(img, center, radius, (0, 0, 255), 2)
            affected_tree_counter += 1  # Increment the counter for each affected tree
            red_dot_counter += 1  # Increment the counter for each red dot

            # Annotate the coordinates if enabled
            if show_coordinates:
                text = f"({center[0]}, {center[1]})"
                cv2.putText(img, text, (center[0] + 10, center[1] + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # Annotate the tree number and increment it
            text = str(tree_number)
            cv2.putText(img, text, (center[0] - 10, center[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Append the coordinates to the list
            tree_coordinates.append((center[0], center[1]))

            tree_number += 1

    # Check if there are any areca nut trees in the image
    if len(contours_green) > 0 or len(contours_yellow) > 0:
        if len(contours_yellow) > 0:
            # Print a message that some of the areca nut trees are affected by yellow leaf disease
            result = f"Hello User!, {affected_tree_counter} of the areca nut tree leaves are affected by yellow leaf disease."
        else:
            # Print a message that none of the areca nut trees are affected by yellow leaf disease
            result = f"Hello User! None of the areca nut trees are affected by yellow leaf disease."

        # Save the output image
        output_path = "output_image.jpg"
        cv2.imwrite(output_path, img)
        return result, output_path, red_dot_counter, tree_coordinates
    else:
        # Print a message that there are no areca nut trees in the image
        return f"Hello User! There are no areca nut trees in the image.", None, 0

    # Save the output image inside the output folder
    output_path = os.path.join(output_folder_path, "output_image.jpg")
    cv2.imwrite(output_path, img)

    return result, output_path, red_dot_counter, tree_coordinates


def analysis_page():
    analysis_window = tk.Tk()
    analysis_window.title("Areca Nut Tree Analyzer - Analysis Page")
    analysis_window.geometry(f"{analysis_window.winfo_screenwidth()}x{analysis_window.winfo_screenheight()}")  # Set window size
    background_image = Image.open(r"C:\Users\Ancita\Downloads\yellowleaf\backgroungimg.jpg")  # Replace with your background image
    background_image_tk = ImageTk.PhotoImage(background_image)
    background_label = tk.Label(analysis_window, image=background_image_tk)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Load logo image
    logo_image = PhotoImage(file=r"C:\Users\Ancita\Downloads\yellowleaf\png.png")  # Replace with the actual path to your logo image

    # Header Frame
    header_frame = ttk.Frame(analysis_window, style="Header.TFrame", padding=(10, 10, 10, 10))
    header_frame.pack(side=tk.TOP, fill=tk.X)

    # Load the background image for the header
    header_background_image = Image.open(r"back3.jpg")
    header_background_image = header_background_image.resize((analysis_window.winfo_screenwidth(), 200))
    header_background_image_tk = ImageTk.PhotoImage(header_background_image)

    # Create a label within the header frame to display the background image
    header_background_label = tk.Label(header_frame, image=header_background_image_tk)
    header_background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Create and place widgets for the welcome message
    welcome_label = tk.Label(header_frame, text="Yellow Leaf Disease Analyzer", font=("Helvetica", 32), fg="black", bg="lightblue")
    welcome_label.config(bd=5, relief="solid", highlightthickness=5, highlightbackground="gold")
    welcome_label.pack(pady=25)

    # Create and place widget for the logo
    logo_label = tk.Label(header_frame, image=logo_image)
    logo_label.image = logo_image
    logo_label.place(x=10, y=50, anchor=tk.W)

    s = ttk.Style()
    s.configure("Header.TFrame", background="gold")

    
    def select_image():
        global selected_image_path
        selected_image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if selected_image_path:
            image_preview.config(text=" Image Successfully Analyzed", image=None)
            result_text.config(text="")
            result_image.config(image=None)
            save_button.config(state="disabled")
            analyze_image_handler()

    def analyze_image_handler():
        if selected_image_path:
            loading_label.config(text="Analyzed")
            loading_label.update()

            show_coordinates = coordinates_var.get() == 1

        # Perform the image analysis
            result, output_path, red_dot_counter, tree_coordinates = analyze_image(selected_image_path, show_coordinates)
            result_text.config(text=result)

            if output_path:
            # Get the current timestamp
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # Create the folder if it doesn't exist
                yld_images_folder = os.path.join(output_folder_path, "YLD Images")
                if not os.path.exists(yld_images_folder):
                    os.makedirs(yld_images_folder)

            # Construct the filename with timestamp
                analyzed_image_filename = f"analyzed_image_{timestamp}.jpg"
                analyzed_image_path = os.path.join(yld_images_folder, analyzed_image_filename)

            # Save the analyzed image with the timestamped filename
                img = Image.open(output_path)
                img.save(analyzed_image_path)

                image = Image.open(analyzed_image_path)
                image.thumbnail((500, 400))
                result_image.image = ImageTk.PhotoImage(image)
                result_image.config(image=result_image.image)
                save_button.config(state="normal")

                loading_label.config(text="")
        else:
            result_text.config(text="Please select an image.")
        
    def save_image():
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG Image", "*.jpg")])
        if file_path:
            output_path = os.path.join(output_folder_path, "output_image.jpg")
            try:
                # Save the analyzed image with the user-specified file name
                img = Image.open(output_path)
                img.save(file_path)
                save_label.config(text="Image saved successfully.")
            except Exception as e:
                save_label.config(text="Failed to save the image.")
                print(e)


                
    # Create and place widget
    button_frame = ttk.Frame(analysis_window, style="TFrame", borderwidth=10, relief=tk.RAISED)  # Added borderwidth and relief options
    button_frame.pack(side=tk.TOP, pady=20)   # Center the frame at the top

    select_button = tk.Button(button_frame, text="Select Image", command=select_image, bg="#0074D9", fg="white", font=("Arial", 12), bd=2, relief=tk.GROOVE, highlightbackground="#001F3F")
    select_button.pack(side=tk.LEFT, padx=10)

    coordinates_var = tk.IntVar()
    coordinates_check = tk.Checkbutton(button_frame, text="Show Coordinates", variable=coordinates_var, background="#2E2E2E", foreground="white")
    coordinates_check.pack(side=tk.LEFT, padx=10)

    save_button = tk.Button(button_frame, text="Save Image", state="disabled", command=save_image, bg="#0074D9", fg="white", font=("Arial", 12), bd=2, relief=tk.GROOVE, highlightbackground="#001F3F")
    save_button.pack(side=tk.LEFT, padx=10)

    ttk.Style().configure("TFrame", background="#2E2E2E")   # Set checkbutton background and foreground color

    image_preview = tk.Label(analysis_window, text="No Image Selected")
    image_preview.pack(pady=10)

    result_text = tk.Label(analysis_window, text="")
    result_text.pack(pady=10)

    result_image_frame = tk.Frame(analysis_window)
    result_image_frame.pack()

    result_image_canvas = tk.Canvas(result_image_frame, width=400, height=400)
    result_image_canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    result_image = tk.Label(result_image_canvas)
    result_image.pack()


    save_label = tk.Label(analysis_window, text="", font=("Helvetica", 12), fg="#e74c3c")  # Modern font and color
    save_label.pack(pady=30)

    loading_label = tk.Label(analysis_window, text="", font=("Helvetica", 12), fg="#f39c12")  # Modern font and color
    loading_label.pack()

    analysis_window.mainloop()

# Main program
analysis_page()
