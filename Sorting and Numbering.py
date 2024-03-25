import arcpy
import os

def get_gdb_path_of_layer(layer_name):
    """
    This function retrieves the filepath of the geodatabase (GDB) where a specified layer is located.

    Args:
        layer_name (str): The name of the target layer.

    Returns:
        str: The full filepath of the GDB containing the layer.

    Note:
        The function assumes that the map document containing the layer is already open in the current ArcGIS Pro project.
    """
    # Initialize the ArcGISProject object with the "CURRENT" keyword to reference
    # the active ArcGIS project.
    aprx = arcpy.mp.ArcGISProject("CURRENT")

    # Access the active map/layer within the project.
    map_obj = aprx.activeMap

    # Iterate through the layers of the active map, and find the desired layer
    # by matching the input `layer_name` with the layer's name.
    layer_obj = [layer for layer in map_obj.listLayers() if layer.name == layer_name][0]

    # Check if the layer_obj is defined and is a feature layer.
    if layer_obj and layer_obj.isFeatureLayer:

        # Extract the layer's data source path and return it.
        return os.path.dirname(layer_obj.dataSource)

    # In case the layer is not a feature layer or not found, the function returns None.
    else:
        return None


def get_selected_features_dictionary(feature_class, unique_id_field):
    """
    # Function to get a dictionary containing the selected features and their centroid
    # coordinates from the given feature class.
    #
    # Parameters:
    #   feature_class (str): The path of the feature class to get the selected features.
    #   unique_id_field (str): The name of the unique identifier field for each feature.
    #
    # Returns:
    #   dict: A dictionary containing the unique_id_field values as keys and the
    #         centroid coordinates as values.
    """
    selected_features = arcpy.analysis.Select(feature_class)
    feature_dict = {}
    # Populate the dictionary with unique_id_field and centroid coordinates `{'x': x, 'y': y}`
    with arcpy.da.SearchCursor(selected_features, [unique_id_field, 'SHAPE@']) as cursor:
        for key, geo in cursor:
            # Get centroid coordinates
            centroid = geo.centroid
            x, y = centroid.X, centroid.Y
            feature_dict[key] = {'x': x, 'y': y}
    # Delete the selection since the search cursor is used to avoid locking the dataset
    arcpy.management.Delete(selected_features)
    return feature_dict


def update_numbering_field(feature_class, dictionary, numbering_field, unique_id_field):
    """
    # Function to update the `numbering_field` for a given set of features based on their unique_id_field
    # -------------------------------------------------------------------------------------------------
    # Parameters:
    #   feature_class (str): The input feature class to update the `numbering_field`
    #   dictionary (dict): A dictionary containing the unique_id_field and corresponding new number for each feature
    #   numbering_field (str): The field name to update the new number
    #   unique_id_field (str): The name of the unique identifier field for each feature
    """
    try:
        # Create a set of unique ids for faster lookup
        unique_ids = set(dictionary.keys())
        # Iterate through the features and update the numbering field based on their unique identifier
        with arcpy.da.UpdateCursor(feature_class, [unique_id_field, numbering_field]) as cursor:
            for row in cursor:
                if row[0] in unique_ids:
                    # Update the numbering field based on the unique identifier
                    row[1] = dictionary[row[0]]['numbering']  
                    cursor.updateRow(row)
    except arcpy.ExecuteError as e:
        print(f"Error while updating the numbering field: {e}")


def sort_features_by_coordinate(feature_dict, direction='x', ascending=False, start_count=1):
    """
    # This function sorts a given dictionary of features by their coordinate values in either the 'x' or 'y' direction.
    # By default, the direction will be set to 'x'. The order in which the features are sorted can be specified
    # using the `ascending` parameter, which is set to 'False' by default. The coordinate key used in the feature
    # dictionary to be sorted is specified by the `direction` parameter.
    #
    # The `start_count` parameter marks the number at which the feature's numbering should start.
    #
    # The function returns the sorted dictionary of features with the 'numbering' key set to the corresponding
    # number in the sorted list.
    #
    # Example:
    #   input:  feature_dict = {'A': {'x': 2, 'y': 2}, 'B': {'x': 1, 'y': 1}, 'C': {'x': 4, 'y': 4}, 'D': {'x': 3, 'y': 3}},
    #           direction = 'x', ascending = True, start_count = 1:
    #   output: {'B': {'numbering': 1, 'x': 1, 'y': 1}, 'D': {'numbering': 2, 'x': 3, 'y': 3}, 'A': {'numbering': 3, 'x': 2, 'y': 2}, 'C': {'numbering': 4, 'x': 4, 'y': 4}}

    """
    sorted_feature_dict = dict(sorted(feature_dict.items(), key=lambda item: item[1][direction], reverse=(ascending == False)))
    for unique_id in sorted_feature_dict.keys():
        # Assign a new numbering for each feature based on the sort order
        sorted_feature_dict[unique_id]['numbering'] = start_count
        start_count += 1
    # Return the sorted feature dictionary
    return sorted_feature_dict


def main_script(parcels_fc, unique_id_field, start_count, numbering_field, direction, ascending):

    gdb_path = get_gdb_path_of_layer(parcels_fc)

    if not gdb_path:
        arcpy.AddError(f"The layer {parcels_fc} has no data source or Geodatabase.")
        return
    
    # Set the environment
    arcpy.env.workspace = gdb_path

    try:
        start_count = int(start_count)
    except ValueError:
        arcpy.AddError(f'Please enter a valid integer number: {start_count}')
        return

    feature_dict = get_selected_features_dictionary(parcels_fc, unique_id_field)

    sorted_feature_dict = sort_features_by_coordinate(feature_dict, direction=direction, ascending=ascending, start_count=start_count)

    # Determine field type
    fields = arcpy.ListFields(parcels_fc)
    field_obj = next((f for f in fields if f.name == numbering_field), None)
    if not field_obj:
        print(f"Field '{numbering_field}' not found in the feature class.")
        arcpy.AddError(f"Field '{numbering_field}' not found in the feature class.")
        return
    field_type = field_obj.type

    # Create the domain based on field type
    if field_type not in ['String', 'Date','Double','Integer','FLOAT','LONG','SHORT']:
        print(f"Invalid field type '{field_type}'.")
        arcpy.AddError(f"Invalid field type '{field_type}'.")
        return

    update_numbering_field(parcels_fc, sorted_feature_dict, numbering_field, unique_id_field)


if __name__ == '__main__':
    parcels_fc = arcpy.GetParameterAsText(0)  # Input
    unique_id_field = arcpy.GetParameterAsText(1)
    start_count = arcpy.GetParameterAsText(2)   # Input
    numbering_field = arcpy.GetParameterAsText(3)  # Input
    direction = arcpy.GetParameterAsText(4)   # Input

    if direction == 'Left to Right':
        direction, ascending = 'x', True
    elif direction == 'Right to Left':
        direction, ascending = 'x', False
    elif direction == 'Up to Down':
        direction, ascending = 'y', False
    elif direction == 'Down to Up':
        direction, ascending = 'y', True

    main_script(parcels_fc, unique_id_field, start_count, numbering_field, direction, ascending)
