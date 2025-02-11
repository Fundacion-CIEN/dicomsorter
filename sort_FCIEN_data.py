import os
import re

input_dir = '/mnt/nasneuro_share/TEMP_BACKUP'
output_dir = '/mnt/nasneuro_share/BACKUP_RM'

order_ = 'StudyDescription PatientID StudyDate SeriesDescription'

for root, dirs, files in os.walk(input_dir):
    # Check if the current directory has no subdirectories.
    if not dirs:
        # Optionally, process only if there are files in the directory.
        if files:

            # Build the command string.
            command = (
                f'dicomsorter "{root}" "{output_dir}" --path {order_} '
                f'--original-filename --force --overwrite'
            )
            print("Processing: ", root)
            #print("Executing command:", command)  # For debugging/logging
            os.system(command)



# Regular expression to match folder names starting with "Series"
# It captures the series number and the rest of the description.
# Example: "Series0001_AAhead_scout_HeadNeck 64" will have:
#   series_num = "0001"
#   description = "AAhead_scout_HeadNeck 64"
series_pattern = re.compile(r'^Series(\d+)_(.+)$')


def shorten_name(long_name):
    """
    Splits the original folder description on underscores and spaces,
    converts tokens to lowercase, removes duplicate tokens, and then
    shortens each token to its first three characters. The final tokens
    are joined with underscores.
    """
    # Split on underscores and spaces.
    tokens = re.split(r'[\s_]+', long_name)

    # Convert tokens to lowercase and filter out any empty tokens.
    tokens = [token.lower() for token in tokens if token]

    # Remove duplicate tokens while preserving order.
    seen = set()
    deduped = []
    for token in tokens:
        if token not in seen:
            seen.add(token)
            deduped.append(token)

    # Shorten each token to its first three characters.
    short_tokens = [token[:3] for token in deduped]

    # Join the tokens with underscores to form the short name.
    return "_".join(short_tokens)


# === Renaming Loop ===
for dirpath, dirnames, filenames in os.walk(output_dir, topdown=False):
    for folder in dirnames:
        old_path = os.path.join(dirpath, folder)
        match = series_pattern.match(folder)
        if match:
            series_num_str, description = match.groups()
            # Convert the series number string to an integer (leading zeros removed)
            series_num_int = int(series_num_str)
            # Generate a shortened description.
            short_desc = shorten_name(description)
            # Build the new base name by prefixing with the series number.
            new_base = f"{series_num_int}_{short_desc}"
            new_name = new_base
            # Ensure the new name is unique within the current directory.
            new_path = os.path.join(dirpath, new_name)
            counter = 1
            while os.path.exists(new_path):
                new_name = f"{new_base}_{counter}"
                new_path = os.path.join(dirpath, new_name)
                counter += 1
            # Log the renaming action.
            print(f"Renaming '{old_path}' to '{new_path}'")
            os.rename(old_path, new_path)
        else:
            print(f"Skipping folder '{old_path}' (does not match expected Series pattern)")