````md
# Project: Voice-Narrated Function Transformation Animation

**Version:** 2.1.0
**Last Updated:** 2025-08-29
**Primary Author:** vladdiethecoder
**Status:** Stable on v0.18.1, Experimental on v0.19.0

---

## 1. Project Overview

### 1.1. Project Name
FinalAnimation

### 1.2. Purpose
This project produces a high-quality, voice-narrated educational animation that visually explains the principles of 2D function transformations. It demonstrates a step-by-step application of reflections and translations to a single point on a Cartesian plane, making the abstract mathematical concept easy to understand.

### 1.3. Core Technologies
* **Language:** Python
* **Animation Engine:** Manim Community
* **Voiceover Extension:** `manim-voiceover`
* **Text-to-Speech (TTS) Engine:** Piper TTS (local, high-quality neural TTS)

---

## 2. Critical Versioning Information & Next Steps

This project's stability is highly dependent on the Manim version used. A critical rendering bug was discovered in Manim `v0.19.0` that causes text elements to be misplaced.

### 2.1. Priority Task: Test Hard-Coded Coordinate Fix on v0.19.0

**Hypothesis:** The rendering bug in Manim `v0.19.0` is limited to its relative positioning engine (`.next_to()`). Using hard-coded, absolute coordinates (`.move_to()`) should bypass this bug and allow the animation to render correctly even on the unstable version.

**Next Step:** The immediate priority is to test this hypothesis. This would confirm a viable path forward for using newer Manim versions and simplify the project's dependency requirements.

#### **Test Procedure:**
1.  **Setup a Python 3.13+ environment.**
2.  **Install Manim `v0.19.0` or newer:** `pip install manim manim-voiceover`
3.  **Use the `FinalAnimation.py` script with hard-coded coordinates.** (The latest version in the repository).
4.  **Create a `manim.cfg` file** to handle the configuration, as in-script `config` is deprecated in `v0.19.0`.
    ```ini
    [CLI]
    quality = h
    preview = True
    background_color = #0e1a25
    pixel_height = 1080
    pixel_width = 1920
    frame_rate = 30
    ```
5.  **Render the animation:** `manim FinalAnimation.py FinalAnimation`
6.  **Verify:** Confirm that the caption text is correctly positioned below the graph.

### 2.2. Stable Production Path (Current Recommendation)

The guaranteed method for a perfect render is to use the stable, long-term support versions of the dependencies.

* **Python Version:** **`3.11.x`**
* **Manim Version:** **`v0.18.1`**

---

## 3. Getting Started (Stable Path)

### 3.1. Step 1: Create an Isolated Environment
```bash
# Navigate to the project directory and create a virtual environment with Python 3.11
python -m venv manim_venv_stable
# Activate it
.\manim_venv_stable\Scripts\activate
```
````

### 3.2. Step 2: Install Dependencies

```bash
pip install manim==0.18.1 manim-voiceover
```

### 3.3. Step 3: Run Automated Setup

This downloads the Piper TTS engine and FFmpeg.

```bash
setup_piper.bat
```

### 3.4. Step 4: Render the Animation

Ensure any `manim.cfg` file is **deleted** for this version. Configuration is handled by the script.

```bash
manim -pql FinalAnimation.py FinalAnimation
```

-----

## 4\. Project Structure & File Descriptions

The project is organized into a modular structure for better readability and maintenance.

```
.
├── config.py                # Contains all configuration variables, palettes, and narration text.
├── utils.py                 # Contains helper functions and the PiperService class.
├── FinalAnimation.py        # The main Manim scene, containing the core animation logic.
├── setup_piper.bat          # Windows batch script to automate dependency downloads.
...
```

  - **`config.py`**: Centralizes all project settings, including Manim configurations for `v0.18.1`, color palettes, and voiceover text.
  - **`utils.py`**: A collection of utility functions and classes, including the `PiperService` class for TTS management.
  - **`FinalAnimation.py`**: The main entry point, containing the scene's animation logic. It now uses hard-coded coordinates for text positioning to ensure stability across different Manim versions.
  - **`setup_piper.bat`**: A Windows batch script to automate the download of the Piper TTS engine and FFmpeg, making the setup process self-contained.

```
```