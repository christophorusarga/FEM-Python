import tkinter as tk
from tkinter import filedialog, messagebox
import pygmsh
import meshio
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.TopoDS import TopoDS_Shape

def read_step_file(file_path):
    """Read STEP file and return shape."""
    step_reader = STEPControl_Reader()
    status = step_reader.ReadFile(file_path)
    
    if status != 1:
        raise Exception("Error reading STEP file.")
    
    step_reader.TransferRoots()
    shape = step_reader.OneShape()
    return shape

def create_mesh_from_shape(shape):
    """Create a mesh from the given shape."""
    geom = pygmsh.built_in.Geometry()
    
    # Add the STEP shape to the geometry
    geom.add_surface_mesh(shape)
    
    # Set mesh parameters
    mesh_size = 1.5e-3  # Element Size in meters (1.5 mm)
    geom.characteristic_length_min = mesh_size
    geom.characteristic_length_max = mesh_size
    
    # Generate the mesh
    mesh = geom.generate_mesh()
    return mesh

def save_mesh(mesh, filename):
    """Save the mesh to a file."""
    meshio.write(filename, mesh)

def mesh_quality_statistics(mesh_file):
    """Print mesh quality statistics."""
    mesh = meshio.read(mesh_file)
    
    num_nodes = len(mesh.points)
    num_elements = len(mesh.cells)
    
    print(f"Nodes: {num_nodes}")
    print(f"Elements: {num_elements}")

def process_step_file():
    """Handle the STEP file processing."""
    step_file = filedialog.askopenfilename(filetypes=[("STEP files", "*.stp")])
    if not step_file:
        return
    
    try:
        shape = read_step_file(step_file)
        mesh = create_mesh_from_shape(shape)
        mesh_file = "mesh.vtk"
        save_mesh(mesh, mesh_file)
        mesh_quality_statistics(mesh_file)
        messagebox.showinfo("Success", f"Mesh saved as {mesh_file} and statistics printed.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create GUI
root = tk.Tk()
root.title("STEP File Processor")
root.geometry("300x150")

# Create and place the browse button
browse_button = tk.Button(root, text="Browse STEP File", command=process_step_file)
browse_button.pack(expand=True)

# Run the GUI main loop
root.mainloop()
