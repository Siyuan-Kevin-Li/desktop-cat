# Desktop Cat

A cute cat that lives on your Mac desktop. When you've been inactive too long, it runs around the screen to remind you to focus.

## Requirements

- macOS
- Python 3.9+

## Setup

```bash
git clone https://github.com/Siyuan-Kevin-Li/desktop-cat.git
cd desktop-cat
pip3 install -r requirements.txt
```

Go to **System Settings → Privacy & Security → Accessibility** and add Terminal.

## Run

```bash
python3 main.py
```

## Controls

- **Drag** to reposition
- **Right-click** to quit

## Configuration

Edit `config.json`:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `distraction_threshold` | Seconds of inactivity before the cat starts running | 300 |
| `eat_size` | Cat size in idle state (px) | 100 |
| `move_size` | Cat size in running state (px) | 150 |
| `move_speed` | Movement speed | 3 |
| `pause_probability` | Chance of pausing mid-run (0–1) | 0.3 |
| `sound_on_pause` | Play sound when pausing | true |
| `sound_pause_file` | Audio file to play on pause | bgm.wav |

## Credits

GIF animations by 月薪喵 (bilibili @44678789).
**Non-commercial use only. Do not redistribute or use for commercial purposes.**
