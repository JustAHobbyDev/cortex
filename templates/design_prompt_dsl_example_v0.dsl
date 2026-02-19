# Design Prompt DSL v0 example
# Compile with:
# python3 scripts/design_prompt_dsl_compile_v0.py \
#   --dsl-file templates/design_prompt_dsl_example_v0.dsl \
#   --out-file templates/design_prompt_dsl_example_v0.json

id saas_futurist_dsl_v0
version v0
name SaaS Futurist DSL Example

token layout.grid | 12-column asymmetric grid
token layout.spacing | 96px vertical rhythm
token layout.structure | hero-dominant above fold
set layout.density | "airy"
set layout.rhythm | "alternating panel cadence"
set layout.narrative_flow | "problem-to-solution arc"

token typography.hero | oversized neo-grotesk hero
set typography.body | "18px high x-height body face with line-height breathing room"
set typography.families | ["Space Grotesk", "IBM Plex Sans"]
set typography.scale | "optical size contrast"
set typography.weight_strategy | "weight-contrast ladder"
token typography.tracking_strategy | tight display tracking

token surface.base | charcoal base layer
token surface.accent | electric accent glow
token surface.panels | frosted glass panel
token surface.depth_model | hybrid
token surface.shadows | ambient shadow cloud
add surface.textures | "restrained gradient diffusion"
add surface.textures | "textured haze overlay"

token motion.scroll | fade-up staggered reveal
token motion.hover | 200ms ease-out hover scale
token motion.timing_profile | snappy timing profile
add motion.interaction_signatures | "magnetic CTA pull"
add motion.interaction_signatures | "card lift hover"
set motion.reduced_motion_strategy | "opacity-only fallback"

token influence.primary | Swiss grid discipline
token influence.secondary | SaaS futurism
token influence.style_cluster | tech minimalism cluster
add influence.anti_patterns | "avoid ornamental motion"
add influence.anti_patterns | "avoid gradient oversaturation"

score clarity | 9
score novelty | 7
score usability | 8
score brand_fit | 8
