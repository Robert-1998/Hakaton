from PIL import Image, ImageDraw, ImageFont
import os
import textwrap
import uuid

class CompositionModule:
    # ✅ ПРАВКА 1: Шрифт для Docker + кириллица
    FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" 

    @staticmethod
    def _find_font(size):
        """Загрузка шрифта с fallback."""
        try:
            return ImageFont.truetype(CompositionModule.FONT_PATH, size)
        except IOError:
            print(f"⚠️ Шрифт {CompositionModule.FONT_PATH} не найден.")
            return ImageFont.load_default()

    @staticmethod
    def compose_banner(image_path: str, title: str, output_dir: str = "generated_media") -> str:
        """Накладывает marketing_data['title'] на изображение."""
        
        # 1. Загрузка изображения
        try:
            img = Image.open(image_path)
            img = img.resize((1920, 1080), Image.Resampling.LANCZOS)  # Гарантия размера
        except FileNotFoundError:
            print(f"❌ {image_path} не найден → заглушка")
            img = Image.new('RGB', (1920, 1080), color='gray')
            draw = ImageDraw.Draw(img)
            draw.text((10,10), "ОШИБКА: Изображение отсутствует", fill=(255,255,255))
        
        draw = ImageDraw.Draw(img)
        
        # 2. Текст из JSON (title)
        display_title = title if isinstance(title, str) else title.get('title', 'Без заголовка')[:100]
        
        font_size = 90
        font = CompositionModule._find_font(font_size)
        text_color = (255, 255, 255)
        wrapped_text = textwrap.fill(display_title, width=20)
        x, y = 70, 50

        # Тень для читаемости
        shadow_color = (0, 0, 0)
        shadow_offset = 5
        for dx in [-shadow_offset, 0, shadow_offset]:
            for dy in [-shadow_offset, 0, shadow_offset]:
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), wrapped_text, font=font, fill=shadow_color)
        draw.text((x, y), wrapped_text, font=font, fill=text_color)
        
        # 3. Сохранение
        unique_name = f"final_banner_{uuid.uuid4().hex[:8]}.png"
        save_path = os.path.join(output_dir, unique_name)
        img.save(save_path, "PNG")
        
        return save_path
