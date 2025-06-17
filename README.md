# h3forge

A Python tool for processing geospatial data into H3 hexagonal grids. h3forge simplifies the workflow of downloading, processing, and aggregating geospatial data into the H3 spatial indexing system, making it easier to perform spatial analysis and visualization.

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
```

## 🛰️ Datasets

- **Sentinel-5P**
- **Sentinel 2 Level-2**
- **Global Human Settlements Layer (GHSL)**

## ⚙️ Installation

Clone the repo and install dependencies:

```bash
# Clone the repository
git clone https://github.com/jeronimoluza/h3forge.git
cd h3forge

# Install dependencies using Poetry
poetry install
```

## 🚀 Usage

h3forge provides a streamlined workflow for processing geospatial data into H3 hexagons.

```python
import h3forge

# 1. Define your region of interest (WKT format)
region = h3forge.utils.load_wkt(
    "POLYGON((-58.521952 -34.549793, -58.487812 -34.549793, -58.487812 -34.568679, -58.521952 -34.568679, -58.521952 -34.549793))"
)

# 2. Download satellite data (e.g., Sentinel-2 NDVI)
start_date = "2020-01-01"
end_date = "2020-01-20"
cloud_cover = 0.2

ndvi_array = h3forge.download.sentinel2.get_ndvi(
    region=region,
    start_date=start_date,
    end_date=end_date,
    cloud_cover=cloud_cover,
)

# 3. Vectorize the raster data
vectors = h3forge.preprocess.vectorize(ndvi_array, region=region)

# 4. Convert vectors to H3 hexagons
hexes = h3forge.features.vector_to_h3(vectors, region=region, resolution=13)

# 5. Aggregate to coarser resolution with time aggregation
h3_agg = h3forge.features.h3_aggregation(
    hexes, 
    region=region, 
    resolution=8,  # Target resolution 
    time_agg='yearly',  # Temporal aggregation (options: 'daily', 'monthly', 'yearly', None)
    strategy='mean'  # Aggregation strategy (options: 'mean', 'sum', 'min', 'max')
)
```
## 🧪 Testing

```bash
pytest tests/
```

## 📚 License

[MIT License](LICENSE)