from modules.processing import apply_color_correction, setup_color_correction
import gradio as gr
from modules import scripts_postprocessing
import launch
import packaging.version
import copy

NAME = 'Color Correction'
METHODS = ['A1111', 'Wavelet', 'AdaIN']

def extraImagesAvaliable():
    try:
        if packaging.version.parse(launch.git_tag()) >= packaging.version.parse("1.7.0"):
            return True
        else:
            return False
    except Exception as e:
        print(f'[{NAME}]: {e}')
        return False



def a1111_color_correction(targetImage, sampleImage):
    return apply_color_correction(setup_color_correction(sampleImage), targetImage)


def applyColorCorrectionMethod(method, targetImage, sampleImage):
    if method == 'A1111':
        color_correction_func = a1111_color_correction
    else:
        from srmodule.colorfix import adain_color_fix, wavelet_color_fix
        if targetImage.mode == "RGBA":
            targetImage = targetImage.convert(mode = "RGB")
        if sampleImage.mode == "RGBA":
            sampleImage = sampleImage.convert(mode = "RGB")
        if targetImage.size != sampleImage.size:
            sampleImage = sampleImage.resize(targetImage.size)

        if method == 'Wavelet':
            color_correction_func = wavelet_color_fix
        else:
            color_correction_func = adain_color_fix

    return color_correction_func(targetImage, sampleImage)


class ColorCorrectionExtras(scripts_postprocessing.ScriptPostprocessing):
    name = NAME
    order = 19000

    def ui(self):
        global METHODS
        with gr.Accordion(NAME, open=False):
            enable = gr.Checkbox(False, label="Enable")
            img = gr.Image(label="Sample Image", source="upload", interactive=True, type="pil", elem_id="image")   
            with gr.Row():
                try:
                    from srmodule.colorfix import adain_color_fix, wavelet_color_fix
                    method = gr.Dropdown(METHODS, label="Method", value='A1111')
                except ImportError:
                    METHODS = ['A1111']
                    method = gr.Textbox(value='A1111', visible=False)         
                extraProcessVisiable = extraImagesAvaliable()
                if len(METHODS) == 1:
                    extraProcessVisiable = False
                extraProcess = gr.Checkbox(False, label="Extra use all methods", visible=extraProcessVisiable)
        args = {
            'img': img,
            'enable': enable,
            'method' : method,
            'extraProcess' : extraProcess,
        }
        return args

    def process(self, pp: scripts_postprocessing.PostprocessedImage, **args):
        if args['enable'] == False:
            return
        targetImage = copy.copy(pp.image)
        sampleImage = args['img']
        method = args['method']
        extraProcess = args['extraProcess']

        pp.image = applyColorCorrectionMethod(method, targetImage, sampleImage)
        pp.info[NAME] = method

        if extraProcess and len(METHODS) > 1 and extraImagesAvaliable():
            for extraMethod in METHODS:
                if extraMethod == method:
                    continue
                image = applyColorCorrectionMethod(extraMethod, targetImage, sampleImage)
                pp.extra_images.append(image)
