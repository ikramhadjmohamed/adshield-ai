from PIL import Image, ImageDraw, ImageFont

def make_text_image(text: str, filename: str, size=(600, 400)):
    img = Image.new("RGB", size, color="white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except OSError:
        font = ImageFont.load_default()
    draw.multiline_text((30, 30), text, fill="black", font=font, spacing=15)
    img.save(filename)

make_text_image(
    "New Air Max Collection\nFree shipping on orders\nover $50",
    "legit_ad.png"
)