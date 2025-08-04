import os
import shutil
import subprocess

from .mumax_template_editing import generate_ovf_headers_footers, paste_settings_to_script_template
from .ovf_data_formatting import extract_data, convert_to_ovf
from .physics import compute_j_tunnel, compute_B_oe


""" CREATE STARTING FREE LAYER MAGNETIZATION DATA """
def get_m_free_start_data(m_free_start_filename, simulation_settings, num_iter):
    Nx = simulation_settings['Nx']
    Ny = simulation_settings['Ny']
    m_free_start_data = [[None for _ in range(Ny)] for _ in range(Nx)]
    # During the first iteration, the free layer magnetization is set to be uniform
    if num_iter == 0:
        m_free_uniform = simulation_settings['m_free_start_uniform']
        for j in range(Ny):
            for i in range(Nx):
                m_free_start_data[i][j] = [m_free_uniform[0], m_free_uniform[1], m_free_uniform[2]]
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


""" RUN QUASI-STATIC SIMULATION: LLGS COMPUTATION WITH ITERATIVELY CHANGING TUNNEL CURRENT AND OERSTED FIELD DISTRIBUTION """
def run_simulation(simulation_settings, scripts_folders):

    # Clearing previous simulation dynamics data
    shutil.rmtree(scripts_folders['M_DYNAMICS_DATA_FOLDER'])
    os.makedirs(scripts_folders['M_DYNAMICS_DATA_FOLDER'], exist_ok=True)

    # Clearing previous simulation tunnel current data
    shutil.rmtree(scripts_folders['J_TUNNEL_DATA_FOLDER'])
    os.makedirs(scripts_folders['J_TUNNEL_DATA_FOLDER'], exist_ok=True)

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

        # Iteratively updating tunnel current and oerted field for fixed external field and calling mumax MTJ script at each iteration
        num_iterations = simulation_settings['num_iterations']
        for num_iter in range(num_iterations):

            # Creating ovf file of magnetization in free layer
            m_free_data = get_m_free_start_data('m_free_start_data.ovf', simulation_settings, num_iter)
            convert_to_ovf(
                'm_free_start_data.ovf',
                parameters_headers_footers_data['m'][0],
                parameters_headers_footers_data['m'][1],
                m_free_data
            )

            # Computing starting approximations for tunnel current
            j_tunnel_data = compute_j_tunnel(m_free_data, simulation_settings)
            convert_to_ovf(
                'j_tunnel_data.ovf',
                parameters_headers_footers_data['J'][0],
                parameters_headers_footers_data['J'][1],
                j_tunnel_data
            )

            # Computing starting approximations for Oersted field
            B_oe_data = compute_B_oe(j_tunnel_data, simulation_settings)
            convert_to_ovf(
                'B_oe_data.ovf',
                parameters_headers_footers_data['Bext'][0],
                parameters_headers_footers_data['Bext'][1],
                B_oe_data
            )

            # Inserting settings into script
            paste_settings_to_script_template(simulation_settings, scripts_folders['MTJ_SCRIPT_TEMPLATE'], scripts_folders['MTJ_SCRIPT_INSTANCE'])

            # Running MTJ script
            subprocess.run(
                ['mumax3', scripts_folders['MTJ_SCRIPT_INSTANCE']],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Replacing previous free layer starting magnetization with this iteration result
            output_folder = f'{os.path.splitext(scripts_folders["MTJ_SCRIPT_INSTANCE"])[0]}.out'
            os.remove('m_free_start_data.ovf')
            shutil.copyfile(f'{output_folder}/m_free_start_data.ovf', 'm_free_start_data.ovf')
            os.remove(f'{output_folder}/m_free_start_data.ovf')

            # Saving m dynamics data
            m_dynamics_iter_folder = f'{scripts_folders["M_DYNAMICS_DATA_FOLDER"]}/sim_B_ext_{num_sweep_value}/m_dynamics_iteration_{num_iter}'
            os.makedirs(m_dynamics_iter_folder, exist_ok=True)
            for m_step_filename in os.listdir(output_folder):
                if m_step_filename.startswith('m') and m_step_filename.endswith('.ovf'):
                    shutil.copyfile(
                        os.path.join(output_folder, m_step_filename),
                        os.path.join(m_dynamics_iter_folder, m_step_filename)
                    )

            # Saving tunnel current distribution data
            j_tunnel_iter_folder = f'{scripts_folders["J_TUNNEL_DATA_FOLDER"]}/sim_B_ext_{num_sweep_value}/j_tunnel_iteration_{num_iter}'
            os.makedirs(j_tunnel_iter_folder, exist_ok=True)
            shutil.copyfile(
                'j_tunnel_data.ovf',
                os.path.join(j_tunnel_iter_folder, 'j_tunnel.ovf')
            )

            # Cleaning up
            shutil.rmtree(output_folder)
            os.remove(scripts_folders['MTJ_SCRIPT_INSTANCE'])
            os.remove('B_oe_data.ovf')
            os.remove('j_tunnel_data.ovf')

            # Displaying progress
            os.system('cls' if os.name=='nt' else 'clear')
            print(f'COMPUTED:   B_ext sweep {num_sweep_value+1} / {num_sweep_values_total};   quasi-static step {num_iter + 1} / {num_iterations}')

        os.remove('B_ext_data.ovf')
        os.remove('m_free_start_data.ovf')
