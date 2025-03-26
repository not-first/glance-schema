import os
import json
import yaml
import glob
from pathlib import Path
from alive_progress import alive_it


def main():
    script_path = Path(os.path.abspath(__file__))
    script_dir = script_path.parent
    project_dir = script_dir.parent

    # Use absolute paths to prevent working directory issues
    schemas_dir = project_dir / "schemas"
    widgets_dir = schemas_dir / "widgets"
    output_file = project_dir / "schema.json"

    # load the base schema
    base_schema_path = schemas_dir / "base.yml"
    with open(base_schema_path, 'r') as f:
        combined_schema = yaml.safe_load(f)

    combined_schema['properties'] = {}

    # pick out top level headings (excluding the base tempalte)
    yaml_files = [f for f in glob.glob(
        str(schemas_dir / "*.yml")) if not f.endswith("base.yml")]

    for yaml_file in alive_it(yaml_files, title="Base Properties"):
        with open(yaml_file, 'r') as f:
            schema_content = yaml.safe_load(f)

            # add top level headings to the sceyaml
            for key, value in schema_content.items():
                combined_schema['properties'][key] = value

    # load the base widget (common properties shared across all widgets)
    widget_base_path = widgets_dir / "base.yml"
    with open(widget_base_path, 'r') as f:
        widget_base = yaml.safe_load(f)

    # pick out all widgets (excluding the base template)
    widget_files = [f for f in glob.glob(
        str(widgets_dir / "*.yml")) if not f.endswith("base.yml")]

    widget_types = []
    widget_definitions = {}

    for widget_file in alive_it(widget_files, title="Widgets"):
        widget_name = os.path.basename(widget_file).replace('.yml', '')  # extract widget name
        widget_types.append(widget_name)  # add the widget name to the list of valid widget types

        with open(widget_file, 'r') as f:
            widget_schema = yaml.safe_load(f)

            widget_schema['properties']['type'] = {'enum': [widget_name]}  # add widget type to schema

            # store widget definition
            widget_def_name = f"{widget_name}-widget"
            widget_definitions[widget_def_name] = widget_schema

    # update widget base enum with all widget types
    widget_base['properties']['type']['enum'] = widget_types

    # add definitions section to combined schema
    combined_schema['definitions'] = {}

    # create base widget definition
    combined_schema['definitions']['widget-base'] = widget_base

    # create a definition for each widget
    for widget_name, widget_def in widget_definitions.items():
        combined_schema['definitions'][widget_name] = widget_def

    # create main widget definition that handles all others
    widget_refs = []
    for widget_name in widget_definitions.keys():
        widget_refs.append({"$ref": f"#/definitions/{widget_name}"})

    combined_schema['definitions']['widget'] = {
        "allOf": [
            {"$ref": "#/definitions/widget-base"},
            {"oneOf": widget_refs}
        ]
    }

    # dunp the full schema to a json file
    with open(output_file, 'w') as f:
        json.dump(combined_schema, f, indent=2)

    print(f"Schema successfully generated at {output_file}")


if __name__ == "__main__":
    main()
