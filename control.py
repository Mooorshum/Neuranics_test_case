import numpy

from math import sin, cos, radians

from backend.simulation import run_simulation
from backend.data_visualization import plot_results

""" MUMAX SCRIPT SETTINGS """
simulation_settings = {}
# MTJ free layer geometry
simulation_settings['size_x'] = 5e-9 #1000e-9
simulation_settings['size_y'] = 5e-9 #1000e-9
simulation_settings['size_z'] = 5e-9
simulation_settings['Nx'] = 1 #200
simulation_settings['Ny'] = 1 #200
simulation_settings['Nz'] = 1 # DO NOT CHANGE !!!
# Free layer properties (TAKEN FROM https://doi.org/10.1016/j.jmmm.2021.167853)
simulation_settings['Msat'] = 1.2e6
simulation_settings['Aex'] = 1e-11
simulation_settings['alpha'] = 0.02
simulation_settings['Ku1'] = 30 * 1.256e-6 * simulation_settings['Msat'] / 2 # For an effective H_ku = 30 A/m
simulation_settings['anisU'] = f'vector(0, 1, 0)'
# Reference layer properties
simulation_settings['lambda'] = 1
simulation_settings['Pol'] = 1e-3 # 0.5 # HAS TO BE > 1 !!!
simulation_settings['epsilonprime'] = 0
simulation_settings['fixedlayer'] = 'vector(0, -1, 0)'
# Reference layer magnetization
simulation_settings['m_reference'] = [0, -1, 0] # Presumed to be fixed & aligned with polarization vector & real life pinned layer
# Free layer starting magnetization
simulation_settings['m_free_start_uniform'] = [-1, 0, 0]
# External field amplitude
B_ext_x = 0.2e-3
B_ext_z = 0
B_ext_min_y = -5e-3
B_ext_max_y = 5e-3
num_points_sweep = 1
simulation_settings['B_ext_uniform'] = [
    [B_ext_x, B_ext_y, B_ext_z] 
    for B_ext_y in numpy.arange(
        B_ext_min_y, 
        B_ext_max_y, 
        (B_ext_max_y-B_ext_min_y)/num_points_sweep
    )
]
""" B_ext_amp = 1
min_angle = 0
max_angle = 180
num_points_sweep = 10
simulation_settings['B_ext_uniform'] = [
    [B_ext_amp * numpy.sin(angle), B_ext_amp * numpy.cos(angle), 0]
    for angle in numpy.arange(
        numpy.radians(min_angle),
        numpy.radians(max_angle),
        numpy.radians(max_angle - min_angle) / num_points_sweep
    )
] """
# Time for 1 quasi-static LLGS computation with fixed tunnel current
simulation_settings['t_total'] = 0.01e-9
# Step to save m-dynamics data
simulation_settings['t_save_step'] = simulation_settings['t_total'] / 10
# Number of times the quasi-static MTJ script will be called, with each external field sweep iteration
simulation_settings['num_quasi_static_iterations'] = 1000


""" TUNNEL CURRENT RELATED SETTINGS """
# MTJ bias voltage
simulation_settings['V_bias'] = 10e-3
# MTJ resistance in parallel and anti-parallel states (experimental data or other model result)
simulation_settings['R_p'] = 74.86
simulation_settings['R_ap'] = 18000


""" MODULE FOLDERS AND FILENAMES """
scripts_folders = {}
# Script to simulate MTJ for fixed tunnel current and oersted field
scripts_folders['MTJ_SCRIPT_TEMPLATE'] = 'templates/simulate_MTJ_template.mx3'
# Script to generate template ovf files for header and footer extraction
scripts_folders['OVF_TEMPLATE_CREATION_SCRIPT'] = 'templates/create_ovf_m_Bext_J_template.mx3'
# Name of temporary script formed automatically at each iteration
scripts_folders['MTJ_SCRIPT_INSTANCE'] = 'templates/simulate_MTJ.mx3'
# Names of folders where results will be saved at each iteration
scripts_folders['M_DYNAMICS_DATA_FOLDER'] = 'output_data/m_dynamics'
scripts_folders['J_TUNNEL_DATA_FOLDER'] = 'output_data/j_tunnel_iterations'


""" DATA VISUALIZATION SETTINGS """
plot_options = {}
plot_options['show_convergence'] = True
plot_options['show_unit_sphere_dynamics'] = True
plot_options['show_j_tunnel_convergence'] = True
plot_options['show_j_tunnel_converged'] = True
plot_options['show_R_MTJ_converged'] = True


""" RUNNING SIMULATION """
#run_simulation(simulation_settings, scripts_folders)
plot_results(simulation_settings, scripts_folders, plot_options)
