''' FIBO uses a VLM that transforms short prompts into detailed structured prompts that are used to generate images. You can use the following code to generate images using Gemini via the Google API - **requires a GOOGLE_API_KEY**, or uncomment the relevant section to run a local VLM instead (FIBO-VLM):'''

import json
import os

import torch
from diffusers import BriaFiboPipeline
from diffusers.modular_pipelines import ModularPipeline

# -------------------------------
# Load the VLM pipeline
# -------------------------------
torch.set_grad_enabled(False)
# Using Gemini API, requires GOOGLE_API_KEY environment variable
assert os.getenv("GOOGLE_API_KEY") is not None, "GOOGLE_API_KEY environment variable is not set"
vlm_pipe = ModularPipeline.from_pretrained("briaai/FIBO-gemini-prompt-to-JSON", trust_remote_code=True)

# Using local VLM, uncomment to run
# vlm_pipe = ModularPipeline.from_pretrained("briaai/FIBO-VLM-prompt-to-JSON", trust_remote_code=True)


# Load the FIBO pipeline
pipe = BriaFiboPipeline.from_pretrained(
    "briaai/FIBO",
    torch_dtype=torch.bfloat16,
)
pipe.to("cuda")
# pipe.enable_model_cpu_offload() # uncomment if you're getting CUDA OOM errors

# -------------------------------
# Run Prompt to JSON
# -------------------------------

# Create a prompt to generate an initial image
output = vlm_pipe(
    prompt="A hyper-detailed, ultra-fluffy owl sitting in the trees at night, looking directly at the camera with wide, adorable, expressive eyes. Its feathers are soft and voluminous, catching the cool moonlight with subtle silver highlights. The owl's gaze is curious and full of charm, giving it a whimsical, storybook-like personality."
)
json_prompt_generate = output.values["json_prompt"]

def get_default_negative_prompt(existing_json: dict) -> str:
    negative_prompt = ""
    style_medium = existing_json.get("style_medium", "").lower()
    if style_medium in ["photograph", "photography", "photo"]:
        negative_prompt = """{'style_medium':'digital illustration','artistic_style':'non-realistic'}"""
    return negative_prompt


negative_prompt = get_default_negative_prompt(json.loads(json_prompt_generate))

# -------------------------------
# Run Image Generation
# -------------------------------
# Generate the image from the structured json prompt
results_generate = pipe(
    prompt=json_prompt_generate, num_inference_steps=50, guidance_scale=5, negative_prompt=negative_prompt
)
results_generate.images[0].save("image_generate.png")
with open("image_generate_json_prompt.json", "w") as f:
    f.write(json_prompt_generate)


'''FIBO supports iterative generation. Given a structured prompt and an instruction, FIBO refines the output.'''

output = vlm_pipe(
    json_prompt=json_prompt_generate, prompt="make the owl brown"
)
json_prompt_refine_from_image = output.values["json_prompt"]

negative_prompt = get_default_negative_prompt(json.loads(json_prompt_refine_from_image))
results_refine_from_image = pipe(
    prompt=json_prompt_refine_from_image, num_inference_steps=50, guidance_scale=5, negative_prompt=negative_prompt
)
results_refine_from_image.images[0].save("image_refine_from_image.png")
with open("image_refine_from_image_json_prompt.json", "w") as f:
    f.write(json_prompt_refine_from_image)

'''Start from an image as inspiration and let Fibo regenerate a variation of it or merge your creative intent into the next generation'''

from PIL import Image
original_astronaut_image = Image.open("<path to original astronaut image>") 
output = vlm_pipe(
    image=original_astronaut_image, prompt="")
json_prompt_inspire = output.values["json_prompt"]
negative_prompt = get_default_negative_prompt(json.loads(json_prompt_inspire))
results_inspire = pipe(
    prompt=json_prompt_inspire, num_inference_steps=50, guidance_scale=5, negative_prompt=negative_prompt
)
results_inspire.images[0].save("image_inspire_no_prompt.png")
with open("image_inspire_json_prompt_no_prompt.json", "w") as f:
    f.write(json_prompt_inspire)

output = vlm_pipe(
    image=original_astronaut_image, prompt="Make futuristic")
json_prompt_inspire = output.values["json_prompt"]
negative_prompt = get_default_negative_prompt(json.loads(json_prompt_inspire))

results_inspire = pipe(
    prompt=json_prompt_inspire, num_inference_steps=50, guidance_scale=5, negative_prompt=negative_prompt
)
results_inspire.images[0].save("image_inspire_with_prompt.png")
with open("image_inspire_json_prompt_with_prompt.json", "w") as f:
    f.write(json_prompt_inspire)

