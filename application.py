from http import HTTPStatus
from datetime import datetime
from flask import Flask,request,jsonify
from utils import*
import secrets
import hashlib

app=Flask(__name__)

@app.route('/')
def index():
    return "Welcome to my bibliotech!\
    \nYou must be logged in to enjoy many great things!\
    \nLet's go create an account or log in to your account!"

@app.route('/register',methods=['POST'])
def register(): 
    #preluare date
    first_name=request.form['first_name']
    last_name=request.form['last_name']
    email=request.form['email']
    password=request.form['password']
    typeUser=request.form['type']
    new_pass=hashlib.sha256(password.encode()) #parola va fi hash-uita in formatul SHA256 pentru a putea fi salvata in fisier
    #verificare date introduse pentru typeUser
    if typeUser not in ['Administrator', 'Simple User']:
        return jsonify({'message': 'Invalid type'}),HTTPStatus.FORBIDDEN
    #verificare existenta utilizator 
    if check_user(email):
        return jsonify({'message': 'User already exists'}),HTTPStatus.FORBIDDEN
    user={
        "first_name":first_name,
        "last_name":last_name,
        "email":email,
        "password":str(new_pass.hexdigest()),
        "type":typeUser,
        "deviations":0,
        "status":"ok"}

    auth_token=secrets.token_hex(5) #preluare valoare token unica generata aleator
    user.update({'auth_token': str(auth_token)})
    write_file(user, 'users.json')
    del user['password']
    del user['auth_token']
    del user['deviations']
    del user['status']
    return jsonify(user),HTTPStatus.OK

@app.route('/login',methods=['POST'])
def login():
    #preluare date
    email=request.form['email']
    password=request.form['password']
    new_password=hashlib.sha256(password.encode('utf-8'))
    #verificare existenta utilizator pentru returnare valoare token
    if  check_user(email) and check_user(new_password.hexdigest()):
        auth_token=get_token(email)
        return jsonify({'auth_token':auth_token}),HTTPStatus.OK
    else:
        return jsonify({'Username does not exists!':email } )

@app.route('/book',methods=['POST'])
def add_book():
    #preluare date
    request_auth_token=request.form['auth_token']
    book_name=request.form['book_name']
    book_author=request.form['book_author']
    book_description=request.form['book_description']
    #verificare user pe baza tokenului introdus
    user_type = get_user(request_auth_token)
    if user_type is None:  
        return jsonify ({'message': 'Wrong auth_token'}),HTTPStatus.FORBIDDEN 
    if user_type != 'Administrator':
        return jsonify ({'message': 'Simple user'}),HTTPStatus.FORBIDDEN  
    books=read_file('books.json')
     #preluarea ultimului id din lista pentru incrementare
    book={
                    'id':len(books)+1,
                    'book_name':book_name,
                    'book_author':book_author,
                    'book_description':book_description
                    }
    #verificare existenta carte in fisier, scriere in fisier in cazul in care nu exista
    if check_book(book_name)==True:
            return jsonify ({ 'Book already exists':book_name})
    book.update({'status': 'available', 'rating': 0, 'reviews':{"review_author": " ",
   "rating": 0,"text": " "}})
    write_file(book,'books.json')
    return jsonify(book), HTTPStatus.OK

@app.route('/books',methods=['POST'])
def add_books():
    #preluare date
    request_auth_token=request.form['auth_token']
    data=eval(request.form['data'])
    book_name=data.get('book_name')
    book_author=data.get('book_author')
    book_description=data.get('book_description')
    #verificare user pe baza tokenului introdus
    user_type = get_user(request_auth_token)
    if user_type is None:  
        return jsonify ({'message': 'Wrong auth_token'}),HTTPStatus.FORBIDDEN 
    if user_type != 'Administrator':
        return jsonify ({'message': 'Simple user'}),HTTPStatus.FORBIDDEN 
    books=read_file('books.json')
    book={
             'id':len(books)+1,
             'book_name':book_name,
             'book_author':book_author,
             'book_description':book_description
            }
    #verificare existenta carte in fisier, scriere in fisier in cazul in care nu exista
    if check_book(book_name)==True:
            return jsonify ({ 'Book already exists':book_name})
    book.update({'status': 'available', 'rating': 0, 'reviews':{"review_author": " ",
   "rating": 0,"text": " "}})
    write_file(book,'books.json')
    return jsonify(book), HTTPStatus.OK

@app.route('/book/get',methods=['GET'])
def get_book():
    #preluare date
    request_auth_token=request.args.get('auth_token')
    book_id=int(request.args.get('id'))
    #preluare carte din fisier pe baza id-ului introdus
    book=getBook('books.json',book_id)
    #verificam in lista de carti existenta carte cu id
    if book is None:
        return jsonify({"message": "Book not found"}),HTTPStatus.FORBIDDEN
    #verificare tokenului introdus
    user_type = get_user(request_auth_token)
    if user_type is not None:  
        return jsonify(book),HTTPStatus.OK
    del book['reviews']['review_author'] # stergere date care nu se afiseaza in cazul in care nu este folosit tokenul
    return jsonify(book),HTTPStatus.OK

@app.route('/books/get')
def get_books():
    #preluare lista carti din fisier pentru afisare
    books=read_file('books.json')
    print(books)
    return jsonify({'books': books}),HTTPStatus.OK

@app.route('/transaction',methods=['POST'])
def add_transaction():
    #preluare date
    request_auth_token=request.form['auth_token']
    book_id=int(request.form['id'])
    borrow_time=request.form['borrow_time']
    #verificare tokenului introdus
    user_type = get_user(request_auth_token)
    if user_type is None:  
        return jsonify ({'message': 'Wrong auth_token'}),HTTPStatus.FORBIDDEN 
    transactions=read_file('transactions.json') #preluare id tranzactie pentru incrementere si verificare incadrare in limita de 5 tranzactii
    transactionId=len(transactions)+1
    if transactionId not in range(1,6):
        return jsonify({'message':'you have reached the limit of 5 transactions'}),HTTPStatus.NOT_ACCEPTABLE
    if int(borrow_time) not in range(1,21): #verificare incareare borrow_time in limita de 20 zile
        return jsonify({"message": "Value outside the rage"}),HTTPStatus.NOT_ACCEPTABLE
    #citire fisier pentru preluare date pe baza id introdus
    book=getBook('books.json',book_id)
    books=read_file('books.json')
    if book is None:#verificam exitenta carte
        return jsonify({"message": "Book not found"}),HTTPStatus.NOT_FOUND 
    if book['status']=='borrowed': #verificam statusul catii cu id-ul primit
        return jsonify({"message": "Book not available"}),HTTPStatus.NOT_FOUND  
    books.remove(book)#stergem carte pentru readaugare cu date actualizate in lista
    book["status"]='borrowed'  #actualizare date pentru cartea cu id
    books.append(book) #adaugare carte cu date actualizate in lista
    rewrite_file(books,'books.json') #introducere date actualizate in fisier
    transaction={
                'transactionId': transactionId,
                'book_id': book_id,
                'borrow_time':borrow_time
                }
    borrow_time= datetime.today()+timedelta(days=int(borrow_time))
    remaning_time=borrow_time-datetime.today() #calculare data limita de returnare
    transaction.update({'return date': str(borrow_time),'remaining_time':str(remaning_time),'number_of_extensions':0,'status':'borrowed'  })   #actualizare date tranzactie si scriere tranzactie in fisier       
    write_file(transaction,'transactions.json')
    return jsonify({'You borrow ':book['book_name'],
         'transactionId':transactionId}),HTTPStatus.OK
    
@app.route('/transaction/get')
def get_transaction_by_id():
    request_auth_token=request.args.get('auth_token')
    id=int(request.args.get('id'))
    #verificare tokenului introdus
    user_type = get_user(request_auth_token)
    if user_type is None:  
        return jsonify ({'message': 'Wrong auth_token'}),HTTPStatus.FORBIDDEN 
    #preluare tranzactie din fisier pe baza id-ului pentru afisare
    transaction=getTransaction('transactions.json',id)
    #verificam in existenta tranzactie cu id
    if transaction is not None:
        return jsonify(transaction),HTTPStatus.ACCEPTED
    return jsonify({"message": "Transaction not found"}),HTTPStatus.NOT_FOUND 

@app.route('/transactions')
def get_transactions():
    request_auth_token=request.args.get('auth_token')
    #verificare tokenului introdus
    user_type = get_user(request_auth_token)
    if user_type is None:  
        return jsonify ({'message': 'Wrong auth_token'}),HTTPStatus.FORBIDDEN 
    #preluare tranzactii din fisier pentru afisare
    transactions=read_file('transactions.json')
    return jsonify({'transactions': transactions}),HTTPStatus.OK

@app.route('/extend',methods=['POST'])
def extend():
    request_auth_token=request.form['auth_token']
    transactionId=int(request.form['transactionId'])
    extend_time=request.form['extend_time']
    #verificare tokenului introdus
    user_type = get_user(request_auth_token)
    if user_type is None:  
        return jsonify ({'message': 'Wrong auth_token'}),HTTPStatus.FORBIDDEN 
    if int(extend_time) not in range(1,6): #verificare data pentru incadrare in limita
        return jsonify({'error_message': 'Invalid borrow time'}),HTTPStatus.FORBIDDEN
    transaction=getTransaction('transactions.json',int(transactionId)) #preluare tranzactie din fisier pe baza id
    transactions=read_file('transactions.json') #preluare tranzactii din fisier
    transactions.remove(transaction)
    #preluare data ca si tip datetime pentru a putea adauga termenul de extindere
    return_date= datetime.strptime(transaction['return date'], "%Y-%m-%d %H:%M:%S.%f")+ timedelta(int(extend_time))#actualizare data de reurnare
    remaning_time= return_date - datetime.today() #calculare data limita de returnare
    #verificam in lista de tranzactii existenta tranzactie cu id
    for transaction in transactions:
        if transaction['transactionId']!=id:
            return jsonify({"message": "Transaction not found"}),HTTPStatus.NOT_FOUND
    if transaction["number_of_extensions"] == 2: #verificare limita numar extinderi termen
        return jsonify({"message": "You have reached the maximum number for term extension"}),HTTPStatus.NOT_FOUND  
    transaction['number_of_extensions'] += 1
    transaction['return date']=str(return_date)
    transaction['remaining_time'] =str(remaning_time)
    transactions.append(transaction)#adaugare tranzactie cu date actualizate in lista
    rewrite_file(transactions,'transactions.json')#rescriere lista actualizata
    return jsonify({'message':'You extended the loan term with '+ extend_time +' days'}),HTTPStatus.OK
   
@app.route('/return', methods=['POST'])
def init_return():
    request_auth_token=request.form['auth_token']
    transactionId=request.form['transactionId']
    #verificare tokenului introdus
    user_type = get_user(request_auth_token)
    if user_type is None:  
        return jsonify ({'message': 'Wrong auth_token'}),HTTPStatus.FORBIDDEN 
    transaction=getTransaction('transactions.json',int(transactionId)) #preluare tranzactie din fisier pe baza id
    transactions=read_file('transactions.json') #preluare tranzactii din fisier
    if transaction is None:
        return jsonify({"message": "Transaction not found"}),HTTPStatus.NOT_FOUND
    if transaction['status'] == 'is returned': #verificare daca exista cerere de returnare
        return jsonify({"message": "A return request has already been registered"}),HTTPStatus.NOT_FOUND 
    past = datetime.strptime(transaction['return date'],"%Y-%m-%d %H:%M:%S.%f") #preluare data ca tip datetime pentru a putea verifica daca termenul de returnare a fost depasit
    present = datetime.now() 
    transactions.remove(transaction)
    return_id=secrets.token_hex(2) #generare cod retur
    transaction.update({'return_id':return_id})
    transaction['status'] = 'is returned' # actualizare status
    users=read_file('users.json')
    for user in users: #preluare user pentru actualizare
        if user['auth_token']==request_auth_token:   
            if past.date() < present.date(): #verificare daca termenul de returnare a fost depasit
                users.remove(user)
                user['deviations']+=1
                users.append(user)
                rewrite_file(users,'users.json')
        if user['deviations']==1:
            transaction['number_of_extensions'] += 1 #preluare tranzactii pentru limitare numar de extinderi la 1 si rescriere in fisier
            transactions.append(transaction) 
            rewrite_file(transactions, 'transactions.json')
            return jsonify({'The deadline has been exceeded once. Registered return request with id : ':return_id}), HTTPStatus.FORBIDDEN 
        elif user['deviations']==2:  
            transaction['number_of_extensions'] += 1 #preluare tranzactii pentru limitare numar de extinderi la 1 si rescriere in fisier
            transactions.append(transaction) 
            rewrite_file(transactions, 'transactions.json')
            return jsonify({'The deadline has been exceeded twice. Registered return request with id : ':return_id}), HTTPStatus.FORBIDDEN
        elif user['deviations']==3:
            transaction['number_of_extensions'] += 2   #preluare tranzactii pentru eliminare numar de extinderi si rescriere in fisier
            transactions.append(transaction) 
            rewrite_file(transactions, 'transactions.json')
            return jsonify({'The deadline has been exceeded three times. Registered return request with id:  ':return_id }), HTTPStatus.FORBIDDEN  
        elif user['deviations']==4:
            for user in users:
                if user['auth_token']==request_auth_token:  #preluare user pentru actualizare
                    users.remove(user)
                    user['status']='user blocked'
                    users.append(user)
                    rewrite_file(users,'users.json')
                    transaction['number_of_extensions'] += 1 #preluare tranzactii pentru limitare numar de extinderi la 1 si rescriere in fisier
                    transactions.append(transaction) 
                    rewrite_file(transactions, 'transactions.json')
                    return jsonify({'The deadline has been exceeded four times. Registered return request with id : ':return_id }), HTTPStatus.FORBIDDEN  
        else:
            transactions.append(transaction) 
            rewrite_file(transactions, 'transactions.json')  #rescriere fisier cu date actualizate
            return jsonify({'Registered return request with id ': return_id,'You initiated a return request for the transaction':transaction['transactionId']}), HTTPStatus.FORBIDDEN       
  
@app.route('/returns', methods=['GET'])
def get_returns():
    request_auth_token=request.args.get('auth_token')
    #verificare tokenului introdus si tip user
    user_type = get_user(request_auth_token)
    if user_type is None:  
        return jsonify ({'message': 'Wrong auth_token'}),HTTPStatus.FORBIDDEN 
    if user_type != 'Administrator':
        return jsonify ({'message': 'Simple user'}),HTTPStatus.FORBIDDEN  
    transactions = read_file('transactions.json')
    for transaction in transactions: #preluare din fisier tranzactii cu status:'is returned'
        if transaction['status'] == 'is returned':   
            return jsonify({'transactions':transactions})
        return jsonify({"message": "Transaction not found"}),HTTPStatus.NOT_FOUND
    
@app.route('/return/end', methods=['POST'])
def return_book():
    request_auth_token=request.form['auth_token']
    return_id=request.form['return_id']
    #verificare tokenului introdus si tip user
    user_type = get_user(request_auth_token)
    if user_type is None:  
        return jsonify ({'message': 'Wrong auth_token'}),HTTPStatus.FORBIDDEN 
    if user_type != 'Administrator':
        return jsonify ({'message': 'Simple user'}),HTTPStatus.FORBIDDEN  
    transactions = read_file('transactions.json')
    for transaction in transactions: 
        if transaction['return_id'] == return_id: #verificare daca exista cerere de retur pe baza id
            transactions.remove(transaction)
            transaction['status']='returned'
            transactions.append(transaction)#adaugare tranzactie cu date actualizate in lista
            rewrite_file(transactions,'transactions.json')#rescriere lista actualizata  
            book_id=transaction['book_id']
            book=getBook('books.json',book_id)
            books=read_file('books.json')
            books.remove(book)#stergem carte pentru readaugare cu date actualizate in lista
            book["status"]='available'  #actualizare status pentru cartea cu id in fisierul de carti
            books.append(book) #adaugare carte cu date actualizate in lista
            rewrite_file(books,'books.json') #introducere date actualizate in fisier
            return jsonify({'The return was successfully completed':{'transactionId':transaction['transactionId'],'book returned':book['book_name']}}),HTTPStatus.ACCEPTED
    return jsonify({"message": "Transaction not found"}),HTTPStatus.NOT_FOUND
               
@app.route('/review', methods=['POST'])
def post_review():
    #preluare date 
    request_auth_token=request.form['auth_token']
    book_id=int(request.form['book_id'])
    rating=int(request.form['rating'])
    text=request.form['text']
    users=read_file('users.json')
    for user in users: #preluare nume user pentru adaugare la review_author
        if user['auth_token']==request_auth_token:
            user_name=user['first_name']
    user_type = get_user(request_auth_token)
    if user_type is None:    #verificare tokenului introdus 
        return jsonify ({'message': 'Wrong auth_token'}),HTTPStatus.FORBIDDEN  
    if int(rating) not in range(1,6): #verificare valoare rating
        return jsonify ({'message': 'Wrong value'}),HTTPStatus.FORBIDDEN  
    book=getBook('books.json',book_id) #preluare carte pe baza id
    books=read_file('books.json')
    if book_id is  None:
        return jsonify({"message": "Book not found"}),HTTPStatus.NOT_FOUND
    val_rating=0
    for book in books:
        if book['id']==book_id:
            val_rating+=book['rating'] 
    books.remove(book)#stergem carte pentru readaugare cu date actualizate in lista
    book['reviews']=({
        'review_author':user_name,
        'rating': rating,
        'text': text
            })
    print(book['reviews'])
    book['rating'] = round(val_rating+rating/ len(book['reviews'])*3, 2)# calculare medie rating
    books.append(book) #adaugare carte cu date actualizate in lista
    rewrite_file(books,'books.json') #introducere date actualizate in fisier
    return jsonify({'You posted a review for the book':book['book_name']}),HTTPStatus.ACCEPTED 
        
if __name__=='__main__':
    app.run(debug=True)



