import bpy
import requests
import argparse
import os

def main():

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

    #Check that if coordinates are not set, the name directory already exists.
    if not args.coordinates:
        if not os.path.exists(f'{args.world_store}/worlds/{args.name}/{args.name}.sdf'):
            if args.data_type == 'google-3d-tiles' and not os.path.exists(f'{args.world_store}/worlds/{args.name}/materials/{args.name}.dae'):
                print("No coordinates set and world directory is not completely defined. Exiting...")
                exit(0)
    else:
        args.coordinates = [float(elem) for elem in args.coordinates[0].split(',')]

    # Set up environment variables to look for models for simulation
    args.world_store = os.path.expanduser(args.world_store)
    blender_maps_storage  = os.path.expanduser(args.blender_store)

    # If the file with the correct name already exists and the dae file exists as well (when running google-3d-tiles) then don't run the generation.
    if os.path.exists(f'{args.world_store}/worlds/{args.name}/{args.name}.sdf') or (args.data_type =='google-3d-tiles' and os.path.exists(f'{args.world_store}/worlds/{args.name}/materials/{args.name}.dae')):
        print(f'A world with the name {args.name} already exists. Exiting...')
        exit(0)

    # Generate file folder
    if not os.path.exists(f'{args.world_store}/worlds/{args.name}') or not os.path.exists(f'{args.world_store}/worlds/{args.name}/materials'):
        os.makedirs(f'{args.world_store}/worlds/{args.name}/materials')

    # Enable blosm addon
    bpy.ops.preferences.addon_install(overwrite=True, filepath="./blosm.zip")
    bpy.ops.preferences.addon_enable(module="blosm")

    bpy.context.preferences.addons["blosm"].preferences.googleMapsApiKey = args.google_api_key

    # Clean up old blender maps
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

    # Set center point of map
    c_lat = (maxLat + minLat)/2
    c_lon = (maxLon + minLon)/2

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

    if args.data_type == 'google-3d-tiles':
        bpy.data.objects['Google 3D Tiles'].select_set(True)
        bpy.ops.blosm.replace_materials()

    # Save blender file
    if args.data_type == 'google-3d-tiles':
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

    # # Make request for global elevation
    if args.data_type == 'google-3d-tiles':
        base_url = 'https://maps.googleapis.com/maps/api/elevation/json'
        response = response = requests.get(f'{base_url}?locations={c_lat},{c_lon}&key={args.google_api_key}')
        c_elevation = response.json()['results'][0]['elevation']
        pass
    elif args.data_type == 'osm':
        c_elevation = 0

    # Generate sdf file with placeholders replaced
    os.system(f'cp ./world_template.sdf {args.world_store}/{args.name}/{args.name}.sdf')

    with open(f'{args.world_store}/{args.name}/{args.name}.sdf', 'r') as file:
        filedata = file.read()
        file.close()

    filedata = filedata.replace('#NEG_ELEVATION#', str(-max_elev))
    filedata = filedata.replace('#NAME#', args.name)
    filedata = filedata.replace('#GLOB_ELEVATION#', str(c_elevation))
    filedata = filedata.replace('#LATITUDE#', str(c_lat))
    filedata = filedata.replace('#LONGITUDE#', str(c_lon))
    # filedata = filedata.replace('#ELEVATION#', str(max_elev))
    # filedata = filedata.replace('#CAM_ELEVATION#', str(max_elev + 5))

    with open(f'{args.world_store}/{args.name}/{args.name}.sdf', 'w') as file:
        file.write(filedata)
        file.close()

if __name__ == "__main__":
    main()
