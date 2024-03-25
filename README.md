# Parcel-Sorting-and-Numbering Script Tool
![main](https://github.com/Eng-Moka/Parcel-Sorting-and-Numbering/assets/132586649/9fb84a7a-876b-4696-af25-d67f70a33e62)

This Python script provides a set of tools for managing feature layers within ArcGIS using ArcPy.
It includes functionalities for sorting features based on their coordinates, updating numbering fields,
and processing selected features within a geodatabase.

## Features

- **Get GDB Path of Layer**: Retrieve the file path of the geodatabase (GDB) containing a specified layer within the current ArcGIS Pro project.
- **Get Selected Features Dictionary**: Obtain a dictionary containing selected features and their centroid coordinates from a given feature class.
- **Update Numbering Field**: Update a specified numbering field for a set of features based on their unique identifiers.
- **Sort Features by Coordinate**: Sort a dictionary of features by their coordinate values in either the 'x' or 'y' direction, with options for customizing sorting direction and starting numbering count.

## Usage

1. Ensure that ArcGIS Pro is installed and the script is run within an active ArcGIS Pro project.
2. Add the script toolbox (Numbering.atbx) to the ArcGIS Pro project or run it from the Python Console.
![0](https://github.com/Eng-Moka/Parcel-Sorting-and-Numbering/assets/132586649/04a92be6-3b52-4735-9efc-1d1371c964e8)

3. Provide input parameters such as the feature class, unique identifier field, start count for numbering, numbering field, and sorting direction.
![1](https://github.com/Eng-Moka/Parcel-Sorting-and-Numbering/assets/132586649/fa06389d-9a4f-4604-8c42-b3c18a4b1f97)

4. Execute the script to perform feature management tasks within the specified geodatabase.
![2](https://github.com/Eng-Moka/Parcel-Sorting-and-Numbering/assets/132586649/867a879a-9cdb-414c-9072-59ec8796a269)

## Requirements

- ArcGIS Pro
- Python (included with ArcGIS Pro installation)

## Usage Example

```python
# Example usage within ArcGIS Pro Python Console
parcels_fc = "path/to/parcels_feature_class"
unique_id_field = "Parcel_ID"
start_count = 1
numbering_field = "Parcel_Number"
direction = "Left to Right"

sorting_and_numbering(parcels_fc, unique_id_field, start_count, numbering_field, direction)
