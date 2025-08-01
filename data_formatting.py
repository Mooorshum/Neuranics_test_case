""" FUNCTION WHICH INSERTS SCRIPT SETTINGS INTO MUMAX TEMPLATE """
def paste_settings_to_script_template(settings_data, template_filename, output_filename):
    with open(template_filename, 'r') as file:
        lines = file.readlines()
    for key, value in settings_data.items():
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

