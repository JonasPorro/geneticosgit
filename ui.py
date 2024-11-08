import threading
import pygame
from GPT import get_summary
from config import CELL_SIZE, SCREEN_SIZE,BLACK,WHITE,RED,GREEN,font_large, font, font_huge
from utils import divide_text, get_colour_name

def show_initial_screen():
  screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
  pygame.display.set_caption("Configuración Inicial")
  
  # Parámetros y valores por defecto
  params = {
      "population_size": 10,
      "carnivore_percentage": 20,
      "initial_food": 20,
      "size_min": 10,
      "size_max": 35,
      "speed_min": 1.0,
      "speed_max": 4.0,
      "save_csv": True
  }
  random_carnivore = False

  # Loop de configuración
  selected_option = 0
  options_keys = list(params.keys())

  while True:
      screen.fill(WHITE)
      
      screen.blit(font_huge.render("Bienvenido a la simulación de sociedades", True, BLACK), (150, 50))
      screen.blit(font_large.render("Presiona Enter para iniciar, o flechas para ajustar valores.", True, BLACK), (150, 100))
      
      # Mostrar opciones
      options_text = [
          f"Tamaño de Población: {params['population_size']}",
          f"% Carnívoros: {params['carnivore_percentage']} {'(Aleatorio)' if random_carnivore else ''}",
          f"Comida inicial: {params['initial_food']}",
          f"Tamaño mínimo: {params['size_min']}",
          f"Tamaño máximo: {params['size_max']}",
          f"Velocidad mínima: {params['speed_min']}",
          f"Velocidad máxima: {params['speed_max']}",
          f"Guardar CSV: {'Sí' if params['save_csv'] else 'No'}"
      ]
      
      for i, text in enumerate(options_text):
          color = BLACK if i != selected_option else (255, 0, 0)
          screen.blit(font.render(text, True, color), (150, 160 + i * 40))
          
      screen.blit(font_large.render("Durante la simulación puede presionar ESC para detenerla.", True, BLACK), (150, 490))
      
      pygame.display.flip()
      
      # Eventos para cambiar valores
      for event in pygame.event.get():
          if event.type == pygame.QUIT:
              pygame.quit()
              return params, random_carnivore
          elif event.type == pygame.KEYDOWN:
              if event.key == pygame.K_RETURN:
                  return params, random_carnivore
              elif event.key == pygame.K_DOWN:
                  selected_option = (selected_option + 1) % len(options_keys)
              elif event.key == pygame.K_UP:
                  selected_option = (selected_option - 1) % len(options_keys)
              elif event.key == pygame.K_RIGHT:
                  option = options_keys[selected_option]
                  if option == "population_size":
                      params["population_size"] += 5
                  elif option == "carnivore_percentage":
                      params["carnivore_percentage"] = min(100, params["carnivore_percentage"] + 5)
                  elif option == "initial_food":
                      params["initial_food"] = min(100, params["initial_food"] + 1)
                  elif option == "size_min":
                      params["size_min"] = max(1, params["size_min"] + 1)
                  elif option == "size_max":
                      params["size_max"] = min(100, params["size_max"] + 1)
                  elif option == "speed_min":
                      params["speed_min"] = max(1, params["speed_min"] + 1)
                  elif option == "speed_max":
                      params["speed_max"] = min(10.0, params["speed_max"] + 1)
                  elif option == "save_csv":
                      params["save_csv"] = not params["save_csv"]
                  elif option == "carnivore_percentage":
                      random_carnivore = not random_carnivore
              elif event.key == pygame.K_LEFT:
                  option = options_keys[selected_option]
                  if option == "population_size":
                      params["population_size"] = max(5, params["population_size"] - 5)
                  elif option == "carnivore_percentage":
                      params["carnivore_percentage"] = max(0, params["carnivore_percentage"] - 5)
                  elif option == "initial_food":
                      params["initial_food"] = max(1, params["initial_food"] - 1)
                  elif option == "size_min":
                      params["size_min"] = max(1, params["size_min"] - 1)
                  elif option == "size_max":
                      params["size_max"] = max(params["size_min"], params["size_max"] - 1)
                  elif option == "speed_min":
                      params["speed_min"] = max(1, params["speed_min"] - 1)
                  elif option == "speed_max":
                      params["speed_max"] = max(params["speed_min"], params["speed_max"] - 1)
                  elif option == "save_csv":
                      params["save_csv"] = not params["save_csv"]
                  elif option == "carnivore_percentage":
                      random_carnivore = not random_carnivore
                    
def visualize_population(screen, population, food_sources):
  """Visualiza la población y la comida en la ventana de pygame."""
  screen.fill(WHITE)

  # Dibujar comida (verde)
  for food in food_sources:
      pygame.draw.circle(screen, GREEN, (food.x * CELL_SIZE + CELL_SIZE // 2, food.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)

  # Dibujar criaturas (en colores según el padre)
  for creature in population:
      if creature.alive:
          # Dibujar la criatura como un círculo con el tamaño de la criatura
          pygame.draw.circle(screen, creature.parent_color, 
                              (creature.x * CELL_SIZE + CELL_SIZE // 2, creature.y * CELL_SIZE + CELL_SIZE // 2), 
                              creature.size)
          # Dibujar el ID de la criatura sobre su cabeza
          id_text = font.render(str(creature.id) , True, RED if creature.is_carnivore else BLACK)
          screen.blit(id_text, (creature.x * CELL_SIZE, creature.y * CELL_SIZE))

  pygame.display.flip()

def show_statistics(screen, population):
  """Muestra las estadísticas de las criaturas en la pantalla final."""
  # Ordenar las estadísticas
  top_lived = sorted(population, key=lambda x: x.time_alive, reverse=True)[:3]
  top_eaten = sorted(population, key=lambda x: x.food_eaten_total, reverse=True)[:3]
  top_reproductions = sorted(population, key=lambda x: x.reproductions, reverse=True)[:3]
  top_families = []
  for creature in population:
      found = False
      for color in top_families:
          if color[0] == creature.parent_color:
              found = True
              
      if not found:
          occurences = 0
          for creature2 in population:
              if creature2.parent_color == creature.parent_color:
                  occurences += 1
          top_families.append((creature.parent_color, occurences, creature.is_carnivore, creature.personality))
      
  top_families = sorted(top_families, key=lambda x:x[1], reverse=True)[:3]
  
  screen.fill(WHITE)

  # Títulos
  screen.blit(font_large.render("Top 3 Criaturas por Tiempo Vivido", True, BLACK), (50, 70))
  screen.blit(font_large.render("Top 3 Criaturas por Comidas", True, BLACK), (50, 250))
  screen.blit(font_large.render("Top 3 Criaturas por Reproducciones", True, BLACK), (50, 420))
  screen.blit(font_large.render("Top 3 Familias por tamaño", True, BLACK), (50, 590))

  # Top 3 por tiempo vivido
  for i, creature in enumerate(top_lived):
      text = f"ID {creature.id} - Vivido: {round(creature.time_alive, 2)}s - Vel: {round(creature.speed, 2)} - Tam: {creature.size} - Familia: {get_colour_name(creature.parent_color)}"
      screen.blit(font.render(text, True, creature.parent_color), (50, 100 + i * 45))
      text = f"Carnivoro: {creature.is_carnivore} - personalidad: {creature.personality}"
      screen.blit(font.render(text, True, creature.parent_color), (50, 125 + i * 45))
      
  # Top 3 por comidas
  for i, creature in enumerate(top_eaten):
      text = f"ID {creature.id} - Comidas: {creature.food_eaten_total} - Vel: {round(creature.speed, 2)} - Tam: {creature.size} - Familia: {get_colour_name(creature.parent_color)}"
      screen.blit(font.render(text, True, creature.parent_color), (50, 270 + i * 45))
      text = f"Carnivoro: {creature.is_carnivore} - personalidad: {creature.personality}"
      screen.blit(font.render(text, True, creature.parent_color), (50, 295 + i * 45))

  # Top 3 por reproducciones
  for i, creature in enumerate(top_reproductions):
      text = f"ID {creature.id} - Reproducciones: {creature.reproductions} - Vel: {round(creature.speed, 2)} - Tam: {creature.size} - Familia: {get_colour_name(creature.parent_color)}"
      screen.blit(font.render(text, True, creature.parent_color), (50, 440 + i * 45))
      text = f"Carnivoro: {creature.is_carnivore} - personalidad: {creature.personality}"
      screen.blit(font.render(text, True, creature.parent_color), (50, 465 + i * 45))

  # Top 3 familias
  for i, family in enumerate(top_families):
      text = f"Familia {get_colour_name(family[0])} - Integrantes totales: {family[1]} - Carnivoros: {family[2]} - Personalidad: {family[3]}"
      screen.blit(font.render(text, True, family[0]), (50, 610 + i * 30))

    # Botón para Volver al Menú Inicial
  button_restart = pygame.Rect((SCREEN_SIZE // 2 - 100, SCREEN_SIZE - 100, 250, 50))
  pygame.draw.rect(screen, RED, button_restart)
  button_text = font_large.render("Reiniciar Simulación", True, WHITE)
  screen.blit(button_text, (button_restart.x + 10, button_restart.y + 10))
  
    # Botón para generar resumen con IA
  button_summary = pygame.Rect((SCREEN_SIZE // 2 - 100, SCREEN_SIZE - 170, 250, 50))
  pygame.draw.rect(screen, GREEN, button_summary)
  button_text = font_large.render("Generar resumen", True, WHITE)
  screen.blit(button_text, (button_summary.x + 10, button_summary.y + 10))

  pygame.display.flip()

  summary = False
  
  # Detectar clic en el botón
  waiting = True
  while waiting:
      for event in pygame.event.get():
          if event.type == pygame.QUIT:
              pygame.quit()
              exit()
          elif event.type == pygame.MOUSEBUTTONDOWN:
              if button_restart.collidepoint(event.pos):
                  waiting = False  # Salir del bucle para volver al menú inicial
              elif button_summary.collidepoint(event.pos):
                  waiting = False
                  summary = True
          elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
              waiting = False
  
  if summary:
    display_summary(screen)

def display_summary(screen):
  screen.fill(WHITE)
  summary = []
  hilo = threading.Thread(target=get_summary, args=(summary,))
  hilo.start()
  
  while len(summary) == 0:
    screen.blit(font_large.render("Generando...", True, BLACK), (SCREEN_SIZE // 2 - 100, SCREEN_SIZE - 100))
    pygame.display.flip()
  
  summary_divided = divide_text(summary[0], 12)
  
  for i, line in enumerate(summary_divided):
    screen.blit(pygame.font.Font(None, 27).render(line, True, BLACK), (50, 70 + i*20))
  
    # Botón para Volver al Menú Inicial
  button_restart = pygame.Rect((SCREEN_SIZE // 2 - 100, SCREEN_SIZE - 100, 250, 50))
  pygame.draw.rect(screen, RED, button_restart)
  button_text = font_large.render("Reiniciar Simulación", True, WHITE)
  screen.blit(button_text, (button_restart.x + 10, button_restart.y + 10))
  
  pygame.display.flip()
  
  waiting = True
  while waiting:
      for event in pygame.event.get():
          if event.type == pygame.QUIT:
              pygame.quit()
              exit()
          elif event.type == pygame.MOUSEBUTTONDOWN:
              if button_restart.collidepoint(event.pos):
                  waiting = False  # Salir del bucle para volver al menú inicial
          elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
              waiting = False
  