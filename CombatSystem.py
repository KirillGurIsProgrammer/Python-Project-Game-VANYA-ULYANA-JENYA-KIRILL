from Gun import MagicStick


class CombatSystem:


    ZOMBIE_ATTACK_INTERVAL = 0.8  # секунды между ударами

    def __init__(self):
        self._zombie_hit_timers: dict[int, float] = {}

    #  Публичные методы                                                    #

    def update(self, dt: float,
               hero, alive_zombies: list, projectiles: list,
               enemy_projectiles: list | None = None) -> int:
        score_gained = self._resolve_projectiles(projectiles, alive_zombies, hero)
        self._resolve_melee(dt, hero, alive_zombies)
        if enemy_projectiles:
            self._resolve_enemy_projectiles(enemy_projectiles, hero)
        return score_gained

    def reset(self) -> None:
        """Сбрасывает таймеры урона (при смене уровня)."""
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
                    hero.hp = min(
                        hero.max_hp,
                        hero.hp + MagicStick.HEAL_AMOUNT // 3,
                    )
                elif p.kind == "fear":
                    zombie.afraid()
                else:
                    zombie.take_damage(p.damage)

                if not zombie.is_alive:
                    score_gained += 10

                p.alive = False
                break

        return score_gained

    def _resolve_enemy_projectiles(self, enemy_projectiles: list, hero) -> None:
        """Пули врагов (например, бандита), долетевшие до героя."""
        for p in enemy_projectiles:
            if not p.alive:
                continue
            if hero.rect.colliderect(p.rect):
                hero.take_damage(p.damage)
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
                timer = self.ZOMBIE_ATTACK_INTERVAL
            self._zombie_hit_timers[zid] = timer

        # чистим мёртвых
        alive_ids = {id(z) for z in alive_zombies}
        self._zombie_hit_timers = {
            k: v for k, v in self._zombie_hit_timers.items() if k in alive_ids
        }