import numpy

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

# Free layer properties (TAKEN FROM https://doi.org/10.1016/j.jmmm.2021.167853)
simulation_settings['Msat'] = 1.2e6
simulation_settings['Aex'] = 1e-11
simulation_settings['alpha'] = 0.05
simulation_settings['Ku1'] = 0.9e6
simulation_settings['anisU'] = 'vector(1e-6, 1, 0)'

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
simulation_settings['B_ext_uniform'] = [
    [0, B_ext_y, 0] for B_ext_y in numpy.arange(-100e-3, 100e-3, 10e-3)
]

# Simulation time
simulation_settings['t_total'] = 0.05e-9 # 0.1e-3
simulation_settings['t_save_step'] = 1e-11


""" TUNNEL CURRENT COMPUTATION SETTINGS """

# MTJ bias voltage
simulation_settings['V_bias'] = 5

# MTJ resistance in parallel and anti-parallel states
simulation_settings['R_p'] = 1000
simulation_settings['R_ap'] = 5000


""" SIMULATION SETTINGS """

# Number of times the quasi-static MTJ script will be called, with each external field sweep iteration
simulation_settings['num_iterations'] = 20 #10


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

plot_options['show_convergence'] = False
plot_options['show_unit_sphere_dynamics'] = False
plot_options['show_j_tunnel_convergence'] = False
plot_options['show_j_tunnel_converged'] = True



""" RUNNING SIMULATION """
run_simulation(simulation_settings, scripts_folders)
plot_results(simulation_settings, scripts_folders, plot_options)
