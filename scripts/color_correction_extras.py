from modules.processing import apply_color_correction, setup_color_correction
import gradio as gr
from modules import scripts_postprocessing
import copy

NAME = 'Color Correction'
METHODS = None

def extraImagesAvaliable():
    pp = scripts_postprocessing.PostprocessedImage(None)
    return hasattr(pp, 'extra_images')

if hasattr(scripts_postprocessing.ScriptPostprocessing, 'process_firstpass'):  # webui >= 1.7
    from modules.ui_components import InputAccordion
else:
    InputAccordion = None


colorfix = None
try:
    from modules import colorfix
except ImportError:
    try:
        from srmodule import colorfix
    except ImportError:
        pass


def a1111_color_correction(targetImage, sampleImage):
    return apply_color_correction(setup_color_correction(sampleImage), targetImage)


def applyColorCorrectionMethod(method, targetImage, sampleImage):
    if method == 'A1111':
        color_correction_func = a1111_color_correction
    else:
        if targetImage.mode == "RGBA":
            targetImage = targetImage.convert(mode = "RGB")
        if sampleImage.mode == "RGBA":
            sampleImage = sampleImage.convert(mode = "RGB")
        if targetImage.size != sampleImage.size:
            sampleImage = sampleImage.resize(targetImage.size)

        if method == 'Wavelet':
            color_correction_func = colorfix.wavelet_color_fix
        else:
            color_correction_func = colorfix.adain_color_fix

    print('Appling color correction', method)
    return color_correction_func(targetImage, sampleImage)


class ColorCorrectionExtras(scripts_postprocessing.ScriptPostprocessing):
    name = NAME
    order = 21000

    def __init__(self):
        self.init_image = None

    def ui(self):
        global METHODS
        with (
            InputAccordion(False, label=NAME) if InputAccordion
            else gr.Accordion(NAME, open=False)
            as enable
        ):
            if not InputAccordion:
                enable = gr.Checkbox(False, label="Enable")
            img = gr.Image(label="Sample Image", source="upload", interactive=True, type="pil", elem_id="image")
            gr.Markdown("*if not image provided, init image is used*")
            with gr.Row():
                if colorfix:
                    METHODS = ['A1111', 'Wavelet', 'AdaIN']
                    method = gr.Dropdown(METHODS, label="Method", value='A1111')
                else:
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


    def process_firstpass(self, pp: scripts_postprocessing.PostprocessedImage, **args):
        self.init_image = pp.image.copy()


    def process(self, pp: scripts_postprocessing.PostprocessedImage, **args):
        if args['enable'] == False:
            return
        targetImage = copy.copy(pp.image)
        sampleImage = (args and args['img']) or self.init_image
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
