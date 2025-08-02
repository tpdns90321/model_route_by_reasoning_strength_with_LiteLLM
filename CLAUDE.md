# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
@README.md

## Development Commands

- Install dependencies: `uv sync`

## Architecture

This project implements a LiteLLM proxy callback in Python under `callbacks/model_route_callback.py`. The `ModelRouteByReasoningStrength` class extends `CustomLogger` to route requests based on `reasoning_effort` or `thinking.budget_tokens` in the API call payload.

The proxy handler instance is created at the bottom of this module.

## Project Structure

- callbacks/
  - model_route_callback.py: defines the custom callback class
- pyproject.toml: project metadata and dependencies
- test_config.yaml: configuration for testing scenarios
- README.md: project overview
