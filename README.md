# Frost Runner - Princess Aria

A gentle running and jumping game for young children (age ~6). All artwork is drawn in code and all sounds are generated at runtime, so there are no copyrighted assets and no external files.

## Download the game (no Python needed)

Open the **[Releases](../../releases)** page, download `FrostRunner.exe`, and double-click it.

## Controls

| Key | Action |
|---|---|
| `SPACE` / `UP ARROW` / mouse click | Jump |
| `ENTER` | Start / play again |
| `ESC` | Pause |
| `F11` | Fullscreen |

## Gameplay

- Princess Aria runs automatically across a snowy world.
- Jump over logs, ice blocks and friendly snowmen.
- Collect stars: white star = 10 points, gold star = 50 points.
- Three hearts; losing them shows a happy score screen, never a scary one.
- No ads, no purchases, no accounts, no internet required.

## How the EXE is built

GitHub Actions runs PyInstaller on a Windows runner using `--onefile --windowed`, then attaches the executable to a release automatically.
