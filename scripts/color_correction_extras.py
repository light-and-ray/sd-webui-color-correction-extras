from modules.processing import apply_color_correction, setup_color_correction
import gradio as gr
from modules import scripts_postprocessing

NAME = 'Color Correction'

class ColorCorrectionExtras(scripts_postprocessing.ScriptPostprocessing):
    name = NAME
    order = 19000

    def ui(self):
        with gr.Accordion(NAME, open=False):
            enable = gr.Checkbox(False, label="Enable")
            img = gr.Image(label="Sample Image", source="upload", interactive=True, type="pil", elem_id="image")   
            useSourceInstead = gr.Checkbox(False, label="Use Source image instead of sample")
        args = {
            'img': img,
            'enable': enable,
            'useSourceInstead' : useSourceInstead,
        }
        return args

    def process(self, pp: scripts_postprocessing.PostprocessedImage, **args):
        if args['enable']:
            targetImage = pp.image
            if args['useSourceInstead']:
                sampleImage = targetImage
            else:
                sampleImage = args['img']

            pp.image = apply_color_correction(setup_color_correction(sampleImage), targetImage)
            pp.info[NAME] = True
