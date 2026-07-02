import pygame
import os

class SoundManager: 
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        self.sounds = {}
        self._load_sounds()
        self.music_playing = False
    
    def _load_sounds(self):
        sound_files = {
            'attack': 'sounds/attack.wav',
            'hit': 'sounds/hit.wav',
            'player_hit': 'sounds/player_hit.wav',
            'death': 'sounds/death.wav',
            'step': 'sounds/step.wav',
            'enemy_death': 'sounds/enemy_death.wav',
            'heal': 'sounds/heal.wav',
            'portal': 'sounds/portal.wav',
            'level_up': 'sounds/level_up.wav'
        }
        
        for name, path in sound_files.items():
            try:
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
                else:
                    self.sounds[name] = None
                    print(f"Предупреждение: Звук не найден - {path}")
            except Exception as e:
                print(f"Ошибка загрузки звука {name}: {e}")
                self.sounds[name] = None
    
    def play(self, sound_name, volume=0.5, loops=0):
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].set_volume(volume)
            self.sounds[sound_name].play(loops)
    
    def play_attack(self):
        self.play('attack', 0.2)
    
    def play_hit(self):
        self.play('hit', 0.3)
    
    def play_player_hit(self):
        self.play('player_hit', 0.3)
    
    def play_death(self):
        self.play('death', 0.5)
    
    def play_step(self):
        self.play('step', 0.1)
    
    def play_enemy_death(self):
        self.play('enemy_death', 0.3)
    
    def play_heal(self):
        self.play('heal', 0.5)
    
    def play_portal(self):
        self.play('portal', 0.3)
    
    def play_level_up(self):
        self.play('level_up', 0.2)
    
    def play_music(self, music_path, volume=0.3, loops=-1):
        try:
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(loops)
                self.music_playing = True
            else:
                print(f"Музыка не найдена: {music_path}")
        except Exception as e:
            print(f"Ошибка загрузки музыки: {e}")
    
    def stop_music(self):
        pygame.mixer.music.stop()
        self.music_playing = False
    
    def pause_music(self):
        if self.music_playing:
            pygame.mixer.music.pause()
    
    def unpause_music(self):
        if self.music_playing:
            pygame.mixer.music.unpause()