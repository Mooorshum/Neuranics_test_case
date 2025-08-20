import numpy

from control_scripts.simulation import run_simulation
from control_scripts.data_visualization import plot_results

""" MUMAX SCRIPT SETTINGS """
simulation_settings = {}
# MTJ free layer geometry
simulation_settings['size_x'] = 80e-9 #1000e-9
simulation_settings['size_y'] = 80e-9 #1000e-9
simulation_settings['size_z'] = 80e-9
simulation_settings['Nx'] = 16 #200
simulation_settings['Ny'] = 16 #200
simulation_settings['Nz'] = 1 # DO NOT CHANGE !!!
# Free layer properties (TAKEN FROM https://doi.org/10.1016/j.jmmm.2021.167853)
simulation_settings['Msat'] = 1.2e6
simulation_settings['Aex'] = 1.3e-11
simulation_settings['alpha'] = 0.1
simulation_settings['Ku1'] = 1.0e5 # 30 * 1.256e-6 * simulation_settings['Msat'] / 2 # For an effective H_ku = 30 A/m
simulation_settings['anisU'] = f'vector(0.01, 0.99, 0)'
# Reference layer properties
simulation_settings['lambda'] = 1
simulation_settings['Pol'] = 0.56 # HAS TO BE > 0 !!!
simulation_settings['epsilonprime'] = 0
simulation_settings['fixedlayer'] = 'vector(0, -1, 0)'
# Reference layer magnetization
simulation_settings['m_reference'] = 'vector(0, -1, 0)' # Presumed to be fixed & aligned with reference layer polarization & real life pinned layer
# Free layer starting magnetization
simulation_settings['m_free_start_uniform'] = [-1, 0, 0]
# Constant external field
B_ext_x = 0.05e-3 # Adding a small field to assist switching
B_ext_y = 0.0
B_ext_z = 0.0
""" # Rotating external field
B_ext_amp = 20e-3
B_ext_angle_x_start = 180.0
B_ext_angle_x_end = 0.0
num_points_sweep = 20
from numpy import sin, cos, radians
simulation_settings['B_ext_uniform'] = [
    [B_ext_amp*cos(radians(angle_x)), B_ext_amp*sin(radians(angle_x)), B_ext_z] 
    for angle_x in numpy.arange(
        B_ext_angle_x_start, 
        B_ext_angle_x_end, 
        (B_ext_angle_x_end - B_ext_angle_x_start) / num_points_sweep
    )
] """
# Swept external field
B_ext_y_start = -0.3e-3
B_ext_y_end = 0.3e-3
num_points_sweep = 50
simulation_settings['B_ext_uniform'] = [
    [B_ext_x, B_ext_y, B_ext_z] 
    for B_ext_y in numpy.arange(
        B_ext_y_start,
        B_ext_y_end,
        (B_ext_y_end-B_ext_y_start)/num_points_sweep
    )
]
# Time for 1 quasi-static LLGS computation with fixed tunnel current
simulation_settings['t_quasi_static_step'] = 0.01e-9
# Number of quasi static steps per B_ext sweep value
simulation_settings['num_quasi_static_steps'] = 700


""" TUNNEL CURRENT RELATED SETTINGS """
# MTJ bias voltage
simulation_settings['V_bias'] = 1e-3
# Full MTJ resistance in parallel and anti-parallel states
simulation_settings['R_p'] = 74.86
simulation_settings['R_ap'] = 18000.0


""" FILENAMES FOR QUASI-STATIC SUB-SIMULATION OUTPUT """ 
simulation_settings['m_quasi_static_final_name'] = '"m_final_quasi_static_step_"' # Double brackets are needed due to mumax syntax
simulation_settings['j_tunnel_quasi_static_final_name'] = '"j_tunnel_final_quasi_static_step_"'


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
plot_options['show_configuration_dynamics'] = False
plot_options['show_unit_sphere_dynamics'] = False
plot_options['show_j_tunnel_convergence'] = False
plot_options['show_j_tunnel_final'] = True
plot_options['num_field_steps_resolution'] = 1
plot_options['num_quasistatic_steps_resolution'] = 5


""" RUNNING SIMULATION """
run_simulation(simulation_settings, scripts_folders)
plot_results(simulation_settings, scripts_folders, plot_options)
