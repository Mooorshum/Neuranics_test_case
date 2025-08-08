import os
import shutil
import subprocess
import glob

from .mumax_template_editing import generate_ovf_headers_footers, paste_settings_to_script_template
from .ovf_data_formatting import extract_data, convert_to_ovf


""" CREATE STARTING FREE LAYER MAGNETIZATION DATA """
def get_m_free_start_data(m_free_start_filename, simulation_settings, num_iter):
    Nx = simulation_settings['Nx']
    Ny = simulation_settings['Ny']
    m_free_start_data = [[None for _ in range(Ny)] for _ in range(Nx)]
    # During the first iteration, the free layer magnetization is set to be uniform
    if num_iter == 0:
        for j in range(Ny):
            for i in range(Nx):
                m_free_start_data[i][j] = simulation_settings['m_free_start_uniform']
    # During subsequent iterations, the free layer magnetization is set equal to the previous iteration result
    else:
        m_free_start_data = extract_data(m_free_start_filename, simulation_settings)
    return m_free_start_data


""" GET EXTERNAL MAGNETIC FIELD DISTRIBUTION """
def get_B_ext_data(simulation_settings, num_sweep_value):
    Nx = simulation_settings['Nx']
    Ny = simulation_settings['Ny']
    B_ext_uniform = simulation_settings['B_ext_uniform'][num_sweep_value]
    B_ext_data = [[None for _ in range(Ny)] for _ in range(Nx)]
    for j in range(Ny):
        for i in range(Nx):
            B_ext_data[i][j] = [B_ext_uniform[0], B_ext_uniform[1], B_ext_uniform[2]]
    return B_ext_data

""" REMOVE PREVIOUS RESULTS AND TEMPORARY FILES FROM PROJECT FOLDERS """
def preclean_folders(scripts_folders):
    # Clearing previous simulation dynamics data
    shutil.rmtree(scripts_folders['M_DYNAMICS_DATA_FOLDER'])
    os.makedirs(scripts_folders['M_DYNAMICS_DATA_FOLDER'], exist_ok=True)

    # Clearing previous simulation tunnel current data
    shutil.rmtree(scripts_folders['J_TUNNEL_DATA_FOLDER'])
    os.makedirs(scripts_folders['J_TUNNEL_DATA_FOLDER'], exist_ok=True)


""" RUN QUASI-STATIC SIMULATION: LLGS COMPUTATION WITH ITERATIVELY CHANGING TUNNEL CURRENT AND OERSTED FIELD DISTRIBUTION """
def run_simulation(simulation_settings, scripts_folders):

    # Cleaning up project folders
    preclean_folders(scripts_folders)

    # Generating ovf headers and footers for given settings
    parameters_headers_footers_data = generate_ovf_headers_footers(simulation_settings, scripts_folders['OVF_TEMPLATE_CREATION_SCRIPT'])

    # Looping through each B_ext value
    num_sweep_values_total = len(simulation_settings['B_ext_uniform'])
    for num_sweep_value in range(num_sweep_values_total):
    
        # Creating ovf file of external magnetic field
        B_ext_data = get_B_ext_data(simulation_settings, num_sweep_value)
        convert_to_ovf(
            'B_ext_data.ovf',
            parameters_headers_footers_data['Bext'][0],
            parameters_headers_footers_data['Bext'][1],
            B_ext_data
        )

        # Creating ovf file for starting magnetization distribution in free layer
        m_free_data = get_m_free_start_data('m_free_start_data.ovf', simulation_settings, 0)
        convert_to_ovf(
            'm_free_start_data.ovf',
            parameters_headers_footers_data['m'][0],
            parameters_headers_footers_data['m'][1],
            m_free_data
        )

        # Inserting settings into script
        paste_settings_to_script_template(simulation_settings, scripts_folders['MTJ_SCRIPT_TEMPLATE'], scripts_folders['MTJ_SCRIPT_INSTANCE'])

        # Running MTJ script
        subprocess.run(
            ['mumax3', scripts_folders['MTJ_SCRIPT_INSTANCE']],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Copying results to project output folder
        mumax_script_output_folder = f'{os.path.splitext(scripts_folders["MTJ_SCRIPT_INSTANCE"])[0]}.out'
        m_dynamics_B_ext_sweep_folder = f'{scripts_folders["M_DYNAMICS_DATA_FOLDER"]}/B_ext_sweep_{num_sweep_value}'
        j_tunnel_B_ext_sweep_folder = f'{scripts_folders["J_TUNNEL_DATA_FOLDER"]}/B_ext_sweep_{num_sweep_value}'
        os.makedirs(m_dynamics_B_ext_sweep_folder, exist_ok=True)
        os.makedirs(j_tunnel_B_ext_sweep_folder, exist_ok=True)
        file_pattern_m = f'{mumax_script_output_folder}/{simulation_settings["m_quasi_static_final_name"][1:-1]}*'
        file_pattern_j_tunnel = f'{mumax_script_output_folder}/{simulation_settings["j_tunnel_quasi_static_final_name"][1:-1]}*'
        matching_files_m = glob.glob(file_pattern_m)
        matching_files_j_tunnel = glob.glob(file_pattern_j_tunnel)
        for file in matching_files_m:
            shutil.copy(file, m_dynamics_B_ext_sweep_folder)
        for file in matching_files_j_tunnel:
            shutil.copy(file, j_tunnel_B_ext_sweep_folder)

        # Cleaning up
        shutil.rmtree(mumax_script_output_folder)
        os.remove(scripts_folders['MTJ_SCRIPT_INSTANCE'])
        os.remove('m_free_start_data.ovf')
        os.remove('B_ext_data.ovf')

        # Displaying progress
        os.system('cls' if os.name=='nt' else 'clear')
        print(f'COMPUTED:   B_ext sweep {num_sweep_value+1} / {num_sweep_values_total}')
