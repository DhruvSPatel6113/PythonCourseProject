# Python Course Project -- Poker Game

## Requirements

- Python **3.12** or **3.13** (NOTE: **NOT** compatible with Python 3.14)
- [pygame](https://pygame.org) library  
  Install it globally (virtual environments not required):

  ```bash
  pip install pygame
  ```

## How to Run

Simply run the `main.py` file from the project folder:

```bash
python main.py
```

## Game Instructions

- The bet is always set at **10**.
- Click **Deal** to start a new hand.
- Select cards by clicking on them to hold, then click **Draw**.
- After the draw, click **New Hand** to reset.
- Click **Deal** again to start the next round.

## Sound Support

The game supports background music and sound effects such as clicks and wins.  
To enable sounds:

- Place the appropriate sound files in the `assets/sounds` directory:
  - `deal.wav`
  - `flip.wav`
  - `click.wav`
  - `win.wav`

Make sure each of the above files exists in `assets/sounds`.

Enjoy playing!
