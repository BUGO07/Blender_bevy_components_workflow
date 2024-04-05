import bpy
import os 
import json
import pytest
import shutil

@pytest.fixture
def setup_data(request):
    print("\nSetting up resources...")

    def finalizer():
        root_path =  "../../testing/bevy_example"
        assets_root_path = os.path.join(root_path, "assets")
        models_path =  os.path.join(assets_root_path, "models")
        materials_path = os.path.join(assets_root_path, "materials")
        #other_materials_path = os.path.join("../../testing", "other_materials")

        print("\nPerforming teardown...")
        if os.path.exists(models_path):
            shutil.rmtree(models_path)

        if os.path.exists(materials_path):
            shutil.rmtree(materials_path)

        diagnostics_file_path = os.path.join(root_path, "bevy_diagnostics.json")
        if os.path.exists(diagnostics_file_path):
            os.remove(diagnostics_file_path)
        
        hierarchy_file_path = os.path.join(root_path, "bevy_hierarchy.json")
        if os.path.exists(hierarchy_file_path):
            os.remove(hierarchy_file_path)

        screenshot_observed_path = os.path.join(root_path, "screenshot.png")
        if os.path.exists(screenshot_observed_path):
            os.remove(screenshot_observed_path)

    request.addfinalizer(finalizer)

    return None

import bpy
import os 
import json
import pytest
import shutil

@pytest.fixture
def setup_data(request):
    print("\nSetting up resources...")

    def finalizer():
        root_path =  "../../testing/bevy_example"
        assets_root_path = os.path.join(root_path, "assets")
        models_path =  os.path.join(assets_root_path, "models")
        materials_path = os.path.join(assets_root_path, "materials")
        #other_materials_path = os.path.join("../../testing", "other_materials")

        print("\nPerforming teardown...")
        if os.path.exists(models_path):
            shutil.rmtree(models_path)

        if os.path.exists(materials_path):
            shutil.rmtree(materials_path)

        diagnostics_file_path = os.path.join(root_path, "bevy_diagnostics.json")
        if os.path.exists(diagnostics_file_path):
            os.remove(diagnostics_file_path)
        
        hierarchy_file_path = os.path.join(root_path, "bevy_hierarchy.json")
        if os.path.exists(hierarchy_file_path):
            os.remove(hierarchy_file_path)

        screenshot_observed_path = os.path.join(root_path, "screenshot.png")
        if os.path.exists(screenshot_observed_path):
            os.remove(screenshot_observed_path)

    request.addfinalizer(finalizer)

    return None


"""
- setup gltf parameters & auto_export parameters
- calls exporter on the testing scene
- saves timestamps of generated files
- changes things in the main scene and/or library
- checks if timestamps have changed
- if all worked => test is a-ok
- removes generated files

"""
def test_export_changed_parameters(setup_data):
    root_path = "../../testing/bevy_example"
    assets_root_path = os.path.join(root_path, "assets")
    models_path = os.path.join(assets_root_path, "models")
    auto_export_operator = bpy.ops.export_scenes.auto_gltf

    # with change detection
    # first, configure things
    # we use the global settings for that
    export_props = {
        "main_scene_names" : ['World'],
        "library_scene_names": ['Library'],
    }
  
    # store settings for the auto_export part
    stored_auto_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_auto_settings.clear()
    stored_auto_settings.write(json.dumps(export_props))

    gltf_settings = {
        "export_animations": False,
        "export_optimize_animation_size": False
    }
    # and store settings for the gltf part
    stored_gltf_settings = bpy.data.texts[".gltf_auto_export_gltf_settings"] if ".gltf_auto_export_gltf_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_gltf_settings")
    stored_gltf_settings.clear()
    stored_gltf_settings.write(json.dumps(gltf_settings))

    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_legacy_mode=False,
        export_materials_library=False
    )

    world_file_path = os.path.join(models_path, "World.glb")
    assert os.path.exists(world_file_path) == True

    models_library_path = os.path.join(models_path, "library")
    model_library_file_paths = list(map(lambda file_name: os.path.join(models_library_path, file_name), sorted(os.listdir(models_library_path))))
    modification_times_first = list(map(lambda file_path: os.path.getmtime(file_path), model_library_file_paths + [world_file_path]))
    #print("files", model_library_file_paths)
    #print("mod times", modification_times_first)

    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_legacy_mode=False,
        export_materials_library=False
    )

    modification_times_no_change = list(map(lambda file_path: os.path.getmtime(file_path), model_library_file_paths + [world_file_path]))
    assert modification_times_no_change == modification_times_first

    # now move the main cube & export again
    print("----------------")
    print("main scene change")
    print("----------------")

    #py.context.window_manager.auto_export_tracker.enable_change_detection() # FIXME: should not be needed, but ..
    bpy.data.objects["Cube"].location = [1, 0, 0]
    
    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_legacy_mode=False,
        export_materials_library=False
    )

    modification_times = list(map(lambda file_path: os.path.getmtime(file_path), model_library_file_paths + [world_file_path]))
    assert modification_times != modification_times_first
    modification_times_first = modification_times


    # now same, but move the cube in the library
    print("----------------")
    print("library change")
    print("----------------")

    bpy.data.objects["Blueprint1_mesh"].location = [1, 2, 1]
    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_legacy_mode=False,
        export_materials_library=False
    )

    modification_times = list(map(lambda file_path: os.path.getmtime(file_path), model_library_file_paths + [world_file_path]))
    assert modification_times != modification_times_first
    modification_times_first = modification_times

    # now same, but using an operator
    print("----------------")
    print("change using operator")
    print("----------------")

    bpy.ops.transform.translate(value=(20.0, 0.0, 0.0))

    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_legacy_mode=False,
        export_materials_library=False
    )

    modification_times = list(map(lambda file_path: os.path.getmtime(file_path), model_library_file_paths + [world_file_path]))
    assert modification_times != modification_times_first
    modification_times_first = modification_times

    


   