## USAGE ##
This repo can be used to automatically generate maps for Gazebo Sim. It currently supports Google 3D tiles (with an appropriate API key) and OSM tiles.

## GET STARTED ##

You can start map_generation by running either the python command below, the provided Dockerfile or the Github actions workflow which can be manually triggered in the Auterion/sdf-map-generation repo.

```python
python3 map_generation.py [ARGS]
```

The arguments that can be passed are as follows:

- `blender_store` This sets the director where the blender files are stored. The default is `~/.blender_maps`
- `coordinates` This argument defines the boundaries of the map that is to be generated. It should be provided as a comma separated list of 4 values with the order: minimum_longitude, minimum_latitude, maximum_longitude, maximum_latitude. An example would be 7.70,45.09,7.71,45.1. This argument is not required but should be provided if the map doesn't already exist.
- `data_type` The type of data that is used to generate the maps. The currently supported types are: "google-3d-tiles", "osm".
- `google_api_key` When running google-3d-tiles, this API key is necessary in order to be able to make API requests.
- `lod` This argument specifies the level of detail when running Google 3D tiles. Allowed values are 1 to 6 with 1 being essentially a 2D terrain map of the region and 6 being highest fidelity, rendering individual trees and cars. Default is set at 3.
- `name` The name that your world should have. This argument is required.
- `world_store` This is the place where your finalized sdf files and associated .dae and imagery will be stored. Per default this is set to `~/.simulation-gazebo`. (In actual fact the maps will be stored in `world_store/worlds`).
