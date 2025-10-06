import RPi.GPIO as GPIO
import pygame
import cv2
import time

# Initialisation de pygame
pygame.init()
screen_size = (1680, 1050)  # Taille de l'écran
screen = pygame.display.set_mode(screen_size)

# Initialisation des GPIO
BUTTONS = [4, 17, 27, 22, 18]  
GPIO.setmode(GPIO.BCM)
for button in BUTTONS:
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-down pour détecter le 3.3V

# Charger les images statiques
STATIC_IMAGES = [
    pygame.image.load("image1.jpg"),
    pygame.image.load("image2.jpg"),
    pygame.image.load("image3.jpg"),
    pygame.image.load("image4.jpg"),
    pygame.image.load("image5.jpg")
]

# Liste des vidéos
VIDEOS = [
    "video1.mp4",
    "video2.mp4",
    "video3.mp4"
]

# Fonction pour redimensionner une image en gardant le ratio
def scale_image_keep_aspect(img, screen_size):
    img_width, img_height = img.get_size()
    screen_width, screen_height = screen_size
    scale_factor = min(screen_width / img_width, screen_height / img_height)
    new_size = (int(img_width * scale_factor), int(img_height * scale_factor))
    return pygame.transform.scale(img, new_size)

# Fonction pour afficher une image statique
def display_static_image(image):
    """Affiche une image statique redimensionnée."""
    screen.fill((0, 0, 0))  # Nettoie l'écran
    image = scale_image_keep_aspect(image, screen_size)
    image_rect = image.get_rect(center=(screen_size[0] // 2, screen_size[1] // 2))
    screen.blit(image, image_rect)
    pygame.display.flip()

# Fonction pour lire une vidéo avec OpenCV et l'afficher avec pygame
def play_video(video_path):
    """Lit une vidéo et l'affiche frame par frame."""
    cap = cv2.VideoCapture(video_path)
    running = True
    clock = pygame.time.Clock()

    while cap.isOpened() and running:
        ret, frame = cap.read()
        if not ret:
            break

        # Convertir le format BGR (OpenCV) en RGB (Pygame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, screen_size)  # Redimensionner pour l'écran
        surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

        screen.blit(surf, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        clock.tick(30)  # Contrôle de la vitesse de lecture

    cap.release()

# Mapping des boutons : associer chaque bouton à une action
# Les deux premiers boutons affichent des images statiques
# Les trois suivants jouent des vidéos
MAPPING = [
    {"type": "image", "data": STATIC_IMAGES[0]},
    {"type": "image", "data": STATIC_IMAGES[1]},
    {"type": "image", "data": STATIC_IMAGES[2]},
    {"type": "image", "data": STATIC_IMAGES[3]},
    {"type": "image", "data": STATIC_IMAGES[4]}
]

# Boucle principale
try:
    print("Appuyez sur les boutons pour afficher des images ou des vidéos.")
    while True:
        for i, button in enumerate(BUTTONS):
            if GPIO.input(button) == GPIO.HIGH:  # Si le bouton est appuyé
                action = MAPPING[i]
                if action["type"] == "image":
                    display_static_image(action["data"])  # Affiche une image statique
                elif action["type"] == "video":
                    play_video(action["data"])  # Joue une vidéo
                time.sleep(0.2)  # Délai pour éviter les déclenchements multiples
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt
except KeyboardInterrupt:
    print("Programme arrêté.")
finally:
    GPIO.cleanup()
    pygame.quit()
