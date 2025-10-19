import gpiozero as gpio
import pygame
import cv2
import time

# Initialisation de pygame
pygame.init()
#1680, 1050
#1200,900 taille minoréess
screen_size = (1260, 950) #Taille de l'écran
screen = pygame.display.set_mode(screen_size)

# Initialisation des GPIO
BUTTONS = [2,3,4,17,27,22]  
buttons = [gpio.Button(pin, pull_up=True) for pin in BUTTONS]  # Pull-down pour détecter le 3.3V

# Charger les images statiques
STATIC_IMAGES = []
for i in range(64):  # de 0 à 63 inclus
    binaire = format(i, '06b')  # convertit en binaire sur 6 bits
    name = "images0/" + str(binaire) + ".png"
    STATIC_IMAGES.append(pygame.image.load(name))


def switch_to_string(switchs):
    img_name=""
    for switch in switchs:
        img_name+=str(switch)
    return img_name

def switch_to_num(switchs):
    sum=0
    for i in range(len(switchs)):
        sum+= 2**i * switchs[i]
    return sum

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

SWITCHS=[0,0,0,0,0,0]

# Boucle principale
try:
    print("Appuyez sur les boutons pour afficher des images.")
    while True:
        SWITCHS=[0,0,0,0,0,0]
        any_pressed = False  # Variable pour vérifier si un bouton a été pressé

        for i, button in enumerate(buttons):
            if button.is_pressed:
                any_pressed = True  # On note qu'un bouton a été pressé
                SWITCHS[i]=1
                time.sleep(0.01)  # Anti-rebond

        num=switch_to_num(SWITCHS)
        display_static_image(STATIC_IMAGES[num])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt
except KeyboardInterrupt:
    print("Programme arrêté.")
finally:
    pygame.quit()
