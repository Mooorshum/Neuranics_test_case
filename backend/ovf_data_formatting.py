""" EXTRACT DATA FROM OVF FILE AND CONVERT IT TO PYTHON READABLE FORMAT """
def extract_data(filepath, simulation_settings):
    # Extracting data in string format
    data_lines = []
    extracting_data = False
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip() == '# Begin: Data Text':
                extracting_data = True
                continue
            elif line.strip() == '# End: Data Text':
                break
            if extracting_data:
                data_lines.append(line)
    data_string = ''.join(data_lines)
    # COnverting data to numeric values
    Nx = simulation_settings['Nx']
    Ny = simulation_settings['Ny']
    flat_values = list(map(float, data_string.split()))
    data_numeric = [[None for _ in range(Ny)] for _ in range(Nx)]
    index = 0
    for j in range(Ny):
        for i in range(Nx):
            vector = flat_values[index:index+3]
            data_numeric[i][j] = vector
            index += 3
    return data_numeric


""" CONVERT OVF FILE FORMATTING FROM DOS FILE TO UNIX """
def convert_to_unix(filename):
    with open(filename, 'r') as f:
        content = f.read()
    with open(filename, 'w', newline='\n') as f:
        f.write(content)


""" CONSTRUCT OVF FILE FROM PYTHON DATA """
def convert_to_ovf(output_filename, header, footer, data):
    Nx = len(data)
    Ny = len(data[0])
    with open(output_filename, 'w') as f:
        # Writing header
        f.write(header)
        if not header.endswith('\n'):
            f.write('\n')
        # Writing data
        for j in range(Ny):
            for i in range(Nx):
                vector = data[i][j]
                line = f'{vector[0]} {vector[1]} {vector[2]}\n'
                f.write(line)
        # Writing footer
        if not footer.startswith('\n') and not footer.startswith('#'):
            f.write('\n')
        f.write(footer)
    convert_to_unix(output_filename)
