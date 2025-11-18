import os
import sys

def check_paths():
    print("=== ПРОВЕРКА ПУТЕЙ ===")
    
    # Текущая директория
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Текущая папка: {current_dir}")
    
    # Папка проекта
    project_dir = os.path.dirname(current_dir)
    print(f"Папка проекта: {project_dir}")
    
    # Папка assets
    assets_path = os.path.join(project_dir, 'assets')
    print(f"Путь к assets: {assets_path}")
    print(f"Assets существует: {os.path.exists(assets_path)}")
    
    # Проверяем основные файлы
    files_to_check = ['main.py', 'game_manager.py', 'player.py', 'level_outline.py']
    for file in files_to_check:
        file_path = os.path.join(current_dir, file)
        print(f"{file}: {os.path.exists(file_path)}")
    
    print("======================")

if __name__ == "__main__":
    check_paths()