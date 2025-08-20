import os
import shutil
import subprocess


""" EXTRACT HEADER FROM TEMPLATE OVF FILE """
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


""" EXTRACT FOOTER FROM TEMPLATE OVF FILE """
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


""" GENERATE OVF FILE HEADERS AND FOOTERS FOR SIMULATION PARAMETERS """
def generate_ovf_headers_footers(simulation_settings, generation_script_template):
        # Insterting simulation settings into ovf generation script
        temporary_script_filename = 'ovf_generation_script_temporary.mx3'
        paste_settings_to_script_template(simulation_settings, generation_script_template, temporary_script_filename)
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


""" INSERT SCRIPT SETTINGS INTO MUMAX TEMPLATE """
def paste_settings_to_script_template(simulation_settings, template_filename, output_filename):
    with open(template_filename, 'r') as file:
        lines = file.readlines()
    for key, value in simulation_settings.items():
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
