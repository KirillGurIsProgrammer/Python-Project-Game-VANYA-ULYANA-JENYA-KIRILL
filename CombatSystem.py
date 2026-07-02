from Gun import Freeze
from sound_manager import SoundManager


class CombatSystem:

    ZOMBIE_ATTACK_INTERVAL = 0.5

    def __init__(self):
        self._zombie_hit_timers: dict[int, float] = {}
        self.sound = SoundManager()

    def update(self, dt: float,
               hero, alive_zombies: list, projectiles: list,
               enemy_projectiles: list | None = None) -> int:
        score_gained = self._resolve_projectiles(projectiles, alive_zombies, hero)
        self._resolve_melee(dt, hero, alive_zombies)
        if enemy_projectiles:
            self._resolve_enemy_projectiles(enemy_projectiles, hero)
        return score_gained

    def reset(self) -> None:
        self._zombie_hit_timers.clear()

    def _resolve_projectiles(self, projectiles: list,
                              alive_zombies: list, hero) -> int:
        score_gained = 0
        for p in projectiles:
            for zombie in alive_zombies:
                if not zombie.is_alive:
                    continue
                if not zombie.rect.colliderect(p.rect):
                    continue

                if p.kind == "ice":
                    zombie.hit_by_ice()
                    zombie.take_damage(p.damage)
                    self.sound.play_hit()
                    hero.hp = min(
                        hero.max_hp,
                        hero.hp + Freeze.HEAL_AMOUNT // 3,
                    )
                elif p.kind == "fear":
                    zombie.afraid()
                else:
                    zombie.take_damage(p.damage)
                    self.sound.play_hit()

                if not zombie.is_alive:
                    score_gained += 10
                    self.sound.play_enemy_death()

                p.alive = False
                break

        return score_gained

    def _resolve_enemy_projectiles(self, enemy_projectiles: list, hero) -> None:
        for p in enemy_projectiles:
            if not p.alive:
                continue
            if hero.rect.colliderect(p.rect):
                hero.take_damage(p.damage)
                self.sound.play_player_hit()
                p.alive = False

    def _resolve_melee(self, dt: float, hero, alive_zombies: list) -> None:
        for zombie in alive_zombies:
            zid = id(zombie)
            if not zombie.is_touching(hero.rect):
                self._zombie_hit_timers[zid] = 0.0
                continue

            timer = self._zombie_hit_timers.get(zid, 0.0) - dt
            if timer <= 0:
                hero.take_damage(zombie.attack)
                self.sound.play_player_hit()
                timer = self.ZOMBIE_ATTACK_INTERVAL
            self._zombie_hit_timers[zid] = timer

        # чистим мёртвых
        alive_ids = {id(z) for z in alive_zombies}
        self._zombie_hit_timers = {
            k: v for k, v in self._zombie_hit_timers.items() if k in alive_ids
        }