# Azazeal_Anime_Characters_ComfyUI
 Anime Character nodes


This custom node for **ComfyUI** adds an **Anime Character Selector** component that allows you to easily choose a character from an anime title node using a dropdown interface.



---

## 📦 Features

- Select a **character** from a dropdown list for the chosen anime
- Outputs a ready-to-use prompt string for image generation
- Automatically loads `.json` character data from `anime_data/YourGroup/*.json`
- character_list.html is the entire list of each avaible anime and their characters
![workflow_example](https://github.com/user-attachments/assets/43c49536-527c-4cb8-b5eb-018a48ae99d6)
![ComfyUI_00024_](https://github.com/user-attachments/assets/f8101083-fb7f-456d-b1fc-1ecfc7d299aa)

---

## 🔧 Installation

Clone this repository into your ComfyUI `custom_nodes` folder:

```bash
git clone https://github.com/azazeal04/Azazeal_Anime_Characters_ComfyUI.git
```

Once cloned, restart ComfyUI. The node will appear in the ComfyUI interface under the **"Anime_Charater"** category (e.g., `Anime_Character/AnimeName`).

---

## 🧩 Node Output

The node outputs a **combined prompt string** like:

```
"Sasuke Uchiha from Naruto"
```

You can connect this directly to a text encoder node such as **CLIPTextEncode** or similar in your ComfyUI workflow.

---

## ✅ Requirements

- Python 3.10+
- A working ComfyUI installation

---

## 📚 License

MIT License — © 2025 Azazeal

---

## 🌐 GitHub Repository

https://github.com/azazeal04/Azazeal_Anime_Characters_ComfyUI.git

