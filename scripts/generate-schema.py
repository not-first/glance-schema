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
    with open(base_schema_path, "r") as f:
        combined_schema = yaml.safe_load(f)

    combined_schema["properties"] = {}

    # pick out top level headings (excluding the base tempalte)
    yaml_files = [
        f for f in glob.glob(str(schemas_dir / "*.yml")) if not f.endswith("base.yml")
    ]

    for yaml_file in alive_it(yaml_files, title="Base Properties"):
        with open(yaml_file, "r") as f:
            schema_content = yaml.safe_load(f)

            # add top level headings to the sceyaml
            for key, value in schema_content.items():
                combined_schema["properties"][key] = value

    # load the base widget (common properties shared across all widgets)
    widget_base_path = widgets_dir / "base.yml"
    with open(widget_base_path, "r") as f:
        widget_base = yaml.safe_load(f)

    # pick out all widgets (excluding the base template)
    widget_files = [
        f for f in glob.glob(str(widgets_dir / "*.yml")) if not f.endswith("base.yml")
    ]

    widget_types = []
    widget_definitions = {}

    for widget_file in alive_it(widget_files, title="Widgets"):
        widget_name = os.path.basename(widget_file).replace(
            ".yml", ""
        )  # extract widget name
        widget_types.append(
            widget_name
        )  # add the widget name to the list of valid widget types

        with open(widget_file, "r") as f:
            widget_schema = yaml.safe_load(f)

            widget_schema["properties"]["type"] = {
                "enum": [widget_name]
            }  # add widget type to schema

            # store widget definition
            widget_def_name = f"{widget_name}-widget"
            widget_definitions[widget_def_name] = widget_schema

    # update widget base enum with all widget types
    widget_base["properties"]["type"]["enum"] = widget_types

    # add definitions section to combined schema
    combined_schema["definitions"] = {}

    # add include definition for $include directive
    combined_schema["definitions"]["include"] = {
        "type": "object",
        "required": ["$include"],
        "properties": {"$include": {"type": "string"}},
    }

    # create base widget definition
    combined_schema["definitions"]["widget-base"] = widget_base

    # create a definition for each widget
    for widget_name, widget_def in widget_definitions.items():
        combined_schema["definitions"][widget_name] = widget_def

    # create main widget definition that handles all others
    widget_refs = []
    for widget_name in widget_definitions.keys():
        # each specific widget should combine widget-base with its specific schema
        widget_refs.append(
            {
                "allOf": [
                    {"$ref": "#/definitions/widget-base"},
                    {"$ref": f"#/definitions/{widget_name}"},
                ]
            }
        )

    # add include support to widget oneOf (without widget-base requirements)
    widget_refs.append({"$ref": "#/definitions/include"})

    # create the single widget-item definition (internal use)
    combined_schema["definitions"]["widget-item"] = {"oneOf": widget_refs}

    # create the widget definition as an array (primary consumer-facing definition)
    # widgets are always defined as arrays in separate files, even for a single widget
    combined_schema["definitions"]["widget"] = {
        "type": "array",
        "items": {"$ref": "#/definitions/widget-item"},
    }

    # extract and expose page schema (array, matching widget pattern)
    if "pages" in combined_schema["properties"]:
        pages_schema = combined_schema["properties"]["pages"]
        if "items" in pages_schema and isinstance(pages_schema["items"], dict):
            # extract the page-item schema (internal use)
            combined_schema["definitions"]["page-item"] = pages_schema["items"]
            # update pages array to reference the definition
            combined_schema["properties"]["pages"]["items"] = {
                "$ref": "#/definitions/page-item"
            }

            # create the page definition as an array (primary consumer-facing definition)
            # pages are always defined as arrays in separate files, even for a single page
            combined_schema["definitions"]["page"] = {
                "type": "array",
                "items": {"$ref": "#/definitions/page-item"},
            }

    # update internal widget references to use widget-item
    def update_widget_refs(obj):
        """Recursively update $ref to widget to use widget-item instead"""
        if isinstance(obj, dict):
            if obj.get("$ref") == "#/definitions/widget":
                obj["$ref"] = "#/definitions/widget-item"
            for value in obj.values():
                update_widget_refs(value)
        elif isinstance(obj, list):
            for item in obj:
                update_widget_refs(item)

    # Apply widget reference updates to properties and definitions
    update_widget_refs(combined_schema["properties"])
    update_widget_refs(combined_schema["definitions"])

    # inject $include support globally with oneOf wrapping
    def wrap_with_include_support(schema_obj, path=""):
        # base case: if not a dict, return as is
        if not isinstance(schema_obj, dict):
            return schema_obj

        # skip if this is the include definition itself
        if path == "definitions.include":
            return schema_obj

        # skip if already wrapped with oneOf that includes include reference
        if "oneOf" in schema_obj:
            return schema_obj

        # skip if this is a simple type without object structure
        if "type" in schema_obj and schema_obj["type"] != "object":
            return schema_obj

        # skip if this doesn't define an object (no properties, no allOf, etc.)
        has_object_structure = any(
            key in schema_obj for key in ["properties", "allOf", "anyOf", "oneOf"]
        )

        if schema_obj.get("type") == "object" or has_object_structure:
            # wrap with oneOf to allow either original schema or include
            return {"oneOf": [schema_obj, {"$ref": "#/definitions/include"}]}

        return schema_obj

    # wrap top-level properties
    for prop_name in list(combined_schema["properties"].keys()):
        prop_schema = combined_schema["properties"][prop_name]
        combined_schema["properties"][prop_name] = wrap_with_include_support(
            prop_schema, f"properties.{prop_name}"
        )

    # wrap definitions (except include itself and widget-base which is only used internally)
    for def_name in list(combined_schema["definitions"].keys()):
        # skip include, widget-base, widget, page, widget-item, and page-item
        # widget and page are arrays that already have their items wrapped
        # widget-item and page-item are internal definitions that get wrapped when creating widget/page
        if def_name in (
            "include",
            "widget-base",
            "widget",
            "page",
            "widget-item",
            "page-item",
        ):
            continue

        def_schema = combined_schema["definitions"][def_name]
        combined_schema["definitions"][def_name] = wrap_with_include_support(
            def_schema, f"definitions.{def_name}"
        )

    # dunp the full schema to a json file
    with open(output_file, "w") as f:
        json.dump(combined_schema, f, indent=2)

    print(f"Schema successfully generated at {output_file}")


if __name__ == "__main__":
    main()
