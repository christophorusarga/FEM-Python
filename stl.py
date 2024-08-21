import tkinter as tk
from tkinter import filedialog, messagebox
import pygmsh
import meshio
import numpy as np

# Global variables to store the file path and mesh data
stl_file_path = None
mesh_data = None

def read_stl_file(file_path):
    """Read a binary STL file and return the geometry for meshing."""
    with open(file_path, 'rb') as f:
        stl_data = f.read()

    geom = pygmsh.occ.Geometry()
    geom.add_volume_from_stl_string(stl_data.decode('utf-8', errors='ignore'))  # Decode binary data
    return geom

def process_stl_file():
    """Handle the STL file processing."""
    global stl_file_path, mesh_data
    stl_file_path = filedialog.askopenfilename(filetypes=[("STL files", "*.stl")])
    
    if not stl_file_path:
        messagebox.showwarning("Warning", "No file selected.")
        return
    
    print(f"Selected file: {stl_file_path}")
    
    try:
        geom = read_stl_file(stl_file_path)
        with pygmsh.geo.Geometry() as geom:
            mesh_data = geom.generate_mesh(dim=3)
        messagebox.showinfo("Success", f"File {stl_file_path} loaded and meshed successfully.")
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
root.title("STL File Processor with pygmsh")
root.geometry("400x400")

# Create and place the browse button
browse_button = tk.Button(root, text="Browse STL File", command=process_stl_file)
browse_button.pack(pady=10)

# Create and place the visualize mesh button
visualize_mesh_button = tk.Button(root, text="Visualize Mesh", command=visualize_mesh)
visualize_mesh_button.pack(pady=10)

# Create and place the save mesh button
save_mesh_button = tk.Button(root, text="Save Mesh", command=save_mesh)
save_mesh_button.pack(pady=10)

# Run the GUI main loop
root.mainloop()
