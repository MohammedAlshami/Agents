# Humanize Agent System Prompts

This directory contains the modular system prompts for the Humanize Agent, designed to transform AI-generated text into human-like writing through constraint-driven prompting.

## Structure

- `main_system_prompt.py` - Main system prompt that combines all sub-prompts
- `sub_prompts/` - Individual focused sub-system prompts
- `few_shot_examples/` - High-quality human writing examples
- `style_presets/` - Predefined style configurations

## Architecture

The humanize agent uses a hierarchical prompt structure with six functional blocks:

1. **Core Identity and Precedence** - Establishes persona and rule priority
2. **Negative Constraints** - Prevents known AI writing patterns
3. **Statistical Tuning** - Enforces perplexity and burstiness countermeasures
4. **Rhetorical Mandates** - Injects human subjectivity and emotion
5. **Few-Shot Style Guide** - Provides examples for style replication
6. **Input/Output Processing** - Governs task execution

## Usage

The main system prompt combines all sub-prompts and should be used as the primary system message for the humanize agent. Individual sub-prompts can be used for specific humanization tasks or testing.
