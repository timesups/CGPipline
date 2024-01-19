#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
# version: 3.9.7
##################################################################
import unreal

# NOTE 获取主菜单
menus = unreal.ToolMenus.get()

# NOTE 获取主界面的主菜单位置
main_menu = menus.find_menu("LevelEditor.MainMenu")
if not main_menu:
    raise RuntimeError(
        "Failed to find the 'Main' menu. Something is wrong in the force!")

# NOTE 添加一个下拉菜单
script_menu = main_menu.add_sub_menu(main_menu.get_name(), "PythonTools", "ToolsN", "UE工具集新")

entry = unreal.ToolMenuEntry(
            name="showCameraImporter",
            type=unreal.MultiBlockType.MENU_ENTRY,
            insert_position=unreal.ToolMenuInsert(
                "", unreal.ToolMenuInsertType.FIRST)
        )
entry.set_label("相机导入工具")
entry.set_tool_tip("打开相机导入窗口")
entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, "", "import ShowWindow\nShowWindow.showCameraImporter()")
script_menu.add_menu_entry("Test Section",entry)


entry = unreal.ToolMenuEntry(
            name="showStaticMeshImporter",
            type=unreal.MultiBlockType.MENU_ENTRY,
            insert_position=unreal.ToolMenuInsert(
                "", unreal.ToolMenuInsertType.FIRST)
        )
entry.set_label("静态网格体导入")
entry.set_tool_tip("打开静态网格体导入窗口")
entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, "", "import ShowWindow\nShowWindow.showStaticMeshImporter()")
script_menu.add_menu_entry("Test Section",entry)

entry = unreal.ToolMenuEntry(
            name="showLevelDesignTool",
            type=unreal.MultiBlockType.MENU_ENTRY,
            insert_position=unreal.ToolMenuInsert(
                "", unreal.ToolMenuInsertType.FIRST)
        )
entry.set_label("地编常用工具")
entry.set_tool_tip("打开地编常用工具窗口")
entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, "", "import ShowWindow\nShowWindow.showLevelDesignTool()")
script_menu.add_menu_entry("Test Section",entry)


entry = unreal.ToolMenuEntry(
            name="showLightTools",
            type=unreal.MultiBlockType.MENU_ENTRY,
            insert_position=unreal.ToolMenuInsert(
                "", unreal.ToolMenuInsertType.FIRST)
        )
entry.set_label("灯光常用工具")
entry.set_tool_tip("打开灯光常用工具")
entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, "", "import ShowWindow\nShowWindow.showLightTools()")
script_menu.add_menu_entry("Test Section",entry)


menus.refresh_all_widgets()

import uCommon as UC
global Application
Application = UC.getApplication()
