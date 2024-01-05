# This script can be used to inject an execute function into the blosm addon, which allows you to run the replaceMaterial operator using the API.

inject_string = """
    def execute(self, context):
        addon = context.scene.blosm
        if addon.replaceMaterialsWith == "export-ready":
            self.replaceWithExportReadyMaterials(context)
        else: # if addon.replaceMaterialsWith == "custom":
            materialName = addon.replacementMaterial
            if not materialName:
                self.report({'ERROR'}, "Material for the replacement is not set!")
                return {'CANCELLED'}
            elif not materialName in bpy.data.materials:
                self.report({'ERROR'}, "Material name for the replacement is not correct!")
                return {'CANCELLED'}

            templateMaterial = bpy.data.materials[materialName]
            imageTextureNodeName = ''
            if templateMaterial.use_nodes and templateMaterial.node_tree.nodes:
                # # check if there is an Image Texture node with the label "BASE COLOR"
                for node in templateMaterial.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.label == "BASE COLOR":
                        imageTextureNodeName = node.name
                        break
            self.replaceMaterialsWithTemplate(templateMaterial, imageTextureNodeName, context)

        return {'FINISHED'}
"""

def main():

    line_number = 282

    with(open("/work/blosm/gui/__init__.py", "r")) as f:
        lines = f.readlines()

    lines.insert(line_number - 1, inject_string)

    with(open("/work/blosm/gui/__init__.py", "w")) as f:
        f.writelines(lines)


if __name__ == "__main__":
    main()
