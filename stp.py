import tkinter as tk
from tkinter import filedialog, messagebox
import pygmsh
import meshio
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Extend.DataExchange import read_step_file

# Global variables to store the file path and mesh data
step_file_path = None
mesh_data = None

def create_geometry():
    """Create a pygmsh geometry object."""
    geom = pygmsh.occ.Geometry()
    print("Geometry object initialized.")
    return geom

def add_step_to_geometry(geom, file_path):
    """Add a STEP file shape to the pygmsh geometry."""
    shape = read_step_file(file_path)
    geom.add_geometry(shape)
    print("STEP file added to geometry.")
    return geom

def process_step_file():
    """Handle the STEP file processing."""
    global step_file_path, mesh_data
    step_file_path = filedialog.askopenfilename(filetypes=[("STEP files", "*.step"), ("STEP files", "*.stp")])
    
    if not step_file_path:
        messagebox.showwarning("Warning", "No file selected.")
        return
    
    print(f"Selected file: {step_file_path}")
    
    try:
        # Initialize geometry first
        geom = create_geometry()

        # Add STEP model to geometry
        geom = add_step_to_geometry(geom, step_file_path)
        
        # Generate mesh
        mesh_data = geom.generate_mesh(dim=3)
        
        messagebox.showinfo("Success", f"File {step_file_path} loaded and meshed successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def visualize_mesh():
    """Display the mesh points."""
    global mesh_data
    
    if mesh_data is None:
        messagebox.showwarning("Warning", "No mesh data to visualize.")
        return

    # Simple visualization of mesh points (centroid of triangles)
    centroids = np.mean(mesh_data.points[mesh_data.cells_dict['triangle']], axis=1)
    print("Mesh Centroids (sample):", centroids[:5])  # Display a sample of mesh centroids

    messagebox.showinfo("Mesh Information", f"Number of cells: {len(mesh_data.cells_dict['triangle'])}")

def save_mesh():
    """Save the mesh to a file."""
    global mesh_data
    
    if mesh_data is None:
        messagebox.showwarning("Warning", "No mesh data to save.")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".msh", filetypes=[("Gmsh files", "*.msh")])
    
    if not save_path:
        messagebox.showwarning("Warning", "No file selected for saving.")
        return
    
    meshio.write(save_path, mesh_data)
    messagebox.showinfo("Success", f"Mesh saved to {save_path}.")

# Create GUI
root = tk.Tk()
root.title("STEP File Processor with pygmsh")
root.geometry("400x400")

# Create and place the browse button
browse_button = tk.Button(root, text="Browse STEP File", command=process_step_file)
browse_button.pack(pady=10)

# Create and place the visualize mesh button
visualize_mesh_button = tk.Button(root, text="Visualize Mesh", command=visualize_mesh)
visualize_mesh_button.pack(pady=10)

# Create and place the save mesh button
save_mesh_button = tk.Button(root, text="Save Mesh", command=save_mesh)
save_mesh_button.pack(pady=10)

# Run the GUI main loop
root.mainloop()
