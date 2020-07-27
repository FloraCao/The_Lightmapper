import bpy, os, importlib
from os import listdir
from os.path import isfile, join

class TLM_CV_Filtering:

    image_output_destination = ""

    def init(lightmap_dir, denoise):

        scene = bpy.context.scene

        print("Beginning filtering for files: ")

        if denoise:
            file_ending = "_denoised.hdr"
        else:
            file_ending = "_baked.hdr"

        dirfiles = [f for f in listdir(lightmap_dir) if isfile(join(lightmap_dir, f))]

        cv2 = importlib.util.find_spec("cv2")

        if cv2 is None:
            print("CV2 not found - Ignoring filtering")
            return 0
        else:
            cv2 = importlib.__import__("cv2")

        for file in dirfiles:

            if denoise:
                file_ending = "_denoised.hdr"
                file_split = 13
            else:
                file_ending = "_baked.hdr"
                file_split = 10

            if file.endswith(file_ending):

                file_input = os.path.join(lightmap_dir, file)
                os.chdir(lightmap_dir)

                opencv_process_image = cv2.imread(file_input, -1)

                print("Filtering: " + file_input)

                print(os.path.join(lightmap_dir, file))

                if scene.TLM_SceneProperties.tlm_filtering_mode == "Box":
                    if scene.TLM_SceneProperties.tlm_filtering_box_strength % 2 == 0:
                        kernel_size = (scene.TLM_SceneProperties.tlm_filtering_box_strength + 1,scene.TLM_SceneProperties.tlm_filtering_box_strength + 1)
                    else:
                        kernel_size = (scene.TLM_SceneProperties.tlm_filtering_box_strength,scene.TLM_SceneProperties.tlm_filtering_box_strength)
                    opencv_bl_result = cv2.blur(opencv_process_image, kernel_size)
                    if scene.TLM_SceneProperties.tlm_filtering_iterations > 1:
                        for x in range(scene.TLM_SceneProperties.tlm_filtering_iterations):
                            opencv_bl_result = cv2.blur(opencv_bl_result, kernel_size)

                elif scene.TLM_SceneProperties.tlm_filtering_mode == "Gaussian":
                    if scene.TLM_SceneProperties.tlm_filtering_gaussian_strength % 2 == 0:
                        kernel_size = (scene.TLM_SceneProperties.tlm_filtering_gaussian_strength + 1,scene.TLM_SceneProperties.tlm_filtering_gaussian_strength + 1)
                    else:
                        kernel_size = (scene.TLM_SceneProperties.tlm_filtering_gaussian_strength,scene.TLM_SceneProperties.tlm_filtering_gaussian_strength)
                    sigma_size = 0
                    opencv_bl_result = cv2.GaussianBlur(opencv_process_image, kernel_size, sigma_size)
                    if scene.TLM_SceneProperties.tlm_filtering_iterations > 1:
                        for x in range(scene.TLM_SceneProperties.tlm_filtering_iterations):
                            opencv_bl_result = cv2.GaussianBlur(opencv_bl_result, kernel_size, sigma_size)

                elif scene.TLM_SceneProperties.tlm_filtering_mode == "Bilateral":
                    diameter_size = scene.TLM_SceneProperties.tlm_filtering_bilateral_diameter
                    sigma_color = scene.TLM_SceneProperties.tlm_filtering_bilateral_color_deviation
                    sigma_space = scene.TLM_SceneProperties.tlm_filtering_bilateral_coordinate_deviation
                    opencv_bl_result = cv2.bilateralFilter(opencv_process_image, diameter_size, sigma_color, sigma_space)
                    if scene.TLM_SceneProperties.tlm_filtering_iterations > 1:
                        for x in range(scene.TLM_SceneProperties.tlm_filtering_iterations):
                            opencv_bl_result = cv2.bilateralFilter(opencv_bl_result, diameter_size, sigma_color, sigma_space)
                else:

                    if scene.TLM_SceneProperties.tlm_filtering_median_kernel % 2 == 0:
                        kernel_size = (scene.TLM_SceneProperties.tlm_filtering_median_kernel + 1 , scene.TLM_SceneProperties.tlm_filtering_median_kernel + 1)
                    else:
                        kernel_size = (scene.TLM_SceneProperties.tlm_filtering_median_kernel, scene.TLM_SceneProperties.tlm_filtering_median_kernel)

                    opencv_bl_result = cv2.medianBlur(opencv_process_image, kernel_size[0])
                    if scene.TLM_SceneProperties.tlm_filtering_iterations > 1:
                        for x in range(scene.TLM_SceneProperties.tlm_filtering_iterations):
                            opencv_bl_result = cv2.medianBlur(opencv_bl_result, kernel_size[0])

                filter_file_output = os.path.join(lightmap_dir, file[:-file_split] + "_filtered.hdr")

                cv2.imwrite(filter_file_output, opencv_bl_result)

                print("Written to: " + filter_file_output)

            # if file.endswith(file_ending):
            #     print()
            #     baked_image_array.append(file)