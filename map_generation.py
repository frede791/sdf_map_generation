## This file will be used to auto generate maps using blender

# Deliverables:
# 1. Using blender API to generate stl file for maps - Delivered
# 2. Position default map correctly in world (correct elevation) and generate correct world file - Delivered
# 3. Dynamic expansion of world at runtime. (This is a stretch goal)

import bpy
import requests
import argparse
import os
import folium
import webbrowser
import math

def main():

    # os.system("BLENDER_EXTERN_DRACO_LIBRARY_PATH=/home/fremarkus/blender-4.0.2-linux-x64/4.0/python/lib/python3.10/site-packages/libextern_draco.so.")

    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Map creation using Blender')

    parser.add_argument('--blender_store', help='Path to blender storage directory', required=False, default="~/.blender_maps")
    parser.add_argument('--coordinates',nargs='+', help='Corner points of the map in order W, S, E, N', required=True)
    parser.add_argument('--data_type', help='Data type for map', required=False, default="osm")
    parser.add_argument('--google_api_key', help='Google Tiles API key', required=False)
    parser.add_argument('--lod', help='Level of detail for map', required=False, default="lod3")
    parser.add_argument('--name', help='Name of the world', required=True)
    parser.add_argument('--world_store', help='Path to world storage directory', required=False, default="~/.simulation-gazebo/worlds")

    args = parser.parse_args()
    args.coordinates = [float(elem) for elem in args.coordinates[0].split(',')]

    # Set up environment variables to look for models for simulation
    args.world_store = os.path.expanduser(args.world_store)
    blender_maps_storage  = os.path.expanduser(args.blender_store)


    # Generate file folder
    if not os.path.exists(f'{args.world_store}/{args.name}') or not os.path.exists(f'{args.world_store}/{args.name}/materials'):
        os.makedirs(f'{args.world_store}/{args.name}/materials')


    # Enable blosm addon
    bpy.ops.preferences.addon_install(overwrite=False, filepath="./blosm.zip")
    bpy.ops.preferences.addon_enable(module="blosm")


    bpy.context.preferences.addons["blosm"].preferences.googleMapsApiKey = args.google_api_key


    if os.path.exists(f'{blender_maps_storage}/{args.name}'):
        os.system(f'rm -rf {blender_maps_storage}/{args.name}')
    os.system(f'mkdir -p {blender_maps_storage}/{args.name}')
    bpy.context.preferences.addons["blosm"].preferences.dataDir = f'{blender_maps_storage}/{args.name}'

    # Specify coordinates of corner points
    bpy.context.scene.blosm.maxLat = args.coordinates[3]
    maxLat = bpy.context.scene.blosm.maxLat

    bpy.context.scene.blosm.minLat = args.coordinates[1]
    minLat = bpy.context.scene.blosm.minLat

    bpy.context.scene.blosm.maxLon = args.coordinates[2]
    maxLon = bpy.context.scene.blosm.maxLon

    bpy.context.scene.blosm.minLon = args.coordinates[0]
    minLon = bpy.context.scene.blosm.minLon


    bpy.context.scene.blosm.relativeToInitialImport = True
    bpy.context.scene.blosm.join3dTilesObjects = True
    bpy.context.scene.blosm.lodOf3dTiles = f'lod{args.lod}'

    # Set some osm-specific details
    if args.data_type == 'osm':
        bpy.context.scene.blosm.forests = False
        bpy.context.scene.blosm.vegetation = False
        bpy.context.scene.blosm.water = False
        bpy.context.scene.blosm.highways = False
        bpy.context.scene.blosm.osmServer = "vk maps"
        bpy.context.scene.blosm.terrainPrimitiveType = "triangle"
        bpy.context.scene.blosm.materialType = "fo"
        bpy.context.scene.blosm.defaultRoofShape = "gabled"


    # Replace materials with export ready materials
    bpy.context.scene.blosm.replaceMaterialsWith = 'export-ready'

    # Delete all default objects from blender (Camera, Cube, Light)
    default_objects = ['Camera', 'Cube', 'Light']
    for obj in default_objects:
        bpy.data.objects[obj].select_set(True)
    bpy.ops.object.delete()


    #If you are using osm, first import the terrain and then the buildings
    if args.data_type == 'osm':
        bpy.context.scene.blosm.dataType = 'terrain'
        bpy.ops.blosm.import_data()
        bpy.context.scene.blosm.dataType = 'osm'
        bpy.ops.blosm.import_data()

    else: # Google 3D Tiles
        bpy.context.scene.blosm.dataType = args.data_type
        bpy.ops.blosm.import_data()

    # Get max elevation of map
    # Also get corner points of map
    if args.data_type == 'osm':
        mesh = bpy.data.objects['Terrain'].data
    elif args.data_type == 'google-3d-tiles':
        mesh = bpy.data.objects['Google 3D Tiles'].data

    max_elev = float('-inf')

    # get outer perimeter of map and elevation
    for vert in mesh.vertices:
        if vert.co[2] > max_elev:
          max_elev = vert.co[2]

    # Add 15 meters to get safely above average osm building height.
    if args.data_type == 'osm':
        max_elev = max_elev + 15

    eps = 0.2
    # minLon = float('inf')
    # maxLon = float('-inf')
    # minLat = float('inf')
    # maxLat = float('-inf')
    # if abs(vert.co[2]) <= eps:
    #     if vert.co[0] < minLon:
    #         minLon = vert.co[0]
    #     if vert.co[0] > maxLon:
    #         maxLon = vert.co[0]
    #     if vert.co[1] < minLat:
    #         minLat = vert.co[1]
    #     if vert.co[1] > maxLat:
    #         maxLat = vert.co[1]

    # Now find the outer perimeter points of the map
    # north_bound_min = (float('inf'),maxLat)
    # north_bound_max = (float('-inf'),maxLat)
    # south_bound_min = (float('inf'),minLat)
    # south_bound_max = (float('-inf'),minLat)
    # east_bound_min = (maxLon,float('inf'))
    # east_bound_max = (maxLon,float('-inf'))
    # west_bound_min = (minLon,float('inf'))
    # west_bound_max = (minLon,float('-inf'))

    # for vert in mesh.vertices:
    #     if vert.co[0] == minLon:
    #         if vert.co[1] < west_bound_min[1]:
    #             west_bound_min = (minLon, vert.co[1])
    #         if vert.co[1] > west_bound_max[1]:
    #             west_bound_max = (minLon, vert.co[1])
    #     if vert.co[0] == maxLon:
    #         if vert.co[1] < east_bound_min[1]:
    #             east_bound_min = (maxLon, vert.co[1])
    #         if vert.co[1] > east_bound_max[1]:
    #             east_bound_max = (maxLon, vert.co[1])
    #     if vert.co[1] == minLat:
    #         if vert.co[0] < south_bound_min[0]:
    #             south_bound_min = (vert.co[0], minLat)
    #         if vert.co[0] > south_bound_max[0]:
    #             south_bound_max = (vert.co[0], minLat)
    #     if vert.co[1] == maxLat:
    #         if vert.co[0] < north_bound_min[0]:
    #             north_bound_min = (vert.co[0], maxLat)
    #         if vert.co[0] > north_bound_max[0]:
    #             north_bound_max = (vert.co[0], maxLat)

    # With these outer perimeter points, we can now try to find the inner perimeter points
    # top_left = (north_bound_min[0],west_bound_max[1])
    # top_right = (north_bound_max[0],east_bound_max[1])
    # bottom_left = (south_bound_min[0],west_bound_min[1])
    # bottom_right = (south_bound_max[0],east_bound_min[1])

    # Convert to lat/lon
    # r_earth = 6378000 #radius of earth in meters to the nearest kilometer

    # old_maxLat = args.coordinates[3]
    # old_minLat = args.coordinates[1]
    # old_maxLon = args.coordinates[2]
    # old_minLon = args.coordinates[0]

    # maxLat = old_maxLat + (maxLat/r_earth)*(180/math.pi)
    # minLat = old_minLat + (minLat/r_earth)*(180/math.pi)
    # maxLon = old_maxLon + ((maxLon/r_earth)*(180/math.pi))/math.cos(old_maxLat * math.pi/180)
    # minLon = old_minLon + ((minLon/r_earth)*(180/math.pi))/math.cos(old_minLat * math.pi/180)


    if args.data_type == 'google-3d-tiles':
        bpy.data.objects['Google 3D Tiles'].select_set(True)
        bpy.ops.blosm.replace_materials()


    # Save blender file
    bpy.ops.wm.save_mainfile(filepath=f'{blender_maps_storage}/{args.name}/{args.name}.blend')
    bpy.ops.file.unpack_all(method='USE_LOCAL')


    # Use bpy.ops.wm.collada_export https://docs.blender.org/api/current/bpy.ops.wm.html#bpy.ops.wm.collada_export
    bpy.ops.wm.collada_export(filepath=f'{blender_maps_storage}/{args.name}/{args.name}.dae', check_existing=False, export_mesh_type_selection="view", use_texture_copies=True)


    # Move images to correct folder
    if args.data_type == 'google-3d-tiles':
        os.system(f'cp {blender_maps_storage}/{args.name}/textures/* {args.world_store}/{args.name}/materials/ -r')
        # Saving .blend and .dae both create jpgs. Only keep the ones in the same folder as the .dae
        os.system(f'rm -rf {blender_maps_storage}/{args.name}/textures')

    os.system(f'cp {blender_maps_storage}/{args.name}/{args.name}.dae {args.world_store}/{args.name}/materials/ -r')



    # # Make request for altitude
    # if args.data_type == 'google-3d-tiles':
    # #     base_url = 'https://maps.googleapis.com/maps/api/elevation/json'
    # #     response = response = requests.get(f'{base_url}?locations={c_lat},{c_lon}&key={API_KEY}')
    #     # c_elevation = response.json()['results'][0]['elevation']
    #     pass
    # elif args.data_type == 'osm':
    #     c_elevation = 0

    # Generate correct sdf file
    os.system(f'cp ./world_template.sdf {args.world_store}/{args.name}/{args.name}.sdf')

    with open(f'{args.world_store}/{args.name}/{args.name}.sdf', 'r') as file:
        filedata = file.read()
        file.close()

    filedata = filedata.replace('#ELEVATION#', str(max_elev))
    filedata = filedata.replace('#NAME#', args.name)

    with open(f'{args.world_store}/{args.name}/{args.name}.sdf', 'w') as file:
        file.write(filedata)
        file.close()


    # Test run generating existing maps
    # if os.path.exists(f'~/Documents/map_storage/{args.lod}_{minLon}_{minLat}_{maxLon}_{maxLat}_{args.name}'):
    #     os.system(f'rm -rf ~/Documents/map_storage/{args.lod}_{minLon}_{minLat}_{maxLon}_{maxLat}_{args.name}')

    # os.system(f'mkdir -p ~/Documents/map_storage/{args.lod}_{minLon}_{minLat}_{maxLon}_{maxLat}_{args.name}')

    # os.system(f'cp -r {args.world_store}/{args.name}/materials/* ~/Documents/map_storage/{args.lod}_{minLon}_{minLat}_{maxLon}_{maxLat}_{args.name}')

    # #Run test image overlay.
    # world_map = folium.Map(location=[0, 0], zoom_start=2)

    # for directory in os.listdir(os.path.expanduser('~/Documents/map_storage')):
    #     print(directory)
    #     if not os.path.isdir(os.path.expanduser(f'~/Documents/map_storage/{directory}')):
    #         continue

    #     #Split the directory name to get the coordinates
    #     dir_split = directory.split('_')
    #     print(dir_split)
    #     lod = dir_split[0]
    #     top_left_corner = [dir_split[4], dir_split[1]]
    #     top_right_corner = [dir_split[4], dir_split[3]]
    #     bottom_left_corner = [dir_split[2], dir_split[1]]
    #     bottom_right_corner = [dir_split[2], dir_split[3]]
    #     polygon_coordinates = [
    #         (float(top_left_corner[0]), float(top_left_corner[1])),
    #         (float(top_right_corner[0]), float(top_right_corner[1])),
    #         (float(bottom_right_corner[0]), float(bottom_right_corner[1])),
    #         (float(bottom_left_corner[0]), float(bottom_left_corner[1])),
    #     ]

    #     #Set name
    #     label_name = ''
    #     for i in range(5, len(dir_split)):
    #         if i == len(dir_split) - 1:
    #             label_name += dir_split[i]
    #         else:
    #             label_name += dir_split[i] + '_'

    #     folium.Polygon(locations=polygon_coordinates,
    #                    color='red',
    #                    fill=True,
    #                    fill_color='rgba(255, 0, 0, 0.5)',
    #                    popup=folium.Popup(label_name, parse_html=True)).add_to(world_map)

    # html_file_path = "world_map_polygon.html"
    # world_map.save(html_file_path)

    # webbrowser.open("file://" + os.path.realpath(html_file_path))

    # In background, start creating tiles around current tile (figure out how these can fit together)

if __name__ == "__main__":
    main()
