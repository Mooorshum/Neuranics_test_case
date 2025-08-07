from math import acos, cos, sqrt, pi


""" COMPUTE TUNNEL CURRENT DISTRIBUTION DATA """
def compute_j_tunnel(m_free_data, simulation_settings):
    Nx = len(m_free_data)
    Ny = len(m_free_data[0])
    V_bias = simulation_settings['V_bias']
    R_p = simulation_settings['R_p']
    R_ap = simulation_settings['R_ap']
    cell_size_x = simulation_settings['size_x'] / Nx
    cell_size_y = simulation_settings['size_y'] / Ny
    m_reference = simulation_settings['m_reference']
    m_reference_x, m_reference_y, m_reference_z = m_reference[0], m_reference[1], m_reference[2]
    j_tunnel_data = [[None for _ in range(Ny)] for _ in range(Nx)]
    for j in range(Ny):
        for i in range(Nx):
            m_free = m_free_data[i][j]
            m_free_x, m_free_y, m_free_z = m_free[0], m_free[1], m_free[2]
            cos_m_free_ref = (m_free_x * m_reference_x + m_free_y * m_reference_y + m_free_z * m_reference_z) / \
                (sqrt(m_free_x**2 + m_free_y**2 + m_free_z**2) * sqrt(m_reference_x**2 + m_reference_y**2 + m_reference_z**2))

            # If we imagine that the MTJ consists of many single-cell MTJs, 
            # then the resistance of each in uniformely parallel and antiparallel states is
            R_p_cell = R_p * (Nx * Ny)
            R_ap_cell = R_ap * (Nx * Ny)
            R_cell = R_p_cell + (R_ap_cell - R_p_cell) / 2 * (1 - cos_m_free_ref)

            I_cell = V_bias / R_cell
            j_cell = I_cell / (cell_size_x * cell_size_y)
            j_tunnel_data[i][j] = [0, 0, j_cell] #[0, 0, 0]
    return j_tunnel_data


""" COMPUTE OERSTED FIELD DISTRIBUTION DATA """
def compute_B_oe(j_tunnel_data, simulation_settings):
    mu0 = 1.256e-6
    Nx = len(j_tunnel_data)
    Ny = len(j_tunnel_data[0])
    cell_size_x = simulation_settings['size_x'] / Nx
    cell_size_y = simulation_settings['size_y'] / Ny
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
            B_oe_data[i][j] = [B_oe_cell_total_x, B_oe_cell_total_y, 0] # [0, 0, 0]
    return B_oe_data
