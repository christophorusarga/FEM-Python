import pycalculix as pyc

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

    # Define a simple part (e.g., a block)
    part = pyc.Part(name='part-1')
    model.add_part(part)
    
    # Define geometry (e.g., a block)
    part.add_block(dimensions=(10, 10, 10))  # Define dimensions of the block

    # Set material properties
    steel = pyc.Material('steel')
    steel.set_mech_props(young_mod=210e9,  # Young's modulus in Pa
                         poisson_ratio=0.3) # Poisson's ratio
    model.set_material(steel)

    # Set mesh properties
    part.set_elem_shape('hex')  # Hexahedral elements
    part.set_elem_type('C3D8')  # 3D solid elements
    part.set_mesh_size(1.0)     # Mesh element size
    part.generate_mesh()        # Generate the mesh

    # Define loads and constraints
    model.add_boundary_condition('fix', 'part-1', face=1)  # Fix one face of the block

    # Apply forces based on user input
    direction_map = {'x+': 'x+', 'x-': 'x-', 'y+': 'y+', 'y-': 'y-', 'z+': 'z+', 'z-': 'z-'}
    direction_code = direction_map[direction_from]
    
    # Apply force in the 'from' direction
    model.add_load('force', 'part-1', face=2, direction=direction_code, magnitude=-force)

    # Write the input file for CalculiX
    model.write_inp('model.inp')

    # Run the FEA simulation using CalculiX (you would need to call CalculiX externally)
    # For example: os.system('ccx model')

    # Post-process the results
    # Here you would use CalculiX's output files to read results

    # Visualize the results (not implemented in pycalculix directly)
    # You would need to use external tools or custom code to visualize the results

# GUI code remains the same
