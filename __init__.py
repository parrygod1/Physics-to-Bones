#  Copyright (c) 2019 Andrei Tudor Paraschiv gparaschiv@gmail.com
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Physics to Bones",
    "description": "Converts rigid body simulation to bone animation.",
    "author": "parrygod",
    "version": (1, 0, 1),
    "blender": (2, 80, 0),
    "location": "View3D -> Object -> Quick Effects | Quick Action Menu",
    "wiki_url": "https://github.com/parrygod1/Physics-to-Bones",
    "category": "Object"
    }


import bpy   
from . import ptb

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       )


def main(self, context):
    ptb.init()
    objectList = []
    
    if self.selected_objects_only == False:
        objectList = [obj for obj in bpy.context.collection.objects if ptb.checkIfValidType(obj, 'MESH')]
    else:
        objectList = bpy.context.selected_objects
    
    if self.create_backup == True:
        ptb.createBackupCollection(objectList)
          
    if self.merge_objects == True:
        ptb.setOriginToGeom(objectList)
    
    currentArmature = ptb.createArmature()
    armData = currentArmature.data
    
    bpy.context.scene.frame_set(self.FRAMESTART)
    #important: current frame has to be set to the start otherwise the bones won't be placed correctly
    
    for obj in objectList:
        boneName = 'bone_' + obj.name
        
        ptb.addVertGroup(obj, boneName, 1)
        obj.parent = currentArmature
        
        ptb.createBone(currentArmature, boneName)
        ptb.moveBoneToObject(armData.edit_bones[boneName], self.BONESIZE, obj)
        armData.edit_bones[boneName].parent = armData.edit_bones['rootTransform']
    
        ptb.addBoneConstraints(currentArmature, boneName, obj)
    
    
    if self.bake_animations == True:
        bpy.ops.nla.bake(frame_start = self.FRAMESTART, 
                        frame_end = self.FRAMEEND, 
                        step = self.STEP, 
                        only_selected=True, visual_keying=True, 
                        clear_constraints=True, clear_parents=False, 
                        use_current_action=False, bake_types={'POSE'})
                            
    ptb.returnToObjectMode()
    ptb.removeAnimData(objectList)
    
    if self.merge_objects == True and len(objectList) > 1:
        ptb.joinObjectsInList(objectList)
        ptb.setOriginToObject(currentArmature)
        if bpy.context.object.rigid_body is not None:
            bpy.ops.rigidbody.object_remove()
        ptb.addArmatureModifier(currentArmature)
    else: #a loop is needed since the objects are not merged 
        ptb.addArmatureAndRemovePhys(objectList,currentArmature)

    self.report({'INFO'}, 'PhysicsToBones: Finished; Processed ' + str(len(objectList)) + ' objects')
    
class PhysicsToBones(bpy.types.Operator):
    bl_idname = "object.physicstobones"
    bl_label = "Physics to Bones"
    bl_description = "Converts rigid body animation to bones"
    bl_options = {'REGISTER', 'UNDO'}
    
    create_backup: BoolProperty(
        name = 'Create backup',
        description = 'Create a new collection with duplicated objects',
        default = True
        )   
    
    merge_objects: BoolProperty(
        name = 'Merge objects',
        description = 'Merge objects after all operations',
        default = True
        )

    selected_objects_only: BoolProperty(
        name = 'Selected objects only',
        description = 'If unselected it will use the whole collection',
        default = False
        )
        
    bake_animations: BoolProperty(
        name = 'Bake animations',
        description = 'Bake animations for bones. Disable to only add the bones',
        default = True
        )
        
    FRAMESTART: IntProperty(
        name = 'Start',
        description = '',
        default = 1,
        min = 0,
        max = 10000
        )
        
    FRAMEEND: IntProperty(
        name = 'End',
        description = '',
        default = 250,
        min = 0,
        max = 10000
        )
        
    STEP: IntProperty(
        name = 'Step',
        description = '',
        default = 1,
        min = 1,
        max = 10000
        )
    
    BONESIZE: FloatProperty(
        name = 'Bone Size',
        description = 'Length of the bone',
        default = 3,
        min = 0.1,
        max = 10000
        )
        
    def execute(self, context):
        main(self, context)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)
        
    def draw(self, context):
        layout = self.layout
        
        split = layout.split()
        
        row = layout.row()
        row.prop(self, 'create_backup')
        
        row = layout.row()
        row.prop(self, 'selected_objects_only')
                
        row = layout.row()
        row.prop(self, 'merge_objects')
        
        row = layout.row()
        row.prop(self, 'bake_animations')
        
        row = layout.row()
        row.label(text = ' Animation length (frames):')
        
        row = layout.row()
        row.prop(self, 'FRAMESTART')
        row.prop(self, 'FRAMEEND')
        row.prop(self, 'STEP')
        
        row = layout.row()
        row.label(text = ' Bone options:')
        row = layout.row()
        row.prop(self, 'BONESIZE')
        

def menu_func(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("object.physicstobones", text="Physics to Bones")

classes = (
    PhysicsToBones,
)
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.VIEW3D_MT_object_quick_effects.append(menu_func)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls) 
    bpy.types.VIEW3D_MT_object_quick_effects.remove(menu_func)

if __name__ == '__main__':
    register()