## USAGE ##

This repo can be used to automatically generate maps for Gazebo Sim. It currently supports Google 3D tiles (with an appropriate API key) and OSM tiles.

## Requirements ##

The only required package is Blender's python package which can be installed with:

```shell
pip install bpy
```

### Note on loading speed ###

Depending on the size and fidelity of the map, binary installed Gazebo Garden may take a long time to open the map. As such it may be advisable to install Gazebo from source as shown [here](https://gazebosim.org/docs/harmonic/install_ubuntu_src). Ensure that you run colcon build with Release Mode. On top of that is the need to modify the Collada Loader which can be found in `src/gz-common/` within the gz-garden source install. There is currently (15.02.24) a PR to improve the [Loader](https://github.com/gazebosim/gz-common/pull/569) and get this merged upstream, but for the time being, it is necessary to checkout this particular branch of gz-common and build gz-garden with that. It will significantly accelerate loading times into Gazebo.

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

## Running your world in Gazebo Sim ##

Running your new world in Gazebo can be achieved either through the simulation-gazebo package (may not work depending on package version in which case it may be advisable to check out the source code in the Github repo under Auterion/simulation-gazebo) or directly through the commandline:

```shell
GZ_SIM_RESOURCE_PATH=~/.simulation-gazebo/worlds:~/.simulation-gazebo/models GZ_PARTITION=virtual_skynode_relay GZ_IP=10.41.200.1 gz sim -r ~/.simulation-gazebo/worlds/MYWORLD/MYWORLD.sdf
```

`GZ_SIM_RESOURCE_PATH` sets the gazebo resource path to the source directory of your model (should be identical with the `world_store` argument above). `GZ_PARTITION` and `GZ_IP` set environmental variables required to connect your simulation to the virtual skynode. If you are not planning on using a virtual skynode, or have a different setup, adjust them to your liking. `MYWORLD` is the name of your world that you provided in the map generation.

## Other branches ##

There are also two experimental branches called "dynamic_tile_rendering" and "multi_drone_support". These provide tile rendering and multi-drone support features but are less stable that then main branch and may contain code-breaking bugs. Multi-drone builds on top of dynamic tile rendering and allows the user to spawn multiple drone simultaneously and have each one spawn their own set of tiles around them, irregardless of the direction that they fly in.

## Current issues ##

One bug that persists is the existence of libextern_draco.so not being found. I have placed the shared object file in the necessary location and it seems to work. I believe the issue is related to having both the blender desktop app installed and the bpy package.

## Future work ##

- While the main branch can be used and is (mostly) stable, it should still be polished and tested before release. Instead of providing a service where people can generate their own maps, it could also be an option to provide only a selection of maps to customers.
- When using dynamic tile rendering, one bug that still needs to be figured out is the difference in elevation between different tiles. I have not yet managed to ensure that they are perfectly aligned at all times.
- Fixing the elevation with relation to the drone is still necessary. Placing the drone at 0 elevation in the world may lead to the drone spawning inside of buildings or other objects and thus necessitates moving upwards. Having this upwards move also be registered in PX4 may require some additional tinkering. The way this is done at the moment is to set a platform at 0 elevation and move the map's elevation down by its highest point.
- Collision models for these new maps need to be added. At the moment, there is only the starting plattform that has collisions enabled. This appears to be a bug with gazebo's dartsim physics engine.
