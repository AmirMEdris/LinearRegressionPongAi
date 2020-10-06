import pygame
import numpy as np
from math import atan,cos,sin
import pandas as pd
import pickle as pkl
pygame.init()
lr = pkl.load(open('model.pkl','rb'))
scaler = pkl.load(open('scaler.pkl','rb'))
def PredPos(ballxpos, ballypos
            ,paddlexpos, paddleypos,vector, theta
            ,trainedmodel,scaler):


    params = np.array([ballxpos, ballypos,paddlexpos, paddleypos,vector, theta]).reshape(1, -1)
    params = scaler.transform(params)
    return trainedmodel.predict(params)

win = pygame.display.set_mode((750,500))

pygame.display.set_caption('Pong game')

white = (255,255,255)
black = (0,0,0)

movespeed = 20

class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([10,75])
        self.image.fill(white)
        self.rect = self.image.get_rect()
        self.points = 0
class Ball(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([10,10])
        self.image.fill(white)
        self.rect = self.image.get_rect()
        self.speed = 7
        self.dx = 1
        self.dy = 0.5
    def collide(self):

        self.dx = -self.dx
        self.dy = np.random.randint(low=-4,high=4)/4

    def is_collided_with(self, padd):
        return self.rect.colliderect(padd.rect)
    def vector(self,ball):
        self.magnitude = ((self.dx)**2 + (self.dy)**2)**(1/2)
        self.theta = atan((self.dy/self.dx))
        vectorinfo = (f'magnitude:{self.magnitude}\n angle:{self.theta}')
        self.posx = ball.rect.x
        posxofrightwall = 715
        time = (715-self.posx)/self.dx
        self.yshouldbe = ball.rect.y + (self.magnitude*sin(self.theta)) * time
        return self.magnitude,self.theta,self.yshouldbe

paddle1 = Paddle()
paddle1.rect.x = 25
paddle1.rect.y = 225
paddle2 = Paddle()
paddle2.rect.x = 715
paddle2.rect.y = 255

ball = Ball()
ball.rect.x = 375
ball.rect.y = 250

all_sprites = pygame.sprite.Group()
all_sprites.add(paddle1,paddle2,ball)

score = 0
def redraw():
    win.fill(black)
    all_sprites.draw(win)
    pygame.display.update()


run = True
datalist = []
counter = 0
while run:
    pygame.time.wait(10)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    key = pygame.key.get_pressed()
    if key[pygame.K_w]:
        paddle1.rect.y += - movespeed
    if key[pygame.K_s]:
        paddle1.rect.y += movespeed
    vvv, vvvv, vvvvv = ball.vector(ball)
    # XXX=[ball.rect.x,ball.rect.y, paddle2.rect.y,vvv,vvvv, lr, scaler]
    paddle2.rect.y= PredPos(ball.rect.x,ball.rect.y
                            , paddle2.rect.x,paddle2.rect.y
                            ,vvv,vvvv
                            , lr, scaler)
    # if key[pygame.K_UP]:
    #     paddle2.rect.y += - movespeed
    # if key[pygame.K_DOWN]:
    #     paddle2.rect.y += movespeed
    ball.rect.x += ball.speed*ball.dx
    ball.rect.y += ball.speed*ball.dy
    if ball.is_collided_with(paddle1) or ball.is_collided_with(paddle2):
        ball.collide()
        vect1, tetha1, ypos = ball.vector(ball)
        datalist.append((ball.rect.x, ball.rect.y, paddle2.rect.x, paddle2.rect.y, vect1, tetha1, ypos,ball.rect.y))


    if ball.rect.y < 5 or ball.rect.y > 455:
        vect1, tetha1, ypos = ball.vector(ball)
        datalist.append((ball.dx, ball.dy, paddle2.rect.x, paddle2.rect.y, vect1, tetha1, ypos,ball.rect.y))
        ball.dy = -ball.dy
    if counter == 5:
        counter = 0
        vect1, tetha1, ypos = ball.vector(ball)
        # datalist.append((ball.dx, ball.dy, paddle2.rect.x, paddle2.rect.y, vect1, tetha1, ypos, ball.rect.y))
    if (ball.rect.x < 0 and ball.dx<0) or (ball.rect.x > 800 and ball.dx>0):
        vect1, tetha1, ypos = ball.vector(ball)
        ball.rect.x = 375
        ball.rect.y = 250
        score-=1
        if ball.rect.x >20:
            datalist.append((ball.rect.x, ball.rect.y, paddle2.rect.x, paddle2.rect.y, vect1, tetha1, ypos,ball.rect.y))

    counter +=1


    print(('ballxy:',ball.rect.x,ball.rect.y),('paddle xy',paddle2.rect.x,paddle2.rect.y))
    print(ball.vector(ball))
    redraw()

pygame.quit()
columnx = ['Ball_dx','Ball_dy','Ai_paddle_pos_x','Ai_paddle_pos_y','Ball_movement_vector_magnitude','Ball_movement_vector_angle','pred_ball_y_on_impact']
df = datalist
file1 = open('data.pkl','wb')
pkl.dump(df,file = file1)
