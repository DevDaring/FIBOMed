# Generate Image

Description

Generates a new image based on your inputs.

This all-in-one endpoint first translates your input (prompt and/or images) into a structured JSON prompt using the state-of-the-art Gemini 2.5 Flash VLM bridge. It then internally uses that JSON to generate the final, deterministic image.

Use this endpoint for professional workflows that demand the highest-fidelity interpretation of your creative vision. The response includes both the final image_url and the structured_prompt (JSON).

For advanced, programmatic control, you can also pass in your own structured_prompt (e.g., from a previous response or the /v2/structured_prompt/generate endpoint) to bypass the internal VLM bridge. This allows for precise, auditable refinement or recreation of an image, or to generate multiple variations from the same structured prompt.

---

Input Combination Rules

The request body must include one of the following mutually exclusive combinations:

* prompt (Generates a new image from text)
* images (Generates a new image inspired by a reference image)
* images + prompt (Generates a new image inspired by an image and guided by text)
* structured_prompt (Recreates a previous image exactly, combined with a seed)
* structured_prompt + prompt (Refines a previous image using new text instructions, combined with a seed)

---
API Access

You can register and access the API Token through Bria's platform by clicking here.

---
Examples

Use Case 1: Using a textual prompt

* Input Prompt: photorealistic, high resolution rendering, balloon of lettering, "HAPPY NEW YEAR 2026", used color is Pantone Bran, Crocus, Deja vu blue, perfect composition and alignment, natural light set, white backdrop, ultra realistic, rich detail
* Output Image: !Example of text-to-image output
* Output structured_prompt:
    json
    
    {
      "short_description": "A photorealistic, high-resolution rendering of balloon lettering spelling out \"HAPPY NEW YEAR 2026\" against a pristine white backdrop. The balloons are meticulously crafted with a metallic, reflective surface, showcasing a vibrant color palette of Pantone Bran, Crocus, and Deja vu blue. The composition is perfectly aligned and balanced, emphasizing the celebratory message with natural, soft lighting that creates subtle, elegant reflections and shadows.",
      "objects": [
        {
          "description": "A cluster of individual balloon letters forming the word \"HAPPY\". Each letter is inflated and has a smooth, highly reflective metallic surface, catching and distorting the ambient light. The letters are arranged horizontally, slightly overlapping to create a cohesive word.",
          "location": "top-left to center",
          "relationship": "Part of the main textual display, positioned above 'NEW YEAR'.",
          "relative_size": "large within frame",
          "shape_and_color": "Irregular letter shapes, primarily Pantone Bran (a rich, deep orange-brown) with hints of Crocus (a vibrant purple) and Deja vu blue (a muted, dusty blue) in the reflections.",
          "texture": "Smooth, highly reflective metallic foil.",
          "appearance_details": "Slightly rounded edges, showing subtle seams where the foil is joined. The surface exhibits a high degree of realism with minor imperfections and creases visible upon close inspection.",
          "number_of_objects": 5,
          "orientation": "Horizontal"
        },
        {
          "description": "A cluster of individual balloon letters forming the phrase \"NEW YEAR\". These letters are also inflated and possess the same metallic, reflective quality as the 'HAPPY' balloons. They are arranged horizontally, directly below 'HAPPY', maintaining a consistent visual style.",
          "location": "center",
          "relationship": "Part of the main textual display, positioned below 'HAPPY' and above '2026'.",
          "relative_size": "large within frame",
          "shape_and_color": "Irregular letter shapes, primarily Crocus (a vibrant purple) with reflections of Pantone Bran and Deja vu blue.",
          "texture": "Smooth, highly reflective metallic foil.",
          "appearance_details": "Each letter is distinct, with a slightly inflated, three-dimensional appearance. The metallic sheen creates a dynamic interplay of light and color across their surfaces.",
          "number_of_objects": 7,
          "orientation": "Horizontal"
        },
        {
          "description": "A cluster of individual balloon numbers forming \"2026\". These numbers are crafted from the same metallic balloon material, maintaining visual continuity with the words above. They are positioned centrally below 'NEW YEAR'.",
          "location": "bottom-center",
          "relationship": "Part of the main textual display, positioned below 'NEW YEAR'.",
          "relative_size": "large within frame",
          "shape_and_color": "Numerical shapes, primarily Deja vu blue (a muted, dusty blue) with reflections of Pantone Bran and Crocus.",
          "texture": "Smooth, highly reflective metallic foil.",
          "appearance_details": "The numbers appear robust and fully inflated, with crisp edges and a flawless metallic finish that reflects the surrounding light sources.",
          "number_of_objects": 4,
          "orientation": "Horizontal"
        },
        {
          "description": "Several small, spherical balloons scattered around the main lettering, acting as decorative accents. These balloons are also metallic and share the same color palette, adding depth and a festive touch to the scene.",
          "location": "scattered around the main lettering",
          "relationship": "Complementary decorative elements to the main balloon lettering.",
          "relative_size": "small",
          "shape_and_color": "Spherical, in Pantone Bran, Crocus, and Deja vu blue.",
          "texture": "Smooth, reflective metallic.",
          "appearance_details": "Perfectly round and shiny, reflecting miniature versions of the light sources and the main lettering.",
          "number_of_objects": 5,
          "orientation": "Various, floating"
        }
      ],
      "background_setting": "A clean, seamless white studio backdrop, providing a stark contrast that makes the colorful balloons pop. The backdrop extends smoothly from the floor to the wall, creating an infinite white space that eliminates distractions and emphasizes the subject.",
      "lighting": {
        "conditions": "Bright, natural light, simulating a well-lit studio environment.",
        "direction": "Soft, diffused light coming from slightly above and in front of the balloons, with secondary fill light from the sides.",
        "shadows": "Soft, subtle, and elongated shadows cast behind and beneath the balloons, indicating depth and dimension without being harsh or distracting. The shadows are light gray against the white background."
      },
      "aesthetics": {
        "composition": "Centered and perfectly aligned, with the balloon lettering arranged in a clear, readable hierarchy. The overall composition is balanced and symmetrical, drawing the viewer's eye directly to the celebratory message.",
        "color_scheme": "A vibrant, harmonious palette of Pantone Bran (orange-brown), Crocus (purple), and Deja vu blue, creating a festive yet sophisticated feel against the neutral white background.",
        "mood_atmosphere": "Joyful, celebratory, optimistic, and clean.",
        "preference_score": "very high",
        "aesthetic_score": "very high"
      },
      "photographic_characteristics": {
        "depth_of_field": "Shallow, with the balloons in sharp focus and the background subtly blurred to emphasize the subject, though the white backdrop inherently provides minimal blur.",
        "focus": "Sharp focus on the balloon lettering, highlighting the intricate details and reflective surfaces.",
        "camera_angle": "Eye-level, providing a direct and engaging view of the balloon arrangement.",
        "lens_focal_length": "Standard lens (e.g., 50mm), ensuring a natural perspective without distortion, ideal for capturing the full arrangement clearly."
      },
      "style_medium": "photograph",
      "text_render": [
        {
          "text": "HAPPY NEW YEAR 2026",
          "location": "center",
          "size": "large within frame",
          "color": "Pantone Bran, Crocus, Deja vu blue (as balloon colors)",
          "font": "inflated balloon lettering",
          "appearance_details": "Metallic, reflective, three-dimensional balloon letters."
        }
      ],
      "context": "This is a concept for a high-resolution, ultra-realistic promotional image or greeting card for a New Year's celebration, intended for digital display or print media.",
      "artistic_style": "realistic, detailed, vibrant"
    }
    
---

Use Case 2: Drawing inspiration from a reference image

* Input Image: !Example of reference image input
* Input Prompt: a ring inspired by the image
* Output Image: !Example of image-to-image output
* Output structured_prompt:
    json
    {
      "short_description": "A close-up shot of an elegant ring featuring a prominent, teardrop-shaped red gemstone set in a thick, golden chain-link band. The ring is displayed on a smooth, light-colored surface, with soft, diffused lighting highlighting its intricate details and the vibrant color of the stone. The overall impression is one of luxury and sophisticated design, emphasizing the jewelry's craftsmanship.",
      "objects": [
        {
          "description": "A luxurious ring with a thick, golden chain-link band. The band is composed of interlocking oval links, giving it a substantial and modern feel. The gold has a polished, reflective finish.",
          "location": "center",
          "relationship": "The band holds the red gemstone securely.",
          "relative_size": "large within frame",
          "shape_and_color": "Curved, interlocking golden links",
          "texture": "smooth, metallic",
          "appearance_details": "The links are uniform in size and have a high-shine finish, suggesting quality craftsmanship.",
          "orientation": "circular, with the gemstone facing upwards"
        },
        {
          "description": "A vibrant, translucent red gemstone, cut into a teardrop or pear shape. It is set securely within a golden bezel at the top of the chain-link band. The stone catches and reflects light, showcasing its deep red hue.",
          "location": "top-center of the ring",
          "relationship": "It is the focal point of the ring, contrasting with the golden band.",
          "relative_size": "medium within the ring",
          "shape_and_color": "Teardrop-shaped, deep red",
          "texture": "smooth, glassy",
          "appearance_details": "The gemstone has multiple facets that contribute to its sparkle and depth of color.",
          "orientation": "vertical, with the pointed end facing downwards"
        }
      ],
      "background_setting": "A clean, minimalist background consisting of a smooth, light beige or off-white surface, providing a neutral canvas that allows the jewelry to stand out without distraction. There are no other discernible objects or textures in the background.",
      "lighting": {
        "conditions": "soft, diffused studio lighting",
        "direction": "overhead and slightly front-lit",
        "shadows": "minimal, very soft, and subtle shadows cast directly beneath the ring, indicating a gentle light source"
      },
      "aesthetics": {
        "composition": "centered, close-up shot",
        "color_scheme": "warm complementary colors (gold and red against a neutral background)",
        "mood_atmosphere": "elegant, luxurious, sophisticated",
        "preference_score": "very high",
        "aesthetic_score": "very high"
      },
      "photographic_characteristics": {
        "depth_of_field": "shallow, with the ring in sharp focus and the background softly blurred",
        "focus": "sharp focus on subject",
        "camera_angle": "eye-level, slightly overhead",
        "lens_focal_length": "macro"
      },
      "style_medium": "photograph",
      "context": "This is a product photograph for a high-end jewelry brand, intended for e-commerce, catalog, or editorial use, showcasing the design and quality of the ring."
    }
    

---

Use Case 3: Refining a previously generated image

* Input Image (from previous response - shouldn't be part of the refine request): !Example of input image
* Input structured_prompt (from previous response - should be part of the refine request, toegther with the seed of the visual result):
    json
    {
      "short_description": "A close-up, photorealistic image of an ultra-fluffy owl perched on a tree branch at night. The owl's large, expressive eyes gaze directly at the viewer, conveying curiosity and charm. Its voluminous feathers, a mix of soft browns and creams, are subtly illuminated by cool moonlight, revealing delicate silver highlights. The background is a soft blur of dark, leafy trees, enhancing the owl's prominence and creating a whimsical, storybook-like atmosphere.",
      "objects": [
        {
          "description": "A hyper-detailed, ultra-fluffy owl with soft, voluminous feathers. Its head is slightly tilted, and its body is plump and rounded, emphasizing its fluffiness. The feathers are a blend of warm browns, creams, and grays, with individual strands visible and catching subtle silver highlights from the moonlight.",
          "location": "center",
          "relationship": "The primary subject, perched on a tree branch, looking directly at the viewer.",
          "relative_size": "large within frame",
          "shape_and_color": "Rounded, plump body with a distinct head; mottled browns, creams, and grays with silver highlights.",
          "texture": "Extremely soft, downy, and voluminous feathers.",
          "appearance_details": "Large, round, dark eyes with a bright, curious, and charming expression. The eyes reflect a tiny pinpoint of moonlight, adding to their expressiveness. Small, dark beak partially hidden by feathers.",
          "expression": "Curious, charming, and adorable with wide, expressive eyes.",
          "orientation": "Facing directly forward, head slightly tilted to its right."
        },
        {
          "description": "A sturdy, dark tree branch, partially visible, providing a perch for the owl. Its surface is rough and textured, suggesting aged bark.",
          "location": "bottom-center",
          "relationship": "Supports the owl, providing its perch.",
          "relative_size": "medium",
          "shape_and_color": "Irregular, horizontal shape; dark brown to black.",
          "texture": "Rough, gnarled bark.",
          "appearance_details": "Some moss or lichen might be subtly visible on its surface.",
          "orientation": "Horizontal, extending from left to right across the lower part of the frame."
        }
      ],
      "background_setting": "A dense, dark forest at night. The background consists of blurred, indistinct shapes of tree trunks and foliage, suggesting depth and a natural, nocturnal environment. A faint, ethereal glow from the moon filters through the canopy.",
      "lighting": {
        "conditions": "Cool moonlight, nighttime.",
        "direction": "Softly diffused from above and slightly to the front, highlighting the owl's features.",
        "shadows": "Soft, subtle shadows on the owl's underside and within the tree branches, adding depth without obscuring details. The background is largely in deep shadow."
      },
      "aesthetics": {
        "composition": "Centered, close-up portrait composition, with the owl filling a significant portion of the frame.",
        "color_scheme": "Cool blues, grays, and dark greens in the background, contrasting with the warm browns and creams of the owl, accented by silver highlights.",
        "mood_atmosphere": "Whimsical, enchanting, serene, and slightly mysterious.",
        "preference_score": "very high",
        "aesthetic_score": "very high"
      },
      "photographic_characteristics": {
        "depth_of_field": "Shallow, with the owl in sharp focus and the background softly blurred (bokeh).",
        "focus": "Sharp focus on the owl's eyes and face, with a gradual fall-off of focus towards its body and the branch.",
        "camera_angle": "Eye-level, as if directly encountering the owl.",
        "lens_focal_length": "Portrait lens (e.g., 85mm-100mm) to achieve a tight crop and shallow depth of field."
      },
      "style_medium": "photograph",
      "context": "This is a concept for a high-quality, photorealistic image intended for nature photography, children's book illustrations, or a whimsical art print.",
      "artistic_style": "realistic, detailed, ethereal"
    }
    
* Input Refinement Prompt: add sunlight
* Output Image: !Example of refinement output
* Output structured_prompt (refined):
    json
    {
      "short_description": "A close-up, photorealistic image of an ultra-fluffy owl perched on a tree branch, bathed in warm sunlight. The owl's large, expressive eyes gaze directly at the viewer, conveying curiosity and charm. Its voluminous feathers, a mix of soft browns and creams, are brightly illuminated by golden sunlight, revealing delicate golden highlights. The background is a soft blur of sun-dappled, leafy trees, enhancing the owl's prominence and creating a whimsical, storybook-like atmosphere.",
      "objects": [
        {
          "description": "A hyper-detailed, ultra-fluffy owl with soft, voluminous feathers. Its head is slightly tilted, and its body is plump and rounded, emphasizing its fluffiness. The feathers are a blend of warm browns, creams, and grays, with individual strands visible and catching bright golden highlights from the sunlight.",
          "location": "center",
          "relationship": "The primary subject, perched on a tree branch, looking directly at the viewer.",
          "relative_size": "large within frame",
          "shape_and_color": "Rounded, plump body with a distinct head; mottled browns, creams, and grays with golden highlights.",
          "texture": "Extremely soft, downy, and voluminous feathers.",
          "appearance_details": "Large, round, dark eyes with a bright, curious, and charming expression. The eyes reflect a tiny pinpoint of sunlight, adding to their expressiveness. Small, dark beak partially hidden by feathers.",
          "expression": "Curious, charming, and adorable with wide, expressive eyes.",
          "orientation": "Facing directly forward, head slightly tilted to its right."
        },
        {
          "description": "A sturdy, dark tree branch, partially visible, providing a perch for the owl. Its surface is rough and textured, suggesting aged bark, with patches illuminated by sunlight.",
          "location": "bottom-center",
          "relationship": "Supports the owl, providing its perch.",
          "relative_size": "medium",
          "shape_and_color": "Irregular, horizontal shape; dark brown to black.",
          "texture": "Rough, gnarled bark.",
          "appearance_details": "Some moss or lichen might be subtly visible on its surface, highlighted by the sun.",
          "orientation": "Horizontal, extending from left to right across the lower part of the frame."
        }
      ],
      "background_setting": "A dense forest during the day, with sunlight filtering through the canopy. The background consists of blurred, indistinct shapes of tree trunks and foliage, with dappled light and shadow, suggesting depth and a natural, daytime environment.",
      "lighting": {
        "conditions": "Bright, warm sunlight, daytime.",
        "direction": "Strongly from above and slightly to the front, creating clear highlights on the owl's features.",
        "shadows": "Defined, yet soft shadows on the owl's underside and within the tree branches, adding depth. The background features dappled light and shadow."
      },
      "aesthetics": {
        "composition": "Centered, close-up portrait composition, with the owl filling a significant portion of the frame.",
        "color_scheme": "Warm yellows, greens, and browns in the background, complementing the warm browns and creams of the owl, accented by golden highlights.",
        "mood_atmosphere": "Whimsical, enchanting, serene, and joyful.",
        "preference_score": "very high",
        "aesthetic_score": "very high"
      },
      "photographic_characteristics": {
        "depth_of_field": "Shallow, with the owl in sharp focus and the background softly blurred (bokeh).",
        "focus": "Sharp focus on the owl's eyes and face, with a gradual fall-off of focus towards its body and the branch.",
        "camera_angle": "Eye-level, as if directly encountering the owl.",
        "lens_focal_length": "Portrait lens (e.g., 85mm-100mm) to achieve a tight crop and shallow depth of field."
      },
      "style_medium": "photograph",
      "context": "This is a concept for a high-quality, photorealistic image intended for nature photography, children's book illustrations, or a whimsical art print.",
      "artistic_style": "realistic, detailed, ethereal"
    }

Endpoint: POST /image/generate

## Header parameters:

  - `api_token` (string, required)

## Request fields (application/json):

  - `prompt` (string)
    Text-based instruction. Can be used alone to create a new prompt, or as a refinement command with an images or structured_prompt.

  - `images` (array)
    Publicly available URL or Base64-encoded image. Currently supports a single image. 
Supported formats: JPEG, JPG, PNG, WEBP.

  - `structured_prompt` (string)
    A string containing the structured prompt in JSON format. Use a structured_prompt from a previous generation's response or the /v2/structured_prompt/generate endpoint for precise refinement.

  - `negative_prompt` (string)
    A text prompt specifying concepts, styles, or objects to exclude from the generated image. This parameter is optional.

  - `guidance_scale` (integer)
    Determines how closely the generated image should adhere to the content in the prompt parameter. This parameter is optional.

  - `model_version` (string)
    Generation model version. This parameter is optional.
* If omitted (Default): Your request will automatically use Bria's current default model. This ensures you always benefit from our latest improvements.
* If specified (e.g., "FIBO"): Your request will be pinned to this exact version.
    Enum: "FIBO"

  - `aspect_ratio` (string)
    Image aspect ratio. This parameter is optional.
    Enum: "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9"

  - `steps_num` (integer)
    Number of diffusion steps. Uses model default if omitted. This parameter is optional.

  - `seed` (integer)
    Seed for deterministic generation. Uses a random seed if omitted. This parameter is optional.

  - `sync` (boolean)
    Response mode. This parameter is optional.
* false (default): Asynchronous. Returns 202 with a status_url to poll.
* true: Synchronous. Holds the connection and returns 200 with the final result.

  - `ip_signal` (boolean)
    If true, returns a warning for potential IP content in the prompt parameter. This parameter is optional.

  - `prompt_content_moderation` (boolean)
    If true, returns 422 on input prompt moderation failure in the prompt parameter. This parameter is optional.

  - `visual_input_content_moderation` (boolean)
    If true, returns 422 on visual input moderation failure. This parameter is optional.

  - `visual_output_content_moderation` (boolean)
    If true, returns 422 on visual output moderation failure. This parameter is optional.

## Response 200 fields (application/json):

  - `result` (object, required)

  - `result.image_url` (string, required)

  - `result.seed` (integer, required)

  - `result.structured_prompt` (string, required)

  - `request_id` (string, required)

  - `warning` (string)
    Returned only when ip_signal = true and the prompt field included IP content.

## Response 202 fields (application/json):

  - `request_id` (string, required)

  - `status_url` (string, required)

  - `warning` (string)
    Returned only when ip_signal = true and the prompt field included IP content.

## Response 400 fields (application/json):

  - `error` (object, required)

  - `error.code` (integer, required)
    Example: 123

  - `error.message` (string, required)

  - `error.details` (string)

  - `request_id` (string, required)

## Response 401 fields (application/json):

  - `error` (object, required)

  - `error.code` (integer, required)
    Example: 123

  - `error.message` (string, required)

  - `error.details` (string)

  - `request_id` (string, required)

## Response 403 fields (application/json):

  - `error` (object, required)

  - `error.code` (integer, required)
    Example: 123

  - `error.message` (string, required)

  - `error.details` (string)

  - `request_id` (string, required)

## Response 422 fields (application/json):

  - `error` (object, required)

  - `error.code` (integer, required)
    Example: 123

  - `error.message` (string, required)

  - `error.details` (string)

  - `request_id` (string, required)

## Response 429 fields (application/json):

  - `error` (object, required)

  - `error.code` (integer, required)
    Example: 123

  - `error.message` (string, required)

  - `error.details` (string)

  - `request_id` (string, required)

## Response 5XX fields (application/json):

  - `error` (object, required)

  - `error.code` (integer, required)
    Example: 123

  - `error.message` (string, required)

  - `error.details` (string)

  - `request_id` (string, required)

############################################################
API Call Example
##########################################################

post
/image/generate
curl

Generate a new image using a textual prompt
Generate a new image using a textual prompt


curl -i -X POST \
  https://engine.prod.bria-api.com/v2/image/generate \
  -H 'Content-Type: application/json' \
  -H 'api_token: string' \
  -d '{
    "prompt": "A photorealistic, high-resolution rendering of balloon lettering spelling out \"HAPPY NEW YEAR 2026\" against a pristine white backdrop. The balloons are meticulously crafted with a metallic, reflective surface, showcasing a vibrant color palette of Pantone Bran, Crocus, and Deja vu blue. The composition is perfectly aligned and balanced, emphasizing the celebratory message with natural, soft lighting that creates subtle, elegant reflections and shadows."
  }'

  post
/image/generate
curl

Generate an image inspired by a reference image
Generate an image inspired by a reference image


curl -i -X POST \
  https://engine.prod.bria-api.com/v2/image/generate \
  -H 'Content-Type: application/json' \
  -H 'api_token: string' \
  -d '{
    "prompt": "a ring inspired by the image",
    "images": [
      "https://bria-datasets.s3.us-east-1.amazonaws.com/api_doc/fibo/ref_1.jpg"
    ]
  }'

  post
/image/generate
curl

Generate an image inspired by only a reference image
Generate an image inspired by only a reference image


curl -i -X POST \
  https://engine.prod.bria-api.com/v2/image/generate \
  -H 'Content-Type: application/json' \
  -H 'api_token: string' \
  -d '{
    "images": [
      "https://bria-datasets.s3.us-east-1.amazonaws.com/api_doc/fibo/ref_1.jpg"
    ]
  }'


post
/image/generate
curl

Refine a previously generated image using its structured_prompt and seed
Refine a previously generated image using its structured_prompt and seed


curl -i -X POST \
  https://engine.prod.bria-api.com/v2/image/generate \
  -H 'Content-Type: application/json' \
  -H 'api_token: string' \
  -d '{
    "prompt": "add sunlight",
    "structured_prompt": "{\"short_description\":\"A close-up, photorealistic image of an ultra-fluffy owl perched on a tree branch at night. The owl'\''s large, expressive eyes gaze directly at the viewer, conveying curiosity and charm. Its voluminous feathers, a mix of soft browns and creams, are subtly illuminated by cool moonlight, revealing delicate silver highlights. The background is a soft blur of dark, leafy trees, enhancing the owl'\''s prominence and creating a whimsical, storybook-like atmosphere.\",\"objects\":[{\"description\":\"A hyper-detailed, ultra-fluffy owl with soft, voluminous feathers. Its head is slightly tilted, and its body is plump and rounded, emphasizing its fluffiness. The feathers are a blend of warm browns, creams, and grays, with individual strands visible and catching subtle silver highlights from the moonlight.\",\"location\":\"center\",\"relationship\":\"The primary subject, perched on a tree branch, looking directly at the viewer.\",\"relative_size\":\"large within frame\",\"shape_and_color\":\"Rounded, plump body with a distinct head; mottled browns, creams, and grays with silver highlights.\",\"texture\":\"Extremely soft, downy, and voluminous feathers.\",\"appearance_details\":\"Large, round, dark eyes with a bright, curious, and charming expression. The eyes reflect a tiny pinpoint of moonlight, adding to their expressiveness. Small, dark beak partially hidden by feathers.\",\"expression\":\"Curious, charming, and adorable with wide, expressive eyes.\",\"orientation\":\"Facing directly forward, head slightly tilted to its right.\"},{\"description\":\"A sturdy, dark tree branch, partially visible, providing a perch for the owl. Its surface is rough and textured, suggesting aged bark.\",\"location\":\"bottom-center\",\"relationship\":\"Supports the owl, providing its perch.\",\"relative_size\":\"medium\",\"shape_and_color\":\"Irregular, horizontal shape; dark brown to black.\",\"texture\":\"Rough, gnarled bark.\",\"appearance_details\":\"Some moss or lichen might be subtly visible on its surface.\",\"orientation\":\"Horizontal, extending from left to right across the lower part of the frame.\"}],\"background_setting\":\"A dense, dark forest at night. The background consists of blurred, indistinct shapes of tree trunks and foliage, suggesting depth and a natural, nocturnal environment. A faint, ethereal glow from the moon filters through the canopy.\",\"lighting\":{\"conditions\":\"Cool moonlight, nighttime.\",\"direction\":\"Softly diffused from above and slightly to the front, highlighting the owl'\''s features.\",\"shadows\":\"Soft, subtle shadows on the owl'\''s underside and within the tree branches, adding depth without obscuring details. The background is largely in deep shadow.\"},\"aesthetics\":{\"composition\":\"Centered, close-up portrait composition, with the owl filling a significant portion of the frame.\",\"color_scheme\":\"Cool blues, grays, and dark greens in the background, contrasting with the warm browns and creams of the owl, accented by silver highlights.\",\"mood_atmosphere\":\"Whimsical, enchanting, serene, and slightly mysterious.\",\"preference_score\":\"very high\",\"aesthetic_score\":\"very high\"},\"photographic_characteristics\":{\"depth_of_field\":\"Shallow, with the owl in sharp focus and the background softly blurred (bokeh).\",\"focus\":\"Sharp focus on the owl'\''s eyes and face, with a gradual fall-off of focus towards its body and the branch.\",\"camera_angle\":\"Eye-level, as if directly encountering the owl.\",\"lens_focal_length\":\"Portrait lens (e.g., 85mm-100mm) to achieve a tight crop and shallow depth of field.\"},\"style_medium\":\"photograph\",\"context\":\"This is a concept for a high-quality, photorealistic image intended for nature photography, children'\''s book illustrations, or a whimsical art print.\",\"artistic_style\":\"realistic, detailed, ethereal\"}",
    "seed": 123456789
  }'

  post
/image/generate
curl

Recreate a previously generated image
Recreate a previously generated image


curl -i -X POST \
  https://engine.prod.bria-api.com/v2/image/generate \
  -H 'Content-Type: application/json' \
  -H 'api_token: string' \
  -d '{
    "structured_prompt": "{\"short_description\":\"A close-up, photorealistic image of an ultra-fluffy owl perched on a tree branch at night. The owl'\''s large, expressive eyes gaze directly at the viewer, conveying curiosity and charm. Its voluminous feathers, a mix of soft browns and creams, are subtly illuminated by cool moonlight, revealing delicate silver highlights. The background is a soft blur of dark, leafy trees, enhancing the owl'\''s prominence and creating a whimsical, storybook-like atmosphere.\",\"objects\":[{\"description\":\"A hyper-detailed, ultra-fluffy owl with soft, voluminous feathers. Its head is slightly tilted, and its body is plump and rounded, emphasizing its fluffiness. The feathers are a blend of warm browns, creams, and grays, with individual strands visible and catching subtle silver highlights from the moonlight.\",\"location\":\"center\",\"relationship\":\"The primary subject, perched on a tree branch, looking directly at the viewer.\",\"relative_size\":\"large within frame\",\"shape_and_color\":\"Rounded, plump body with a distinct head; mottled browns, creams, and grays with silver highlights.\",\"texture\":\"Extremely soft, downy, and voluminous feathers.\",\"appearance_details\":\"Large, round, dark eyes with a bright, curious, and charming expression. The eyes reflect a tiny pinpoint of moonlight, adding to their expressiveness. Small, dark beak partially hidden by feathers.\",\"expression\":\"Curious, charming, and adorable with wide, expressive eyes.\",\"orientation\":\"Facing directly forward, head slightly tilted to its right.\"},{\"description\":\"A sturdy, dark tree branch, partially visible, providing a perch for the owl. Its surface is rough and textured, suggesting aged bark.\",\"location\":\"bottom-center\",\"relationship\":\"Supports the owl, providing its perch.\",\"relative_size\":\"medium\",\"shape_and_color\":\"Irregular, horizontal shape; dark brown to black.\",\"texture\":\"Rough, gnarled bark.\",\"appearance_details\":\"Some moss or lichen might be subtly visible on its surface.\",\"orientation\":\"Horizontal, extending from left to right across the lower part of the frame.\"}],\"background_setting\":\"A dense, dark forest at night. The background consists of blurred, indistinct shapes of tree trunks and foliage, suggesting depth and a natural, nocturnal environment. A faint, ethereal glow from the moon filters through the canopy.\",\"lighting\":{\"conditions\":\"Cool moonlight, nighttime.\",\"direction\":\"Softly diffused from above and slightly to the front, highlighting the owl'\''s features.\",\"shadows\":\"Soft, subtle shadows on the owl'\''s underside and within the tree branches, adding depth without obscuring details. The background is largely in deep shadow.\"},\"aesthetics\":{\"composition\":\"Centered, close-up portrait composition, with the owl filling a significant portion of the frame.\",\"color_scheme\":\"Cool blues, grays, and dark greens in the background, contrasting with the warm browns and creams of the owl, accented by silver highlights.\",\"mood_atmosphere\":\"Whimsical, enchanting, serene, and slightly mysterious.\",\"preference_score\":\"very high\",\"aesthetic_score\":\"very high\"},\"photographic_characteristics\":{\"depth_of_field\":\"Shallow, with the owl in sharp focus and the background softly blurred (bokeh).\",\"focus\":\"Sharp focus on the owl'\''s eyes and face, with a gradual fall-off of focus towards its body and the branch.\",\"camera_angle\":\"Eye-level, as if directly encountering the owl.\",\"lens_focal_length\":\"Portrait lens (e.g., 85mm-100mm) to achieve a tight crop and shallow depth of field.\"},\"style_medium\":\"photograph\",\"context\":\"This is a concept for a high-quality, photorealistic image intended for nature photography, children'\''s book illustrations, or a whimsical art print.\",\"artistic_style\":\"realistic, detailed, ethereal\"}",
    "seed": 123456789
  }'