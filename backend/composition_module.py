# composition_module.py
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap
import uuid

class CompositionModule:
    
    # Путь к шрифту (Для кириллицы нужен шрифт, поддерживающий русский язык)
    # Если на macOS/Linux, попробуйте указать системный шрифт.
    # Если это не сработает, нужно будет скачать файл .ttf (например, 'arial.ttf')
    FONT_PATH = "Arial.ttf"

    @staticmethod
    def _find_font(size):
        """Пытается загрузить шрифт. В случае ошибки использует шрифт по умолчанию."""
        try:
            # Попытка загрузить шрифт по указанному пути/имени
            return ImageFont.truetype(CompositionModule.FONT_PATH, size)
        except IOError:
            print(f"ВНИМАНИЕ: Шрифт {CompositionModule.FONT_PATH} не найден. Используется шрифт по умолчанию.")
            # Используем шрифт по умолчанию, который может не поддерживать кириллицу
            return ImageFont.load_default()

    @staticmethod
    def compose_banner(image_path: str, title: str, output_dir: str = "generated_media") -> str:
        """
        Компоновка баннера: наложение текста на изображение 1920x1080.
        """
        
        # 1. ЗАГРУЗКА/ПОДГОТОВКА ИЗОБРАЖЕНИЯ
        try:
            img = Image.open(image_path)
            # Изменяем размер до требуемого 1920x1080
            if img.size != (1920, 1080):
                 img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
        except FileNotFoundError:
            # Запасной вариант, если даже заглушка не была создана (для устойчивости)
            print(f"Ошибка: Исходный файл изображения {image_path} не найден. Создание серой заглушки.")
            img = Image.new('RGB', (1920, 1080), color = 'gray')
            draw_error = ImageDraw.Draw(img)
            draw_error.text((10,10), "ОШИБКА: Изображение отсутствует", fill=(255,255,255))
        
        draw = ImageDraw.Draw(img)
        
        # 2. НАСТРОЙКА И КОМПОЗИЦИЯ ТЕКСТА
        font_size = 90
        font = CompositionModule._find_font(font_size)
        text_color = (255, 255, 255)  # Белый цвет
        
        # Перенос строки (максимум 20 символов на строку для большого заголовка)
        wrapped_text = textwrap.fill(title, width=20)
        
        # Расположение (Верхний левый угол)
        margin_x = 70
        margin_y = 50
        x = margin_x
        y = margin_y

        # Добавляем тень (черный контур) для читаемости (критерий хакатона)
        shadow_color = (0, 0, 0)
        shadow_offset = 5 # Смещение тени
        
        # Рисуем тень
        for dx in [-shadow_offset, 0, shadow_offset]:
            for dy in [-shadow_offset, 0, shadow_offset]:
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), wrapped_text, font=font, fill=shadow_color)
                    
        # Рисуем сам текст
        draw.text((x, y), wrapped_text, font=font, fill=text_color)
        
        # 3. СОХРАНЕНИЕ ФИНАЛЬНОГО БАННЕРА
        # Используем уникальный идентификатор для имени файла
        unique_name = f"final_banner_{uuid.uuid4()}.png"
        save_path = os.path.join(output_dir, unique_name)
        
        img.save(save_path)
        
        return save_path
