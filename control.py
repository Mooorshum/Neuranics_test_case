import os
import shutil
import subprocess

from math import acos, cos, sqrt, pi


""" FUNCTION WHICH INSERTS SCRIPT SETTINGS INTO MUMAX TEMPLATE """
def paste_settings_to_script_template(settings_data, template_filename, output_filename):
    with open(template_filename, 'r') as file:
        lines = file.readlines()
    for key, value in settings_data.items():
        for i, line in enumerate(lines):
            if key in line:
                if f'{key} :=' in line:
                    op = ':='
                elif f'{key} =' in line:
                    op = '='
                else:
                    continue
                parts = line.split(op)
                if len(parts) == 2:
                    left = parts[0].rstrip()
                    right = parts[1].lstrip()
                    value_str = str(value)
                    lines[i] = f'{left} {op} {value_str}\n'
                    break
    with open(output_filename, 'w') as file:
        file.writelines(lines)


""" FUNCTION WHICH EXTRACTS HEADER FROM A SINGLE OVF FILE """
def extract_header(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    header_lines = []
    for line in lines:
        header_lines.append(line)
        if line.strip() == '# Begin: Data Text':
                break
    header = ''.join(header_lines)
    return header


""" FUNCTION WHICH EXTRACTS FOOTER FROM A SINGLE OVF FILE """
def extract_footer(filepath):
    footer_lines = []
    in_footer = False
    with open(filepath, 'r') as f:
        for line in f:
            if in_footer:
                footer_lines.append(line)
            elif line.strip() == '# End: Data Text':
                footer_lines.append(line)
                in_footer = True
    return ''.join(footer_lines)


""" FUNCTION WHICH EXTRACTS DATA FROM OVF FILE AND CONVERTS IT TO PYTHON READABLE FORMAT """
def extract_data(filepath, settings_data):
    # Extracting data in string format
    data_lines = []
    extracting_data = False
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip() == '# Begin: Data Text':
                extracting_data = True
                continue
            elif line.strip() == '# End: Data Text':
                break
            if extracting_data:
                data_lines.append(line)
    data_string = ''.join(data_lines)
    # COnverting data to numeric values
    Nx = settings_data['Nx']
    Ny = settings_data['Ny']
    flat_values = list(map(float, data_string.split()))
    data_numeric = [[None for _ in range(Ny)] for _ in range(Nx)]
    index = 0
    for j in range(Ny):
        for i in range(Nx):
            vector = flat_values[index:index+3]
            data_numeric[i][j] = vector
            index += 3
    return data_numeric


""" FUNCTION WHICH GENERATES OVF FILE HEADERS AND FOOTERS FOR SIMULATION PARAMETERS """
def generate_ovf_headers_footers(settings_data, generation_script_template):
        # Insterting simulation settings into ovf generation script
        temporary_script_filename = 'ovf_generation_script_temporary.mx3'
        paste_settings_to_script_template(settings_data, generation_script_template, temporary_script_filename)
        # Running ovf generation script
        subprocess.run(['mumax3', temporary_script_filename])
        # Getting ovf files from output folder
        output_folder = f'{os.path.splitext(temporary_script_filename)[0]}.out'
        m_ovf = f'{output_folder}/m.ovf'
        Bext_ovf = f'{output_folder}/B_ext.ovf'
        J_ovf = f'{output_folder}/J.ovf'
        # Extracting headers and footers
        m_header = extract_header(m_ovf)
        m_footer = extract_footer(m_ovf)
        Bext_header = extract_header(Bext_ovf)
        Bext_footer = extract_footer(Bext_ovf)
        J_header = extract_header(J_ovf)
        J_footer = extract_footer(J_ovf)
        # Saving results
        parameters_headers_footers = {}
        parameters_headers_footers['m'] = [m_header, m_footer]
        parameters_headers_footers['Bext'] = [Bext_header, Bext_footer]
        parameters_headers_footers['J'] = [J_header, J_footer]
        # Cleaning up
        shutil.rmtree(output_folder)
        os.remove(temporary_script_filename)
        return parameters_headers_footers
    

""" FUNCTION WHICH CONVERTS OVF FILE FORMATTING FROM DOS FILE TO UNIX """
def convert_to_unix(filename):
    with open(filename, 'r') as f:
        content = f.read()
    with open(filename, 'w', newline='\n') as f:
        f.write(content)


""" FUNCTION WHICH CONSTRUCTS OVF FILE FROM PYTHON DATA """
def convert_to_ovf(output_filename, header, footer, data):
    Nx = len(data)
    Ny = len(data[0])
    with open(output_filename, 'w') as f:
        # Writing header
        f.write(header)
        if not header.endswith('\n'):
            f.write('\n')
        # Writing data
        for j in range(Ny):
            for i in range(Nx):
                vector = data[i][j]
                line = f'{vector[0]} {vector[1]} {vector[2]}\n'
                f.write(line)
        # Writing footer
        if not footer.startswith('\n') and not footer.startswith('#'):
            f.write('\n')
        f.write(footer)
    convert_to_unix(output_filename)


""" FUNCTION WHICH COMPUTES TUNNEL CURRENT DISTRIBUTION DATA """
def compute_j_tunnel(m_free_data, settings_data):
    Nx = len(m_free_data)
    Ny = len(m_free_data[0])
    V_bias = settings_data['V_bias']
    R_p = settings_data['R_p']
    R_ap = settings_data['R_ap']
    cell_size_x = settings_data['size_x'] / Nx
    cell_size_y = settings_data['size_y'] / Ny
    m_reference = settings_data['m_reference']
    m_reference_x, m_reference_y = m_reference[0], m_reference[1]
    j_tunnel_data = [[None for _ in range(Ny)] for _ in range(Nx)]
    for j in range(Ny):
        for i in range(Nx):
            m_free = m_free_data[i][j]
            m_free_x, m_free_y = m_free[0], m_free[1]
            angle_m_free_ref = acos((m_free_x * m_reference_x + m_free_y * m_reference_y) / (sqrt(m_free_x ** 2 + m_free_y ** 2) * sqrt(m_reference_x ** 2 + m_reference_y ** 2)))
            R_full_MTJ = R_p + (R_ap - R_p) / 2 * (1 - cos(angle_m_free_ref))
            I_cell = V_bias / R_full_MTJ / (Nx * Ny)
            j_cell = I_cell / (cell_size_x * cell_size_y)
            j_tunnel_data[i][j] = [0, 0, j_cell]
    return j_tunnel_data


""" FUNCTION WHICH COMPUTES OERSTED FIELD DISTRIBUTION DATA """
def compute_B_oe(j_tunnel_data, settings_data):
    mu0 = 1.256e-6
    Nx = len(j_tunnel_data)
    Ny = len(j_tunnel_data[0])
    cell_size_x = settings_data['size_x'] / Nx
    cell_size_y = settings_data['size_y'] / Ny
    B_oe_data = [[None for _ in range(Ny)] for _ in range(Nx)]
    for j in range(Ny):
        for i in range(Nx):
            B_oe_cell_total_x = 0
            B_oe_cell_total_y = 0 
            for m in range(Ny):
                for n in range(Nx):
                    if (i != n) and (j != m):
                        dx = (i - n) * cell_size_x
                        dy = (j - m) * cell_size_y
                        I_contributing_cell = j_tunnel_data[n][m][2] * cell_size_x * cell_size_y
                        B_oe_x = mu0 * I_contributing_cell / (2 * pi * sqrt(dx**2 + dy**2)) * dx
                        B_oe_y = mu0 * I_contributing_cell / (2 * pi * sqrt(dx**2 + dy**2)) * (-dy)
                        # Summing up contribution across all other cells (Note that fields are in T units in mumax)
                        B_oe_cell_total_x += B_oe_x * mu0
                        B_oe_cell_total_y += B_oe_y * mu0
            B_oe_data[i][j] = [B_oe_cell_total_x, B_oe_cell_total_y, 0]
    return B_oe_data


""" FUNCTION WHICH CREATES STARTING FREE LAYER MAGNETIZATION DATA """
def get_m_free_start_data(m_free_start_filename, settings_data, num_iter):
    Nx = settings_data['Nx']
    Ny = settings_data['Ny']
    m_free_start_data = [[None for _ in range(Ny)] for _ in range(Nx)]
    # During the first iteration, the free layer magnetization is set to be uniform
    if num_iter == 0:
        m_free_uniform = settings_data['m_free_start_uniform']
        for j in range(Ny):
            for i in range(Nx):
                m_free_start_data[i][j] = [m_free_uniform[0], m_free_uniform[1], m_free_uniform[2]]
    # During subsequent iterations, the free layer magnetization is set equal to the previous iteration result
    else:
        m_free_start_data = extract_data(m_free_start_filename, settings_data)
    return m_free_start_data


""" FUNCTION TO GET EXTERNAL MAGNETIC FIELD DISTRIBUTION """
def get_B_ext_data(settings_data):
    Nx = settings_data['Nx']
    Ny = settings_data['Ny']
    B_ext_uniform = settings_data['B_ext_uniform']
    B_ext_data = [[None for _ in range(Ny)] for _ in range(Nx)]
    for j in range(Ny):
        for i in range(Nx):
            B_ext_data[i][j] = [B_ext_uniform[0], B_ext_uniform[1], B_ext_uniform[2]]
    return B_ext_data




""" MUMAX SCRIPT SETTINGS """
settings_data = {}

# MTJ free layer geometry
settings_data['size_x'] = 40e-9
settings_data['size_y'] = 40e-9
settings_data['size_z'] = 5e-9
settings_data['Nx'] = 8
settings_data['Ny'] = 8
settings_data['Nz'] = 1

# Free layer properties
settings_data['Msat'] = 700e3
settings_data['Aex'] = 13e-12
settings_data['alpha'] = 0.02
settings_data['Ku1'] = 0.59e6
settings_data['anisU'] = 'vector(0, 1, 0)'

# Reference layer properties
settings_data['lambda'] = 1
settings_data['Pol'] = 0.5
settings_data['epsilonprime'] = 0
settings_data['angle'] = 0.01
settings_data['fixedlayer'] = 'vector(px, py, 0)'

# Simulation time
settings_data['t_total'] = 0.1e-9
settings_data['t_save_step'] = 1e-11

# Reference layer magnetization
settings_data['m_reference'] = [0, 1, 0]

# Free layer starting magnetization
settings_data['m_free_start_uniform'] = [-1, 0, 0]

# External field amplitude
settings_data['B_ext_uniform'] = [0, 100e-3, 0]


""" TUNNEL CURRENT COMPUTATION SETTINGS """

# MTJ bias voltage
settings_data['V_bias'] = 5

# MTJ resistance in parallel and anti-parallel states
settings_data['R_p'] = 1000
settings_data['R_ap'] = 5000




""" SIMULATION SETTINGS """

# Name of MTJ scripts
MTJ_SCRIPT_TEMPLATE = 'simulate_MTJ_template.mx3'
MTJ_SCRIPT_COMPLETE = 'simulate_MTJ.mx3'

# Number of times the MTJ script will be called, with each iteration result being used as input for the next iteration
num_simulations = 3





""" RUNNING SIMULATION  """

# Clearing dynamics data
shutil.rmtree('dynamics')
os.makedirs('dynamics', exist_ok=True)

# Generating ovf headers and footers for given settings
parameters_headers_footers_data = generate_ovf_headers_footers(settings_data, 'create_ovf_m_Bext_J_template.mx3')

# Creating ovf file of external magnetic field
B_ext_data = get_B_ext_data(settings_data)
convert_to_ovf(
    'B_ext_data.ovf',
    parameters_headers_footers_data['Bext'][0],
    parameters_headers_footers_data['Bext'][1],
    B_ext_data
)

for num_iter in range(num_simulations):

    # Creating ovf file of magnetization in free layer
    m_free_data = get_m_free_start_data('m_free_start_data.ovf', settings_data, num_iter)
    convert_to_ovf(
        'm_free_start_data.ovf',
        parameters_headers_footers_data['m'][0],
        parameters_headers_footers_data['m'][1],
        m_free_data
    )

    # Computing starting approximations for tunnel current
    j_tunnel_data = compute_j_tunnel(m_free_data, settings_data)
    convert_to_ovf(
        'j_tunnel_data.ovf',
        parameters_headers_footers_data['J'][0],
        parameters_headers_footers_data['J'][1],
        j_tunnel_data
    )

    # Computing starting approximations for Oersted field
    B_oe_data = compute_B_oe(j_tunnel_data, settings_data)
    convert_to_ovf(
        'B_oe_data.ovf',
        parameters_headers_footers_data['Bext'][0],
        parameters_headers_footers_data['Bext'][1],
        B_oe_data
    )

    # Inserting settings into script
    paste_settings_to_script_template(settings_data, MTJ_SCRIPT_TEMPLATE, MTJ_SCRIPT_COMPLETE)

    # Running MTJ script
    subprocess.run(['mumax3', MTJ_SCRIPT_COMPLETE])

    # Replacing previous free layer starting magnetization with this iteration result
    output_folder = f'{os.path.splitext(MTJ_SCRIPT_COMPLETE)[0]}.out'
    os.remove('m_free_start_data.ovf')
    shutil.copyfile(f'{output_folder}/m_free_start_data.ovf', 'm_free_start_data.ovf')
    os.remove(f'{output_folder}/m_free_start_data.ovf')

    # Saving dynamics data
    dynamics_iter_folder = f'dynamics/dynamics_iteration_{num_iter}'
    os.makedirs(dynamics_iter_folder, exist_ok=True)
    for m_step_filename in os.listdir(output_folder):
        if m_step_filename.startswith('m') and m_step_filename.endswith('.ovf'):
            shutil.copyfile(
                os.path.join(output_folder, m_step_filename),
                os.path.join(dynamics_iter_folder, m_step_filename)
            )

    # Cleaning up
    shutil.rmtree(output_folder)
    os.remove(MTJ_SCRIPT_COMPLETE)
    os.remove('B_oe_data.ovf')
    os.remove('j_tunnel_data.ovf')

    print(f'****** STEP {num_iter + 1} / {num_simulations} COMPUTED ******')

os.remove('B_ext_data.ovf')
os.remove('m_free_start_data.ovf')
