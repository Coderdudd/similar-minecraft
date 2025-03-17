from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import math
import random

app = Ursina()

Sky()

# === Block Types ===
block_types = {
    1: {'name': 'grass', 'texture': 'grass.png'},
    2: {'name': 'stone', 'texture': 'stone.png'},
    3: {'name': 'dirt', 'texture': 'dirt.png'},
    4: {'name': 'break-only', 'texture': None},
    5: {'name': 'door', 'texture': 'white_cube'}
}
selected_block = 1
doors = []  # To track door entities

# === Flying Variables ===
is_flying = False
last_space_press = 0  # To track double-tap timing

# Generate terrain
def generate_terrain(width, depth):
    boxes = []
    for i in range(width):
        for j in range(depth):
            height = int(5 * (math.sin(i / 10) + math.cos(j / 10)))
            box = Button(color=color.white, model='cube', position=(i, height, j),
                         texture=block_types[1]['texture'], parent=scene, origin_y=0.5, collider='box')
            boxes.append(box)
    return boxes

terrain = generate_terrain(43, 43)

# === Define start_game() BEFORE it's referenced ===
def start_game():
    player.position = (25, 20, 25)
    player.enabled = True
    player_hand.enabled = True
    mouse.locked = True
    menu.enabled = False
    hotbar.enabled = True

# === Define other necessary functions ===
def pause_game():
    mouse.locked = False
    player.enabled = False
    player_hand.enabled = False
    menu.title = 'Paused'
    menu.enabled = True
    hotbar.enabled = False

def resume_game():
    mouse.locked = True
    player.enabled = True
    player_hand.enabled = True
    menu.enabled = False
    hotbar.enabled = True

# === Input ===
def input(key):
    global selected_block, is_flying, last_space_press
    if key == 'i' and player.enabled:
        pause_game()
    if key == 'p':
        if not player.enabled:
            start_game()
        else:
            resume_game()
    if key == 'q' and menu.enabled:
        application.quit()

    # Hotbar keys
    if key == '1':
        selected_block = 1
        player_hand.enabled = True
        player_hand.texture = block_types[selected_block]['texture']
        update_selector()
    if key == '2':
        selected_block = 2
        player_hand.enabled = True
        player_hand.texture = block_types[selected_block]['texture']
        update_selector()
    if key == '3':
        selected_block = 3
        player_hand.enabled = True
        player_hand.texture = block_types[selected_block]['texture']
        update_selector()
    if key == '4':
        selected_block = 4
        player_hand.enabled = False
        update_selector()
    if key == '5':
        selected_block = 5
        player_hand.enabled = True
        player_hand.texture = block_types[selected_block]['texture']
        update_selector()

    # Flying toggle (double-tap spacebar)
    if key == 'space':
        current_time = time.time()
        if current_time - last_space_press < 0.3:  # If double-tapped within 0.3 seconds
            is_flying = not is_flying
            if is_flying:
                player.gravity = 0  # Disable gravity
                player.fall_speed = 0  # Stop falling
            else:
                player.gravity = 1  # Restore gravity
        last_space_press = current_time

    # Placing and interacting with blocks
    if player.enabled and not menu.enabled:
        for box in terrain:
            if box.hovered:
                if key == 'left mouse down' and selected_block != 4:  # Place blocks
                    if selected_block == 5:  # Place door
                        door = Button(color=color.white, model='cube', position=box.position + mouse.normal,
                                      texture=block_types[selected_block]['texture'], parent=scene,
                                      origin_y=0.5, collider='box', scale=(1, 2, 0.1))
                        terrain.append(door)
                        doors.append(door)
                    else:
                        new = Button(color=color.white, model='cube', position=box.position + mouse.normal,
                                     texture=block_types[selected_block]['texture'], parent=scene,
                                     origin_y=0.5, collider='box')
                        terrain.append(new)
                elif key == 'left mouse down' and selected_block == 4 and box in doors:  # Open door
                    box.rotation_y += 90
                elif key == 'right mouse down':  # Break blocks
                    if box in doors:
                        doors.remove(box)
                    terrain.remove(box)
                    destroy(box)

# === Update ===
def update():
    for cloud in clouds:
        cloud.x += time.dt * 0.1

    # Flying movement
    if is_flying:
        player.y += held_keys['space'] * time.dt * 5  # Ascend when space is held
        player.y -= held_keys['shift'] * time.dt * 5  # Descend when shift is held

# === Player and Hand ===
player = FirstPersonController()
player.enabled = False

player_hand = Entity(model='cube', texture=block_types[selected_block]['texture'], scale=0.3,
                     position=(0.5, -0.5, 1.5), parent=camera)

# === UI Hotbar ===
hotbar = Entity(parent=camera.ui, y=-0.45, z=0)
hotbar_bg = Entity(parent=hotbar, model='quad', scale=(0.4, 0.05), color=color.gray, z=0.1)

slot1 = Entity(parent=hotbar, model='quad', texture=block_types[1]['texture'],
               scale=(0.04, 0.04), x=-0.07, z=0)
slot2 = Entity(parent=hotbar, model='quad', texture=block_types[2]['texture'],
               scale=(0.04, 0.04), x=0, z=0)
slot3 = Entity(parent=hotbar, model='quad', texture=block_types[3]['texture'],
               scale=(0.04, 0.04), x=0.07, z=0)
slot4 = Entity(parent=hotbar, model='quad', texture=None, color=color.gray,
               scale=(0.04, 0.04), x=0.14, z=0)
slot5 = Entity(parent=hotbar, model='quad', texture=block_types[5]['texture'],
               scale=(0.04, 0.04), x=0.21, z=0)

selector = Entity(parent=hotbar, model='quad', color=color.azure, scale=(0.045, 0.045),
                  x=slot1.x, z=-0.01)

def update_selector():
    if selected_block == 1:
        selector.x = slot1.x
    elif selected_block == 2:
        selector.x = slot2.x
    elif selected_block == 3:
        selector.x = slot3.x
    elif selected_block == 4:
        selector.x = slot4.x
    elif selected_block == 5:
        selector.x = slot5.x

# === Menu ===
menu = WindowPanel(title='Main Menu', content=(
    Button('Play (P)', on_click=start_game),  # References start_game(), now fixed
    Button('Quit (Q)', on_click=application.quit)
), enabled=True, popup=True)
menu.scale *= 1.2
menu.position = Vec2(0, 0)

# === Moving Clouds ===
clouds = []

def generate_clouds(num_clouds):
    for _ in range(num_clouds):
        x = random.randint(0, 50)
        z = random.randint(0, 50)
        y = random.randint(25, 35)
        size = random.randint(2, 4)

        for i in range(size):
            for j in range(size):
                cloud_block = Entity(
                    model='cube',
                    color=color.white,
                    position=(x + i, y, z + j),
                    scale=1,
                    collider=None
                )
                clouds.append(cloud_block)

generate_clouds(10)

# Start UI hidden
hotbar.enabled = False

app.run()
