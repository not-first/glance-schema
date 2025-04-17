# Glance Schema
*A JSON schema detailing the [Glance](https://github.com/glanceapp/glance) config file.*

> [!NOTE]
> Currently supports version: v0.7.12

## Usage
For custom usage, the schema link can be found at https://raw.githubusercontent.com/not-first/glance-schema/master/schema.json.

### VS Code
If you use VS Code to edit your `glance.yml`, the schema can be used to provide typing completions, hover descriptions and incorrect configuration errors.

1. Install the [YAML extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml).
2. At the top of your `glance.yml` file, add this line:
   ```yaml
   # yaml-language-server: $schema=https://raw.githubusercontent.com/not-first/glance-schema/master/schema.json
   ```
  3. Done.

## Planned Features
- Widget specific parameter requirements
  - DNS stats widget, correct restriction of `username`, `password` and `token` field depending on service.
- autocomplete, validation and description for the $insert parameter

## Known Limitations
Although the schema allows using the `$include` parameter to include other files, it will not work correctly if you set up validation for these additional files. There is because Glance is very flexible in the structure of an added file (a seperate file can contain a widget, a page, properties etc).

Some error messages can be autogenerated by the schema validator and are unhelpful to figure out what is wrong. Please create an issue if you experience one.

## Contribution

Any help in maintaining the schema is appreciated. This may include:
- Adding new widgets
- Updating widget properties as they change
- Updating property descriptions to be more specific/helpful
- Updating property examples

### Schema Generation Script
In order to make building the schema easier, it is split into a file per each base property (e.g server, branding, pages) and widgets. A script is then run to build a singular JSON file for the schema.

#### Local Testing
To test locally, install the packages `alive-progress` and `pyyaml` in a python environment and run the script in `scripts/generate-schema.py`. It will generate a `schema.json` at the root of the repo. Then use:
```
yaml-language-server: $schema=file://{PATH_TO_YOUR_SCHEMA.JSON}
```
at the top of any `glance.yml` to test the locally generated version of the schema (in vscode).

Remove this `schema.json` file from your commit if possible, as it is built by a Github Action on push to ensure consistency. A locally generated schema will function the same as one generated automatically.

#### Script Functionality
1. Combines all the top-level properties into the base schema template (branding, pages etc)
2. Loads the widget base properties, creates a specific schema combining this with every widget file
3. Creates a definition for each widget and reference it in the schema
4. Output schema to `schema.json`

