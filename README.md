BIBLIOTECH
------------
A REST API application to easily manage both the books of a library and its users, as well as the interaction between users and the library.

REQUIREMENTS
------------
This module requires no modules outside of Python 3.8.

CONFIGURATION
-------------
No system configuration changes are required.

INSTALLATION
-------------
https://code.visualstudio.com
https://www.postman.com


PROJECT STRUCURE
-------------
* utils.py: Certain functions used in application.py have been defined
* application.py:Application that has the following structure

* @app.route('/'): represents the home page (index page)

* @app.route('/register',methods=['POST']):the register method has the role of creating a user.Based on the retrieved data, we check if the user exists, and if it does not exist, we add the user to the file. The password is hashed before being entered into the file.

* @app.route('/login',methods=['POST']): the login method has the role of authenticating a user.Based on the email, if the user is registered, a token code will be returned.

* @app.route('/book',methods=['POST']):this method is used to add a book to the library.The token code is checked, the user type is checked and based on the perulated data,we check if the book exists,and if it does not exist is added to the file.The method returns the entered book

* @app.route('/books',methods=['POST']):this method is for adding books to the library.Token code verification, user verification. A list of books can be uploaded. If the book does not exist in the file, it is added to the file. The method returns the entered books.

* @app.route('/book/get',methods=['GET']):this method returns a book from the list based on the entered id.Token code verification. Based on the id value, the book corresponding to it is retrieved from the file. The method returns the book

* @app.route('/books/get'):this method returns a list of books from the libraryThe list of books in the file is retrieved. The method returns this list of books

* @app.route('/transaction',methods=['POST']):this transaction method will create a request to borrow a book.Token code check, eligibility check within the limit of 5 transactions, loan period eligibility check within the 20 day limit. Pick up book based on id, change status for it. Rewriting the book list with the updated data for the borrowed book. For the transaction data, the return limit date, the remaining term, adding the transaction to the list of transactions was calculated. The method returns the title of the borrowed book.

* @app.route('/transaction/get'):this method has the role of displaying the information of a transaction.Taking transaction from the file. The method returns the transaction data.

* @app.route('/transactions'):the method is to display the transaction history.Taking transactions from the file. The method returns the transactions.

* @app.route('/extend',methods=['POST'])the extend method has the role of extending the loan time of the book.Token code verification, extension time verification within the limit of 5 days, enrollment extension number verification within the limit of 2 times. Data recalculation for the return date, number of days left. Rewrite transaction with updated data. The method returns the number of days extending the term.

* @app.route('/return', methods=['POST']):the method will create a request to return a book.Check the token code, check the transaction id, check the card status, calculate if the return time has been exceeded for applying actions. Depending on the actions, updating data and rewriting files. The method returns the id generated for recording the return and if sanctions have been applied, the number of the user's sanctions is also returned.

* @app.route('/returns', methods=['GET']):the GET /returns method has the role of presenting the existing return requests.
* @app.route('/return/end', methods=['POST']):the POST /return/end method will end a request to return a book. Retrieve data for return based on return id. Transaction status change, card status change and their rewriting with the updated data in the files. The method returns the transaction id and card name for which the return was made

* @app.route('/review', methods=['POST']):the POST /review method is used to create a book review.Based on the token, the user's name is taken to add it to the review author. Picking up a book based on the id, adding data for review and rewriting it in the file.

To start the application locally, you can just run python3 application.py and this will launch the app on port 5000
If you navigate to http://localhost:5000, you will see the response created by the above route 

AUTHORS
-------------
Steluta Visan