from flask import Flask, request, jsonify, abort
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
#db_drop_and_create_all()

# ROUTES
@app.route('/drinks')
def get_drinks():
    '''
    implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
    '''
    try:
        # query the database for the drinks and format the response
        drinks = Drink.query.all()
        formatted_drinks = [drink.short() for drink in drinks]

    except Exception as e:
        err = e
        print('Err => ', {err})
        # abort on error
        abort(404)

    return jsonify({
        'success' : True,
        'drinks' : [formatted_drinks]
    })

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(token):
    '''
    implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
    '''

    try:
        # query the database for the drinks and format the response
        drinks = Drink.query.all()
        formatted_drinks = [drink.long() for drink in drinks]

        if len(drinks) == 0:
            raise AuthError({
                'code' : 'not found',
                'description' : 'no object was found'
            }, 404)

    except Exception as e:
        err = e
        print('Err => ', {err})
        raise AuthError({
            'code' : 'bad request',
            'description' : 'something went wrong'
        }, 400)

    return jsonify({
        'success' : True,
        'drinks' : [formatted_drinks]
    })

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink(token):
    '''
    implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
    '''

    #get the body of the json
    body = request.get_json()
    drink_title = body['title']
    drink_recipe = body['recipe']

    # convert to json object
    str_recipe = json.dumps(drink_recipe)

    # insert into the database
    drink = Drink(title = drink_title, recipe = str_recipe)
    formatted_drink = drink.long()

    try:
        drink.insert()

    except Exception as e:
        err = e
        print('Err => ', {err})

        #abort on error
        raise AuthError({
            'code' : 'bad request',
            'description' : 'something is not right'
        }, 400)

    return jsonify({
        'success' : True,
        'drinks' : [formatted_drink]
    })

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(token,**kwargs):
    id = kwargs['id']
    '''
    implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
    '''
    # get the json body
    body = request.get_json()


    drink = Drink.query.get(id)
    if drink is None:
        raise AuthError({
            'code' : 'not found',
            'description' : 'no object was found'
        }, 404) 

    try:
        drink_title = body.get('title', None)
        drink_recipe = json.dumps(body.get('recipe', None))

        # update the record in the database
        drink.title = drink_title
        drink.recipe = drink_recipe

        drink.update()


    except:
            # error
            raise AuthError({
            'code' : 'invalid claims',
            'description' : 'you are not allowed to do this'
        }, 403)

    formatted_drink = [drink.long()]


    return jsonify({
        'success' : True,
        'drinks' : [formatted_drink]
    })

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token,**kwargs):
    id = kwargs['id']
    '''
        implement endpoint
        DELETE /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should delete the corresponding row for <id>
            it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    '''
    try:
        # get drink from the database
        drink = Drink.query.get(id)
        if drink is None:
            abort(404)
    
        # delete drink
        drink.delete()
    except:
        # catch error
        abort(400)

    return jsonify({
        'success' : True,
        'deleted' : id
    })




# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
    implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


'''
    implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error_handling(error):
    response = jsonify(error.error)
    response.status_code = error.status_code

    return response

if __name__ == "__main__":
    app.debug = True
    app.run()
