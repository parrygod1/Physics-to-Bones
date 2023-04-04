# Physics to Bones 1.0.1
An addon for Blender 2.80 and higher versions that converts rigid body simulation to bone animation

How to install: Go into Blender -> Edit -> Preferences -> Add-ons -> Click install -> select object_physicstobones.zip

How to use: 
* Select a mesh that has rigid body enabled or an action attached to it
* Access the addon from Object mode -> Object -> Quick Effects -> Physics to Bones or from the action menu (F3)
* Adjust the options and click 'OK'
* The backup collection is called 'Backup_ptb'

Any animation/movement the object has will be converted to bone animation and the object will be parented to the armature. It works for normal objects too, not only rigid bodies, as long as they are a mesh.
It might take a while to finish if there are a lot of objects selected, because animation baking takes time. 

Known issues:
* After the script is finished, objects might disappear or appear in a random location. Once you play the animation it will be fine.

Changelog 1.0.2:
* Objects will be parented to the armature after the bake
