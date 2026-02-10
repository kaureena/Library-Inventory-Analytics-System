# Context and Objective

## Problem statement
A library needs a simple, reliable way to:
- maintain book inventory
- register members
- issue and return books
- track overdues and fines
- export operational data for reporting

## Portfolio objective
This repository demonstrates two layers:

### v1 — Baseline operational system (BCA scope)
- clean data entry and validation rules
- issue/return workflow
- fine calculation logic
- exports for reporting

### v2 — Analytics modernisation
- repeatable ETL pipeline (raw → staged → curated)
- data quality gate with JSON + HTML reports
- warehouse/star schema artefacts
- dashboard exports as high-resolution PNG pages

## Roles (typical)
- **Librarian/Staff:** issue/return, member management, fines
- **Admin:** system setup, roles, audit reviews
- **Viewer:** read-only reporting

## What is out of scope (deliberately)
- real payment gateway
- RFID integration
- production authentication system

## Data safety
All data in this repo is synthetic (see `DATA_README.md`).
