import yaml

def load_sources(path):

    with open(path, 'r') as f:

        yaml_data = yaml.safe_load(f)

    return yaml_data.get('sources', [])