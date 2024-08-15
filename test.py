import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Display.SimpleGui import init_display
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRep import BRep_Tool
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE
import pycalculix as pyc

# Global variables to store the file path and other parameters
step_file_path = None
mass_kg = 0
include_gravity = False
direction_from = 'y'
direction_to = 'y'

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

def apply_forces_and_run_simulation():
    """Apply forces, run simulation, and visualize results."""
    if not step_file_path:
        messagebox.showwarning("Warning", "No file selected for simulation.")
        return

    # Read mass and direction inputs
    global mass_kg, include_gravity, direction_from, direction_to
    
    try:
        mass_kg = float(mass_entry.get())
        direction_from = direction_from_entry.get().strip().lower()
        direction_to = direction_to_entry.get().strip().lower()

        # Validate directions
        valid_directions = {'x+', 'x-', 'y+', 'y-', 'z+', 'z-'}
        if direction_from not in valid_directions or direction_to not in valid_directions:
            raise ValueError("Invalid direction specified. Use 'x+', 'x-', 'y+', 'y-', 'z+', 'z-'.")

    except ValueError as ve:
        messagebox.showerror("Error", f"Invalid input: {ve}")
        return

    # Calculate the force
    gravity = 9.81  # m/s^2
    force = mass_kg * gravity if include_gravity else mass_kg

    # Create the FEA model
    model = pyc.FeaModel('example')

    # Create the part (e.g., a block)
    part = model.create_part('part-1')

    # Define geometry (e.g., a block)
    part.create_block(0, 0, 0, 10, 10, 10)  # Create a block with dimensions

    # Set material properties
    steel = pyc.Material('steel')
    steel.set_mech_props(young_mod=210e9,  # Young's modulus in Pa
                         poisson_ratio=0.3) # Poisson's ratio
    model.set_matl(steel)

    # Set mesh properties
    part.set_elem_shape('quad')  # Use quadrilateral elements
    part.set_elem_type('S4')     # Shell elements
    part.set_mesh_size(1.0)      # Mesh element size
    part.generate_mesh()         # Generate the mesh

    # Define loads and constraints
    model.apply_bc_fix('part-1', 'face', 1)  # Fix one face of the block

    # Apply forces based on user input
    direction_map = {'x+': 0, 'x-': 3, 'y+': 1, 'y-': 4, 'z+': 2, 'z-': 5}
    direction_from_code = direction_map[direction_from]
    
    # Apply force in the 'from' direction
    model.apply_force('part-1', 'face', 2, direction_from, -force)

    # Run the FEA simulation
    model.write_inp()  # Write input file for CalculiX
    model.run()        # Run the simulation

    # Post-process the results
    displacement = model.read_nodal_displacement('part-1', 'max')  # Get maximum displacement
    stress = model.read_element_stress('part-1', 'max')  # Get maximum stress

    print(f"Max displacement: {displacement} meters")
    print(f"Max stress: {stress} Pa")

    # Visualize the results
    model.plot_disp()  # Plot displacement field
    model.plot_stress()  # Plot stress field

# Create GUI
root = tk.Tk()
root.title("STEP File Processor and FEA Simulation")
root.geometry("400x400")

# Create and place the browse button
browse_button = tk.Button(root, text="Browse STEP File", command=process_step_file)
browse_button.pack(pady=10)

# Create and place the visualize shape button
visualize_button = tk.Button(root, text="Visualize STEP File", command=visualize_step_file)
visualize_button.pack(pady=10)

# Create and place the visualize mesh button
visualize_mesh_button = tk.Button(root, text="Visualize Mesh", command=visualize_mesh)
visualize_mesh_button.pack(pady=10)

# Create and place the mass entry
tk.Label(root, text="Mass (kg):").pack(pady=5)
mass_entry = tk.Entry(root)
mass_entry.pack(pady=5)

# Create and place direction axis entry
tk.Label(root, text="Direction From:").pack(pady=5)
direction_from_entry = tk.Entry(root)
direction_from_entry.pack(pady=5)

tk.Label(root, text="Direction To:").pack(pady=5)
direction_to_entry = tk.Entry(root)
direction_to_entry.pack(pady=5)

# Create and place the checkbox for gravity
gravity_var = tk.BooleanVar()
gravity_checkbox = tk.Checkbutton(root, text="Include Gravity", variable=gravity_var)
gravity_checkbox.pack(pady=10)

# Create and place the apply forces button
apply_forces_button = tk.Button(root, text="Apply Forces and Run Simulation", command=apply_forces_and_run_simulation)
apply_forces_button.pack(pady=10)

# Run the GUI main loop
root.mainloop()
