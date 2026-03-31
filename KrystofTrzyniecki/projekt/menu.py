import pygame # Knihovna pro grafiku
import settings # Přístup k barvám a rozlišení
import os # Práce se složkami pro načítání obrázků

class Menu: # Třída, která spravuje všechna menu ve hře
    def __init__(self, screen): # Spustí se při vytvoření menu
        self.screen = screen # Uloží si herní okno
        self.update_fonts() # Vytvoří písma správné velikosti
        self.update_buttons() # Vytvoří obdélníky pro tlačítka

    def update_fonts(self): # Funkce pro změnu velikosti písma podle rozlišení
        font_scale = settings.HEIGHT / 600 # Vypočítá měřítko podle výšky okna
        self.large_font = pygame.font.Font(None, int(85 * font_scale)) # Velké písmo (nadpisy)
        self.font = pygame.font.Font(None, int(45 * font_scale)) # Střední písmo (tlačítka)
        self.small_font = pygame.font.Font(None, int(30 * font_scale)) # Malé písmo (popisky)

    def update_buttons(self): # Funkce pro přepočet pozic tlačítek na střed okna
        w, h = settings.WIDTH // 2, settings.HEIGHT // 2 # Zjistí střed obrazovky
        btn_w, btn_h = int(240 * (settings.WIDTH / 800)), int(60 * (settings.HEIGHT / 600)) # Velikost tlačítka
        spacing = int(80 * (settings.HEIGHT / 600)) # Mezera mezi tlačítky

        # Definice obdélníků (Rect) pro hlavní tlačítka menu
        self.btn_play = pygame.Rect(w - btn_w // 2, h - spacing * 1.5, btn_w, btn_h) # Tlačítko PLAY
        self.btn_shop = pygame.Rect(w - btn_w // 2, h - spacing * 0.5, btn_w, btn_h) # Tlačítko SHOP
        self.btn_settings = pygame.Rect(w - btn_w // 2, h + spacing * 0.5, btn_w, btn_h) # Tlačítko SETTINGS
        self.btn_exit = pygame.Rect(w - btn_w // 2, h + spacing * 1.5, btn_w, btn_h) # Tlačítko EXIT

    def draw_button(self, rect, text, base_color): # Univerzální funkce pro vykreslení tlačítka
        mouse_pos = pygame.mouse.get_pos() # Zjistí, kde je myš
        # Pokud je myš nad tlačítkem, barva se trochu zesvětlí
        color = tuple(min(c + 40, 255) for c in base_color) if rect.collidepoint(mouse_pos) else base_color
        # Vykreslení stínu tlačítka (posunutý tmavý obdélník)
        pygame.draw.rect(self.screen, (20, 20, 20), (rect.x + 4, rect.y + 4, rect.width, rect.height), border_radius=15)
        pygame.draw.rect(self.screen, color, rect, border_radius=15) # Hlavní plocha tlačítka
        pygame.draw.rect(self.screen, settings.WHITE, rect, width=2, border_radius=15) # Bílý rámeček
        txt_surf = self.font.render(text, True, settings.WHITE) # Vytvoří text
        # Vykreslí text doprostřed tlačítka
        self.screen.blit(txt_surf, (rect.centerx - txt_surf.get_width()//2, rect.centery - txt_surf.get_height()//2))

    def draw(self, coins): # Vykreslení hlavního menu
        self.update_fonts() # Obnoví písma při změně rozlišení
        self.update_buttons() # Obnoví tlačítka při změně rozlišení
        for i in range(settings.HEIGHT): # Cyklus pro vytvoření jednoduchého přechodu (gradientu) pozadí
            color = (0, 0, max(0, 50 - i // (settings.HEIGHT // 50))) # Postupné tmavnutí modré
            pygame.draw.line(self.screen, color, (0, i), (settings.WIDTH, i)) # Vykreslí vodorovnou čáru

        title_main = self.large_font.render("SPACE SHOOTER", True, settings.YELLOW) # Titulek hry
        self.screen.blit(title_main, (settings.WIDTH // 2 - title_main.get_width() // 2, int(settings.HEIGHT * 0.1))) # Vykreslí titulek
        
        pygame.draw.circle(self.screen, settings.YELLOW, (35, 35), 15) # Žluté kolečko jako ikona mince
        self.screen.blit(self.font.render(f"{coins}", True, settings.YELLOW), (60, 18)) # Počet mincí

        self.draw_button(self.btn_play, "PLAY", (0, 100, 200)) # Vykreslí modré tlačítko PLAY
        self.draw_button(self.btn_shop, "SHOP", (0, 150, 100)) # Vykreslí zelené tlačítko SHOP
        self.draw_button(self.btn_settings, "SETTINGS", (80, 80, 80)) # Vykreslí šedé tlačítko nastavení
        self.draw_button(self.btn_exit, "EXIT", (150, 0, 0)) # Vykreslí červené tlačítko ukončení

    def handle_event(self, e): # Zpracovává kliknutí v menu
        if e.type == pygame.MOUSEBUTTONDOWN: # Pokud hráč kliknul tlačítkem myši
            if self.btn_play.collidepoint(e.pos): return "play" # Klikl na PLAY
            if self.btn_shop.collidepoint(e.pos): return "shop" # Klikl na SHOP
            if self.btn_settings.collidepoint(e.pos): return "settings" # Klikl na SETTINGS
            if self.btn_exit.collidepoint(e.pos): return "exit" # Klikl na EXIT
        return None # Pokud neklikl na nic

    def draw_login(self, user_input, pass_input, active_field, is_logging_in, login_error): # Menu pro přihlášení
        self.screen.fill((10, 10, 30)) # Tmavé pozadí
        title = self.large_font.render("SPACE SHOOTER", True, settings.WHITE) # Název hry
        self.screen.blit(title, (settings.WIDTH//2 - title.get_width()//2, 80)) # Vykreslí název
        
        u_label = self.small_font.render("Username:", True, settings.WHITE) # Text nad jménem
        self.screen.blit(u_label, (settings.WIDTH//2 - 150, 190)) # Pozice popisku
        u_rect = pygame.Rect(settings.WIDTH//2 - 150, 220, 300, 45) # Pole pro jméno
        u_color = settings.YELLOW if active_field == "user" else (100, 100, 100) # Žlutý rámeček, pokud se tam píše
        pygame.draw.rect(self.screen, (30, 30, 30), u_rect, border_radius=8) # Pozadí pole
        pygame.draw.rect(self.screen, u_color, u_rect, width=2, border_radius=8) # Rámeček pole
        self.screen.blit(self.font.render(user_input, True, settings.WHITE), (u_rect.x + 10, u_rect.y + 8)) # Vykreslí psaný text
        
        p_label = self.small_font.render("Password:", True, settings.WHITE) # Text nad heslem
        self.screen.blit(p_label, (settings.WIDTH//2 - 150, 280)) # Pozice popisku
        p_rect = pygame.Rect(settings.WIDTH//2 - 150, 310, 300, 45) # Pole pro heslo
        p_color = settings.YELLOW if active_field == "pass" else (100, 100, 100) # Žlutý rámeček, pokud se tam píše
        pygame.draw.rect(self.screen, (30, 30, 30), p_rect, border_radius=8) # Pozadí pole hesla
        pygame.draw.rect(self.screen, p_color, p_rect, width=2, border_radius=8) # Rámeček pole hesla
        self.screen.blit(self.font.render('*' * len(pass_input), True, settings.WHITE), (p_rect.x + 10, p_rect.y + 8)) # Heslo zobrazí jako hvězdičky
        
        if is_logging_in: # Pokud probíhá ověřování...
            msg = self.font.render("CONNECTING...", True, settings.YELLOW) # Zobrazí hlášku
            self.screen.blit(msg, (settings.WIDTH//2 - msg.get_width()//2, 380)) # Vykreslí hlášku
        elif login_error: # Pokud nastala chyba...
            err = self.font.render(login_error, True, settings.RED) # Zobrazí chybu červeně
            self.screen.blit(err, (settings.WIDTH//2 - err.get_width()//2, 380)) # Vykreslí chybu
            
        info = self.small_font.render("[TAB] Switch   [ENTER] Sign in", True, settings.GRAY) # Nápověda ovládání
        self.screen.blit(info, (settings.WIDTH//2 - info.get_width()//2, settings.HEIGHT - 50)) # Vykreslí nápovědu

    def draw_settings(self): # Menu nastavení hry
        self.screen.fill(settings.BLACK) # Černé pozadí
        title = self.large_font.render("SETTINGS", True, settings.WHITE) # Nadpis nastavení
        self.screen.blit(title, (settings.WIDTH//2 - title.get_width()//2, 50)) # Vykreslí nadpis
        
        diff_label = self.font.render("DIFFICULTY:", True, settings.YELLOW) # Popisek pro obtížnost
        self.screen.blit(diff_label, (settings.WIDTH//2 - diff_label.get_width()//2, 140)) # Pozice popisku
        d_btns = [] # Seznam pro tlačítka obtížností
        diffs = ["EASY", "MEDIUM", "HARD"] # Možné úrovně
        total_width = len(diffs) * 110 + (len(diffs) - 1) * 10 # Výpočet celkové šířky řady tlačítek
        start_x = settings.WIDTH // 2 - total_width // 2 # Počáteční X pro vycentrování
        
        for i, d in enumerate(diffs): # Pro každou obtížnost vytvoří tlačítko
            r = pygame.Rect(start_x + i * 120, 180, 110, 45) # Obdélník tlačítka
            color = settings.GREEN if settings.CURRENT_DIFF == d else settings.GRAY # Zelená, pokud je vybraná
            pygame.draw.rect(self.screen, color, r, border_radius=8) # Vykreslí tlačítko
            txt = self.small_font.render(d, True, settings.WHITE) # Název obtížnosti
            self.screen.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2)) # Vykreslí název
            d_btns.append((r, d)) # Uloží do seznamu pro pozdější kontrolu kliknutí
            
        res_label = self.font.render("RESOLUTION:", True, settings.YELLOW) # Popisek pro rozlišení
        self.screen.blit(res_label, (settings.WIDTH//2 - res_label.get_width()//2, 260)) # Pozice popisku
        res_btns = [] # Seznam pro tlačítka rozlišení
        for i, res in enumerate(settings.RES_OPTIONS): # Pro každé rozlišení ze settings.py
            r = pygame.Rect(settings.WIDTH // 2 - 110, 300 + i * 55, 220, 45) # Pozice pod sebou
            # Modrá barva, pokud toto rozlišení právě používáme
            color = settings.BLUE if (settings.WIDTH, settings.HEIGHT) == res else (60, 60, 60)
            pygame.draw.rect(self.screen, color, r, border_radius=8) # Vykreslí tlačítko rozlišení
            txt = self.font.render(f"{res[0]} x {res[1]}", True, settings.WHITE) # Text rozlišení
            self.screen.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2)) # Vykreslí text
            res_btns.append((r, res)) # Uloží pro kontrolu kliknutí
            
        back = pygame.Rect(settings.WIDTH//2 - 100, settings.HEIGHT - 80, 200, 50) # Tlačítko zpět
        pygame.draw.rect(self.screen, settings.RED, back, border_radius=12) # Červené pozadí
        txt = self.font.render("BACK", True, settings.WHITE) # Text zpět
        self.screen.blit(txt, (back.centerx - txt.get_width()//2, back.centery - txt.get_height()//2)) # Vykreslí text
        return d_btns, res_btns, back # Vrátí tlačítka, aby hlavní smyčka věděla, kde kontrolovat klik

    def draw_shop(self, total_coins, unlocked_skins, current_skin, shop_scroll): # Menu obchodu
        self.screen.fill(settings.BLACK) # Černé pozadí
        s_btns = [] # Seznam tlačítek v obchodu
        base_dir = os.path.dirname(__file__) # Složka skriptu
        for i, (name, data) in enumerate(settings.SKIN_DATA.items()): # Projde každou loď v obchodě
            y_pos = 110 + i * 150 + shop_scroll # Výpočet pozice s přičtením scrollování
            r = pygame.Rect(settings.WIDTH//2 - 250, y_pos, 500, 130) # Obdélník řádku lodi
            if -130 < y_pos < settings.HEIGHT: # Vykreslí loď jen pokud je vidět na obrazovce
                # Zelená, pokud ji už máme, šedá, pokud ne
                color = (30, 70, 30) if data[0] in unlocked_skins else (40, 40, 40)
                if data[0] == current_skin: color = settings.BLUE # Modrá, pokud je právě vybraná
                pygame.draw.rect(self.screen, color, r, border_radius=15) # Pozadí řádku
                pygame.draw.rect(self.screen, settings.WHITE, r, width=2, border_radius=15) # Bílý obrys
                
                try: # Pokus o vykreslení náhledu lodi
                    img_path = os.path.join(base_dir, "picture", data[0]) # Cesta k obrázku
                    ship_img = pygame.transform.scale(pygame.image.load(img_path).convert_alpha(), (110, 110)) # Načte a zmenší
                    self.screen.blit(ship_img, (r.x + 20, r.centery - 55)) # Vykreslí obrázek
                except: # Pokud obrázek chybí...
                    pygame.draw.rect(self.screen, settings.GRAY, (r.x + 20, r.centery - 55, 110, 110)) # Šedý čtverec
                
                # Určení textu statusu (VYBRÁNO / KOUPENO / KOUPIT za peníze)
                status = "SELECTED" if data[0] == current_skin else ("OWNED" if data[0] in unlocked_skins else f"BUY: {data[1]} C")
                self.screen.blit(self.font.render(name, True, settings.WHITE), (r.x + 150, r.y + 35)) # Název lodi
                self.screen.blit(self.font.render(status, True, settings.YELLOW if "BUY" in status else settings.WHITE), (r.x + 150, r.y + 75)) # Status
            s_btns.append((r, data)) # Uloží pro klikání
        
        # Horní fixní lišta s nápisem SHOP a kredity
        pygame.draw.rect(self.screen, settings.BLACK, (0, 0, settings.WIDTH, 110)) # Černý obdélník navrchu
        title = self.large_font.render("SHOP", True, settings.WHITE) # Nadpis SHOP
        self.screen.blit(title, (settings.WIDTH//2 - title.get_width()//2, 20)) # Vykreslí nadpis
        self.screen.blit(self.font.render(f"CREDITS: {total_coins}", True, settings.YELLOW), (20, 20)) # Vykreslí peníze
        
        # Spodní fixní lišta s tlačítkem ZPĚT
        pygame.draw.rect(self.screen, settings.BLACK, (0, settings.HEIGHT - 90, settings.WIDTH, 90)) # Lišta dole
        back = pygame.Rect(settings.WIDTH//2 - 100, settings.HEIGHT - 70, 200, 50) # Tlačítko BACK
        pygame.draw.rect(self.screen, settings.RED, back, border_radius=12) # Červené tlačítko
        txt = self.font.render("BACK", True, settings.WHITE) # Text zpět
        self.screen.blit(txt, (back.centerx - txt.get_width()//2, back.centery - txt.get_height()//2)) # Vykreslí text
        return s_btns, back # Vrátí seznam položek a tlačítko zpět

    def draw_game_over(self, score): # Obrazovka po prohře
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA) # Průhledná vrstva
        overlay.fill((80, 0, 0, 200)) # Tmavě červená s průhledností
        self.screen.blit(overlay, (0,0)) # Vykreslí vrstvu přes hru
        t = self.large_font.render("GAME OVER", True, settings.WHITE) # Velký nápis
        s = self.font.render(f"SCORE: {score}", True, settings.YELLOW) # Finální skóre
        self.screen.blit(t, (settings.WIDTH//2 - t.get_width()//2, 150)) # Vykreslí nápis
        self.screen.blit(s, (settings.WIDTH//2 - s.get_width()//2, 230)) # Vykreslí skóre
        
        btn_restart = pygame.Rect(settings.WIDTH//2 - 120, 330, 240, 60) # Tlačítko RESTART
        btn_menu = pygame.Rect(settings.WIDTH//2 - 120, 410, 240, 60) # Tlačítko MENU
        pygame.draw.rect(self.screen, (0, 150, 50), btn_restart, border_radius=15) # Zelený restart
        pygame.draw.rect(self.screen, (100, 100, 100), btn_menu, border_radius=15) # Šedé menu
        self.screen.blit(self.font.render("RESTART", True, settings.WHITE), (btn_restart.centerx - 55, btn_restart.centery - 12)) # Text restart
        self.screen.blit(self.font.render("MENU", True, settings.WHITE), (btn_menu.centerx - 40, btn_menu.centery - 12)) # Text menu
        return btn_restart, btn_menu # Vrátí obdélníky pro klikání

    def draw_pause(self): # Obrazovka při pauze
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA) # Průhledná vrstva
        overlay.fill((0, 0, 0, 180)) # Černá s vysokou průhledností
        self.screen.blit(overlay, (0,0)) # Zatemní hru
        t = self.large_font.render("PAUSED", True, settings.WHITE) # Nadpis pauzy
        self.screen.blit(t, (settings.WIDTH//2 - t.get_width()//2, 150)) # Vykreslí nadpis
        
        btn_cont = pygame.Rect(settings.WIDTH//2 - 120, 280, 240, 60) # Tlačítko POKRAČOVAT
        btn_menu = pygame.Rect(settings.WIDTH//2 - 120, 360, 240, 60) # Tlačítko MENU
        pygame.draw.rect(self.screen, settings.BLUE, btn_cont, border_radius=15) # Modré pokračovat
        pygame.draw.rect(self.screen, (100, 100, 100), btn_menu, border_radius=15) # Šedé menu
        self.screen.blit(self.font.render("CONTINUE", True, settings.WHITE), (btn_cont.centerx - 70, btn_cont.centery - 12)) # Text pokračovat
        self.screen.blit(self.font.render("MENU", True, settings.WHITE), (btn_menu.centerx - 40, btn_menu.centery - 12)) # Text menu
        return btn_cont, btn_menu # Vrátí obdélníky pro klikání