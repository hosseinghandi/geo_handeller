<img width="1707" height="760" alt="view" src="https://github.com/user-attachments/assets/ca6d084d-7161-4a1b-97d3-9a676a62a3e8" />

## Geo Validator 🔷
A component designed to validate building geometries and prepare models for reliable Ladybug environmental simulations.

## 🧩 Overview
A geometry validation component that checks building models and classifies them based on their suitability for environmental simulations.

## 🎯 Project Goals
The goal of this component was to automate geometry validation and reduce the complexity of preparing models for environmental simulations. Building on previous projects, I focused on improving simulation accuracy, speeding up model preparation, and lowering the barrier for non-expert users working with complex urban geometries.

## 📂📘 Getting Started
To get started, open the provided example files and follow the included instructions.

## 🛠 Tech 
- Python
 
## ✨ Main Features
- Automatic detection of invalid or open solids (e.g. curves or non-closed geometries)
- Identification of non-planar geometries
- Detection of short edges, very small surfaces, and tight angles that can increase simulation time
- Evaluation of geometry complexity and edge conditions
- Classification into valid, suspicious, and invalid geometry
- Visual feedback and warnings directly in the Rhino environment
- User-defined validation criteria and tolerance settings for flexibility across different project scales
  
## ⚠️ Challenges I Faced
- Handling diverse and complex urban geometries across different scales while maintaining flexibility for various project types

## 🤖 How I Used AI
- Supported classification strategies for simulation-ready geometry
- Assisted in structuring the workflow for better usability


## 📚 Research Purpose
This tool was developed to improve the modeling process of Ladybug simulations, such as UTCI, MRT, and energy analysis, which can be challenging in complex urban environments.

---

## 🧾Citation and Project Use
If you use this tool in research, publications, teaching, or professional projects, please cite the repository and kindly inform the author.

**Author:**
Hossein Ghandi 🧑‍💻
📧 Email: [ghandih22@email.com](mailto:ghandih22@email.com)

Feedback, case studies, and derived applications are highly appreciated and help support future development of the workflow.
