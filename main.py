import pygame
import sys
import yt_dlp as youtube_dl
import subprocess
import os
import re

# Bildschirmgröße und Farben
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT_COLOR = (0, 100, 200)
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER_COLOR = (150, 150, 150)
PLACEHOLDER_COLOR = (180, 180, 255)
PROGRESS_BAR_COLOR = (0, 200, 0)

# Pygame initialisieren
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Custom YouTube Client')
font = pygame.font.Font(None, 36)

def draw_button(text, rect, color):
    """Zeichne einen Button."""
    pygame.draw.rect(screen, color, rect)
    label = font.render(text, True, BLACK)
    screen.blit(label, (rect.x + 10, rect.y + 10))

def draw_textbox(rect, text, active):
    """Zeichne ein Textfeld."""
    color = PLACEHOLDER_COLOR if active else WHITE
    pygame.draw.rect(screen, color, rect)
    display_text = text if text else "Search..."
    text_color = BLACK if text else (150, 150, 150)
    label = font.render(display_text, True, text_color)
    screen.blit(label, (rect.x + 10, rect.y + 10))

def draw_progress_bar(progress, rect):
    """Zeichne eine Fortschrittsleiste."""
    pygame.draw.rect(screen, BLACK, rect, 2)
    inner_rect = rect.copy()
    inner_rect.width = rect.width * progress
    pygame.draw.rect(screen, PROGRESS_BAR_COLOR, inner_rect)

def search_videos(query):
    """Führe eine YouTube-Suche aus und gib die Ergebnisse zurück."""
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(f"ytsearch20:{query}", download=False)
            return result.get('entries', [])
        except Exception as e:
            print(f"Fehler beim Abrufen der Videos: {e}")
            return []

def progress_hook(d):
    """Verarbeite den Fortschritt des Downloads und zeige ihn an."""
    if d['status'] == 'downloading':
        progress_str = re.sub(r'\x1b\[[0-9;]*m', '', d['_percent_str']).strip('%')
        try:
            progress = float(progress_str) / 100
        except ValueError:
            progress = 0
        draw_progress_bar(progress, pygame.Rect(10, SCREEN_HEIGHT - 50, SCREEN_WIDTH - 20, 30))
        pygame.display.update()

def download_and_play_video(video_url):
    """Lade ein Video herunter, spiele es ab und lösche es danach."""
    ydl_opts = {
        'quiet': False,
        'format': 'best',
        'outtmpl': '%(id)s.%(ext)s',
        'progress_hooks': [progress_hook],
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=True)
            filename = f"{info['id']}.mp4"
            print(f"Download abgeschlossen: {filename}")
            
            # Display user instructions before playing video
            screen.fill(WHITE)
            instruction_text = font.render("Press ESC to quit, Space to pause.", True, BLACK)
            screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            pygame.display.flip()
            pygame.time.wait(2000)  # Wait for 2 seconds before playing

            # Play video with FFmpeg
            subprocess.run(['ffplay', '-autoexit', filename])
            os.remove(filename)
            print(f"Datei gelöscht: {filename}")
        except Exception as e:
            print(f"Fehler beim Herunterladen oder Abspielen: {e}")

def main():
    query = ''
    search_results = []
    selected_video = 0
    is_typing = False
    text_rect = pygame.Rect(10, 10, SCREEN_WIDTH - 220, 40)
    button_rect = pygame.Rect(text_rect.right + 10, 10, 200, 40)

    while True:
        screen.fill(WHITE)
        draw_textbox(text_rect, query, is_typing)
        
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            draw_button("Search", button_rect, BUTTON_HOVER_COLOR)
            if pygame.mouse.get_pressed()[0]:
                search_results = search_videos(query)
        else:
            draw_button("Search", button_rect, BUTTON_COLOR)

        y_offset = 80
        for i, result in enumerate(search_results):
            color = HIGHLIGHT_COLOR if i == selected_video else BLACK
            video_text = font.render(result['title'], True, color)
            screen.blit(video_text, (10, y_offset))
            y_offset += 40

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if is_typing:
                    if event.key == pygame.K_BACKSPACE:
                        query = query[:-1]
                    elif event.key == pygame.K_RETURN:
                        search_results = search_videos(query)
                    else:
                        query += event.unicode

                elif event.key == pygame.K_DOWN:
                    selected_video = (selected_video + 1) % len(search_results)
                elif event.key == pygame.K_UP:
                    selected_video = (selected_video - 1) % len(search_results)
                elif event.key == pygame.K_RETURN and search_results:
                    download_and_play_video(search_results[selected_video]['url'])
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    # Implement video pause functionality here (if supported by ffplay)
                    pass

            if event.type == pygame.MOUSEBUTTONDOWN:
                if text_rect.collidepoint(event.pos):
                    is_typing = True
                else:
                    is_typing = False
                    if not query:
                        query = ""
                
                for i, result in enumerate(search_results):
                    y_offset = 80 + i * 40
                    video_rect = pygame.Rect(10, y_offset, SCREEN_WIDTH - 20, 40)
                    if video_rect.collidepoint(event.pos):
                        download_and_play_video(result['url'])

if __name__ == '__main__':
    main()

