import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from .ovf_data_formatting import extract_data


""" GATHER DATA FROM SIMULATION RESULTS """
def gather_data(simulation_settings, scripts_folders):
    m_dynamics_folder = scripts_folders['M_DYNAMICS_DATA_FOLDER']
    j_tunnel_folder = scripts_folders['J_TUNNEL_DATA_FOLDER']

    print('Preparing data for plots...')
    m_dynamics_full = []
    j_tunnel_full = []
    j_tunnel_converged = []
    for B_ext_sweep_value_folder in os.listdir(m_dynamics_folder):
        m_dynamics_B_ext_sweep_step = []
        j_tunnel_B_ext_sweep_step = []

        # Looping through simulation iteration folders and appending to m_dynamics_full in such a way that
        # the ith LLGS step of the jth simulation iteration can be accesed as: m_dynamics_full[j][i]
        for m_dynamics_iteration_folder in os.listdir(
            os.path.join(m_dynamics_folder, B_ext_sweep_value_folder)
        ):
            iteration_path = os.path.join(os.path.join(m_dynamics_folder, B_ext_sweep_value_folder), m_dynamics_iteration_folder)
            m_dynamics_quasi_static_steps = []
            # Loop through ovf files
            for ovf_filename in os.listdir(iteration_path):
                ovf_path = os.path.join(iteration_path, ovf_filename)
                m_data = extract_data(ovf_path, simulation_settings)
                # Appending LLGS step result
                m_dynamics_quasi_static_steps.append(m_data)
            # Appending simulation iteration
            m_dynamics_B_ext_sweep_step.append(m_dynamics_quasi_static_steps)
        
        # Looping through simulation iteration folders and appending to j_tunnel_full in such a way that
        # the jth simulation iteration can be accessed as: j_tunnel_full[j]
        for j_tunnel_iteration_folder in os.listdir(os.path.join(j_tunnel_folder, B_ext_sweep_value_folder)):
            iteration_path = os.path.join(os.path.join(j_tunnel_folder, B_ext_sweep_value_folder), j_tunnel_iteration_folder)
            ovf_filename = os.listdir(iteration_path)[0]
            ovf_path = os.path.join(iteration_path, ovf_filename)
            j_tunnel_data_quasi_static_data = extract_data(ovf_path, simulation_settings)
            # Appending simulation iteration result
            j_tunnel_B_ext_sweep_step.append(j_tunnel_data_quasi_static_data)
            
        m_dynamics_full.append(m_dynamics_B_ext_sweep_step)
        j_tunnel_full.append(j_tunnel_B_ext_sweep_step)

        j_tunnel_converged.append(j_tunnel_B_ext_sweep_step[-1])

    return [m_dynamics_full, j_tunnel_full, j_tunnel_converged]


""" PLOT MAGNETIZATION TRAJECTORY FOR ALL SIMULATION ITERATIONS """
def plot_average_magnetization_on_unit_sphere(m_dynamics_full):
    for B_ext_sweep_step in range(len(m_dynamics_full)):
        m_dynamics_B_ext_sweep_step_values = m_dynamics_full[B_ext_sweep_step]
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        colors = plt.cm.get_cmap('tab10', len(m_dynamics_B_ext_sweep_step_values))
        for j_sim_iter, simulation_steps in enumerate(m_dynamics_B_ext_sweep_step_values):
            trajectory = []
            for step_data in simulation_steps:
                m_array = np.array(step_data).reshape(-1, 3)
                avg_vector = np.mean(m_array, axis=0)
                norm = np.linalg.norm(avg_vector)
                if norm == 0:
                    continue
                unit_vector = avg_vector / norm
                trajectory.append(unit_vector)
            trajectory = np.array(trajectory)
            ax.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2],
                    color=colors(j_sim_iter),
                    label=f"Iter {j_sim_iter}")
        u, v = np.linspace(0, 2 * np.pi, 100), np.linspace(0, np.pi, 100)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones_like(u), np.cos(v))
        ax.plot_surface(x, y, z, color='lightgray', alpha=0.2, linewidth=0)
        ax.set_xlabel('mx')
        ax.set_ylabel('my')
        ax.set_zlabel('mz')
        ax.set_title(f'Normalized Average Magnetization Trajectory on Unit Sphere; B_ext sweep step {B_ext_sweep_step+1}/{len(m_dynamics_full)}')
        ax.legend(loc='upper left', bbox_to_anchor=(1.1, 1.05))
        ax.grid(False)
        ticks = [-1, 0, 1]
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_zticks(ticks)
        plt.tight_layout()
        plt.show()


""" PLOT TOTAL TUNNEL CURRENT ACROSS MTJ FOR ALL SIMULATION ITERATIONS """
def plot_average_tunnel_current(j_tunnel_full, simulation_settings):
    size_x = simulation_settings['size_x']
    size_y = simulation_settings['size_y']
    for B_ext_sweep_step in range(len(j_tunnel_full)):
        avg_currents = []
        for j_iter_data in j_tunnel_full[B_ext_sweep_step]:
            j_array = np.array(j_iter_data).reshape(-1)
            total_current = np.sum(j_array) * size_x * size_y
            avg_currents.append(total_current)
        plt.figure()
        plt.plot(range(len(avg_currents)), avg_currents, marker='o', color='tab:red')
        plt.xlabel('Simulation Iteration')
        plt.ylabel('Total Tunnel Current Across MTJ, A')
        plt.title(f'Convergence of Total Tunnel Current; B_ext sweep step {B_ext_sweep_step+1}/{len(j_tunnel_full)}')
        plt.grid(True)
        plt.tight_layout()
        plt.show()


def plot_j_tunnel_converged(j_tunnel_converged, simulation_settings):
    size_x = simulation_settings['size_x']
    size_y = simulation_settings['size_y']
    B_ext_uniform = simulation_settings['B_ext_uniform']

    total_currents = []
    B_labels = []

    for i, j_converged in enumerate(j_tunnel_converged):
        j_array = np.array(j_converged).reshape(-1)
        total_current = np.sum(j_array) * size_x * size_y
        total_currents.append(total_current)

        B = B_ext_uniform[i]
        label = f"Bx={B[0]:.3f}, By={B[1]:.3f}, Bz={B[2]:.3f}"
        B_labels.append(label)

    plt.figure(figsize=(10, 6))
    plt.plot(range(len(total_currents)), total_currents, marker='o', color='tab:blue')
    plt.xticks(ticks=range(len(B_labels)), labels=B_labels, rotation=45, ha='right')
    plt.ylabel('Final Converged Tunnel Current, A')
    plt.xlabel('External Magnetic Field B_ext (T)')
    plt.title('Final Tunnel Current vs B_ext')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_results(simulation_settings, scripts_folders, plot_options):

    m_dynamics_full, j_tunnel_full, j_tunnel_converged = gather_data(simulation_settings, scripts_folders)

    # Two sets of plots meant to show solution convergence:
    if plot_options['show_convergence']:

        # Plotting average magnetization dynamics for each LLGS step at each simulation iteration
        if plot_options['show_unit_sphere_dynamics']:
            plot_average_magnetization_on_unit_sphere(m_dynamics_full)
        
        # Plotting total tunnel current flowing through MTJ at each simulation iteration
        if plot_options['show_j_tunnel_convergence']:
            plot_average_tunnel_current(j_tunnel_full, simulation_settings)

    # final converged tunnel current at each B_ext sweep step
    if plot_options['show_j_tunnel_converged']:
        plot_j_tunnel_converged(j_tunnel_converged, simulation_settings)

