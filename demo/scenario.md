# SPR-1 demo scenario

Date: 2020-07-08

## Required system setup

- macOS Catalina
- Homebrew + CMake + XCode + Ninja + Miniconda

## 1. Deployment + Installation (5 min)

Goal: Show how to download, compile and install Eradiate

Demo execution environment: terminal

1. Go to GitHub
2. Check installation instructions
3. Clone repository
4. Setup environment + activate it
5. Compile Mitsuba
6. Check that Mitsuba is working
7. Install Eradiate in developer mode

## 2. Low-level scene construction (15 min)

Goal: Show how to build a scene, visualise it, run simulations on it

Demo execution environment: Jupyter notebook

1. Kernel interface showcase
	1. Show how to load a scene file corresponding to the Rayleigh test case and visualise it with the Mitsuba binary
	2. Show how to load that scene using the Mitsuba XML loader and visualise it with matplotlib
	3. Show how to create the same scene using a dictionary and visualise it with matplotlib
2. Scene generation interface
	1. Show how to build the Rayleigh scene with the scene helper classes
3. One-dimensional solver interface
	1. Show how to create a `OneDimSolver` instance
	2. Populate its scene dictionary using the interface
	3. Run the simulation for a single angular configuration
	4. Run the simulation to get the BRDF for a single incoming direction
	5. Plot the results

## 3. Rayleigh solver application (10 min)

Goal: Show how to use a high-level solver application

Demo execution environment: Jupyter notebook, then terminal

1. Python interface
	1. Show how to instantiate `RayleighSolverApp` and configure it with a dictionary
	2. Show how to do this from a YAML file
	3. Run the simulation and visualise the results
	4. Visualise RPV lobe flattening vs scattering coefficient increase
2. Command-line interface
	1. Show how to run `RayleighSolverApp` from the terminal using the terminal
	2. Show results

## Todo

- [x] Finish work on scene generator architecture
- [ ] Improve BRDFView class performance (vectorise evaluation)
- [ ] Investigate system test with scattering
