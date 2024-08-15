import tkinter as tk
from tkinter import filedialog, messagebox
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Display.SimpleGui import init_display
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeWire
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepTools import breptools_UVBounds
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE
from OCC.Display.OCCViewer import rgb_color
from OCC.Display.backend import load_backend
import vtk
import os

# Global variable to store the file path
step_file_path = None

def read_step_file(file_path):
    """Read STEP file and return shape."""
    step_reader = STEPControl_Reader()
    status = step_reader.ReadFile(file_path)
    
    if status != 1:
        raise Exception("Error reading STEP file.")
    
    step_reader.TransferRoots()
    shape = step_reader.OneShape()
    return shape

def process_step_file():
    """Handle the STEP file processing."""
    global step_file_path
    step_file_path = filedialog.askopenfilename(filetypes=[("STEP files", "*.stp"), ("STEP files", "*.STEP"), ("STEP files", "*.step")])
    
    if not step_file_path:
        messagebox.showwarning("Warning", "No file selected.")
        return
    
    print(f"Selected file: {step_file_path}")
    
    try:
        shape = read_step_file(step_file_path)
        messagebox.showinfo("Success", f"File {step_file_path} loaded successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def visualize_step_file():
    """Visualize the STEP file."""
    if not step_file_path:
        messagebox.showwarning("Warning", "No file selected for visualization.")
        return

    # Initialize the display
    display, start_display, add_menu, add_function_to_menu = init_display()

    # Read the STEP file
    shape = read_step_file(step_file_path)
    
    # Display the shape
    display.DisplayShape(shape, update=True)
    
    # Start the VTK display
    start_display()

def visualize_mesh():
    """Visualize the mesh of the STEP file."""
    if not step_file_path:
        messagebox.showwarning("Warning", "No file selected for mesh visualization.")
        return

    # Initialize the display
    display, start_display, add_menu, add_function_to_menu = init_display()

    # Read the STEP file
    shape = read_step_file(step_file_path)
    
    # Create mesh for visualization
    mesh = BRepMesh_IncrementalMesh(shape, 0.5)  # Adjust meshing parameters as needed
    mesh.Perform()
    
    # Display the shape with mesh
    display.DisplayShape(shape, update=True)
    
    # Extract and display edges
    edges = TopExp_Explorer(shape, TopAbs_EDGE)
    while edges.More():
        edge = edges.Current()
        display.DisplayShape(edge, update=False)
        edges.Next()
    
    # Extract and display faces with mesh
    faces = TopExp_Explorer(shape, TopAbs_FACE)
    while faces.More():
        face = faces.Current()
        display.DisplayShape(face, update=False)
        faces.Next()
    
    display.FitAll()
    
    # Start the VTK display
    start_display()

# Create GUI
root = tk.Tk()
root.title("STEP File Processor")
root.geometry("300x250")

# Create and place the browse button
browse_button = tk.Button(root, text="Browse STEP File", command=process_step_file)
browse_button.pack(pady=10)

# Create and place the visualize shape button
visualize_button = tk.Button(root, text="Visualize STEP File", command=visualize_step_file)
visualize_button.pack(pady=10)

# Create and place the visualize mesh button
visualize_mesh_button = tk.Button(root, text="Visualize Mesh", command=visualize_mesh)
visualize_mesh_button.pack(pady=10)

# Run the GUI main loop
root.mainloop()
