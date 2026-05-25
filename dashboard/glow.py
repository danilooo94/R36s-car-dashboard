import pygame

def glow_blit(surface, src_surf, pos, passes=3):
    """
    Blits src_surf at pos with a soft glow halo.
    Works on dark backgrounds via BLEND_ADD.
    """
    w, h = src_surf.get_size()
    x, y = pos
    pad = 18

    bg = pygame.Surface((w + pad * 2, h + pad * 2))
    bg.fill((0, 0, 0))
    bg.blit(src_surf, (pad, pad))

    small = pygame.transform.smoothscale(
        bg, (max(1, (w + pad * 2) // 4), max(1, (h + pad * 2) // 4))
    )
    blurred = pygame.transform.smoothscale(small, (w + pad * 2, h + pad * 2))

    for _ in range(passes):
        surface.blit(blurred, (x - pad, y - pad), special_flags=pygame.BLEND_ADD)

    surface.blit(src_surf, pos)
