from backend.simulation import run_simulation
from backend.data_visualization import plot_results

""" MUMAX SCRIPT SETTINGS """
simulation_settings = {}

# MTJ free layer geometry
simulation_settings['size_x'] = 160e-9
simulation_settings['size_y'] = 160e-9
simulation_settings['size_z'] = 5e-9
simulation_settings['Nx'] = 16
simulation_settings['Ny'] = 16
simulation_settings['Nz'] = 1

# Free layer properties
simulation_settings['Msat'] = 700e3
simulation_settings['Aex'] = 13e-12
simulation_settings['alpha'] = 0.02
simulation_settings['Ku1'] = 0.59e6
simulation_settings['anisU'] = 'vector(0, 1, 0)'

# Reference layer properties
simulation_settings['lambda'] = 1
simulation_settings['Pol'] = 0.5
simulation_settings['epsilonprime'] = 0
simulation_settings['angle'] = 0.01
simulation_settings['fixedlayer'] = 'vector(px, py, 0)'

# Reference layer magnetization
simulation_settings['m_reference'] = [0, 1, 0]

# Free layer starting magnetization
simulation_settings['m_free_start_uniform'] = [-1, 0, 0]

# External field amplitude
simulation_settings['B_ext_uniform'] = [0, 10e-3, 0]

# Simulation time
simulation_settings['t_total'] = 0.1e-9
simulation_settings['t_save_step'] = 1e-12


""" TUNNEL CURRENT COMPUTATION SETTINGS """

# MTJ bias voltage
simulation_settings['V_bias'] = 5

# MTJ resistance in parallel and anti-parallel states
simulation_settings['R_p'] = 1000
simulation_settings['R_ap'] = 5000


""" SIMULATION SETTINGS """

# Number of times the MTJ script will be called, with each external field sweep iteration
simulation_settings['num_iterations'] = 10


""" MODULE FOLDERS AND FILENAMES """
scripts_folders = {}

# Script to simulate MTJ for fixed tunnel current and oersted field
scripts_folders['MTJ_SCRIPT_TEMPLATE'] = 'templates/simulate_MTJ_template.mx3'

# Script to generate template ovf files for header and footer extraction
scripts_folders['OVF_TEMPLATE_CREATION_SCRIPT'] = 'templates/create_ovf_m_Bext_J_template.mx3'

# Name of temporary script formed automatically at each iteration
scripts_folders['MTJ_SCRIPT_INSTANCE'] = 'templates/simulate_MTJ.mx3'

# Name of folder where dynamics results will be saved at each iteration 
scripts_folders['M_DYNAMICS_DATA_FOLDER'] = 'output_data/m_dynamics'

scripts_folders['J_TUNNEL_DATA_FOLDER'] = 'output_data/j_tunnel_iterations'


""" DATA VISUALIZATION SETTINGS """
plot_options = {}

plot_options['show_unit_sphere_dynamics'] = True
plot_options['show_j_tunnel_convergence'] = True


""" RUNNING SIMULATION """
run_simulation(simulation_settings, scripts_folders)
plot_results(simulation_settings, scripts_folders, plot_options)
