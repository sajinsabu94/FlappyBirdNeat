import pygame
from pygame.locals import *
import sys
import random
import os
import neat

pygame.init()

clock = pygame.time.Clock()
fps = 60

size = width, height = 400, 600
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Flappy game')

#define font
font = pygame.font.SysFont('Bauhaus 93', 20)
white = (255, 255, 255)

#define game var
ground_scroll = 0
scroll_speed = 4
flying = True
gameover = False
pipegap = 150
pipe_freq = 1500 #milliseconds
last_pipe = pygame.time.get_ticks() - pipe_freq
score = 0
max_score = 0
pipe_pass = False

gen = 0

#images
bg = pygame.image.load('assets/background.png')
ground = pygame.image.load('assets/base.png')

def draw_text(text, font, text_col, x,y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

def reset_game():
    pipe_group.empty()
    birds[0].rect.x = 70
    birds[0].rect.y = int(height/2)

    birds[1].rect.x = 70
    birds[1].rect.y = int(height/3)

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(0,3):
            img = pygame.image.load(f'assets/{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def jump(self):
        self.vel = -10
        self.rect.y += int(self.vel)


    def update(self):
        
        #gravity
        if flying:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 550:            
                self.rect.y += int(self.vel)

        if not gameover:
            #jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
            
            # handle the animation
            self.counter += 1
            flap_cooldown = 15

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            #rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.image.load(f'assets/dead.png')

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        super().__init__()
        self.image = pygame.image.load(f'assets/bottom.png')
        self.rect = self.image.get_rect()

        #if position 1 from top, -1 from bottom
        if position == 1:
            self.image = pygame.image.load(f'assets/top.png')
            self.rect.bottomleft = [x,y - int(pipegap/2)]
        else:
            self.rect.topleft = [x,y + int(pipegap/2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right<0:
            self.kill()

def flappybird(genomes, config):
    global ground_scroll, gameover, flying, scroll_speed, flying, pipegap, pipe_freq, last_pipe, score, max_score, pipe_pass, pipe_group, flappy, birds, gen

    score = 0
    gen += 1
    
    bird_group = pygame.sprite.Group()
    pipe_group = pygame.sprite.Group()


    #birds = [Bird(70, int(height/3)), Bird(70, int(height/2))]

    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        bird = Bird(70, int(height/3))
        bird_group.add(bird)
        birds.append(bird)
        ge.append(genome)
    
    #flappy = Bird(70, int(height/2))
    #bird_group.add(flappy)
    #bird_group.add(birds[0])
    #bird_group.add(birds[1])

    run = True
    while run:

        clock.tick(fps)

        #draw bg
        screen.blit(bg, (0, 0))

        #draw bird
        bird_group.draw(screen)
        bird_group.update()

        #draw pipe
        pipe_group.draw(screen)

        #draw ground
        screen.blit(ground, (ground_scroll, 550))

        #check the score
        if len(pipe_group) > 0 and len(bird_group) > 0:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
               and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
               and pipe_pass == False:
                pipe_pass = True
            if pipe_pass:
                if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                    for bird in birds:
                        ge[birds.index(bird)].fitness += 5
                    score += 1
                    if score > max_score:
                        max_score = score
                    pipe_pass = False

            draw_text(f'Gen : {gen}', font, white, 20, 20)
            draw_text(f'Fitness : {max_score}', font, white, 20, 45)
            draw_text(f'Current Score : {score}', font, white, 20, 70)

        #scroll ground
        #print(gameover, flying)
        if not gameover and flying:
            #generate new pipes
            if len(pipe_group) == 0:
                pipe_height = random.randint(-100, 100)
                btm_pipe = Pipe(width, int(height/2) + pipe_height, -1)
                top_pipe = Pipe(width, int(height/2) + pipe_height, 1)
                pipe_group.add(btm_pipe)
                pipe_group.add(top_pipe)
            '''  
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_freq:
                pipe_height = random.randint(-100, 100)
                btm_pipe = Pipe(width, int(height/2) + pipe_height, -1)
                top_pipe = Pipe(width, int(height/2) + pipe_height, 1)
                pipe_group.add(btm_pipe)
                pipe_group.add(top_pipe)

                last_pipe = time_now
            '''
            #move and reset ground
            ground_scroll -= scroll_speed
            if abs(ground_scroll) > 1079:
                ground_scroll = 0

            pipe_group.update()

        if len(pipe_group) > 0 and len(bird_group) > 0:
            for x, bird in enumerate(birds):  # giving each bird a fitness of 0.1 for each frame it stays alive
                ge[x].fitness += 0.1
                #print(pipe_group)
                # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
                output = nets[birds.index(bird)].activate(
                    (bird.rect.y, abs(bird.rect.y - pipe_group.sprites()[0].rect.top), abs(bird.rect.y - pipe_group.sprites()[1].rect.bottom)))

                if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over, then 0.5 jump
                    bird.jump()


        for bird in birds:
            if bird.rect.top < 0 or bird.rect.bottom > 550:
                ge[birds.index(bird)].fitness -= 1
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.remove(bird)
                #birds.pop(birds.index(bird))
                
                bird.kill()
            if len(birds) == 0:
                #gameover = True
                run = False
                pipe_group.empty()
                bird_group.empty()
                
        #look for collision
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False):
            col_bird = list(pygame.sprite.groupcollide(bird_group, pipe_group, False, False))
            for cbird in col_bird:
                for bird in birds: 
                    if bird.rect == cbird.rect:
                        ge[birds.index(bird)].fitness -= 1
                        nets.pop(birds.index(bird))
                        ge.pop(birds.index(bird))
                        birds.remove(bird)
                        bird.kill()
                        print(len(birds))
            if len(birds) == 0:
                #gameover = True
                run = False
                pipe_group.empty()
                bird_group.empty()

        if gameover == True and pygame.mouse.get_pressed()[0] == 1:
            print('clicked')
            flying = True
            gameover = False
            score = 0
            
            birds = [Bird(70, int(height/3)), Bird(70, int(height/2))]    
            #flappy = Bird(70, int(height/2))
            #bird_group.add(flappy)
            bird_group.add(birds[0])
            bird_group.add(birds[1])
            
            reset_game()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                print('clicked', flying, gameover)
            if event.type == pygame.MOUSEBUTTONDOWN and flying == False and gameover == False:
                flying = True

        pygame.display.update()

def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run for up to 50 generations.
    winner = p.run(flappybird, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)

#flappybird()

#pygame.quit()


