# Copyright (c) 2021 赤目ボトル(Akame Bottle).
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php

import bpy
import os
import glob
import re

bl_info = {
        "name" = "Auto Naming Screenshot",
        "author" = "Akame Bottle",
        "version" = (0,1,0),
        "blender" = (2,79,0),
        "location" = "Properties -> Render -> Auto Naming Screenshot",
        "description" = "スクリーンショットを指定したディレクトリに連番ファイル名で保存します",
        "warning" = "",
        "wiki_url" = "https://github.com/akame-bottle/auto-naming-screenshot/wiki",
        "tracker_url",
        "category" = "Render"
}


class ANSS_PG_Properties(bpy.types.PropertyGroup):
    def path_check(self, context):
        abs_path = bpy.path.abspath(self.dirpath)
        path_ok = os.path.exists(abs_path)
        
    dirpath =     bpy.props.StringProperty(subtype="DIR_PATH", default="//", description="デフォルトはDesktop", update=path_check)
    filename =    bpy.props.StringProperty(subtype="FILE_NAME", default="#.png", description="#を連番に変換")
    full_screen = bpy.props.BoolProperty(default = False)
    path_ok =     bpy.props.BoolProperty(default = True)


class ANSS_OT_Screenshot(bpy.types.Operator):
    bl_idname = "scene.auto_naming_screenshot"
    bl_label = "Save Screenshot"
    
    def execute(self, context):
        props = context.scene.ANSS_props
        
        if not props.path_ok:
            return {'CANCELLED'}
        dir = bpy.path.abspath(props.dirpath)
        
        # file number check
        num = r"\d+"
        sharp = r"#+"
        filename = props.filename + (".png" if os.path.splitext(props.filename)[1] == '' else "")
        target_pattern = re.sub(sharp, r"*", filename)
        file_number = 0
            
        def get_num(name):
            result = re.search(num, name)
            return int(result.group()) if result else 0
        if glob.glob(os.path.join(dir, target_pattern)):
            result = max([f for f in glob.glob(os.path.join(dir, target_pattern))], key=get_num)
            fn = re.search(num, result)
            if fn:
                file_number = int(fn.group())
        
        # merge path
        replaced_filename = re.sub(sharp, str(int(file_number) + 1), filename)
        comp_path = os.path.join(props.dirpath, replaced_filename)
        
        bpy.ops.screen.screenshot(filepath=comp_path, full=props.full_screen)
        
        self.report({'INFO'}, "Save Screenshot! " + comp_path)
        return {'FINISHED'}

class ANSS_PT_Properties(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Auto Naming Screenshot"
    bl_idname = "ANSS_PT_auto_naming_screenshot"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # Auto Naming Screenshot
        row = layout.row()
        row.operator("scene.auto_naming_screenshot")
        
        props = scene.ANSS_props
        row = layout.row()
        row.prop(props, "dirpath", text="")
        if not props.path_ok:
            layout.label(text="Invalid Path", icon="ERROR")
        row = layout.row()
        row.prop(props, "filename", text="File Name")
        row = layout.row()
        row.prop(props, "full_screen", text="Full Screen")

classes = [
    ANSS_PG_Properties,
    ANSS_OT_Screenshot,
    ANSS_PT_Properties
]

addon_keymaps = []

def register_shortcut():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Auto Naming Screenshot", space_type="PROPERTIES")
        # ショートカットキーの登録
        kmi = km.keymap_items.new(
            idname=ANSS_OT_Screenshot.bl_idname,
            type="F3",
            value="PRESS",
            shift=False,
            ctrl=True,
            alt=True
        )
        # ショートカットキー一覧に登録
        addon_keymaps.append((km, kmi))


def unregister_shortcut():
    for km, kmi in addon_keymaps:
        # ショートカットキーの登録解除
        km.keymap_items.remove(kmi)
    # ショートカットキー一覧をクリア
    addon_keymaps.clear()

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.ANSS_props = bpy.props.PointerProperty(type=ANSS_PG_Properties)
    register_shortcut()

def unregister():
    unregister_shortcut()
    for cls in sclasses:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.ANSS_props

# if __name__ == "__main__":
#     register()
