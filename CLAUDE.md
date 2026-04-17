# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python backend project that implements script-based data crawling, Neo4j data storage, and web API services

## Docker

Build and run with Docker:
```bash
sudo docker build -t neo4j-web .
sudo docker run -d --name neo4j-web --restart always neo4j-web
```

## Architecture

- `main.py`: Entry point (currently minimal)
- `scripts/get_Genshin_social_network.py`: Web scraper for Genshin Impact character data
  - `GenshinSocialNetwork` class handles scraping from wiki.biligame.com
  - Currently extracts character names from the character list page
  - Designed to be extended for building social network relationships