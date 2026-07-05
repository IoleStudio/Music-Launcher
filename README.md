# Music-Launcher
A lightweight Python desktop application built with CustomTkinter. It starts with Windows, runs in the system tray, and lets you resume your favorite playlists or songs in one click — no internet connection required.

## Features

-  Resume playlists with one click
-  Launches automatically at Windows startup
-  Runs in the system tray
-  Fully offline
-  Modern interface built with CustomTkinter

---

## Adding a playlist

To add a new playlist:

1. Open the `Music` folder.
2. Create a new folder for your playlist.
3. Place all your audio files inside this folder.
4. (Optional) Add a cover image if supported.

Example:

```text
Music/
├── Chill/
│   ├── Song1.mp3
│   ├── Song2.mp3
│   └── Song3.mp3
├── Rock/
│   ├── Track1.mp3
│   └── Track2.mp3
```

⚠️ Do not modify the folder structure, as the application relies on it to detect playlists correctly.

---

## Technologies

- Python
- CustomTkinter
- Pygame
- Mutagen

---

## License

This project is licensed under the MIT License.
