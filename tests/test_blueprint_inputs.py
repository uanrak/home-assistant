import os
import yaml
import pytest

class InputTag(str):
    pass

class Loader(yaml.SafeLoader):
    pass

def input_constructor(loader, node):
    return InputTag(loader.construct_scalar(node))

Loader.add_constructor('!input', input_constructor)

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
YAML_FILES = [os.path.join(REPO_ROOT, f) for f in os.listdir(REPO_ROOT) if f.endswith('.yaml')]


def collect_input_refs(data):
    refs = []
    if isinstance(data, InputTag):
        refs.append(str(data))
    elif isinstance(data, dict):
        for value in data.values():
            refs.extend(collect_input_refs(value))
    elif isinstance(data, list):
        for item in data:
            refs.extend(collect_input_refs(item))
    return refs

@pytest.mark.parametrize('yaml_file', YAML_FILES)
def test_inputs_defined(yaml_file):
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.load(f, Loader=Loader)
    assert 'blueprint' in data, f"{yaml_file} lacks blueprint section"
    blueprint_inputs = data['blueprint'].get('input', {})
    defined_keys = set(blueprint_inputs.keys())
    refs = collect_input_refs(data)
    for ref in refs:
        assert ref in defined_keys, f"{yaml_file}: !input {ref} not defined in blueprint.input"
