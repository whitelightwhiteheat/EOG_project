import logging
import logging.config
import random
import thread
import time
import json
import collections
import datetime
import re
import os

from flask import Flask, request, redirect

here = os.path.dirname(__file__)
app = Flask(__name__, static_folder=os.path.join(here,'static'), static_url_path='/innovationlab/static')
logging.config.fileConfig(os.path.join(here,'logging.conf'))
logger = logging.getLogger('server')

@app.before_request
def log_request():
    logger.debug(request)

@app.after_request
def print_accesslog(response):
  app.logger.info('{} - {} - {}'.format(request.remote_addr, request.url, response.status_code))
  return response

# dictionary of all games
games={}

# each game itself holds a dictionary of game pieces
# each game piece is a list: [x,y,type,alive,points,pwset,password,hacked]

# the 3 game pieces types, plus not initialised type
defendType = 'rolstoel'
attackType = 'wolk'
rewardType = 'prijs'
noType = 'not_init'
max_players = 1
debug = False
gamesName = 'spel'
gamesNumber = 50

# default values for default player locations
defaultDefend = [80,330,defendType,1,0,0,0,0]
defaultAttack = [240,190,attackType,1,0,0,0,0]
defaultNotInit = [-1,-1,noType,0,0,0,0,0]
defaultReward1 = [400,90,rewardType,1,0,0,0,0]
defaultHillPDefend = [80,330,defendType,1,0,0,[0,0,0,0,0,0,0,0,0],0]
defaultHillPAttack = [240,190,attackType,1,0,0,[0,0,0,0,0,0,0,0,0],0]

@app.route('/innovationlab/games/initialize')
def initgames():
    n = 50
    logger.info("Initializing {n} games".format(n=n))
    for i in range(1, n+1):
      gamename = gamesName + str(i)
      games[gamename] = {'_defenders':0, '_attackers':0, 'reward1':list(defaultReward1)}
    return 'OK'

# returns true if position (x,y) corresponds with a wall
def hitWall(x,y):
  if pixelMap[x][y] != [255,255,255]:
    logger.debug('someone hit a wall')
    return True 

# returns true if user1 with new position (x,y) hits game piece denoted by user2 and updates user data accordingly
# indexes: [0-x,1-y,2-type,3-alive,4-points,5-pwset,6-password,7-hacked]
def hitGamePiece(gamedict, user1, x, y, user2):
  logger.debug('checking hit: {gamedict}, {user1}, {x}, {y}, {user2}'.format(**locals()))
  # we have collision
  if abs(x-gamedict[user2][0])<=10 and abs(y-gamedict[user2][1])<=10:
    # defining all game pieces collision game rules:
    # defender hits reward
    if gamedict[user1][2]==defendType and gamedict[user2][2]==rewardType:
      gamedict[user1][0] = x
      gamedict[user1][1] = y
      gamedict[user1][4] = gamedict[user1][4] + 1
      x2 = gamedict[user2][0]
      y2 = gamedict[user2][1]
      while x2 == gamedict[user2][0] and y2 == gamedict[user2][1]:
        x2 = 240 + 160*random.randrange(-1,2,2)
        y2 = 180 - 90*random.randrange(-1,2,2)
      gamedict[user2][0] = x2
      gamedict[user2][1] = y2
      return True;
    # an attacker hits a reward
    elif gamedict[user1][2]==attackType and gamedict[user2][2]==rewardType:
      gamedict[user1][0] = x
      gamedict[user1][1] = y
#      gamedict[user1][4] = gamedict[user1][4] + 1
      x2 = gamedict[user2][0]
      y2 = gamedict[user2][1]
      while x2 == gamedict[user2][0] and y2 == gamedict[user2][1]:
        x2 = 240 + 160*random.randrange(-1,2,2)
        y2 = 180 - 90*random.randrange(-1,2,2)
      gamedict[user2][0] = x2
      gamedict[user2][1] = y2
      return True;
    # a defender hits an attacker
    elif gamedict[user1][2]==defendType and gamedict[user2][2]==attackType:
      gamedict[user1][0] = 80
      gamedict[user1][1] = 330
      gamedict[user2][0] = 240
      gamedict[user2][1] = 190
      gamedict[user1][4] = gamedict[user1][4] - 5
      gamedict[user2][4] = gamedict[user2][4] + 5
      return True;
    # an attacker hits a defender
    elif gamedict[user1][2]==attackType and gamedict[user2][2]==defendType:
      gamedict[user1][0] = 240
      gamedict[user1][1] = 190
      gamedict[user2][0] = 80
      gamedict[user2][1] = 330
      gamedict[user1][4] = gamedict[user1][4] + 5
      gamedict[user2][4] = gamedict[user2][4] - 5
      return True;

  return False;

######################################################################

f = open(os.path.join(here,'img_array.txt'), 'r')
pixelMap = json.load(f)
f.close()

######################################################################

@app.route('/innovationlab/')
def root():
  return redirect('/innovationlab/static/index.html')

@app.route('/innovationlab/testconnection')
def test_connection():
  """Return OK."""
  return "OK"

@app.route('/innovationlab/games')
def get_games():
  """Return a list of known games."""
  return json.dumps(sorted(games.keys()))

@app.route('/innovationlab/games/status')
def get_status():
  """Return all information for all games."""
  return json.dumps(games)

@app.route('/innovationlab/<gamename>/status')
def get_game_status(gamename):
  """Return all information for the given game."""
  if not gamename in games:
    return json.dumps({'failed':True, 'msg':'Unknown game'})
  return json.dumps(games[gamename])

# initialises a game with the given gamename
@app.route('/innovationlab/<gamename>/init')
def init_game(gamename):
# only rewards need to be set here in the real multiplayer game - all other game pieces are active players
#  games[gamename] = {'_defenders':0, '_attackers':1, 'reward1':list(defaultReward1), 'car1':(defaultAttack)}
  logger.debug('Initializing {gamename}'.format(**locals()))
  games[gamename] = {'_defenders':0, '_attackers':0, 'reward1':list(defaultReward1)}
  return 'OK'

# resets a game with the given gamename
@app.route('/innovationlab/<gamename>/reset')
def reset_users(gamename):
  games[gamename].clear()
  games[gamename] = {'_defenders':0, '_attackers':0, 'reward1':list(defaultReward1)}
  return 'OK'


# sets password for a user, but only if it hasnt been set for that user yet
@app.route('/innovationlab/<gamename>/<username>/password/<pw>')
def set_user_password(gamename,username,pw):
  logger.debug('Setting password {pw} for user {username} in {gamename}'.format(**locals()))
  gamedict = games[gamename]
  playerdict = gamedict.get(username, list(defaultNotInit))
  if playerdict[5] == 0:
  # later add a check to see if pw satisfies the password rules
    playerdict[6] = int(pw)
    playerdict[5] = 1
    gamedict[username] = playerdict
  return 'OK'

@app.route('/innovationlab/<gamename>/<username>/hillpassword/password/<pw0>/<pw1>/<pw2>/<pw3>/<pw4>/<pw5>/<pw6>/<pw7>/<pw8>')
def set_user_hillp_password(gamename,username,pw0,pw1,pw2,pw3,pw4,pw5,pw6,pw7,pw8):
  gamedict = games[gamename]
  playerdict = gamedict.get(username, list(defaultNotInit))
  if playerdict[5] == 0:
  # later add a check to see if pw satisfies the password rules
    playerdict[6][0] = int(pw0)
    playerdict[6][1] = int(pw1)
    playerdict[6][2] = int(pw2)
    playerdict[6][3] = int(pw3)
    playerdict[6][4] = int(pw4)
    playerdict[6][5] = int(pw5)
    playerdict[6][6] = int(pw6)
    playerdict[6][7] = int(pw7)
    playerdict[6][8] = int(pw8)
    playerdict[5] = 1
    gamedict[username] = playerdict
  return 'OK'


# adds the player with the given username and type to the given game
@app.route('/innovationlab/<gamename>/<username>/init/<ptype>')
def init_user_profile(gamename,username,ptype):
  logger.debug('Initializing type {ptype} for user {username} in {gamename}'.format(**locals()))
  gamedict = games[gamename]
  if ptype == defendType and gamedict['_defenders'] < max_players:
    user = list(defaultDefend)
    gamedict['_defenders'] = gamedict['_defenders'] + 1;
  elif ptype == attackType and gamedict['_attackers'] < max_players:
    user = list(defaultAttack)
    gamedict['_attackers'] = gamedict['_attackers'] + 1;
  else:
    return 'Error initialising player'

  # if the user record already created when setting the password
  if gamedict.has_key(username):
    user[5] = gamedict.get(username)[5]
    user[6] = gamedict.get(username)[6]
    user[7] = gamedict.get(username)[7]

  gamedict[username] = user
  return 'OK'

@app.route('/innovationlab/<gamename>/<username>/hillpassword/init/<ptype>')
def init_user_hillp_profile(gamename,username,ptype):
  gamedict = games[gamename]
  if ptype == defendType and gamedict['_defenders'] < max_players:
    user = list(defaultHillPDefend)
    gamedict['_defenders'] = gamedict['_defenders'] + 1;
  elif ptype == attackType and gamedict['_attackers'] < max_players:
    user = list(defaultHillPAttack)
    gamedict['_attackers'] = gamedict['_attackers'] + 1;
  else:
    return 'Error initialising player'

  # if the user record already created when setting the password
  if gamedict.has_key(username):
    user[5] = gamedict.get(username)[5]
    user[6] = gamedict.get(username)[6]
    user[7] = gamedict.get(username)[7]

  gamedict[username] = user
  return 'OK'


# delete user profile
@app.route('/innovationlab/<gamename>/<username>/del')
def del_user_profile(gamename,username):
  game = games[gamename]
  del game[username]
  return 'OK'

# show the user profile for that user
@app.route('/innovationlab/<gamename>/<username>/get')
def show_user_profile(gamename,username):
  if not gamename in games:
    logger.error("Game not known: {0}".format(gamename))
    return ''
  game = games[gamename]
  if not username in game:
    logger.error("User not known: {0}/{1}".format(username, gamename))
    return ''
  return '%d %d %s %d %d' % (game[username][0],game[username][1],game[username][2],game[username][3],game[username][4])

# function that executes commands
def do_cmd(game, username, cmd):
  logger.debug('Doing {cmd} for {username} in {game}'.format(**locals()))
  x = game[username][0]
  y = game[username][1]

  if cmd == "right":
    x = x+20
  elif cmd == "left":
    x = x-20
  elif cmd == "up":
    y = y-20
  elif cmd == "down":
    y = y+20
  # extra command for the hacker
  elif cmd == "h":
    game[username][7] = 1

  #check if we hit wall
  if not(hitWall(x,y)):

    #check if we hit any of the other players or rewards
    hitP = False
    for k,v in game.iteritems():
      if k!='_defenders' and k!='_attackers' and k != username:
        if hitGamePiece(game, username, x, y, k):
          hitP = True
          break

    if not(hitP):
      game[username][0] = x
      game[username][1] = y

  return 'OK'


#execute command only if the password pw is correct and the player is initialised
# indexes: [0-x,1-y,2-type,3-alive,4-points,5-pwset,6-password,7-hacked]
@app.route('/innovationlab/<gamename>/<username>/<cmd>/<pw>')
def exec_cmd(gamename,username, cmd, pw):
  logger.debug('Execute command {} for {} in {}'.format(cmd,username,gamename))
  game = games[gamename]
  if int(pw) == game[username][6] and game[username][2] != noType:
    return do_cmd(game, username, cmd)

  return 'OK'

@app.route('/innovationlab/<gamename>/<username>/hillpassword/<cmd>/<count0>/<count1>/<s0>/<s1>/<s2>')
def exec_cmd_hill(gamename,username, cmd, count0, count1, s0, s1, s2):
  game = games[gamename]
# Vincent: password verification for Hill game
# Vincent: to add later: check that counter is larger than previous time
# Vincent: server computes the expected 3 integers
  c = 0
  if cmd == "up":
    c = 8 
  elif cmd == "left":
    c = 4
  elif cmd == "right":
    c = 6
  elif cmd == "down":
    c = 2
  elif cmd == "h":
    c = 5
  password = game[username][6]
  t0 = int(password[0]) * int(count0) + int(password[1]) * int(count1) + int(password[2]) * c
  t1 = int(password[3]) * int(count0) + int(password[4]) * int(count1) + int(password[5]) * c
  t2 = int(password[6]) * int(count0) + int(password[7]) * int(count1) + int(password[8]) * c
# Vincent: check if received tags match computed tags:
  if (t0 == int(s0)) and (t1 == int(s1)) and (t2 == int(s2)) and game[username][2] != noType:
    return do_cmd(game, username, cmd)

  return 'OK'


# check if password was guessed correctly
@app.route('/innovationlab/<gamename>/<username>/hacked')
def check_hacked_state(gamename,username):
  gamedict = games[gamename]
  userdict = gamedict.get(username, list(defaultNotInit))
  if userdict[7] == 1:
#Vincent: returning the password instead of 'y' is safer against racing conditions
    return str(userdict[6])
  return 'n'

# return data on all the other game pieces by type
@app.route('/innovationlab/<gamename>/<username>/getPiecesLocByType/<typeToGet>')
def get_pieces_by_type(gamename,username,typeToGet):
  game = games[gamename]

  res = ''

  for k,v in game.iteritems():
    if k!='_defenders' and k!='_attackers' and k!=username  and v[2]==typeToGet:
      res = res + `v[0]` + ' ' + `v[1]` + ' ' + `v[3]` + ' '

  res = res.strip()
  if debug:
    logger.debug("Location for {0}: {1}".format(typeToGet,res))
  return res

isdate = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9,:]* - ")

@app.route('/innovationlab/log/', defaults={'readloglines': 1000})
@app.route('/innovationlab/log/<int:readloglines>')
def get_log(readloglines):
  #return json.dumps([{'time':t, 'msg':r.getMessage()} for t,r in fifo_logger.queue])
  with open("logs/server.log", "r") as f:
    f.seek (0, 2)           # Seek @ EOF
    fsize = f.tell()        # Get Size
    f.seek (max (fsize-readloglines*int(1024/5), 0), 0) # Set pos @ last n chars (assumes that a line is <200 bytes)
    lines = f.readlines()       # Read to end

  r = []
  for line in lines[-readloglines:]:
    m = isdate.match(line)
    if not m is None and \
       not "/get" in line and \
       not "static" in line and \
       not "/log" in line:
      try:
        t,msg = line.split(' - ', 1)
        r.append({'time':t, 'msg':msg})
      except ValueError:
        pass
  return json.dumps(r)


if __name__ == '__main__':
    from waitress import serve
    initgames()
    serve(app, host='0.0.0.0', port=5000, expose_tracebacks=True)
