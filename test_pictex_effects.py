"""Test pictex library for modern text effects"""
from pictex import Canvas, Row, Column, Text, Shadow, LinearGradient
import os

os.makedirs("test_outputs", exist_ok=True)

# Test 1: Neon glow effect
print("1. Neon glow...")
canvas1 = (
    Canvas()
    .size(1080, 400)
    .background_color("#1a1a2e")
    .font_size(72)
    .color("white")
    .text_shadows(
        Shadow(offset=(0, 0), blur_radius=5, color="#ff006e"),
        Shadow(offset=(0, 0), blur_radius=15, color="#ff006e"),
        Shadow(offset=(0, 0), blur_radius=30, color="#ff006e"),
    )
)
canvas1.render("Холодные продажи в B2B").save("test_outputs/01_neon_glow.png")
print("✓")

# Test 2: Outline stroke
print("2. Outline stroke...")
canvas2 = (
    Canvas()
    .size(1080, 400)
    .background_color("#0f0f23")
    .font_size(64)
    .color("white")
    .text_stroke(3, "#ff6b35")
)
canvas2.render("47 сделок за 3 месяца").save("test_outputs/02_outline_stroke.png")
print("✓")

# Test 3: Gradient background
print("3. Gradient background...")
canvas3 = (
    Canvas()
    .size(1080, 600)
    .background_color(LinearGradient(["#667eea", "#764ba2"]))
    .font_size(56)
    .color("white")
    .text_shadows(Shadow(offset=(2, 4), blur_radius=10, color="#00000088"))
    .padding(60)
)
canvas3.render("Clay находит ЛПР, которых нет в базах").save("test_outputs/03_gradient_bg.png")
print("✓")

# Test 4: Pill button
print("4. Pill button...")
cta_pill = (
    Text("Забрать гайд →")
    .font_size(36)
    .color("white")
    .padding(20, 50)
    .background_color(LinearGradient(["#f72585", "#7209b7"]))
    .border_radius(40)
)
hook_text = (
    Text("Я потратил $50K на тесты")
    .font_size(52)
    .color("white")
    .text_shadows(Shadow(offset=(0, 0), blur_radius=20, color="#667eea"))
)
content4 = Column(hook_text, cta_pill).align_items("center")
canvas4 = Canvas().size(1080, 500).background_color("#1e1e2f")
canvas4.render(content4).save("test_outputs/04_pill_button.png")
print("✓")

# Test 5: Full ad
print("5. Full ad mockup...")
hook5 = (
    Text("90% холодных писем игнорируют")
    .font_size(54)
    .color("white")
    .text_shadows(
        Shadow(offset=(0, 0), blur_radius=10, color="#f72585"),
        Shadow(offset=(0, 0), blur_radius=30, color="#f7258580"),
    )
)
body5 = (
    Text("После 12 лет в B2B я понял:\nдело не в количестве, а в точности")
    .font_size(36)
    .color("#cccccc")
    .text_shadows(Shadow(offset=(2, 2), blur_radius=5, color="#00000088"))
)
cta5 = (
    Text("Забрать гайд →")
    .font_size(34)
    .color("white")
    .padding(25, 50)
    .background_color(LinearGradient(["#f72585", "#7209b7"]))
    .border_radius(40)
)
content5 = Column(hook5, body5, cta5).align_items("center").padding(80)
canvas5 = Canvas().size(1080, 1080).background_color(LinearGradient(["#0f0c29", "#302b63", "#24243e"]))
canvas5.render(content5).save("test_outputs/05_full_ad.png")
print("✓")

print("\n✅ Done! Check test_outputs/")
