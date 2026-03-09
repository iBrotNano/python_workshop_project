# Python Workshop Project

This is a simple training project for a Python workshop. It uses the [world.openfoodfacts.org](https://world.openfoodfacts.org/) to fetch nutritional information about food products and allows users to create recipes, meal plans, and shopping lists.

![Fat cat](assets/img/repository-open-graph-template.png)

## Running the app

Open a terminal, navigate to the project directory, and run:

```powershell
python .\src\main.py
```

## Initializing the Project

I used Anaconda to set up the project environment.

```powershell
conda create -n python_workshop_project python=3.13
conda activate python_workshop_project
# If you don't have conda, you can use pip to install the required packages.
```

You can install the requirements using:

```powershell
# From requirements.txt
pip install -r requirements.txt

# Or from environment.yml (recommended for conda)
conda env create -f environment.yml -n python_workshop_project
conda activate python_workshop_project
```

> [!IMPORTANT] DEPENDENCIES
> Both files need to be updated whenever new packages are added to the project or existing ones are updated.

```powershell
pip list --format=freeze > requirements.txt & conda env export > environment.yml
```

An existing environment can be updated with:

```powershell
conda env update -f environment.yml -n python_workshop_project
```

## Optional local VS Code terminal setup (opt-in)

Machine-specific terminal profile settings are intentionally not committed to the shared workspace file.
If you want an auto-activating conda terminal in VS Code, add this to your local `.vscode/settings.json` or into a `python_workshop_project.local.code-workspace` file:

```json
{
	"terminal.integrated.profiles.windows": {
		"WorkspacePwsh": {
			"path": "C:\\Program Files\\PowerShell\\7\\pwsh.exe",
			"args": [
				"-NoExit",
				"-Command",
				"cd ${workspaceFolder}; conda activate python_workshop_project"
			]
		}
	},
	"terminal.integrated.defaultProfile.windows": "WorkspacePwsh"
}
```

Adjust the profile name, shell path, and environment name to your local machine.

> [!TIP] Test data
> You can generate test data by executing `tools/create_test_recipes.py`. It will generate recipes under `data`.

## Security and Privacy

Under `docs/pias` is documented what personal data is processed in the app, how it is processed, and what measures are taken to protect it. These are living documents that should be updated whenever there are changes to the data processing in the app. It is important to keep these documents up to date to ensure compliance with data protection regulations and to maintain transparency with users about how their data is being used.