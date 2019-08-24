import bpy, mathutils

def returnToObjectMode():
    bpy.ops.object.mode_set(mode='OBJECT')

def init():
    if bpy.context.view_layer.objects.active is None:
        raise Exception('No active object in scene. Select an object.')
        
    if bpy.context.collection !=  bpy.context.view_layer.objects.active.users_collection[0]:
        raise Exception("Selected collection '%s' is not the same as the selected object's collection '%s'. Select the active object's collection or move it to the other collection."
                       % (bpy.context.collection.name, bpy.context.view_layer.objects.active.users_collection[0].name))
        #without this check the script will pick the other collection if 'selected objects only' is not set
    
    returnToObjectMode()
    bpy.context.scene.cursor.location = (0.0,0.0,0.0)
    
def checkIfValidType(object, desired_type):
    if(object.type != desired_type):
        raise TypeError("Object '%s' is not a %s" % (object.name, desired_type))
    return True
        
def setOriginToObject(object):
    bpy.context.scene.cursor.location = object.location
    bpy.ops.object.origin_set(type = 'ORIGIN_CURSOR')

def createArmature():
    bpy.ops.object.armature_add()
    armature = bpy.context.object
    armature.pose.bones.get('Bone').name = 'rootTransform'
    return armature

def addVertGroup(object, grp_name, vert_weight):
    vgrp = object.vertex_groups.new(name = grp_name)
    vertices= [e for e in object.data.vertices]
    for vert in vertices:
            vgrp.add([vert.index], vert_weight, "ADD")     
    
def createBone(armature, bone_name):
    bpy.ops.object.mode_set(mode='EDIT')
    armature.data.edit_bones.new(bone_name)
    
def moveBoneToObject(bone, bsize, object): #bone from armature.data.edit_bones[...]
    bone.select = True
    bone.head = object.location
    bone.tail = object.location + mathutils.Vector((0.0,0.0, bsize)) #size on Z to point upwards
    
def addBoneConstraints(armature, bone_name, object):
    bpy.ops.object.mode_set(mode='POSE')
    bone = armature.pose.bones[bone_name]
    constraint1 = bone.constraints.new('COPY_LOCATION')
    constraint1.target = object
    constraint2 = bone.constraints.new('COPY_ROTATION')
    constraint2.target = object
    constraint2.use_offset = True

def selectObjectsInList(object_list):
    for obj in object_list:
        obj.select_set(True)

def joinObjectsInList(object_list):
    bpy.context.view_layer.objects.active = object_list[0]
    selectObjectsInList(object_list)
    bpy.ops.object.join()
    
def addArmatureModifier(armature):
    bpy.ops.object.modifier_add(type='ARMATURE')
    bpy.context.object.modifiers["Armature"].object = armature

def addArmatureAndRemovePhys(object_list, armature):
    for obj in object_list:
        bpy.context.view_layer.objects.active = obj
        addArmatureModifier(armature)
        if obj.rigid_body is not None:
            bpy.ops.rigidbody.object_remove()

def setOriginToGeom(object_list):
    selectObjectsInList(object_list)
    bpy.context.view_layer.objects.active = object_list[0]
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = None
    
def separateMesh(object):
    bpy.context.view_layer.objects.active = object
    object.select_set(True)
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.context.view_layer.objects.active = None
    object.select_set(False)

def separateMeshesInList(object_list):
    for obj in object_list:
        obj.select_set(True)
        separateMesh(obj)
        object_list.append(bpy.context.selected_objects)

def removeRigidBodies(object_list):
    for obj in object_list:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.rigidbody.object_remove()
        
def removeAnimData(object_list):
    for obj in object_list:
        obj.animation_data_clear()
        
def createBackupCollection(object_list):
    bpy.data.collections.new('Backup_ptb')
    for obj in object_list:
        bpy.context.view_layer.objects.active = obj
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        bpy.data.collections['Backup_ptb'].objects.link(new_obj)
    bpy.context.scene.collection.children.link(bpy.data.collections['Backup_ptb'])
    bpy.context.view_layer.objects.active = None
    print('PhysicsToBones: Created backup for ' + bpy.context.collection.name)