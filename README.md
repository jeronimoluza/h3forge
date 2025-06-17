# h3forge

This repository contains the data processing pipeline for a research project on environmental inequality. The goal is to understand how environmental factors like air pollution and vegetation are distributed across socio-economic regions in metropolitan areas.

## 🌎 Overview

The pipeline automates:

- Downloading remote sensing and socio-environmental datasets
- Processing raster datasets (NO₂, NDVI, GHSL, etc.)
- Converting raster data into vector formats and spatial features
- Aggregating features to H3 hexagons for spatial analysis

## 📁 Project Structure

```
h3forge/
├── data/                # Raw, processed, and external data
├── notebooks/           # Exploratory Jupyter Notebooks
├── h3forge/             # Core Python package
│   ├── download/        # Downloaders for datasets
│   ├── preprocess/      # Raster/vector transformations
│   ├── features/        # Hexagonal aggregation and spatial features
│   └── utils/           # Helper functions
├── scripts/             # End-to-end pipeline runners
├── tests/               # Unit tests
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
````

## 🛰️ Datasets Used

- **Sentinel-5P NO₂** (Copernicus)
- **Sentinel 2 L2 NDVI**
- **GHSL Population Density**
- Socioeconomic data (to be integrated)

## ⚙️ Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/jeronimoluza/h3forge.git
cd h3forge
pip install -r requirements.txt
````

You may also want to install geospatial dependencies via conda:

```bash
conda create -n h3forge python=3.11 geopandas rasterio h3-py
conda activate h3forge
pip install -r requirements.txt
```

## 🚀 Usage

Run individual modules or use the included scripts to run an end-to-end pipeline. For exploration and documentation, refer to the `notebooks/` folder.

Example:

```bash
python scripts/run_pipeline.py
```

## 🧪 Testing

```bash
pytest tests/
```

## 📖 Notebooks

* `01_download_sources.ipynb`: Download and inspect datasets
* `02_transform_rasters.ipynb`: Raster-to-vector processing
* `03_hex_aggregation.ipynb`: Aggregation to H3 for analysis

## 📚 License

[MIT License](LICENSE)

---

### 📬 Contact

For questions or collaborations, reach out to [jero.luza@gmail.com](mailto:jero.luza@gmail.com).
