import os
import numpy as np
import matplotlib.pyplot as plt

from .ovf_data_formatting import extract_data


""" GATHER DATA FROM SIMULATION RESULTS """
def gather_data(simulation_settings, scripts_folders):
    m_dynamics_folder = scripts_folders['M_DYNAMICS_DATA_FOLDER']
    j_tunnel_folder = scripts_folders['J_TUNNEL_DATA_FOLDER']
    print('Preparing data for plots...')
    # Extracting the final magnetization distribution for each quasi-static sub-simulation for each B_ext sweep value
    # in such a way that the jth LLGS step of the jth B_ext sweep iteration can be accesed as: B_ext_sweep_step_m_dynamics[i][j]
    B_ext_sweep_step_m_dynamics = []
    for B_ext_sweep_value_folder in os.listdir(m_dynamics_folder):
        # Looping through B_ext sweep step folder and appending to m_final_quasi_static_steps 
        m_dynamics_quasi_static_steps_B_ext_sweep_value_folder = os.path.join(m_dynamics_folder, B_ext_sweep_value_folder)
        m_final_quasi_static_steps = []
        for m_final_quasi_static_step in os.listdir(m_dynamics_quasi_static_steps_B_ext_sweep_value_folder):
            m_data = extract_data(os.path.join(m_dynamics_quasi_static_steps_B_ext_sweep_value_folder, m_final_quasi_static_step) , simulation_settings)
            # Appending LLGS step result
            m_final_quasi_static_steps.append(m_data)
        # Appending B_ext sweep value results to B_ext_sweep_step_m_dynamics
        B_ext_sweep_step_m_dynamics.append(m_final_quasi_static_steps)
    # Extracting the final tunnel current distribution for each quasi-static sub-simulation for each B_ext sweep value
    # in such a way that the jth LLGS step of the jth B_ext sweep iteration can be accesed as: B_ext_sweep_step_j_tunnel[i][j]
    B_ext_sweep_step_j_tunnel = []
    for B_ext_sweep_value_folder in os.listdir(j_tunnel_folder):
        # Looping through B_ext sweep step folder and appending to m_final_quasi_static_steps
        j_tunnel_quasi_static_steps_B_ext_sweep_value_folder = os.path.join(j_tunnel_folder, B_ext_sweep_value_folder)
        j_tunnel_quasi_static_steps = []
        for j_tunnel_quasi_static_step in os.listdir(j_tunnel_quasi_static_steps_B_ext_sweep_value_folder):
            j_tunnel_data = extract_data((os.path.join(j_tunnel_quasi_static_steps_B_ext_sweep_value_folder, j_tunnel_quasi_static_step)), simulation_settings)
            # Appending LLGS step result
            j_tunnel_quasi_static_steps.append(j_tunnel_data)
        # Appending B_ext sweep value results to B_ext_sweep_step_m_dynamics
        B_ext_sweep_step_j_tunnel.append(j_tunnel_quasi_static_steps)
    return [B_ext_sweep_step_m_dynamics, B_ext_sweep_step_j_tunnel]


""" PLOT MAGNETIZATION TRAJECTORY FOR ALL SIMULATION ITERATIONS """
def plot_average_magnetization_on_unit_sphere(B_ext_sweep_step_m_dynamics, simulation_settings):
    for B_ext_sweep_step in range(len(B_ext_sweep_step_m_dynamics)):
        m_dynamics_B_ext_sweep_step = B_ext_sweep_step_m_dynamics[B_ext_sweep_step]
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        trajectory = []
        for m_final_quasi_static_step in m_dynamics_B_ext_sweep_step:
            m_x_total = 0
            m_y_total = 0
            m_z_total = 0
            for i in range(simulation_settings['Nx']):
                for j in range(simulation_settings['Ny']):
                    m_cell = m_final_quasi_static_step[i][j]
                    m_x_total += m_cell[0]
                    m_y_total += m_cell[1]
                    m_z_total += m_cell[2]
            norm = np.sqrt(m_x_total**2 + m_y_total**2 + m_z_total**2)
            if norm != 0:
                m_norm = [m_x_total/norm, m_y_total/norm, m_z_total/norm]
            else:
                m_norm = [0, 0, 0]
            trajectory.append(m_norm)
        m_x_trajectory = [point[0] for point in trajectory]
        m_y_trajectory = [point[1] for point in trajectory]
        m_z_trajectory = [point[2] for point in trajectory]
        ax.plot(m_x_trajectory, m_y_trajectory, m_z_trajectory, linewidth=1, color='b')
        # Plotting starting magnetization
        ax.scatter(m_x_trajectory[0], m_y_trajectory[0], m_z_trajectory[0], s=20, edgecolor='k', linewidth=0.5, zorder=5)
        # Plotting ending magnetization
        ax.scatter(m_x_trajectory[-1], m_y_trajectory[-1], m_z_trajectory[-1], s=20, edgecolor='r', linewidth=0.5, zorder=5)
        # Drawing unit sphere surface
        u, v = np.linspace(0, 2 * np.pi, 100), np.linspace(0, np.pi, 100)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones_like(u), np.cos(v))
        ax.plot_surface(x, y, z, color='lightgray', alpha=0.2, linewidth=0)
        # Setting axis and labels
        ax.set_xlabel('mx')
        ax.set_ylabel('my')
        ax.set_zlabel('mz')
        ax.set_title(f'Normalized Avg. Magnetization on Unit Sphere\nB_ext sweep step {B_ext_sweep_step+1}/{len(B_ext_sweep_step_m_dynamics)}')
        ax.legend(loc='upper left', bbox_to_anchor=(1.1, 1.05))
        ax.grid(False)
        ticks = [-1, 0, 1]
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_zticks(ticks)
        ax.set_box_aspect([1, 1, 1])
        plt.tight_layout()
        plt.show()


""" PLOT TOTAL TUNNEL CURRENT ACROSS MTJ FOR ALL SIMULATION ITERATIONS """
def plot_tunnel_current_quasi_static_convergence(B_ext_sweep_step_j_tunnel, simulation_settings):
    size_x = simulation_settings['size_x']
    size_y = simulation_settings['size_y']
    # Computing total current through MTJ for each quasi-static sub-simulation for each B_ext sweep value
    for B_ext_sweep_step in range(len(B_ext_sweep_step_j_tunnel)):
        total_current_B_ext_sweep_step = []
        j_tunnel_B_ext_sweep_step = B_ext_sweep_step_j_tunnel[B_ext_sweep_step]
        for j_tunnel_quasi_static_step in j_tunnel_B_ext_sweep_step:
            j_array = np.array(j_tunnel_quasi_static_step).reshape(-1)
            total_current = np.sum(j_array) * size_x * size_y
            total_current_B_ext_sweep_step.append(total_current)
        plt.figure()
        plt.plot(range(len(total_current_B_ext_sweep_step)), total_current_B_ext_sweep_step, marker='o', color='tab:red')
        plt.xlabel('Quasi-Static Step')
        plt.ylabel('Total Tunnel Current Across MTJ, A')
        plt.title(f'Convergence of Total Tunnel Current; B_ext sweep step {B_ext_sweep_step+1}/{len(B_ext_sweep_step_j_tunnel)}')
        plt.grid(True)
        plt.tight_layout()
        plt.show()


def plot_j_tunnel_converged(B_ext_sweep_step_j_tunnel, simulation_settings):
    size_x = simulation_settings['size_x']
    size_y = simulation_settings['size_y']
    B_ext_uniform = simulation_settings['B_ext_uniform']

    B_labels = []
    final_tunnel_current_B_ext_sweep_step = []
    final_R_MTJ_B_ext_sweep_step = []

    for B_ext_sweep_step in range(len(B_ext_sweep_step_j_tunnel)):
        j_tunnel_B_ext_sweep_step = B_ext_sweep_step_j_tunnel[B_ext_sweep_step]
        index_final_quasi_static_step = len(j_tunnel_B_ext_sweep_step)
        j_tunnel_quasi_static_step_final = j_tunnel_B_ext_sweep_step[index_final_quasi_static_step-1]
        j_array = np.array(j_tunnel_quasi_static_step_final).reshape(-1)
        total_current = np.sum(j_array) * size_x * size_y
        final_tunnel_current_B_ext_sweep_step.append(total_current)
        total_R_MTJ = simulation_settings['V_bias'] / total_current
        final_R_MTJ_B_ext_sweep_step.append(total_R_MTJ)
        B_labels.append(B_ext_uniform[B_ext_sweep_step])

    plt.figure(figsize=(10, 6))
    plt.plot(range(len(final_tunnel_current_B_ext_sweep_step)), final_tunnel_current_B_ext_sweep_step, marker='o', color='tab:blue')
    plt.xticks(ticks=range(len(B_labels)), labels=B_labels, rotation=45, ha='right')
    plt.ylabel('Final Converged Tunnel Current, A')
    plt.xlabel('External Magnetic Field B_ext (T)')
    plt.title('Final Tunnel Current vs B_ext')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.plot(range(len(final_R_MTJ_B_ext_sweep_step)), final_R_MTJ_B_ext_sweep_step, marker='o', color='tab:blue')
    plt.xticks(ticks=range(len(B_labels)), labels=B_labels, rotation=45, ha='right')
    plt.ylabel('Final Full MTJ Resistance, Ohms')
    plt.xlabel('External Magnetic Field B_ext (T)')
    plt.title('Final Full MTJ Resistance vs B_ext')
    plt.grid(True)
    plt.tight_layout()
    plt.show()




def plot_R_MTJ_converged(j_tunnel_converged, simulation_settings):
    size_x = simulation_settings['size_x']
    size_y = simulation_settings['size_y']
    B_ext_uniform = simulation_settings['B_ext_uniform']

    total_R_MTJ = []
    B_labels = []

    for i, j_converged in enumerate(j_tunnel_converged):
        j_array = np.array(j_converged).reshape(-1)
        total_current = np.sum(j_array) * size_x * size_y
        total_R_MTJ_B_ext_value = simulation_settings['V_bias'] / total_current
        total_R_MTJ.append(total_R_MTJ_B_ext_value)

        B = B_ext_uniform[i]
        label = f"Bx={B[0]:.3f}, By={B[1]:.3f}, Bz={B[2]:.3f}"
        B_labels.append(label)

    plt.figure(figsize=(10, 6))
    plt.plot(range(len(total_R_MTJ)), total_R_MTJ, marker='o', color='tab:blue')
    plt.xticks(ticks=range(len(B_labels)), labels=B_labels, rotation=45, ha='right')
    plt.ylabel('Final Converged MTJ Resistance, Ohms')
    plt.xlabel('External Magnetic Field B_ext (T)')
    plt.title('Final MTJ Resistance vs B_ext')
    plt.grid(True)
    plt.tight_layout()
    plt.show()




def plot_results(simulation_settings, scripts_folders, plot_options):

    B_ext_sweep_step_m_dynamics, B_ext_sweep_step_j_tunnel = gather_data(simulation_settings, scripts_folders)

    # Plotting average normalized magnetization dynamics at each LLGS step for each B_ext sweep value
    if plot_options['show_unit_sphere_dynamics']:
        plot_average_magnetization_on_unit_sphere(B_ext_sweep_step_m_dynamics, simulation_settings)
        
    # Plotting total tunnel current flowing through MTJ at each LLGS step for each B_ext sweep value
    if plot_options['show_j_tunnel_convergence']:
        plot_tunnel_current_quasi_static_convergence(B_ext_sweep_step_j_tunnel, simulation_settings)

    # Final converged tunnel current at each B_ext sweep step
    if plot_options['show_j_tunnel_final']:
        plot_j_tunnel_converged(B_ext_sweep_step_j_tunnel, simulation_settings)
