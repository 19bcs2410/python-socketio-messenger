import socketio
import sys
import cv2
import pickle
import subprocess
from PIL import Image
cio=socketio.Client()
global notbusy
notbusy=True
import time

global name

@cio.event
def connect():
    print('Connected To Messenger Server\n')



@cio.event
def disconnect():
    print('disconnected from server')

@cio.event
def receive_message(data):
    print(data)

cio.connect('http://127.0.0.1:5000')
username=input("\nEnter your username:").strip()
password=input("\nEnter you password:").strip()
cio.emit('check_verify',{'username':username,'password':password})

@cio.event
def new_user_added(data):
    print("\nYou Successfuly Created Account")
    print('\n close Connection and Sigin Again')
    sys.exit(1)

@cio.event
def not_exist(data):
    print('Not exist This username: ',data)
    print('\n Sinup (yes//no):')
    ans=input('\nEnter choice: ').strip()
    if ans=='yes':
        new_user = input('\nEnter New Username: ').strip()
        new_password = input('\n Enter new password: ').strip()
        while not new_user or not new_password:
            new_user=input('\nEnter New Username: ').strip()
            new_password=input('\n Enter new password: ').strip()
        cio.emit('new_user',{'username':new_user,'password':new_password})
    if ans=='no':
        sys.exit(1)

@cio.event
def friend_not_exist(data):
    print('\nThis friend not Exits: ',data)

@cio.event
def friend_not_inlist(data):
    print('\n'+data['data'])


@cio.event
def friend_removed(data):
    print("\nFriend Successfully Removed: ",data['data'])



@cio.event
def friend_added_to_client(data):
    print('\nFriend Succesfully Added: ',data['friendname'])

@cio.event
def friend_already(data):
    print('\nThis Friend Already In Friend List',data['friendname'])

@cio.event
def friend_exist(data):


    friendid = data['friend_id']
    print('\nFriend Found: ',data['friendname'])

    choice=input('\nWant Add In your FriendList(yes//no): ').strip()

    if choice =='yes':
        cio.emit('want_add_friend',{'friendname':data['friendname'],'friendid':friendid,'username':data['username']})

    else:
        print('not ok')



@cio.event
def show_friends(data):
    print('\nYour Friends List: \n')
    print(data['friends'])

@cio.event
def empty_friend_list(data):
    print('\n'+data['data'])

@cio.event
def room_created(data):
    print('\n'+data['data'])
    print('\nStart Chat: ')
    while True:
        input_msg = input().strip()
        if input_msg == 'back_home':
            break
        elif input_msg == 'help':
            print('\n1.back_home')
        else:
            if input_msg:
                cio.emit('room_message', {'data':input_msg,'roomname':data['roomname'],'username':name.strip()})
    print('\nYou are At HomePage')

@cio.event
def room_occupied(data):
    print('\n'+data['data'])

@cio.event
def entered_room(data):
    print('\n'+data['data']+data['roomname'])
    print('\nStart Chat: ')
    while True:
        input_msg = input().strip()
        if input_msg == 'back_home':
            break
        elif input_msg == 'help':
            print('\n1.back_home')
        else:
            if input_msg:
                cio.emit('room_message', {'data': input_msg, 'roomname': data['roomname'], 'username': name.strip()})
    print('\nYou are At HomePage')


@cio.event
def room_not_exist(data):
    print('\n'+data['data']+data['roomname'])

@cio.event
def leaved_room(data):
    print('\n'+'you left room '+data['roomname'])

@cio.event
def wrong_room(data):
    print('\n'+'You Entered Wrong Room '+data['roomname'])

@cio.event
def closed_room(data):
    print('\n'+data['data'])

@cio.event
def not_permission(data):
    print('\n'+data['data'])








@cio.event
def valid_user(data):
    global name

    name = input("\nEnter your Profile name: ")
    cio.emit('client_name', name.strip())
    while True:
        msg = input()
        if msg.strip()=='find friends':
            friend_name=input("\nEnter Friend Name: ").strip()
            cio.emit('find_friend',{'friendname':friend_name,'username':name.strip()})
        elif msg.strip()=='show friends':
            cio.emit('show_client_friends',{'username':name.strip()})

        elif msg.strip()=='remove friend':
            friend_name = input("\nEnter Friend Name: ").strip()
            cio.emit('remove_friend', {'friendname': friend_name, 'username': name.strip()})

        elif msg.strip()=='help':
            print('\n*****COMMANDS*****')
            print('\n1.find friends')
            print('\n2.show friends')
            print('\n3.remove friend')
            print('\n4.create room')

            print('\n5.leave room')
            print('\n6.close room')
            print('\n7.join room')
            print('\n8.select friend for message')
            print('\n******************')
        elif msg.strip()=='create room':
            room_name=input('\nEnter room name/No: ')
            cio.emit('create_room',{'username':name.strip(),'roomname':room_name.strip()})
        elif msg.strip()=='live video':
            cap=cv2.VideoCapture(0)

            while True:
                _,frame=cap.read()
                image=cv2.resize(frame,(500,500))
                image_data=pickle.dumps(image)
                cio.emit('render',image_data)

                if cv2.waitKey(1)==113:
                    break
            cap.release()
            cv2.destroyAllWindows()


        elif msg.strip()=='join room':
            room_name = input('\nEnter room name/No: ')
            cio.emit('join_room', {'username': name.strip(), 'roomname': room_name.strip()})



        elif msg.strip()=='leave room':
            room_name = input('\nEnter room name/No: ')
            cio.emit('leave_room', {'username': name.strip(), 'roomname': room_name.strip()})

        elif msg.strip()=='close room':
            room_name = input('\nEnter room name/No: ')
            cio.emit('close_room', {'username': name.strip(), 'roomname': room_name.strip()})


        elif msg.strip()=='select friend for message':
            friend_name = input("\nEnter Friend Name: ").strip()
            print('\n Selected')
            print('\nStart Chat: ')
            while True:
                input_msg=input().strip()
                if input_msg=='back_home':
                    break
                elif input_msg=='help':
                    print('\n1.back_home')
                else:
                    if input_msg:
                        cio.emit('take_message', {'friendname': friend_name, 'username': name.strip(),'data':input_msg})







@cio.event
def wrong_password(data):
    print('Wrong Password :',data)
    username = input("\nEnter your username:").strip()
    password = input("\nEnter you password:").strip()
    while not username or  not password:
        username = input("\nEnter your username:").strip()
        password = input("\nEnter you password:").strip()
    cio.emit('check_verify', {'username': username, 'password': password})


cio.wait()
