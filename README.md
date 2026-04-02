# Geo_Validator
The **`Geo_Validator`** component is designed to **simplify and accelerate geometry preparation for Ladybug simulations**.

It helps users **reduce the time and difficulty of 3D model preparation** by automatically checking whether building geometries are suitable for **energy, solar radiation, and outdoor comfort analysis**.

Instead of manually inspecting complex urban models, the component quickly detects common geometry problems such as:

- invalid or open solids
- non-planar geometries
- very short edges
- overly complex forms
- insufficient building height
- incorrect placement relative to the ground plane
- problematic edge angles
- surfaces that are too small for reliable simulation

By automatically classifying the input into **valid, suspicious, and invalid geometry**, the component significantly reduces **manual cleanup work**, making the modeling workflow faster and easier, especially for **large urban datasets**.

This helps:
- reduce simulation errors
- speed up model preparation
- simplify large-scale geometry cleaning
- improve workflow reliability
- lower the technical barrier for new users

---

## How to Use
### 1. Connect the building geometry
- Input closed **Breps**, massing models, or imported urban blocks

### 2. Run the component
- The geometry will be automatically checked against predefined quality criteria

### 3. Review the outputs
- **Valid geometry** → ready for Ladybug
- **Suspicious geometry** → recommended for review
- **Invalid geometry** → should be removed or fixed

### 4. Check Rhino warnings
- Text markers highlight problematic areas directly in the Rhino model

### 5. Optional cleanup
- Enable automatic repositioning to the ground plane if required

---

## Citation and Project Use
If you use this tool in research, publications, teaching, or professional projects, please cite the repository and kindly inform the author.

**Author:** Hossein Ghandi

Feedback, case studies, and derived applications are highly appreciated and help support future development of the workflow.
