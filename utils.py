import json
from datetime import timedelta, date

def read_file(filename):
    ''' citire fisier in format json'''
    with open(filename,'r+') as file:
        data = json.load(file)
    return data

def write_file(data,filename,):
    '''scriere fisier json in cazul in care dorim adaugare la datele deja existente'''
    datas=[]
    with open(filename,'r+') as file:
        datas = json.load(file)
    datas.append(data)
    with open(filename, 'w') as file:
        json.dump(datas,file,indent=1)
 
def rewrite_file(data,filename,):
    '''scriere fisier json in cazul in care rescriere '''
    with open(filename, 'w') as file:
        json.dump(data,file,indent=1)  
    
                     
def check_user(somthing):
    ''' verificare in user'''
    exists=False
    with open('users.json','r+') as file:
        for line in file.readlines():
            if somthing in line:
                exists=True
                return True       
    if  not exists:
        return False   
       
def check_book(book_name):
    '''
    Verificare existenta carte 
    '''
    exists=False
    with open('books.json','r+') as file:
        for line in file.readlines():
            if book_name in line:
                exists=True
                return True
    if  not exists:
        return False     
             
def get_token(email):
    ''' returnare cod token pe baza email'''
    with open('users.json', 'r+') as file:
         users = json.load(file)  
    token = None
    for user in users:
        if email== user['email']:
            token = user['auth_token']      
    return token
 
def get_user(auth_token):
    ''' returnare tip user pe baza tokenului'''
    with open('users.json', 'r+') as file:
        users = json.load(file)
        
    user_type = None
    for user in users:
        if auth_token == user['auth_token']:
            user_type = user['type']
    return user_type
        

def getBook(fileList,book_id):
    ''' preluare carte din fisier pe baza id-ului'''
    with open(fileList,'r') as file:
        books = json.load(file)
    for book in books:
        if book['id'] == book_id:
            return book
        
def getTransaction(fileList,id):
    ''' preluare tranzactie din fisier pe baza id-ului'''
    with open(fileList,'r') as file:
        transactions = json.load(file)
    for transaction in transactions:
        if transaction['transactionId'] == id:
            return transaction
       
