# Changelog

## SemVer v1.7.11

- 2026-11-06 (d9e94f6): fix(kartenlauf): Dateinamen im Auftrag verbergen, damit Aider keine Dateien nachlÃ¤dt

## SemVer v1.7.10

- 2026-11-06 (486167d): fix(plan): Stufen-Regel fÃ¼r A02 korrigiert, Einstellungen fÃ¼r qwen3-coder
- 2026-11-06 (91eb2f8): fix(kartenlauf): Platzhalter-Hinweise und automatisches Bearbeitungsformat
- 2026-11-05 (e3141dc): fix(kartenlauf): schlanker Kontext und grÃ¶ÃŸeres Kontextfenster
- 2026-11-05 (d2b1993): fix: fix errors
- 2026-11-05 (d4c3c6d): fix(kartenlauf): Conventional Commits, Vorab-PrÃ¼fung und nicht-interaktive Hooks

## SemVer v1.7.9

- 2026-11-05 (efd97a2): fix: fix phase plan to align with the bible
- 2026-11-05 (cba645d): feat(karte-a01): Proben- und Regions-SchlÃ¼ssel angleichen
- 2026-11-05 (d627406): fix: fix card run
- 2026-11-05 (5383147): feat: add new infos and run script for the first test card run with ollama

## SemVer v1.7.8

- 2026-11-04 (d6559c5): feat: re-evaluate all implementation plans and align them with the general direction

## SemVer v1.7.7

- 2026-11-03 (86a72b5): fix: adjust phase 2 and phase 3 plans to align with the current bible implementation

## SemVer v1.7.6

- 2026-11-03 (b0613e8): feat: add new third implementation plan to incorporate more of the absurd and dark humor into the game

## SemVer v1.7.5

- 2026-11-02 (eef0533): feat: expand bible with a phase two plan where the official wiki of noita was taken into consideration to generate new and exciting game contents

## SemVer v1.7.4

- 2026-11-02 (1b68965): fix: update gitignore to prevent reference files from getting uploaded
- 2026-11-01 (f1c6054): fix: fix github actions to prevent the temporary tests from failing the suite

## SemVer v1.7.3

- 2026-11-01 (e672d5e): Merge pull request #22 from TGBox/plan-align
- 2026-11-01 (c7129f3): fix: re-align the implementation plans from claude with the new additions that have been made by gemini - update bible to reflect and consolidate the changes into a coherent plan (hopefully - has to be double checked by claude before real implementation can begin), fix implementation cards not being within the capped scope

## SemVer v1.7.2

- 2026-11-01 (5cd912e): feat: add plan to align the plans

## SemVer v1.7.1

- 2026-11-01 (2d732ea): fix: fix markdownlint error in changelog
- 2026-11-01 (6ffcc6c): feat: add critique document from claude review

## SemVer v1.7.0

- 2026-11-01 (31a29a0): Merge pull request #21 from TGBox/develop
- 2026-11-01 (c6cf8dc): Merge branch 'develop' of <https://github.com/TGBox/py-noita-claude> into develop
- 2026-11-01 (ea02e5f): feat: add huge amount of connected test suite definitions to ensure that the smaller models adhere to a clear pattern that alllows everything to work in the end

## SemVer v1.6.0

- 2026-11-01 (813c192): Merge pull request #20 from TGBox/develop
- 2026-11-01 (41a95cb): Merge pull request #19 from TGBox/master
- 2026-11-01 (607167f): Merge pull request #18 from TGBox/develop
- 2026-11-01 (5e7eda7): feat: update planning documents to separate them into 134 individual S-cards, with 60-80 lines code change each, 1-2 target files + 1 testfile, context per card smaller than 15 kb and without any open design questions

## SemVer v1.5.0

- 2026-11-01 (a380da9): Merge pull request #17 from TGBox/develop
- 2026-11-01 (420c686): Merge pull request #16 from TGBox/master
- 2026-11-01 (f6aaeef): feat: update planning documents to prepare for creating only S cards in the next step

## SemVer v1.4.1

- 2026-11-01 (48a9c72): Merge pull request #15 from TGBox/develop
- 2026-11-01 (8347b94): feat: update planning documents with atomic tasks to get handled by smaller models

## SemVer v1.4.0

- 2026-11-01 (eb0838d): feat: add first new universe with world rules, enemies and rough idea concepts, including new controls in the sandbox for testing the new content, fix: update plan to prevent already noticed issue with global fires in the new world type

## SemVer v1.3.0

- 2026-11-01 (5c4b81d): Merge pull request #14 from TGBox/develop
- 2026-11-01 (f286afc): feat: update implementation plan for cloita-interdimensional

## SemVer v1.2.2

- 2026-11-01 (d0e83e5): Merge pull request #13 from TGBox/develop
- 2026-11-01 (18eae22): fix: apply fixes to remove markdownlint errors in the documentation plan

## SemVer v1.2.1

- 2026-11-01 (67e9978): feat: add implementation plan for the new game offshoot

## SemVer v1.2.0

- 2026-11-01 (8656efd): Merge pull request #12 from TGBox/develop
- 2026-11-01 (8a690f1): fix: fix pickup radius being way to small, fix: fix single pixels getting leftover after fire or explosions, fix: unknown spells are now highlighted to avoid inventory clutter, feat: add save and exit option, feat: add new sorting criteriea for inventory spells, fix: remove healing properties from blood for debuf reasons

## SemVer v1.1.2

- 2026-10-31 (1f99195): Merge pull request #11 from TGBox/develop
- 2026-10-31 (d78fbd6): fix: add new row to the bag, allow spells to stack in the inventory, add sorting to the bag, add fast transfer via double or right clicking

## SemVer v1.1.1

- 2026-10-31 (e575e91): feat: update README, create new roadmap for the upcoming implementation

## SemVer v1.1.0

- 2026-10-31 (694c955): Merge pull request #10 from TGBox/develop
- 2026-10-31 (fb77ee9): feat: add mouse on hover indicator for materials, perks, enemies, fluids, etc., feat: add logging mode to allow for better debugging, feat: add controller input, feat: add control schema adjustment option, fix: fix phioles not getting filled with key s, fix: fix bag access getting denied instead of only wand rebuilding during levels, fix: fix not being able to drop items, fix: menus not having real ui elements and only relying on pure text, fix: fix bag having too little slots

## SemVer v1.0.0

- 2026-10-31 (6c5a344): Merge pull request #9 from TGBox/develop
- 2026-10-31 (1b3b7b5): feat: complete big auto run with claude, feat: add over 400 spells, add 32 biomes, add boss battles, add rigid body physics, add parallel worlds in the east and west

## SemVer v0.4.2

- 2026-10-30 (0241b79): Merge pull request #8 from TGBox/develop
- 2026-10-30 (3264d89): Merge pull request #7 from TGBox/master
- 2026-10-30 (158c0a7): fix: fix ruff errors in Github action

## SemVer v0.4.1

- 2026-10-30 (a94a066): Merge pull request #6 from TGBox/develop
- 2026-10-30 (cad9a5f): Merge pull request #5 from TGBox/master
- 2026-10-30 (c21d87d): feat: add menu, save and pause options

## SemVer v0.4.0

- 2026-10-30 (9d4eb72): Merge pull request #4 from TGBox/develop
- 2026-10-30 (90ddf1d): Merge pull request #3 from TGBox/master
- 2026-10-30 (039e1ac): fix: fix terrain leaving single pixels behind, fix harsh sound files

## SemVer v0.3.2

- 2026-10-30 (51edea7): Merge pull request #2 from TGBox/develop
- 2026-10-30 (9332f19): feat: implement more mutations as wand spells

## SemVer v0.3.1

- 2026-10-30 (285dda0): Merge pull request #1 from TGBox/develop
- 2026-10-30 (d991861): feat: extend core mechanics with wands

## SemVer v0.3.0

- 2026-10-30 (6fb8604): feat: add new theme and interactions

## SemVer v0.2.1

- 2026-10-30 (eb03274): feat(core): add basic physics and interactions

## SemVer v0.1.0

- 2026-10-30 (4c05acc): initial commit
