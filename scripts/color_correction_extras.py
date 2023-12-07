from modules.processing import apply_color_correction, setup_color_correction
import gradio as gr
from modules import scripts_postprocessing

NAME = 'Color Correction'


def a1111_color_correction(targetImage, sampleImage):
    return apply_color_correction(setup_color_correction(sampleImage), targetImage)


class ColorCorrectionExtras(scripts_postprocessing.ScriptPostprocessing):
    name = NAME
    order = 19000

    def ui(self):
        with gr.Accordion(NAME, open=False):
            enable = gr.Checkbox(False, label="Enable")
            img = gr.Image(label="Sample Image", source="upload", interactive=True, type="pil", elem_id="image")   
            try:
                from srmodule.colorfix import adain_color_fix, wavelet_color_fix
                color_fix = gr.Dropdown(['A1111', 'Wavelet', 'AdaIN'], label="Method", value='A1111')
            except ImportError:
                color_fix = gr.Textbox(value='A1111', visible=False)
        args = {
            'img': img,
            'enable': enable,
            'color_fix' : color_fix,
        }
        return args

    def process(self, pp: scripts_postprocessing.PostprocessedImage, **args):
        if args['enable']:
            targetImage = pp.image
            sampleImage = args['img']
            color_fix = args['color_fix']

            if color_fix == 'A1111':
                color_correction_func = a1111_color_correction
            else:
                from srmodule.colorfix import adain_color_fix, wavelet_color_fix
                if targetImage.mode == "RGBA":
                    targetImage = targetImage.convert(mode = "RGB")
                if sampleImage.mode == "RGBA":
                    sampleImage = sampleImage.convert(mode = "RGB")
                if targetImage.size != sampleImage.size:
                    sampleImage = sampleImage.resize(targetImage.size)

                if color_fix == 'Wavelet':
                    color_correction_func = wavelet_color_fix
                else:
                    color_correction_func = adain_color_fix
                    
            pp.image = color_correction_func(targetImage, sampleImage)
            pp.info[NAME] = color_fix
