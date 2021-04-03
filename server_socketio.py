import socketio


import sys
import eventlet
import cv2
import pickle
import subprocess
from PIL import Image

sio=socketio.Server()

username_password={'rahul':'123','palak':'123'}

friend_list_clients={}
room_list={}
valid_room=[]

app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})
all_client={}

@sio.event
def want_add_friend(sid,data):
    username=data['username']
    friendname=data['friendname']
    friendid=data['friendid']


    if friend_list_clients.get(username,'0')=='0':

        friend_list_clients[username]=[]
        friend_list_clients[username].append(friendname)
        sio.emit('friend_added_to_client',{'friendname':friendname},sid)
    else:
        if friendname in friend_list_clients[username]:
            sio.emit('friend_already',{'friendname':friendname},sid)
        else:
            friend_list_clients[username].append(friendname)
            sio.emit('friend_added_to_client', {'friendname': friendname}, sid)

@sio.event
def show_client_friends(sid,data):
    if friend_list_clients.get(data['username'],'0')=='0':
        sio.emit('empty_friend_list',{'data':'Friend List Empty'},sid)
    else:
        friendlist=friend_list_clients[data['username']]
        sio.emit('show_friends',{'friends':friendlist},sid)

@sio.event
def remove_friend(sid,data):
    username=data['username']
    friendname=data['friendname']
    if friend_list_clients.get(username,'0')=='0':
        sio.emit('empty_friend_list', {'data': 'Friend List Empty'}, sid)
    else:
        client_friends=friend_list_clients[username]
        if friendname not in client_friends:
            sio.emit('friend_not_inlist', {'data': 'Friend Not In The List'}, sid)

        else:
            friend_list_clients[username].remove(friendname)
            sio.emit('friend_removed',{'data':friendname},sid)


@sio.event
def find_friend(sid,data):
    friend_name=data['friendname']
    username=data['username']
    if all_client.get(friend_name,'0')=='0':
        sio.emit('friend_not_exist',friend_name,sid)

    else:
        sio.emit('friend_exist',{'friendname':friend_name,'friend_id':all_client[friend_name],'username':username},sid)

@sio.event
def check_verify(sid,data):
    username,password=data['username'],data['password']
    if username_password.get(username,'0')=='0':
        sio.emit('not_exist',username,sid)
    else:
        if username_password[username]==password:
            sio.emit('valid_user',username,sid)
        else:
            sio.emit('wrong_password',username,sid)


@sio.event
def create_room(sid,data):
    roomname=data['roomname']
    username=data['username']
    if roomname not in valid_room:
        if room_list.get(username,'0')=='0':
            room_list[username]=[]
            room_list[username].append(roomname)
            sio.enter_room(sid, roomname)
            valid_room.append(roomname)
            sio.emit('room_created', {'data': 'Room Created','roomname':roomname}, sid)
        else:
            room_list[username].append(roomname)
            sio.enter_room(sid, roomname)
            valid_room.append(roomname)
            sio.emit('room_created', {'data': 'Room Created','roomname':roomname}, sid)

    else:
        sio.emit('room_occupied',{'data':'Room Occupied'},sid)


@sio.event
def room_message(sid,data):
    roomname=data['roomname']
    sendername=data['username']
    msg=data['data']
    sio.emit('receive_message', '\n' + sendername + ' : ' + msg,room=roomname)

@sio.event
def render(sid,data):

    image=pickle.loads(data)
    cv2.imshow(str(sid),image)
    if cv2.waitKey(1)==113:
        sys.exit(1)





@sio.event
def join_room(sid,data):
    roomname = data['roomname']
    username = data['username']
    if roomname in valid_room:
        sio.enter_room(sid,roomname)
        sio.emit('entered_room',{'data':'You Entered In The Room','roomname':roomname},sid)

    else:
        sio.emit('room_not_exist',{'data':'Room not Created ','roomname':roomname},sid)







@sio.event
def leave_room(sid,data):
    roomname = data['roomname']
    username = data['username']
    if roomname in valid_room:
        sio.leave_room(sid,roomname)
        sio.emit('leaved_room',{'roomname':roomname},sid)
    else:
        sio.emit('wrong_room',{'roomname':roomname},sid)




@sio.event
def close_room(sid,data):
    roomname = data['roomname']
    username = data['username']
    if roomname in valid_room:
        if roomname in room_list[username]:
            valid_room.remove(roomname)
            room_list[username].remove(roomname)

            sio.close_room(sid, roomname)
            sio.emit('closed_room',{'data':'Room closed'},sid)

        else:
            sio.emit('not_permission',{'data':'You Have Not Permission'},sid)
    else:

        sio.emit('wrong_room', {'roomname': roomname}, sid)





@sio.event
def new_user(sid,data):
    username=data['username']
    password=data['password']
    username_password[username]=password
    sio.emit('new_user_added',username,sid)



@sio.event
def client_name(sid,data):
    name=data

    all_client[name] = sid

    print(all_client)







@sio.event
def take_message(sid,data):
    sendername=data['username']
    receivername=data['friendname']
    msg=data['data']
    sio.emit('receive_message','\n'+sendername+' : '+msg,all_client[receivername])

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)






